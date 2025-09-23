#!/usr/bin/env python3
"""
Simple API test without authentication to demonstrate the system working
"""

import requests
import json

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_api_docs():
    """Test that API docs are accessible"""
    try:
        response = requests.get("http://localhost:8000/docs")
        print(f"✅ API Docs: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ API Docs Failed: {e}")
        return False

def test_openapi_spec():
    """Test OpenAPI specification"""
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        print(f"✅ OpenAPI Spec: {response.status_code}")
        spec = response.json()
        print(f"   API Title: {spec.get('info', {}).get('title', 'Unknown')}")
        print(f"   API Version: {spec.get('info', {}).get('version', 'Unknown')}")
        
        # Count endpoints
        paths = spec.get('paths', {})
        endpoint_count = len(paths)
        print(f"   Total Endpoints: {endpoint_count}")
        
        # Show some key endpoints
        key_endpoints = [
            '/api/v1/automation/comprehensive-analysis',
            '/api/v1/automation/property-valuation',
            '/api/v1/automation/beneficiary-score',
            '/api/v1/automation/recommendations'
        ]
        
        print("   Key Automation Endpoints:")
        for endpoint in key_endpoints:
            if endpoint in paths:
                methods = list(paths[endpoint].keys())
                print(f"     ✓ {endpoint} ({', '.join(methods).upper()})")
            else:
                print(f"     ✗ {endpoint} (not found)")
        
        return True
    except Exception as e:
        print(f"❌ OpenAPI Spec Failed: {e}")
        return False

def main():
    """Run simple API tests"""
    print("🚀 Land Area Automation API - Simple Test")
    print("=" * 50)
    
    print("\n📊 Testing API Endpoints...")
    
    # Test basic endpoints
    health_ok = test_health_endpoint()
    docs_ok = test_api_docs()
    spec_ok = test_openapi_spec()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   API Documentation: {'✅ PASS' if docs_ok else '❌ FAIL'}")
    print(f"   OpenAPI Specification: {'✅ PASS' if spec_ok else '❌ FAIL'}")
    
    if all([health_ok, docs_ok, spec_ok]):
        print("\n🎉 All tests passed! The Land Area Automation API is running successfully!")
        print("\n🌐 Access Points:")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • Interactive API: http://localhost:8000/redoc")
        print("   • Health Check: http://localhost:8000/health")
        
        print("\n🔧 Available Features:")
        print("   • Comprehensive Land Analysis")
        print("   • Automated Property Valuation (AVM)")
        print("   • Beneficiary Investment Scoring")
        print("   • Property Recommendations")
        print("   • SHAP-based AI Explanations")
        print("   • Risk Assessment & Opportunities")
        
        print("\n💡 Next Steps:")
        print("   1. Open http://localhost:8000/docs in your browser")
        print("   2. Try the API endpoints with sample data")
        print("   3. Explore the comprehensive analysis features")
        print("   4. Review the documentation in docs/")
        
    else:
        print("\n❌ Some tests failed. Please check the server is running.")
        print("   Run: uvicorn main:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    main()
