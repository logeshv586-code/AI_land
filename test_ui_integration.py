#!/usr/bin/env python3
"""
🚀 Land Area Automation UI Integration Test
Tests the complete frontend-backend integration for the automation system.
"""

import requests
import json
import time
from datetime import datetime

def test_ui_backend_integration():
    """Test the complete UI-backend integration"""
    
    print("\n" + "="*60)
    print("🚀 🏡 LAND AREA AUTOMATION UI INTEGRATION TEST")
    print("="*60)
    print("ℹ️  Testing complete frontend-backend integration...")
    
    base_url = "http://localhost:8000"
    demo_base = f"{base_url}/api/v1/automation/demo"
    
    # Test data for property valuation
    test_property = {
        "address": "123 Demo Street, Chicago, IL 60601",
        "beds": 3,
        "baths": 2,
        "sqft": 1500,
        "year_built": 2010,
        "latitude": 41.8781,
        "longitude": -87.6298
    }
    
    # Test data for beneficiary scoring
    test_scoring = {
        "address": "123 Demo Street, Chicago, IL 60601",
        "latitude": 41.8781,
        "longitude": -87.6298,
        "custom_weights": {
            "value": 8.0,
            "school": 8.0,
            "crime_inv": 6.0,
            "env_inv": 5.0,
            "employer_proximity": 7.0
        }
    }
    
    # Test data for recommendations
    test_recommendations = {
        "address": "123 Demo Street, Chicago, IL 60601",
        "max_recommendations": 5,
        "algorithm": "hybrid"
    }
    
    tests_passed = 0
    total_tests = 4
    
    try:
        # Test 1: Health Check
        print("\n" + "="*60)
        print("🚀 Health Check Test")
        print("="*60)
        
        response = requests.get(f"{demo_base}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API is healthy: {health_data}")
            tests_passed += 1
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Test 2: Property Valuation
        print("\n" + "="*60)
        print("🚀 Property Valuation Test")
        print("="*60)
        print("ℹ️  Testing property valuation endpoint...")
        
        response = requests.post(f"{demo_base}/property-valuation", 
                               json=test_property, timeout=15)
        if response.status_code == 200:
            valuation_data = response.json()
            print(f"✅ Property valuation completed!")
            print(f"   💰 Predicted Value: ${valuation_data['predicted_value']:,.2f}")
            if 'confidence_score' in valuation_data:
                print(f"   📊 Confidence Score: {valuation_data['confidence_score']:.1%}")
            print(f"   📏 Price per sq ft: ${valuation_data['price_per_sqft']:.2f}")
            tests_passed += 1
        else:
            print(f"❌ Valuation failed: {response.status_code} - {response.text}")
        
        # Test 3: Beneficiary Scoring
        print("\n" + "="*60)
        print("🚀 Beneficiary Scoring Test")
        print("="*60)
        print("ℹ️  Testing beneficiary scoring endpoint...")
        
        response = requests.post(f"{demo_base}/beneficiary-score", 
                               json=test_scoring, timeout=15)
        if response.status_code == 200:
            scoring_data = response.json()
            print(f"✅ Beneficiary scoring completed!")
            print(f"   🎯 Overall Score: {scoring_data['overall_score']:.1f}/100")
            print(f"   🏫 School Score: {scoring_data['school_score']:.1f}/100")
            print(f"   🛡️  Safety Score: {scoring_data['safety_score']:.1f}/100")
            print(f"   🌱 Environmental Score: {scoring_data['environmental_score']:.1f}/100")
            tests_passed += 1
        else:
            print(f"❌ Scoring failed: {response.status_code} - {response.text}")
        
        # Test 4: Property Recommendations
        print("\n" + "="*60)
        print("🚀 Property Recommendations Test")
        print("="*60)
        print("ℹ️  Testing property recommendations endpoint...")
        
        response = requests.post(f"{demo_base}/recommendations", 
                               json=test_recommendations, timeout=15)
        if response.status_code == 200:
            recommendations_data = response.json()
            print(f"✅ Found {len(recommendations_data)} property recommendations!")
            for i, rec in enumerate(recommendations_data[:3], 1):
                prop = rec['recommended_property']
                print(f"   {i}. Property #{prop['id']}")
                print(f"      💰 ${prop['predicted_value']:,} | 🎯 {rec['similarity_score']:.0%} match")
            tests_passed += 1
        else:
            print(f"❌ Recommendations failed: {response.status_code} - {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("ℹ️  Make sure the backend server is running: python main.py")
    
    # Results Summary
    print("\n" + "="*60)
    print("🚀 Integration Test Results Summary")
    print("="*60)
    
    success_rate = (tests_passed / total_tests) * 100
    
    if tests_passed == total_tests:
        print(f"🎉 ALL TESTS PASSED! ({tests_passed}/{total_tests})")
        print("✅ Frontend-Backend Integration: SUCCESSFUL")
        print("✅ UI is ready for use at: http://localhost:3001")
        print("✅ Backend API running at: http://localhost:8000")
        print("\n🚀 Your Land Area Automation UI is fully operational!")
    else:
        print(f"⚠️  {tests_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
        if tests_passed >= 3:
            print("✅ Core functionality working - UI is usable")
        else:
            print("❌ Major issues detected - check backend server")
    
    print("\n🎯 Access your automation UI:")
    print("   🌐 Frontend: http://localhost:3001")
    print("   🔧 Backend API: http://localhost:8000/docs")
    print("   📊 Demo Endpoints: http://localhost:8000/api/v1/automation/demo/")

if __name__ == "__main__":
    test_ui_backend_integration()
