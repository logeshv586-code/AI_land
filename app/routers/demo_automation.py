"""
Demo Automation Router - No Authentication Required
For testing and demonstration purposes only
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime
import random

from ..database import get_db
from ..services.land_area_automation import LandAreaAutomationService
from ..schemas import (
    LandAreaAnalysisRequest,
    LandAreaAnalysisResponse,
    PropertyValuationResponse,
    BeneficiaryScoreRequest,
    BeneficiaryScoreResponse,
    RecommendationRequest,
    PropertyRecommendationResponse,
    ModelExplanationResponse,
    UserInteractionCreate
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo", tags=["demo-automation"])

# Initialize services
automation_service = LandAreaAutomationService()

@router.get("/health")
async def demo_health_check():
    """Demo health check endpoint"""
    return {
        "status": "healthy",
        "service": "Land Area Automation Demo",
        "timestamp": datetime.now().isoformat(),
        "note": "Demo mode - no authentication required"
    }

@router.post("/comprehensive-analysis", response_model=LandAreaAnalysisResponse)
async def demo_comprehensive_analysis(
    request: LandAreaAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Demo comprehensive land area analysis without authentication
    """
    try:
        logger.info(f"Demo comprehensive analysis for: {request.address}")
        
        # Generate mock comprehensive analysis result for demo
        mock_result = {
            "property_valuation": {
                "id": random.randint(1000, 9999),
                "predicted_value": 200000 + random.randint(50000, 300000),
                "value_uncertainty": 15000 + random.randint(5000, 15000),
                "price_per_sqft": 150 + random.randint(50, 100),
                "comparable_sales_count": random.randint(8, 15),
                "days_on_market_avg": random.uniform(30, 60),
                "valuation_date": datetime.now(),
                "confidence_score": 0.8 + random.uniform(0, 0.15),
                "model_version": "2.0.0-demo"
            },
            "beneficiary_score": {
                "id": random.randint(1000, 9999),
                "overall_score": 60 + random.uniform(0, 35),
                "value_score": 65 + random.uniform(0, 30),
                "school_score": 75 + random.uniform(0, 25),
                "safety_score": 55 + random.uniform(0, 40),
                "environmental_score": 80 + random.uniform(0, 20),
                "accessibility_score": 70 + random.uniform(0, 25),
                "scoring_weights": request.custom_weights or {},
                "score_components": {},
                "calculated_at": datetime.now(),
                "model_version": "2.0.0-demo"
            },
            "recommendations": [],
            "risk_assessment": {
                "risk_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
                "risk_factors": ["Market volatility", "Infrastructure age"],
                "opportunities": ["Development projects", "School district"],
                "confidence_score": 0.75 + random.uniform(0, 0.2)
            },
            "analysis_summary": {
                "total_processing_time": random.uniform(1.5, 3.0),
                "model_versions": {"avm": "2.0.0", "scoring": "2.0.0", "recommendations": "2.0.0"},
                "data_sources_used": ["MLS", "Census", "Crime Data"]
            }
        }

        result = mock_result
        
        logger.info("Demo comprehensive analysis completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Demo comprehensive analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo analysis failed: {str(e)}")

@router.post("/property-valuation", response_model=PropertyValuationResponse)
async def demo_property_valuation(
    request: LandAreaAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Demo property valuation without authentication
    """
    try:
        logger.info(f"Demo property valuation for: {request.address}")
        
        # Generate mock valuation result for demo
        predicted_value = 200000 + random.randint(50000, 300000)
        uncertainty = 15000 + random.randint(5000, 15000)
        confidence = 0.8 + random.uniform(0, 0.15)
        sqft = request.sqft or 1500
        
        # Create response
        response = PropertyValuationResponse(
            id=random.randint(1000, 9999),
            predicted_value=predicted_value,
            value_uncertainty=uncertainty,
            price_per_sqft=predicted_value / sqft,
            comparable_sales_count=random.randint(8, 15),
            days_on_market_avg=random.uniform(30, 60),
            valuation_date=datetime.now(),
            confidence_score=confidence,
            model_version="2.0.0-demo",
            location_id=random.randint(1000, 9999)
        )
        
        logger.info("Demo property valuation completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Demo property valuation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo valuation failed: {str(e)}")

@router.post("/beneficiary-score", response_model=BeneficiaryScoreResponse)
async def demo_beneficiary_score(
    request: dict,  # Use dict to accept flexible input for demo
    db: Session = Depends(get_db)
):
    """
    Demo beneficiary scoring without authentication
    """
    try:
        logger.info(f"Demo beneficiary scoring for: {request.get('address', 'Unknown')}")

        # Generate mock scoring result for demo
        overall_score = 60 + random.uniform(0, 35)
        custom_weights = request.get("custom_weights", {
            "value": 8.0,
            "school": 8.0,
            "crime_inv": 6.0,
            "env_inv": 5.0,
            "employer_proximity": 7.0
        })
        
        # Create response
        response = BeneficiaryScoreResponse(
            id=random.randint(1000, 9999),
            overall_score=overall_score,
            value_score=65 + random.uniform(0, 30),
            school_score=75 + random.uniform(0, 25),
            safety_score=55 + random.uniform(0, 40),
            environmental_score=80 + random.uniform(0, 20),
            accessibility_score=70 + random.uniform(0, 25),
            scoring_weights=custom_weights,
            score_components={
                "value": 65 + random.uniform(0, 30),
                "school": 75 + random.uniform(0, 25),
                "crime": 55 + random.uniform(0, 40),
                "env": 80 + random.uniform(0, 20),
                "employer": 70 + random.uniform(0, 25)
            },
            calculated_at=datetime.now(),
            model_version="2.0.0-demo",
            location_id=random.randint(1000, 9999)
        )
        
        logger.info("Demo beneficiary scoring completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Demo beneficiary scoring failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo scoring failed: {str(e)}")

@router.post("/recommendations", response_model=List[PropertyRecommendationResponse])
async def demo_property_recommendations(
    request: dict,  # Use dict to accept flexible input for demo
    db: Session = Depends(get_db)
):
    """
    Demo property recommendations without authentication
    """
    try:
        logger.info(f"Demo property recommendations for: {request.get('address') or request.get('property_id')}")

        # Generate mock recommendations for demo
        recommendations = []

        for i in range(min(request.get("max_recommendations", 10), 10)):
            # Mock property data as PropertyValuationResponse
            predicted_value = random.randint(200000, 800000)
            mock_property = PropertyValuationResponse(
                id=random.randint(1000, 9999),
                predicted_value=predicted_value,
                value_uncertainty=predicted_value * 0.1,
                price_per_sqft=predicted_value / random.randint(1000, 3000),
                comparable_sales_count=random.randint(8, 15),
                days_on_market_avg=random.uniform(30, 60),
                valuation_date=datetime.now(),
                confidence_score=0.8 + random.uniform(0, 0.15),
                model_version="2.0.0-demo",
                location_id=random.randint(1000, 9999)
            )
            
            recommendation = PropertyRecommendationResponse(
                id=random.randint(1000, 9999),
                recommended_property=mock_property,
                recommendation_type=request.get("recommendation_type", "hybrid"),
                similarity_score=random.uniform(0.6, 0.95),
                confidence_score=random.uniform(0.7, 0.9),
                rank_position=i + 1,
                recommendation_reason=random.choice([
                    "Similar property characteristics and location",
                    "Excellent investment potential in growing area",
                    "Strong market performance and comparable features",
                    "High user rating similarity and preferences match",
                    "Optimal price-to-value ratio in target neighborhood"
                ]),
                created_at=datetime.now()
            )
            
            recommendations.append(recommendation)
        
        # Sort by similarity score
        recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
        
        logger.info(f"Demo property recommendations completed: {len(recommendations)} properties")
        return recommendations
        
    except Exception as e:
        logger.error(f"Demo property recommendations failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo recommendations failed: {str(e)}")

@router.get("/analysis-history")
async def demo_analysis_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Demo analysis history without authentication
    """
    try:
        # Generate mock history data
        history = []
        
        for i in range(min(limit, 20)):
            analysis = {
                "id": random.randint(1000, 9999),
                "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine'])} St",
                "analysis_type": random.choice(["comprehensive", "valuation", "scoring", "recommendations"]),
                "predicted_value": random.randint(200000, 800000),
                "investment_score": random.uniform(40, 95),
                "risk_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
                "created_at": datetime.now().isoformat(),
                "status": "completed"
            }
            history.append(analysis)
        
        logger.info(f"Demo analysis history retrieved: {len(history)} records")
        return history
        
    except Exception as e:
        logger.error(f"Demo analysis history failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo history failed: {str(e)}")

@router.post("/log-interaction")
async def demo_log_interaction(
    interaction: UserInteractionCreate,
    db: Session = Depends(get_db)
):
    """
    Demo user interaction logging without authentication
    """
    try:
        logger.info(f"Demo interaction logged: {interaction.interaction_type}")
        
        # In demo mode, just log and return success
        return {
            "status": "success",
            "message": "Demo interaction logged",
            "interaction_id": random.randint(1000, 9999),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Demo interaction logging failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo logging failed: {str(e)}")

@router.get("/stats")
async def demo_system_stats():
    """
    Demo system statistics
    """
    return {
        "total_analyses": random.randint(10000, 50000),
        "avg_processing_time": round(random.uniform(1.5, 3.0), 2),
        "model_accuracy": round(random.uniform(85, 92), 1),
        "active_users": random.randint(1000, 5000),
        "properties_analyzed_today": random.randint(100, 500),
        "system_uptime": "99.8%",
        "last_updated": datetime.now().isoformat()
    }
