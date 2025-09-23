#!/usr/bin/env python3
"""
Comprehensive Land Area Analysis Example

This example demonstrates how to use the Land Area Automation API
to perform comprehensive real estate analysis including:
- Property valuation (AVM)
- Beneficiary scoring
- Property recommendations
- SHAP explanations
"""

import requests
import json
from typing import Dict, Any
import time

class LandAreaAnalysisClient:
    """Client for Land Area Automation API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_token: str = None):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}" if api_token else None
        }
    
    def comprehensive_analysis(self, analysis_request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive land area analysis"""
        url = f"{self.base_url}/api/v1/automation/comprehensive-analysis"
        
        response = requests.post(url, json=analysis_request, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def property_valuation(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get property valuation using AVM"""
        url = f"{self.base_url}/api/v1/automation/property-valuation"
        
        response = requests.post(url, json=property_data, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_recommendations(self, recommendation_request: Dict[str, Any]) -> list:
        """Get property recommendations"""
        url = f"{self.base_url}/api/v1/automation/recommendations"
        
        response = requests.post(url, json=recommendation_request, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_explanation(self, property_id: int) -> Dict[str, Any]:
        """Get SHAP explanation for property valuation"""
        url = f"{self.base_url}/api/v1/automation/property-valuation/{property_id}/explanation"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()

def main():
    """Main example function"""
    
    # Initialize client (replace with your actual API token)
    client = LandAreaAnalysisClient(api_token="your-api-token-here")
    
    # Example 1: Comprehensive Analysis
    print("🏡 Example 1: Comprehensive Land Area Analysis")
    print("=" * 50)
    
    analysis_request = {
        "address": "1600 Amphitheatre Parkway, Mountain View, CA",
        "latitude": 37.4220,
        "longitude": -122.0841,
        "property_type": "residential",
        "beds": 4,
        "baths": 3,
        "sqft": 2200,
        "year_built": 2010,
        "lot_size": 0.3,
        "investment_budget": 800000,
        "investment_timeline": "3-5 years",
        "risk_tolerance": "medium",
        "include_avm": True,
        "include_beneficiary_score": True,
        "include_recommendations": True,
        "include_explanations": True,
        "custom_weights": {
            "value": 8.0,
            "school": 9.0,  # High priority for families
            "crime_inv": 7.0,
            "env_inv": 6.0,
            "employer_proximity": 8.0  # Important in tech areas
        },
        "max_recommendations": 5
    }
    
    try:
        start_time = time.time()
        analysis = client.comprehensive_analysis(analysis_request)
        processing_time = time.time() - start_time
        
        print(f"✅ Analysis completed in {processing_time:.2f} seconds")
        print(f"📊 Overall Score: {analysis['overall_score']:.1f}/100")
        print(f"💡 Recommendation: {analysis['recommendation'].upper()}")
        print(f"🎯 Confidence Level: {analysis['confidence_level']:.1%}")
        
        if 'property_valuation' in analysis:
            valuation = analysis['property_valuation']
            print(f"💰 Predicted Value: ${valuation['predicted_value']:,.2f}")
            print(f"📈 Uncertainty: ±${valuation['value_uncertainty']:,.2f}")
        
        if 'beneficiary_score' in analysis:
            beneficiary = analysis['beneficiary_score']
            print(f"\n🏆 Beneficiary Score Breakdown:")
            print(f"  Overall: {beneficiary['overall_score']:.1f}/100")
            print(f"  Value: {beneficiary['value_score']:.1f}/100")
            print(f"  Schools: {beneficiary['school_score']:.1f}/100")
            print(f"  Safety: {beneficiary['safety_score']:.1f}/100")
            print(f"  Environment: {beneficiary['environmental_score']:.1f}/100")
            print(f"  Accessibility: {beneficiary['accessibility_score']:.1f}/100")
        
        if 'similar_properties' in analysis and analysis['similar_properties']:
            print(f"\n🏘️ Top Recommendations:")
            for i, rec in enumerate(analysis['similar_properties'][:3], 1):
                prop = rec['recommended_property']
                print(f"  {i}. ${prop['predicted_value']:,.2f} - "
                      f"{prop['beds']}bed/{prop['baths']}bath, {prop['sqft']}sqft "
                      f"(Similarity: {rec['similarity_score']:.2f})")
        
        if 'feature_explanations' in analysis and analysis['feature_explanations']:
            explanations = analysis['feature_explanations']
            if 'avm_explanation' in explanations:
                avm_exp = explanations['avm_explanation']
                print(f"\n🔍 Top Value Drivers:")
                for feature in avm_exp.get('top_positive_features', [])[:3]:
                    print(f"  + {feature['impact_description']}")
                
                for feature in avm_exp.get('top_negative_features', [])[:2]:
                    print(f"  - {feature['impact_description']}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n" + "=" * 50)
    
    # Example 2: Property Valuation Only
    print("💰 Example 2: Property Valuation (AVM)")
    print("=" * 50)
    
    property_data = {
        "address": "123 Market Street, San Francisco, CA",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "property_type": "residential",
        "beds": 2,
        "baths": 2,
        "sqft": 1200,
        "year_built": 1995,
        "lot_size": 0.1
    }
    
    try:
        valuation = client.property_valuation(property_data)
        
        print(f"🏠 Property: {property_data['address']}")
        print(f"💰 Predicted Value: ${valuation['predicted_value']:,.2f}")
        print(f"📊 Price per sqft: ${valuation['price_per_sqft']:.2f}")
        print(f"📈 Uncertainty: ±${valuation['value_uncertainty']:,.2f}")
        print(f"📅 Valuation Date: {valuation['valuation_date']}")
        
        # Get explanation for this valuation
        if 'id' in valuation:
            print(f"\n🔍 Getting explanation for property {valuation['id']}...")
            explanation = client.get_explanation(valuation['id'])
            
            print(f"📊 Base Value: ${explanation['base_value']:,.2f}")
            print(f"🎯 Final Prediction: ${explanation['prediction_value']:,.2f}")
            print(f"🔧 Explanation Type: {explanation['explanation_type']}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Example 3: Location-based Recommendations
    print("🗺️ Example 3: Location-based Recommendations")
    print("=" * 50)
    
    recommendation_request = {
        "location": {
            "lat": 37.7749,  # San Francisco
            "lon": -122.4194
        },
        "radius_km": 15.0,
        "max_recommendations": 8,
        "user_preferences": {
            "min_beds": 2,
            "max_price": 1000000,
            "property_type": "residential"
        }
    }
    
    try:
        recommendations = client.get_recommendations(recommendation_request)
        
        print(f"🏘️ Found {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            prop = rec['recommended_property']
            print(f"  {i}. ${prop.get('predicted_value', 0):,.2f} - "
                  f"{prop.get('beds', 'N/A')}bed/{prop.get('baths', 'N/A')}bath")
            print(f"     Reason: {rec['recommendation_reason']}")
            print(f"     Confidence: {rec['confidence_score']:.1%}")
            print()
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def batch_analysis_example():
    """Example of analyzing multiple properties"""
    
    print("📊 Batch Analysis Example")
    print("=" * 50)
    
    client = LandAreaAnalysisClient(api_token="your-api-token-here")
    
    properties = [
        {
            "address": "Property 1, Chicago, IL",
            "latitude": 41.8781,
            "longitude": -87.6298,
            "beds": 3, "baths": 2, "sqft": 1500
        },
        {
            "address": "Property 2, Austin, TX", 
            "latitude": 30.2672,
            "longitude": -97.7431,
            "beds": 4, "baths": 3, "sqft": 2000
        },
        {
            "address": "Property 3, Denver, CO",
            "latitude": 39.7392,
            "longitude": -104.9903,
            "beds": 2, "baths": 2, "sqft": 1200
        }
    ]
    
    results = []
    
    for i, prop in enumerate(properties, 1):
        print(f"Analyzing property {i}/3: {prop['address']}")
        
        try:
            analysis_request = {
                **prop,
                "property_type": "residential",
                "year_built": 2000,
                "risk_tolerance": "medium",
                "include_avm": True,
                "include_beneficiary_score": True
            }
            
            result = client.comprehensive_analysis(analysis_request)
            results.append({
                "property": prop['address'],
                "score": result['overall_score'],
                "recommendation": result['recommendation'],
                "value": result.get('property_valuation', {}).get('predicted_value', 0)
            })
            
        except Exception as e:
            print(f"  ❌ Error analyzing {prop['address']}: {e}")
            continue
    
    # Sort by overall score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n🏆 Ranking Results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['property']}")
        print(f"     Score: {result['score']:.1f}/100")
        print(f"     Recommendation: {result['recommendation'].upper()}")
        print(f"     Est. Value: ${result['value']:,.2f}")
        print()

if __name__ == "__main__":
    print("🚀 Land Area Automation API Examples")
    print("=" * 60)
    
    # Run main examples
    main()
    
    print("\n" + "=" * 60)
    
    # Run batch analysis example
    batch_analysis_example()
    
    print("✅ Examples completed!")
    print("\n💡 Tips:")
    print("- Replace 'your-api-token-here' with your actual API token")
    print("- Adjust coordinates and property details for your use case")
    print("- Use custom weights to prioritize factors important to you")
    print("- Enable explanations to understand AI decision making")
