import numpy as np
import pandas as pd
import math
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from loguru import logger
import joblib
import os

from app.models import (
    Location, PropertyValuation, BeneficiaryScore, PropertyRecommendation,
    UserInteraction, ModelExplanation, LandAnalysis, Facility, CrimeData,
    DisasterData, MarketData
)
from app.schemas import (
    LandAreaAnalysisRequest, LandAreaAnalysisResponse, PropertyValuationResponse,
    BeneficiaryScoreResponse, PropertyRecommendationResponse, RecommendationType,
    ModelExplanationResponse, FeatureAttribution
)
from app.services.shap_explainer import SHAPExplainer

class LandAreaAutomationService:
    """
    Comprehensive land area automation service combining AVM, beneficiary scoring,
    and recommendation engine with existing land analysis capabilities.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.avm_model = None
        self.suitability_model = None
        self.recommender = None
        self.model_version = "2.0.0"
        self.models_dir = "models"

        # Initialize SHAP explainer
        self.explainer = SHAPExplainer()

        # Initialize models
        self.initialize_models()
        
        # Feature sets for different models
        self.avm_features = [
            "beds", "baths", "sqft", "age", "lot_size",
            "norm_school", "norm_crime_inv", "norm_flood_inv",
            "norm_dist_hospital", "norm_dist_employer", "price_per_sqft_area_avg"
        ]
        
        self.beneficiary_features = [
            "norm_value", "norm_school", "norm_crime_inv", 
            "norm_flood_inv", "norm_dist_employer", "accessibility_score"
        ]
    
    def initialize_models(self):
        """Initialize or load ML models"""
        try:
            if os.path.exists(f"{self.models_dir}/avm_model.pkl"):
                self.avm_model = joblib.load(f"{self.models_dir}/avm_model.pkl")
                logger.info("AVM model loaded successfully")
            else:
                self.avm_model = RandomForestRegressor(
                    n_estimators=100, random_state=42, max_depth=10, n_jobs=-1
                )
                logger.info("Initialized new AVM model")
                
            if os.path.exists(f"{self.models_dir}/scaler.pkl"):
                self.scaler = joblib.load(f"{self.models_dir}/scaler.pkl")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.avm_model = RandomForestRegressor(
                n_estimators=100, random_state=42, max_depth=10, n_jobs=-1
            )
    
    def haversine(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371.0  # Earth's radius in kilometers
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2 * R * math.asin(math.sqrt(a))
    
    def normalize_series(self, s: pd.Series) -> pd.Series:
        """Normalize a pandas series to 0-1 range"""
        if s.max() == s.min():
            return s * 0.0
        return (s - s.min()) / (s.max() - s.min())
    
    async def extract_comprehensive_features(
        self, 
        location: Location, 
        request: LandAreaAnalysisRequest,
        db: Session
    ) -> Dict[str, float]:
        """Extract comprehensive features for all models"""
        features = {
            'latitude': location.latitude or 0.0,
            'longitude': location.longitude or 0.0,
        }
        
        # Property characteristics
        features.update({
            'beds': request.beds or 3,
            'baths': request.baths or 2,
            'sqft': request.sqft or 1500,
            'year_built': request.year_built or 2000,
            'lot_size': request.lot_size or 0.25,
        })
        
        # Calculate age
        features['age'] = 2025 - features['year_built']
        
        # Get facility features
        facility_features = await self.extract_facility_features(location, db)
        features.update(facility_features)
        
        # Get crime and safety features
        crime_features = await self.extract_crime_features(location, db)
        features.update(crime_features)
        
        # Get disaster risk features
        disaster_features = await self.extract_disaster_features(location, db)
        features.update(disaster_features)
        
        # Get market features
        market_features = await self.extract_market_features(location, db)
        features.update(market_features)
        
        # Calculate normalized features for beneficiary scoring
        features = self.calculate_normalized_features(features)
        
        # Calculate completeness metric
        required_fields = ['beds', 'baths', 'sqft', 'year_built', 'latitude', 'longitude']
        non_null_count = sum(1 for field in required_fields if features.get(field, 0) != 0)
        features['completeness'] = non_null_count / len(required_fields)
        
        return features
    
    async def extract_facility_features(self, location: Location, db: Session) -> Dict[str, float]:
        """Extract facility-related features"""
        facilities = db.query(Facility).filter(Facility.location_id == location.id).all()
        
        facility_counts = {
            'schools_1km': 0, 'schools_3km': 0, 'schools_5km': 0,
            'hospitals_1km': 0, 'hospitals_3km': 0, 'hospitals_5km': 0,
            'malls_1km': 0, 'malls_3km': 0, 'malls_5km': 0,
            'transport_1km': 0, 'transport_3km': 0, 'transport_5km': 0
        }
        
        school_ratings = []
        hospital_ratings = []
        
        for facility in facilities:
            facility_type = facility.facility_type.lower()
            distance = facility.distance_km
            
            # Count facilities by distance
            for dist_threshold in [1, 3, 5]:
                if distance <= dist_threshold:
                    key = f"{facility_type}_{dist_threshold}km"
                    if key in facility_counts:
                        facility_counts[key] += 1
            
            # Collect ratings
            if facility.rating:
                if facility_type == 'school':
                    school_ratings.append(facility.rating)
                elif facility_type == 'hospital':
                    hospital_ratings.append(facility.rating)
        
        facility_counts.update({
            'avg_school_rating': np.mean(school_ratings) if school_ratings else 3.0,
            'avg_hospital_rating': np.mean(hospital_ratings) if hospital_ratings else 3.0,
        })
        
        return facility_counts
    
    async def extract_crime_features(self, location: Location, db: Session) -> Dict[str, float]:
        """Extract crime and safety features"""
        crime_data = db.query(CrimeData).filter(CrimeData.location_id == location.id).all()
        
        total_crime_rate = sum(cd.crime_rate_per_1000 for cd in crime_data)
        violent_crime_rate = sum(
            cd.crime_rate_per_1000 for cd in crime_data 
            if cd.crime_type in ['assault', 'robbery', 'murder']
        )
        property_crime_rate = sum(
            cd.crime_rate_per_1000 for cd in crime_data 
            if cd.crime_type in ['theft', 'burglary', 'vandalism']
        )
        
        return {
            'total_crime_rate': total_crime_rate,
            'violent_crime_rate': violent_crime_rate,
            'property_crime_rate': property_crime_rate,
            'crime_severity_avg': np.mean([cd.severity_score for cd in crime_data]) if crime_data else 0.0
        }
    
    async def extract_disaster_features(self, location: Location, db: Session) -> Dict[str, float]:
        """Extract disaster risk features"""
        disaster_data = db.query(DisasterData).filter(DisasterData.location_id == location.id).all()
        
        disaster_risks = {
            'flood_risk': 0.0, 'earthquake_risk': 0.0, 'hurricane_risk': 0.0,
            'wildfire_risk': 0.0, 'tornado_risk': 0.0
        }
        
        for disaster in disaster_data:
            risk_key = f"{disaster.disaster_type}_risk"
            if risk_key in disaster_risks:
                disaster_risks[risk_key] = disaster.probability
        
        return disaster_risks
    
    async def extract_market_features(self, location: Location, db: Session) -> Dict[str, float]:
        """Extract market-related features"""
        market_data = db.query(MarketData).filter(MarketData.location_id == location.id).first()
        
        if market_data:
            return {
                'avg_price_per_sqft': market_data.avg_price_per_sqft,
                'price_trend_6m': market_data.price_trend_6m,
                'price_trend_1y': market_data.price_trend_1y,
                'demand_score': market_data.demand_score,
                'supply_score': market_data.supply_score
            }
        else:
            return {
                'avg_price_per_sqft': 100.0,
                'price_trend_6m': 0.0,
                'price_trend_1y': 0.0,
                'demand_score': 50.0,
                'supply_score': 50.0
            }
    
    def calculate_normalized_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate normalized features for scoring"""
        # Create a temporary dataframe for normalization
        df = pd.DataFrame([features])
        
        # Calculate normalized features
        df['norm_school'] = self.normalize_series(pd.Series([features['avg_school_rating']]))
        df['norm_crime_inv'] = 1.0 - self.normalize_series(pd.Series([features['total_crime_rate'] / 50.0]))
        df['norm_flood_inv'] = 1.0 - self.normalize_series(pd.Series([features['flood_risk']]))
        df['norm_dist_hospital'] = 1.0 - self.normalize_series(pd.Series([features.get('hospitals_3km', 0) / 10.0]))
        df['norm_dist_employer'] = 1.0 - self.normalize_series(pd.Series([features.get('transport_3km', 0) / 10.0]))
        
        # Calculate price per sqft for area (using market average)
        features['price_per_sqft_area_avg'] = features['avg_price_per_sqft']
        df['norm_value'] = self.normalize_series(pd.Series([features['price_per_sqft_area_avg'] / 200.0]))
        
        # Update features with normalized values
        for col in ['norm_school', 'norm_crime_inv', 'norm_flood_inv', 'norm_dist_hospital', 'norm_dist_employer', 'norm_value']:
            features[col] = float(df[col].iloc[0])
        
        return features

    def predict_property_value_with_uncertainty(
        self,
        features: Dict[str, float]
    ) -> Tuple[float, float]:
        """
        Predict property value using AVM with uncertainty estimation
        Returns (predicted_value, uncertainty_std)
        """
        # Prepare feature vector
        feature_vector = []
        for feature_name in self.avm_features:
            feature_vector.append(features.get(feature_name, 0.0))

        X = np.array([feature_vector])

        try:
            if self.avm_model and hasattr(self.avm_model, 'estimators_'):
                # Use ensemble variance for uncertainty
                predictions = np.array([tree.predict(X)[0] for tree in self.avm_model.estimators_])
                mean_prediction = predictions.mean()
                std_prediction = predictions.std()
                return float(mean_prediction), float(std_prediction)
        except AttributeError:
            # Handle case where model doesn't have estimators_ yet
            pass

        # Fallback: simple estimation based on price per sqft and sqft
        base_value = features.get('avg_price_per_sqft', 100) * features.get('sqft', 1500)
        # Add adjustments based on other features
        age_adjustment = max(0.8, 1.0 - (features.get('age', 25) / 100))
        school_adjustment = 0.9 + (features.get('norm_school', 0.5) * 0.2)
        safety_adjustment = 0.9 + (features.get('norm_crime_inv', 0.5) * 0.2)

        predicted_value = base_value * age_adjustment * school_adjustment * safety_adjustment
        uncertainty = predicted_value * 0.15  # 15% uncertainty as default

        return float(predicted_value), float(uncertainty)

    def calculate_beneficiary_score(
        self,
        features: Dict[str, float],
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """Calculate comprehensive beneficiary score"""
        # Default weights
        default_weights = {
            "value": 8.0,
            "school": 8.0,
            "crime_inv": 6.0,
            "env_inv": 5.0,
            "employer_proximity": 7.0,
        }

        if custom_weights:
            default_weights.update(custom_weights)

        weights = default_weights

        # Calculate component scores
        components = {
            "value": features.get("norm_value", 0.5) * weights["value"],
            "school": features.get("norm_school", 0.5) * weights["school"],
            "crime": features.get("norm_crime_inv", 0.5) * weights["crime_inv"],
            "env": features.get("norm_flood_inv", 0.5) * weights["env_inv"],
            "employer": features.get("norm_dist_employer", 0.5) * weights["employer_proximity"]
        }

        # Calculate total weighted score
        total_weighted = sum(components.values())
        total_weights = sum(weights.values())

        # Normalize to 0-100 scale
        beneficiary_raw = total_weighted / total_weights
        beneficiary_score = beneficiary_raw * 100

        # Calculate individual component scores (0-100)
        component_scores = {
            "value_score": (components["value"] / weights["value"]) * 100,
            "school_score": (components["school"] / weights["school"]) * 100,
            "safety_score": (components["crime"] / weights["crime_inv"]) * 100,
            "environmental_score": (components["env"] / weights["env_inv"]) * 100,
            "accessibility_score": (components["employer"] / weights["employer_proximity"]) * 100,
        }

        return {
            "overall_score": float(beneficiary_score),
            **component_scores,
            "scoring_weights": weights,
            "score_components": components
        }

    def calculate_confidence_score(
        self,
        prediction_std: float,
        completeness: float,
        features: Dict[str, float]
    ) -> float:
        """Calculate overall confidence score for the analysis"""
        # Normalize prediction uncertainty (lower std = higher confidence)
        max_reasonable_std = 50000  # $50k standard deviation
        uncertainty_confidence = max(0.0, 1.0 - (prediction_std / max_reasonable_std))

        # Data completeness confidence
        completeness_confidence = completeness

        # Feature quality confidence (based on having key data)
        has_market_data = features.get('avg_price_per_sqft', 0) > 0
        has_facility_data = features.get('schools_3km', 0) > 0 or features.get('hospitals_3km', 0) > 0
        has_safety_data = features.get('total_crime_rate', 0) > 0

        feature_quality = sum([has_market_data, has_facility_data, has_safety_data]) / 3.0

        # Combined confidence score
        confidence = (
            uncertainty_confidence * 0.4 +
            completeness_confidence * 0.3 +
            feature_quality * 0.3
        )

        return max(0.1, min(1.0, confidence))

    def generate_recommendation(
        self,
        overall_score: float,
        beneficiary_score: float,
        risk_tolerance: str,
        features: Dict[str, float]
    ) -> RecommendationType:
        """Generate investment recommendation"""
        # Adjust thresholds based on risk tolerance
        if risk_tolerance == "low":
            buy_threshold = 75
            avoid_threshold = 50
        elif risk_tolerance == "high":
            buy_threshold = 60
            avoid_threshold = 35
        else:  # medium
            buy_threshold = 70
            avoid_threshold = 45

        # Check for critical safety issues
        safety_score = features.get('norm_crime_inv', 0.5) * 100
        disaster_risk = 1.0 - max(
            features.get('flood_risk', 0),
            features.get('earthquake_risk', 0),
            features.get('hurricane_risk', 0)
        )
        disaster_score = disaster_risk * 100

        if safety_score < 30 or disaster_score < 20:
            return RecommendationType.AVOID

        # Use combined score of land suitability and beneficiary score
        combined_score = (overall_score * 0.6) + (beneficiary_score * 0.4)

        if combined_score >= buy_threshold:
            return RecommendationType.BUY
        elif combined_score >= avoid_threshold:
            return RecommendationType.HOLD
        else:
            return RecommendationType.AVOID

    async def perform_comprehensive_analysis(
        self,
        location: Location,
        request: LandAreaAnalysisRequest,
        user_id: int,
        db: Session
    ) -> LandAreaAnalysisResponse:
        """Perform comprehensive land area analysis combining all features"""
        start_time = datetime.now()

        # Extract comprehensive features
        features = await self.extract_comprehensive_features(location, request, db)

        # Predict property value with uncertainty
        predicted_value, value_uncertainty = self.predict_property_value_with_uncertainty(features)

        # Calculate beneficiary score
        beneficiary_data = self.calculate_beneficiary_score(features, request.custom_weights)

        # Calculate confidence score
        confidence = self.calculate_confidence_score(
            value_uncertainty,
            features['completeness'],
            features
        )

        # Calculate overall land suitability score (from existing analyzer)
        land_suitability_score = self.calculate_land_suitability_score(features)

        # Generate recommendation
        recommendation = self.generate_recommendation(
            land_suitability_score,
            beneficiary_data['overall_score'],
            request.risk_tolerance,
            features
        )

        # Save property valuation to database
        property_valuation = PropertyValuation(
            location_id=location.id,
            property_type=request.property_type,
            beds=request.beds,
            baths=request.baths,
            sqft=request.sqft,
            year_built=request.year_built,
            lot_size=request.lot_size,
            predicted_value=predicted_value,
            value_uncertainty=value_uncertainty,
            price_per_sqft=features.get('avg_price_per_sqft', 0),
            valuation_date=datetime.utcnow()
        )
        db.add(property_valuation)
        db.commit()
        db.refresh(property_valuation)

        # Save beneficiary score to database
        beneficiary_score = BeneficiaryScore(
            location_id=location.id,
            property_valuation_id=property_valuation.id,
            overall_score=beneficiary_data['overall_score'],
            value_score=beneficiary_data['value_score'],
            school_score=beneficiary_data['school_score'],
            safety_score=beneficiary_data['safety_score'],
            environmental_score=beneficiary_data['environmental_score'],
            accessibility_score=beneficiary_data['accessibility_score'],
            scoring_weights=beneficiary_data['scoring_weights'],
            score_components=beneficiary_data['score_components'],
            model_version=self.model_version
        )
        db.add(beneficiary_score)
        db.commit()
        db.refresh(beneficiary_score)

        # Generate recommendations if requested
        recommendations = []
        if request.include_recommendations:
            recommendations = await self.generate_property_recommendations(
                property_valuation, request, db
            )

        # Generate explanations if requested
        explanations = None
        if request.include_explanations:
            explanations = self.generate_enhanced_explanations(
                features, predicted_value, beneficiary_data, property_valuation.id, db
            )

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        # Create response (simplified for now - would need full implementation)
        return {
            "analysis_id": property_valuation.id,
            "location": location,
            "overall_score": land_suitability_score,
            "recommendation": recommendation,
            "confidence_level": confidence,
            "property_valuation": property_valuation,
            "beneficiary_score": beneficiary_score,
            "similar_properties": recommendations,
            "feature_explanations": explanations,
            "processing_time_ms": int(processing_time)
        }

    def calculate_land_suitability_score(self, features: Dict[str, float]) -> float:
        """Calculate land suitability score using existing logic"""
        # Facility score (0-100)
        facility_score = min(100, (
            features.get('schools_1km', 0) * 20 +
            features.get('schools_3km', 0) * 10 +
            features.get('hospitals_1km', 0) * 25 +
            features.get('hospitals_3km', 0) * 15 +
            features.get('transport_1km', 0) * 30 +
            features.get('transport_3km', 0) * 20
        ))

        # Safety score (0-100)
        total_crime = features.get('total_crime_rate', 0)
        safety_score = max(0, 100 * (1 - min(1.0, total_crime / 50.0)))

        # Market potential score (0-100)
        demand = features.get('demand_score', 50)
        supply = features.get('supply_score', 50)
        price_trend = features.get('price_trend_1y', 0)
        market_score = min(100, (demand / max(supply, 1)) * 30 + max(0, 50 + price_trend * 10))

        # Disaster risk score (0-100, higher is better)
        disaster_risks = [
            features.get('flood_risk', 0),
            features.get('earthquake_risk', 0),
            features.get('hurricane_risk', 0),
            features.get('wildfire_risk', 0),
            features.get('tornado_risk', 0)
        ]
        avg_disaster_risk = np.mean(disaster_risks)
        disaster_score = max(0, 100 * (1 - avg_disaster_risk))

        # Weighted overall score
        overall_score = (
            facility_score * 0.25 +
            safety_score * 0.25 +
            market_score * 0.25 +
            disaster_score * 0.25
        )

        return max(0, min(100, overall_score))

    async def generate_property_recommendations(
        self,
        property_valuation: PropertyValuation,
        request: LandAreaAnalysisRequest,
        db: Session
    ) -> List[PropertyRecommendationResponse]:
        """Generate property recommendations using content-based filtering"""
        # Get similar properties based on characteristics
        similar_properties = db.query(PropertyValuation).filter(
            PropertyValuation.id != property_valuation.id,
            PropertyValuation.property_type == property_valuation.property_type
        ).limit(50).all()

        recommendations = []

        for similar_prop in similar_properties:
            # Calculate similarity score based on property characteristics
            similarity_score = self.calculate_property_similarity(
                property_valuation, similar_prop
            )

            if similarity_score > 0.5:  # Only include reasonably similar properties
                recommendations.append({
                    "id": similar_prop.id,
                    "recommended_property": similar_prop,
                    "recommendation_type": "content_based",
                    "similarity_score": similarity_score,
                    "confidence_score": similarity_score * 0.8,
                    "rank_position": len(recommendations) + 1,
                    "recommendation_reason": f"Similar property characteristics (similarity: {similarity_score:.2f})",
                    "created_at": datetime.utcnow()
                })

        # Sort by similarity score and limit results
        recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
        return recommendations[:request.max_recommendations]

    def calculate_property_similarity(
        self,
        prop1: PropertyValuation,
        prop2: PropertyValuation
    ) -> float:
        """Calculate similarity between two properties"""
        # Normalize differences
        bed_diff = abs((prop1.beds or 0) - (prop2.beds or 0)) / 5.0
        bath_diff = abs((prop1.baths or 0) - (prop2.baths or 0)) / 4.0
        sqft_diff = abs((prop1.sqft or 0) - (prop2.sqft or 0)) / 3000.0
        age_diff = abs((prop1.year_built or 2000) - (prop2.year_built or 2000)) / 50.0

        # Calculate similarity (1 - normalized_difference)
        similarity = 1.0 - np.mean([bed_diff, bath_diff, sqft_diff, age_diff])
        return max(0.0, min(1.0, similarity))

    def generate_enhanced_explanations(
        self,
        features: Dict[str, float],
        prediction: float,
        beneficiary_data: Dict[str, Any],
        property_valuation_id: int,
        db
    ) -> Dict[str, Any]:
        """Generate comprehensive explanations using SHAP and beneficiary analysis"""

        # Generate AVM prediction explanations using SHAP
        avm_explanation = self.explainer.explain_avm_prediction(features, prediction)

        # Generate beneficiary score explanations
        beneficiary_explanation = self.explainer.explain_beneficiary_score(features, beneficiary_data)

        # Save explanations to database
        if avm_explanation:
            self.explainer.save_explanation_to_db(
                avm_explanation,
                property_valuation_id=property_valuation_id,
                db=db
            )

        # Combine explanations
        combined_explanation = {
            'avm_explanation': avm_explanation,
            'beneficiary_explanation': beneficiary_explanation,
            'model_interpretability': self.explainer.get_model_interpretability_summary('avm'),
            'explanation_summary': self.generate_explanation_summary(
                avm_explanation, beneficiary_explanation
            )
        }

        return combined_explanation

    def generate_explanation_summary(
        self,
        avm_explanation: Dict[str, Any],
        beneficiary_explanation: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate human-readable summary of explanations"""

        summary = {}

        # AVM summary
        if avm_explanation and 'top_positive_features' in avm_explanation:
            top_positive = avm_explanation['top_positive_features'][:3]
            if top_positive:
                summary['value_drivers'] = f"Property value is primarily driven by: {', '.join([f['feature_name'] for f in top_positive])}"

        # Beneficiary summary
        if beneficiary_explanation and 'component_explanations' in beneficiary_explanation:
            top_components = beneficiary_explanation['component_explanations'][:3]
            if top_components:
                summary['beneficiary_drivers'] = f"Investment attractiveness is mainly influenced by: {', '.join([comp['component'] for comp in top_components])}"

        # Overall recommendation summary
        overall_score = beneficiary_explanation.get('overall_score', 0)
        if overall_score >= 75:
            summary['investment_outlook'] = "Strong investment potential with favorable characteristics"
        elif overall_score >= 60:
            summary['investment_outlook'] = "Moderate investment potential with some positive factors"
        elif overall_score >= 45:
            summary['investment_outlook'] = "Mixed investment signals requiring careful consideration"
        else:
            summary['investment_outlook'] = "Limited investment potential with significant challenges"

        return summary
