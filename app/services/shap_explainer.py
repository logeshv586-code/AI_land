import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from loguru import logger
import joblib
import os

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("SHAP not available. Install with: pip install shap")

from app.schemas import FeatureAttribution, ModelExplanationResponse
from app.models import ModelExplanation, PropertyValuation, LandAnalysis

class SHAPExplainer:
    """
    SHAP-based model explainability service for transparent AI decision making
    """
    
    def __init__(self):
        self.explainers = {}
        self.feature_names = []
        self.model_version = "2.0.0"
        
        # Initialize explainers if SHAP is available
        if SHAP_AVAILABLE:
            self.initialize_explainers()
    
    def initialize_explainers(self):
        """Initialize SHAP explainers for different models"""
        try:
            # Load AVM model for explanation
            if os.path.exists("models/avm_model.pkl"):
                avm_model = joblib.load("models/avm_model.pkl")
                if hasattr(avm_model, 'estimators_'):
                    self.explainers['avm'] = shap.TreeExplainer(avm_model)
                    logger.info("SHAP TreeExplainer initialized for AVM model")
                    
            # Define feature names for explanations
            self.feature_names = [
                "beds", "baths", "sqft", "age", "lot_size",
                "norm_school", "norm_crime_inv", "norm_flood_inv",
                "norm_dist_hospital", "norm_dist_employer", "price_per_sqft_area_avg"
            ]
                    
        except Exception as e:
            logger.error(f"Error initializing SHAP explainers: {e}")
    
    def explain_avm_prediction(
        self, 
        features: Dict[str, float], 
        prediction: float
    ) -> Optional[Dict[str, Any]]:
        """
        Generate SHAP explanations for AVM predictions
        """
        if not SHAP_AVAILABLE or 'avm' not in self.explainers:
            return self._fallback_explanation(features, prediction)
        
        try:
            # Prepare feature vector
            feature_vector = []
            for feature_name in self.feature_names:
                feature_vector.append(features.get(feature_name, 0.0))
            
            X = np.array([feature_vector])
            
            # Generate SHAP values
            explainer = self.explainers['avm']
            shap_values = explainer.shap_values(X)
            
            if isinstance(shap_values, list):
                shap_values = shap_values[0]  # For multi-output models
            
            # Get base value (expected value)
            base_value = explainer.expected_value
            if isinstance(base_value, np.ndarray):
                base_value = base_value[0]
            
            # Create feature attributions
            feature_attributions = []
            for i, (feature_name, shap_val) in enumerate(zip(self.feature_names, shap_values[0])):
                feature_attributions.append({
                    'feature_name': feature_name,
                    'attribution_value': float(shap_val),
                    'feature_value': feature_vector[i],
                    'impact_description': self._get_feature_impact_description(
                        feature_name, shap_val, feature_vector[i]
                    )
                })
            
            # Sort by absolute attribution value
            feature_attributions.sort(key=lambda x: abs(x['attribution_value']), reverse=True)
            
            # Separate positive and negative contributions
            positive_features = [f for f in feature_attributions if f['attribution_value'] > 0]
            negative_features = [f for f in feature_attributions if f['attribution_value'] < 0]
            
            return {
                'base_value': float(base_value),
                'prediction_value': prediction,
                'feature_attributions': feature_attributions,
                'top_positive_features': positive_features[:5],
                'top_negative_features': negative_features[:5],
                'explanation_type': 'shap_tree',
                'model_version': self.model_version,
                'shap_values': shap_values[0].tolist(),
                'feature_names': self.feature_names
            }
            
        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {e}")
            return self._fallback_explanation(features, prediction)
    
    def _fallback_explanation(
        self, 
        features: Dict[str, float], 
        prediction: float
    ) -> Dict[str, Any]:
        """
        Fallback explanation when SHAP is not available
        """
        # Simple rule-based feature importance
        feature_importance = {
            'sqft': 0.25,
            'norm_school': 0.20,
            'norm_crime_inv': 0.15,
            'age': 0.10,
            'beds': 0.10,
            'baths': 0.08,
            'norm_flood_inv': 0.07,
            'norm_dist_hospital': 0.05
        }
        
        base_value = prediction * 0.7
        
        feature_attributions = []
        for feature_name, importance in feature_importance.items():
            feature_value = features.get(feature_name, 0)
            # Simple attribution based on feature value and importance
            attribution = (feature_value - 0.5) * importance * prediction * 0.3
            
            feature_attributions.append({
                'feature_name': feature_name,
                'attribution_value': attribution,
                'feature_value': feature_value,
                'impact_description': self._get_feature_impact_description(
                    feature_name, attribution, feature_value
                )
            })
        
        # Sort by absolute attribution
        feature_attributions.sort(key=lambda x: abs(x['attribution_value']), reverse=True)
        
        positive_features = [f for f in feature_attributions if f['attribution_value'] > 0]
        negative_features = [f for f in feature_attributions if f['attribution_value'] < 0]
        
        return {
            'base_value': base_value,
            'prediction_value': prediction,
            'feature_attributions': feature_attributions,
            'top_positive_features': positive_features[:5],
            'top_negative_features': negative_features[:5],
            'explanation_type': 'rule_based_fallback',
            'model_version': self.model_version
        }
    
    def _get_feature_impact_description(
        self, 
        feature_name: str, 
        attribution: float, 
        feature_value: float
    ) -> str:
        """Generate human-readable description of feature impact"""
        
        feature_descriptions = {
            'sqft': ('Property size', 'sq ft'),
            'beds': ('Number of bedrooms', 'bedrooms'),
            'baths': ('Number of bathrooms', 'bathrooms'),
            'age': ('Property age', 'years old'),
            'lot_size': ('Lot size', 'acres'),
            'norm_school': ('School quality', 'rating'),
            'norm_crime_inv': ('Safety level', 'safety score'),
            'norm_flood_inv': ('Flood risk protection', 'risk score'),
            'norm_dist_hospital': ('Hospital accessibility', 'access score'),
            'norm_dist_employer': ('Employment accessibility', 'access score'),
            'price_per_sqft_area_avg': ('Area price level', '$/sq ft')
        }
        
        desc, unit = feature_descriptions.get(feature_name, (feature_name, 'value'))
        
        if attribution > 0:
            impact = "increases"
        else:
            impact = "decreases"
        
        return f"{desc} ({feature_value:.2f} {unit}) {impact} property value by ${abs(attribution):,.0f}"
    
    def explain_beneficiary_score(
        self, 
        features: Dict[str, float], 
        beneficiary_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate explanations for beneficiary score calculation
        """
        components = beneficiary_data.get('score_components', {})
        weights = beneficiary_data.get('scoring_weights', {})
        
        explanations = []
        
        for component, value in components.items():
            weight = weights.get(component.replace('_score', '').replace('_inv', ''), 1.0)
            normalized_contribution = value / weight if weight > 0 else 0
            
            explanations.append({
                'component': component,
                'raw_score': normalized_contribution * 100,
                'weight': weight,
                'weighted_contribution': value,
                'description': self._get_beneficiary_component_description(
                    component, normalized_contribution, weight
                )
            })
        
        # Sort by weighted contribution
        explanations.sort(key=lambda x: abs(x['weighted_contribution']), reverse=True)
        
        return {
            'overall_score': beneficiary_data.get('overall_score', 0),
            'component_explanations': explanations,
            'total_weighted_score': sum(comp['weighted_contribution'] for comp in explanations),
            'explanation_type': 'beneficiary_breakdown'
        }
    
    def _get_beneficiary_component_description(
        self, 
        component: str, 
        score: float, 
        weight: float
    ) -> str:
        """Generate description for beneficiary score components"""
        
        component_descriptions = {
            'value': 'Property value competitiveness',
            'school': 'School quality and accessibility',
            'crime': 'Safety and crime levels',
            'env': 'Environmental risk factors',
            'employer': 'Employment and economic opportunities'
        }
        
        desc = component_descriptions.get(component, component)
        score_pct = score * 100
        
        if score_pct >= 80:
            quality = "excellent"
        elif score_pct >= 60:
            quality = "good"
        elif score_pct >= 40:
            quality = "fair"
        else:
            quality = "poor"
        
        return f"{desc}: {quality} ({score_pct:.1f}%) with weight {weight:.1f}"
    
    def save_explanation_to_db(
        self,
        explanation_data: Dict[str, Any],
        analysis_id: Optional[int] = None,
        property_valuation_id: Optional[int] = None,
        db = None
    ) -> Optional[ModelExplanation]:
        """Save explanation to database"""
        if not db:
            return None
        
        try:
            explanation = ModelExplanation(
                analysis_id=analysis_id,
                property_valuation_id=property_valuation_id,
                feature_attributions=explanation_data.get('feature_attributions', {}),
                base_value=explanation_data.get('base_value', 0.0),
                prediction_value=explanation_data.get('prediction_value', 0.0),
                top_positive_features=explanation_data.get('top_positive_features', []),
                top_negative_features=explanation_data.get('top_negative_features', []),
                explanation_type=explanation_data.get('explanation_type', 'unknown'),
                model_version=self.model_version
            )
            
            db.add(explanation)
            db.commit()
            db.refresh(explanation)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error saving explanation to database: {e}")
            return None
    
    def get_model_interpretability_summary(self, model_type: str = 'avm') -> Dict[str, Any]:
        """Get overall model interpretability summary"""
        
        if model_type == 'avm' and 'avm' in self.explainers:
            return {
                'model_type': 'Random Forest (Tree-based)',
                'explainability_method': 'SHAP TreeExplainer',
                'feature_count': len(self.feature_names),
                'explanation_quality': 'High',
                'supported_explanations': [
                    'Feature importance',
                    'Individual prediction explanations',
                    'Feature interactions',
                    'Partial dependence'
                ]
            }
        else:
            return {
                'model_type': 'Rule-based fallback',
                'explainability_method': 'Simple attribution',
                'feature_count': len(self.feature_names),
                'explanation_quality': 'Medium',
                'supported_explanations': [
                    'Basic feature importance',
                    'Simple attribution'
                ]
            }
