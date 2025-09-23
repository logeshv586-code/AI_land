import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.land_area_automation import LandAreaAutomationService
from app.services.shap_explainer import SHAPExplainer
from app.models import Location, PropertyValuation, BeneficiaryScore
from app.schemas import LandAreaAnalysisRequest, RecommendationType

class TestLandAreaAutomationService:
    
    @pytest.fixture
    def automation_service(self):
        return LandAreaAutomationService()
    
    @pytest.fixture
    def mock_location(self):
        location = Mock(spec=Location)
        location.id = 1
        location.latitude = 41.8781
        location.longitude = -87.6298
        location.address = "123 Test St, Chicago, IL"
        return location
    
    @pytest.fixture
    def sample_request(self):
        return LandAreaAnalysisRequest(
            address="123 Test St, Chicago, IL",
            latitude=41.8781,
            longitude=-87.6298,
            property_type="residential",
            beds=3,
            baths=2,
            sqft=1500,
            year_built=2000,
            lot_size=0.25,
            investment_budget=300000,
            risk_tolerance="medium",
            include_avm=True,
            include_beneficiary_score=True,
            include_recommendations=True,
            include_explanations=True
        )
    
    @pytest.fixture
    def sample_features(self):
        return {
            'latitude': 41.8781,
            'longitude': -87.6298,
            'beds': 3,
            'baths': 2,
            'sqft': 1500,
            'year_built': 2000,
            'age': 25,
            'lot_size': 0.25,
            'schools_1km': 2,
            'schools_3km': 5,
            'hospitals_1km': 1,
            'hospitals_3km': 3,
            'avg_school_rating': 4.2,
            'avg_hospital_rating': 4.0,
            'total_crime_rate': 15.5,
            'violent_crime_rate': 3.2,
            'flood_risk': 0.1,
            'earthquake_risk': 0.05,
            'avg_price_per_sqft': 150.0,
            'price_trend_1y': 0.05,
            'demand_score': 65.0,
            'supply_score': 45.0,
            'completeness': 0.95,
            'norm_school': 0.84,
            'norm_crime_inv': 0.69,
            'norm_flood_inv': 0.9,
            'norm_dist_hospital': 0.7,
            'norm_dist_employer': 0.6,
            'norm_value': 0.75,
            'price_per_sqft_area_avg': 150.0
        }
    
    def test_haversine_distance_calculation(self, automation_service):
        """Test Haversine distance calculation"""
        # Chicago to New York (approximate)
        distance = automation_service.haversine(-87.6298, 41.8781, -74.0060, 40.7128)
        assert 1100 < distance < 1200  # Approximately 1145 km
    
    def test_normalize_series(self, automation_service):
        """Test series normalization"""
        import pandas as pd
        
        series = pd.Series([1, 2, 3, 4, 5])
        normalized = automation_service.normalize_series(series)
        
        assert normalized.min() == 0.0
        assert normalized.max() == 1.0
        assert len(normalized) == 5
    
    def test_predict_property_value_with_uncertainty(self, automation_service, sample_features):
        """Test AVM prediction with uncertainty"""
        predicted_value, uncertainty = automation_service.predict_property_value_with_uncertainty(sample_features)
        
        assert isinstance(predicted_value, float)
        assert isinstance(uncertainty, float)
        assert predicted_value > 0
        assert uncertainty > 0
        assert uncertainty < predicted_value  # Uncertainty should be less than prediction
    
    def test_calculate_beneficiary_score(self, automation_service, sample_features):
        """Test beneficiary score calculation"""
        beneficiary_data = automation_service.calculate_beneficiary_score(sample_features)
        
        assert 'overall_score' in beneficiary_data
        assert 'value_score' in beneficiary_data
        assert 'school_score' in beneficiary_data
        assert 'safety_score' in beneficiary_data
        assert 'environmental_score' in beneficiary_data
        assert 'accessibility_score' in beneficiary_data
        
        # Scores should be between 0 and 100
        for score_key in ['overall_score', 'value_score', 'school_score', 'safety_score', 'environmental_score', 'accessibility_score']:
            score = beneficiary_data[score_key]
            assert 0 <= score <= 100
    
    def test_calculate_beneficiary_score_with_custom_weights(self, automation_service, sample_features):
        """Test beneficiary score with custom weights"""
        custom_weights = {
            "value": 10.0,
            "school": 5.0,
            "crime_inv": 8.0,
            "env_inv": 3.0,
            "employer_proximity": 4.0
        }
        
        beneficiary_data = automation_service.calculate_beneficiary_score(sample_features, custom_weights)
        
        assert beneficiary_data['scoring_weights'] == custom_weights
        assert 0 <= beneficiary_data['overall_score'] <= 100
    
    def test_calculate_confidence_score(self, automation_service, sample_features):
        """Test confidence score calculation"""
        prediction_std = 15000.0  # $15k uncertainty
        completeness = 0.95
        
        confidence = automation_service.calculate_confidence_score(
            prediction_std, completeness, sample_features
        )
        
        assert 0.1 <= confidence <= 1.0
        assert isinstance(confidence, float)
    
    def test_generate_recommendation(self, automation_service, sample_features):
        """Test recommendation generation"""
        overall_score = 75.0
        beneficiary_score = 80.0
        
        # Test different risk tolerances
        for risk_tolerance in ["low", "medium", "high"]:
            recommendation = automation_service.generate_recommendation(
                overall_score, beneficiary_score, risk_tolerance, sample_features
            )
            assert recommendation in [RecommendationType.BUY, RecommendationType.HOLD, RecommendationType.AVOID]
    
    def test_generate_recommendation_safety_override(self, automation_service, sample_features):
        """Test that safety issues override good scores"""
        # High scores but poor safety
        overall_score = 85.0
        beneficiary_score = 90.0
        
        # Make safety very poor
        unsafe_features = sample_features.copy()
        unsafe_features['norm_crime_inv'] = 0.1  # Very unsafe
        
        recommendation = automation_service.generate_recommendation(
            overall_score, beneficiary_score, "medium", unsafe_features
        )
        
        assert recommendation == RecommendationType.AVOID
    
    def test_calculate_land_suitability_score(self, automation_service, sample_features):
        """Test land suitability score calculation"""
        score = automation_service.calculate_land_suitability_score(sample_features)
        
        assert 0 <= score <= 100
        assert isinstance(score, float)
    
    def test_calculate_property_similarity(self, automation_service):
        """Test property similarity calculation"""
        prop1 = Mock(spec=PropertyValuation)
        prop1.beds = 3
        prop1.baths = 2
        prop1.sqft = 1500
        prop1.year_built = 2000
        
        prop2 = Mock(spec=PropertyValuation)
        prop2.beds = 3
        prop2.baths = 2
        prop2.sqft = 1600
        prop2.year_built = 2005
        
        similarity = automation_service.calculate_property_similarity(prop1, prop2)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.8  # Should be quite similar
    
    @pytest.mark.asyncio
    async def test_extract_comprehensive_features(self, automation_service, mock_location, sample_request):
        """Test comprehensive feature extraction"""
        mock_db = Mock(spec=Session)
        
        # Mock database queries
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        features = await automation_service.extract_comprehensive_features(
            mock_location, sample_request, mock_db
        )
        
        assert isinstance(features, dict)
        assert 'latitude' in features
        assert 'longitude' in features
        assert 'beds' in features
        assert 'baths' in features
        assert 'sqft' in features
        assert 'completeness' in features
        
        # Check that completeness is calculated
        assert 0 <= features['completeness'] <= 1

class TestSHAPExplainer:
    
    @pytest.fixture
    def explainer(self):
        return SHAPExplainer()
    
    @pytest.fixture
    def sample_features(self):
        return {
            'beds': 3,
            'baths': 2,
            'sqft': 1500,
            'age': 25,
            'lot_size': 0.25,
            'norm_school': 0.8,
            'norm_crime_inv': 0.7,
            'norm_flood_inv': 0.9,
            'norm_dist_hospital': 0.6,
            'norm_dist_employer': 0.5,
            'price_per_sqft_area_avg': 150.0
        }
    
    def test_fallback_explanation(self, explainer, sample_features):
        """Test fallback explanation when SHAP is not available"""
        prediction = 250000.0
        
        explanation = explainer._fallback_explanation(sample_features, prediction)
        
        assert 'base_value' in explanation
        assert 'prediction_value' in explanation
        assert 'feature_attributions' in explanation
        assert 'top_positive_features' in explanation
        assert 'top_negative_features' in explanation
        assert explanation['explanation_type'] == 'rule_based_fallback'
    
    def test_feature_impact_description(self, explainer):
        """Test feature impact description generation"""
        description = explainer._get_feature_impact_description('sqft', 5000.0, 1500)
        
        assert isinstance(description, str)
        assert 'Property size' in description
        assert 'increases' in description or 'decreases' in description
    
    def test_beneficiary_component_description(self, explainer):
        """Test beneficiary component description"""
        description = explainer._get_beneficiary_component_description('school', 0.8, 8.0)
        
        assert isinstance(description, str)
        assert 'School quality' in description
        assert 'good' in description or 'excellent' in description
    
    def test_explain_beneficiary_score(self, explainer):
        """Test beneficiary score explanation"""
        sample_features = {
            'norm_value': 0.7,
            'norm_school': 0.8,
            'norm_crime_inv': 0.6,
            'norm_flood_inv': 0.9,
            'norm_dist_employer': 0.5
        }
        
        beneficiary_data = {
            'overall_score': 75.0,
            'score_components': {
                'value': 5.6,
                'school': 6.4,
                'crime': 3.6,
                'env': 4.5,
                'employer': 3.5
            },
            'scoring_weights': {
                'value': 8.0,
                'school': 8.0,
                'crime_inv': 6.0,
                'env_inv': 5.0,
                'employer_proximity': 7.0
            }
        }
        
        explanation = explainer.explain_beneficiary_score(sample_features, beneficiary_data)
        
        assert 'overall_score' in explanation
        assert 'component_explanations' in explanation
        assert 'explanation_type' in explanation
        assert explanation['explanation_type'] == 'beneficiary_breakdown'
    
    def test_model_interpretability_summary(self, explainer):
        """Test model interpretability summary"""
        summary = explainer.get_model_interpretability_summary('avm')
        
        assert 'model_type' in summary
        assert 'explainability_method' in summary
        assert 'explanation_quality' in summary
        assert 'supported_explanations' in summary
        assert isinstance(summary['supported_explanations'], list)

class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_flow(self):
        """Test the complete comprehensive analysis flow"""
        automation_service = LandAreaAutomationService()
        
        # Mock location and request
        mock_location = Mock(spec=Location)
        mock_location.id = 1
        mock_location.latitude = 41.8781
        mock_location.longitude = -87.6298
        
        request = LandAreaAnalysisRequest(
            latitude=41.8781,
            longitude=-87.6298,
            property_type="residential",
            beds=3,
            baths=2,
            sqft=1500,
            year_built=2000,
            include_avm=True,
            include_beneficiary_score=True,
            include_explanations=True
        )
        
        # Mock database
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Test feature extraction
        features = await automation_service.extract_comprehensive_features(
            mock_location, request, mock_db
        )
        
        assert isinstance(features, dict)
        assert len(features) > 10  # Should have many features
        
        # Test AVM prediction
        predicted_value, uncertainty = automation_service.predict_property_value_with_uncertainty(features)
        assert predicted_value > 0
        assert uncertainty > 0
        
        # Test beneficiary scoring
        beneficiary_data = automation_service.calculate_beneficiary_score(features)
        assert 0 <= beneficiary_data['overall_score'] <= 100
        
        # Test confidence calculation
        confidence = automation_service.calculate_confidence_score(
            uncertainty, features['completeness'], features
        )
        assert 0.1 <= confidence <= 1.0
        
        # Test recommendation generation
        land_score = automation_service.calculate_land_suitability_score(features)
        recommendation = automation_service.generate_recommendation(
            land_score, beneficiary_data['overall_score'], "medium", features
        )
        assert recommendation in [RecommendationType.BUY, RecommendationType.HOLD, RecommendationType.AVOID]

if __name__ == "__main__":
    pytest.main([__file__])
