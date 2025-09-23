from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import time

from app.database import get_db
from app.schemas import (
    LandAreaAnalysisRequest, LandAreaAnalysisResponse,
    PropertyValuationResponse, BeneficiaryScoreResponse, BeneficiaryScoreRequest,
    PropertyRecommendationResponse, RecommendationRequest,
    ModelExplanationResponse, UserInteractionCreate
)
from app.services.land_area_automation import LandAreaAutomationService
from app.services.ai_analyzer import LandSuitabilityAnalyzer
from app.services.location_service import LocationService
from app.models import User, Location, PropertyValuation, BeneficiaryScore, UserInteraction
from app.core.auth import get_current_user
from loguru import logger

router = APIRouter()

# Initialize services
automation_service = LandAreaAutomationService()
analyzer = LandSuitabilityAnalyzer()
location_service = LocationService()

@router.post("/comprehensive-analysis", response_model=LandAreaAnalysisResponse)
async def comprehensive_land_analysis(
    request: LandAreaAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive land area analysis combining:
    - Traditional land suitability analysis
    - AVM property valuation with uncertainty
    - Beneficiary scoring
    - Property recommendations
    - SHAP-based explanations
    """
    try:
        start_time = time.time()
        
        # Get or create location
        location = await location_service.get_or_create_location(
            db, request.address, request.latitude, request.longitude
        )
        
        # Perform comprehensive analysis using enhanced analyzer
        analysis_result = await analyzer.analyze_location_comprehensive(
            location, request, current_user.id, db
        )
        
        # Log user interaction
        background_tasks.add_task(
            log_user_interaction,
            current_user.id,
            analysis_result.property_valuation.id if analysis_result.property_valuation else None,
            "comprehensive_analysis",
            db
        )
        
        processing_time = (time.time() - start_time) * 1000
        analysis_result.processing_time_ms = int(processing_time)
        
        logger.info(f"Comprehensive analysis completed for user {current_user.id} in {processing_time:.2f}ms")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/property-valuation", response_model=PropertyValuationResponse)
async def get_property_valuation(
    request: LandAreaAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AVM-based property valuation with uncertainty estimation
    """
    try:
        # Get or create location
        location = await location_service.get_or_create_location(
            db, request.address, request.latitude, request.longitude
        )
        
        # Extract features and predict value
        features = await automation_service.extract_comprehensive_features(location, request, db)
        predicted_value, uncertainty = automation_service.predict_property_value_with_uncertainty(features)
        
        # Create and save property valuation
        property_valuation = PropertyValuation(
            location_id=location.id,
            property_type=request.property_type,
            beds=request.beds,
            baths=request.baths,
            sqft=request.sqft,
            year_built=request.year_built,
            lot_size=request.lot_size,
            predicted_value=predicted_value,
            value_uncertainty=uncertainty,
            price_per_sqft=features.get('avg_price_per_sqft', 0),
            valuation_date=datetime.utcnow()
        )
        
        db.add(property_valuation)
        db.commit()
        db.refresh(property_valuation)
        
        return property_valuation
        
    except Exception as e:
        logger.error(f"Property valuation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Valuation failed: {str(e)}")

@router.post("/beneficiary-score", response_model=BeneficiaryScoreResponse)
async def calculate_beneficiary_score(
    request: BeneficiaryScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate beneficiary score for a location or property
    """
    try:
        # Get location
        location = db.query(Location).filter(Location.id == request.location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Create analysis request for feature extraction
        analysis_request = LandAreaAnalysisRequest(
            latitude=location.latitude,
            longitude=location.longitude,
            custom_weights=request.custom_weights
        )
        
        # Extract features
        features = await automation_service.extract_comprehensive_features(
            location, analysis_request, db
        )
        
        # Calculate beneficiary score
        beneficiary_data = automation_service.calculate_beneficiary_score(
            features, request.custom_weights
        )
        
        # Save to database
        beneficiary_score = BeneficiaryScore(
            location_id=location.id,
            property_valuation_id=request.property_valuation_id,
            overall_score=beneficiary_data['overall_score'],
            value_score=beneficiary_data['value_score'],
            school_score=beneficiary_data['school_score'],
            safety_score=beneficiary_data['safety_score'],
            environmental_score=beneficiary_data['environmental_score'],
            accessibility_score=beneficiary_data['accessibility_score'],
            scoring_weights=beneficiary_data['scoring_weights'],
            score_components=beneficiary_data['score_components'],
            model_version=automation_service.model_version
        )
        
        db.add(beneficiary_score)
        db.commit()
        db.refresh(beneficiary_score)
        
        return beneficiary_score
        
    except Exception as e:
        logger.error(f"Beneficiary score calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")

@router.post("/recommendations", response_model=List[PropertyRecommendationResponse])
async def get_property_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get property recommendations based on user preferences or similar properties
    """
    try:
        recommendations = []
        
        if request.property_id:
            # Get recommendations based on similar property
            property_valuation = db.query(PropertyValuation).filter(
                PropertyValuation.id == request.property_id
            ).first()
            
            if not property_valuation:
                raise HTTPException(status_code=404, detail="Property not found")
            
            # Create analysis request for recommendation generation
            analysis_request = LandAreaAnalysisRequest(
                property_type=property_valuation.property_type,
                beds=property_valuation.beds,
                baths=property_valuation.baths,
                sqft=property_valuation.sqft,
                year_built=property_valuation.year_built,
                lot_size=property_valuation.lot_size,
                max_recommendations=request.max_recommendations
            )
            
            recommendations = await automation_service.generate_property_recommendations(
                property_valuation, analysis_request, db
            )
            
        elif request.location:
            # Get recommendations based on location preferences
            lat = request.location.get("lat")
            lon = request.location.get("lon")
            
            if not lat or not lon:
                raise HTTPException(status_code=400, detail="Location coordinates required")
            
            # Find properties within radius
            # This would need a more sophisticated geospatial query in production
            nearby_properties = db.query(PropertyValuation).join(Location).filter(
                Location.latitude.between(lat - 0.1, lat + 0.1),
                Location.longitude.between(lon - 0.1, lon + 0.1)
            ).limit(request.max_recommendations * 2).all()
            
            # Score and rank properties
            for prop in nearby_properties:
                location = db.query(Location).filter(Location.id == prop.location_id).first()
                if location:
                    distance = automation_service.haversine(
                        lon, lat, location.longitude, location.latitude
                    )
                    
                    if distance <= request.radius_km:
                        recommendations.append({
                            "id": prop.id,
                            "recommended_property": prop,
                            "recommendation_type": "location_based",
                            "similarity_score": max(0.1, 1.0 - (distance / request.radius_km)),
                            "confidence_score": 0.7,
                            "rank_position": len(recommendations) + 1,
                            "recommendation_reason": f"Located {distance:.1f}km from preferred location",
                            "created_at": datetime.utcnow()
                        })
            
            # Sort by similarity score
            recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
            recommendations = recommendations[:request.max_recommendations]
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Recommendation generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@router.get("/property-valuation/{property_id}/explanation", response_model=ModelExplanationResponse)
async def get_property_explanation(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get SHAP-based explanation for property valuation
    """
    try:
        # Get property valuation
        property_valuation = db.query(PropertyValuation).filter(
            PropertyValuation.id == property_id
        ).first()
        
        if not property_valuation:
            raise HTTPException(status_code=404, detail="Property valuation not found")
        
        # Get location and extract features
        location = db.query(Location).filter(Location.id == property_valuation.location_id).first()
        
        analysis_request = LandAreaAnalysisRequest(
            latitude=location.latitude,
            longitude=location.longitude,
            property_type=property_valuation.property_type,
            beds=property_valuation.beds,
            baths=property_valuation.baths,
            sqft=property_valuation.sqft,
            year_built=property_valuation.year_built,
            lot_size=property_valuation.lot_size
        )
        
        features = await automation_service.extract_comprehensive_features(
            location, analysis_request, db
        )
        
        # Generate explanation
        explanation = automation_service.explainer.explain_avm_prediction(
            features, property_valuation.predicted_value
        )
        
        return explanation
        
    except Exception as e:
        logger.error(f"Explanation generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@router.post("/user-interaction")
async def log_user_interaction_endpoint(
    interaction: UserInteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log user interaction for recommendation system improvement
    """
    try:
        await log_user_interaction(
            current_user.id,
            interaction.property_valuation_id,
            interaction.interaction_type,
            db,
            interaction.search_query,
            interaction.referrer_source,
            interaction.device_type,
            interaction.session_duration
        )
        
        return {"message": "Interaction logged successfully"}
        
    except Exception as e:
        logger.error(f"Interaction logging failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Logging failed: {str(e)}")

async def log_user_interaction(
    user_id: int,
    property_valuation_id: Optional[int],
    interaction_type: str,
    db: Session,
    search_query: Optional[str] = None,
    referrer_source: Optional[str] = None,
    device_type: Optional[str] = None,
    session_duration: Optional[int] = None
):
    """Helper function to log user interactions"""
    try:
        # Define interaction weights
        interaction_weights = {
            "view": 1.0,
            "save": 3.0,
            "contact": 5.0,
            "share": 2.0,
            "comprehensive_analysis": 4.0
        }
        
        interaction = UserInteraction(
            user_id=user_id,
            property_valuation_id=property_valuation_id,
            interaction_type=interaction_type,
            interaction_weight=interaction_weights.get(interaction_type, 1.0),
            search_query=search_query,
            referrer_source=referrer_source,
            device_type=device_type,
            session_duration=session_duration
        )
        
        db.add(interaction)
        db.commit()
        
    except Exception as e:
        logger.error(f"Error logging interaction: {e}")
