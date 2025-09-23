#!/usr/bin/env python3
"""
UI Demo Test Script for Land Area Automation System
Tests the backend API endpoints that the frontend will use
"""

import asyncio
import json
import time
from datetime import datetime
import requests
import sys

# API Configuration
API_BASE_URL = "http://localhost:8000"
AUTOMATION_BASE = f"{API_BASE_URL}/api/v1/automation/demo"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_health_check():
    """Test the health check endpoint"""
    print_header("Health Check Test")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is healthy: {data}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_property_valuation():
    """Test property valuation endpoint"""
    print_header("Property Valuation Test")
    
    test_property = {
        "property_details": {
            "address": "123 Demo Street, Chicago, IL",
            "latitude": 41.8781,
            "longitude": -87.6298,
            "property_type": "residential",
            "beds": 3,
            "baths": 2,
            "sqft": 1500,
            "year_built": 2000,
            "lot_size": 0.25
        }
    }
    
    try:
        print_info("Sending property valuation request...")
        response = requests.post(
            f"{AUTOMATION_BASE}/property-valuation",
            json=test_property,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Property valuation completed!")
            print(f"   💰 Predicted Value: ${data.get('predicted_value', 0):,.2f}")
            print(f"   📊 Confidence Score: {data.get('confidence_score', 0)*100:.1f}%")
            print(f"   📏 Price per sq ft: ${data.get('price_per_sqft', 0):.2f}")
            return True
        else:
            print_error(f"Valuation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Valuation error: {e}")
        return False

def test_beneficiary_scoring():
    """Test beneficiary scoring endpoint"""
    print_header("Beneficiary Scoring Test")
    
    test_scoring = {
        "address": "123 Demo Street, Chicago, IL",
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
    
    try:
        print_info("Sending beneficiary scoring request...")
        response = requests.post(
            f"{AUTOMATION_BASE}/beneficiary-score",
            json=test_scoring,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Beneficiary scoring completed!")
            print(f"   🎯 Overall Score: {data.get('overall_score', 0):.1f}/100")
            print(f"   🏫 School Score: {data.get('school_score', 0):.1f}/100")
            print(f"   🛡️  Safety Score: {data.get('safety_score', 0):.1f}/100")
            print(f"   🌱 Environmental Score: {data.get('environmental_score', 0):.1f}/100")
            return True
        else:
            print_error(f"Scoring failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Scoring error: {e}")
        return False

def test_property_recommendations():
    """Test property recommendations endpoint"""
    print_header("Property Recommendations Test")
    
    test_recommendations = {
        "search_type": "location",
        "address": "123 Demo Street, Chicago, IL",
        "radius_km": 10,
        "max_recommendations": 5,
        "recommendation_type": "hybrid",
        "user_preferences": {
            "min_beds": 2,
            "max_beds": 5,
            "min_baths": 1,
            "max_baths": 4,
            "min_price": 100000,
            "max_price": 1000000,
            "property_type": "residential"
        }
    }
    
    try:
        print_info("Sending property recommendations request...")
        response = requests.post(
            f"{AUTOMATION_BASE}/recommendations",
            json=test_recommendations,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {len(data)} property recommendations!")
            for i, rec in enumerate(data[:3], 1):  # Show first 3
                prop = rec.get('recommended_property', {})
                print(f"   {i}. {prop.get('address', 'Unknown Address')}")
                print(f"      💰 ${prop.get('predicted_value', 0):,.0f} | "
                      f"🎯 {rec.get('similarity_score', 0)*100:.0f}% match")
            return True
        else:
            print_error(f"Recommendations failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Recommendations error: {e}")
        return False

def test_comprehensive_analysis():
    """Test comprehensive analysis endpoint"""
    print_header("Comprehensive Analysis Test")
    
    test_comprehensive = {
        "property_details": {
            "address": "123 Demo Street, Chicago, IL",
            "latitude": 41.8781,
            "longitude": -87.6298,
            "property_type": "residential",
            "beds": 3,
            "baths": 2,
            "sqft": 1500,
            "year_built": 2000,
            "lot_size": 0.25
        },
        "custom_weights": {
            "value": 8.0,
            "school": 8.0,
            "crime_inv": 6.0,
            "env_inv": 5.0,
            "employer_proximity": 7.0
        },
        "max_recommendations": 5,
        "recommendation_type": "hybrid"
    }
    
    try:
        print_info("Sending comprehensive analysis request...")
        start_time = time.time()
        response = requests.post(
            f"{AUTOMATION_BASE}/comprehensive-analysis",
            json=test_comprehensive,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Comprehensive analysis completed in {end_time - start_time:.2f} seconds!")
            
            # Property Valuation
            valuation = data.get('property_valuation', {})
            print(f"   💰 Property Value: ${valuation.get('predicted_value', 0):,.2f}")
            
            # Beneficiary Score
            scoring = data.get('beneficiary_score', {})
            print(f"   🎯 Investment Score: {scoring.get('overall_score', 0):.1f}/100")
            
            # Recommendations
            recommendations = data.get('recommendations', [])
            print(f"   🏠 Similar Properties: {len(recommendations)} found")
            
            # Risk Assessment
            risk = data.get('risk_assessment', {})
            print(f"   🛡️  Risk Level: {risk.get('risk_level', 'UNKNOWN')}")
            
            return True
        else:
            print_error(f"Comprehensive analysis failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Comprehensive analysis error: {e}")
        return False

def main():
    """Run all UI demo tests"""
    print_header("🏡 Land Area Automation UI Demo Test")
    print_info("Testing backend API endpoints for frontend integration...")
    
    tests = [
        ("Health Check", test_health_check),
        ("Property Valuation", test_property_valuation),
        ("Beneficiary Scoring", test_beneficiary_scoring),
        ("Property Recommendations", test_property_recommendations),
        ("Comprehensive Analysis", test_comprehensive_analysis),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print_success(f"{test_name} test passed!")
            else:
                print_error(f"{test_name} test failed!")
        except Exception as e:
            print_error(f"{test_name} test error: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print_header("Test Results Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print_success("🎉 All tests passed! The UI backend is ready!")
        print_info("You can now:")
        print_info("  1. Start the frontend: cd frontend && npm start")
        print_info("  2. Access the UI at: http://localhost:3000")
        print_info("  3. Navigate to Automation Hub to test the features")
    else:
        print_error("Some tests failed. Please check the backend server.")
        print_info("Make sure the API server is running: python main.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
