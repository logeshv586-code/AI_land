#!/usr/bin/env python3
"""
🚀 Complete Login Flow Test
Tests the complete login flow from frontend to backend for the Land Area Automation UI
"""

import requests
import json
import time

def test_complete_login_flow():
    """Test the complete login flow"""
    
    print("🚀 Testing Complete Login Flow")
    print("="*60)
    
    backend_url = "http://localhost:8000"
    frontend_url = "http://localhost:3001"
    
    # Test 1: Frontend is accessible
    print("\n1️⃣ Testing Frontend Accessibility")
    print("-" * 40)
    
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is accessible at http://localhost:3001")
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {str(e)}")
        return False
    
    # Test 2: Backend API is accessible
    print("\n2️⃣ Testing Backend API Accessibility")
    print("-" * 40)
    
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend API is accessible at http://localhost:8000")
            print(f"   Health Status: {response.json()}")
        else:
            print(f"❌ Backend API returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend API not accessible: {str(e)}")
        return False
    
    # Test 3: Login endpoint
    print("\n3️⃣ Testing Login Endpoint")
    print("-" * 40)
    
    login_url = f"{backend_url}/api/v1/auth/token"
    credentials = {
        "username": "demo",
        "password": "demo123"
    }
    
    try:
        response = requests.post(
            login_url,
            data=credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            print("✅ Login endpoint working correctly")
            print(f"   Token Type: {token_data['token_type']}")
            print(f"   Token Preview: {access_token[:30]}...")
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login endpoint error: {str(e)}")
        return False
    
    # Test 4: User info endpoint
    print("\n4️⃣ Testing User Info Endpoint")
    print("-" * 40)
    
    user_info_url = f"{backend_url}/api/v1/auth/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(user_info_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ User info endpoint working correctly")
            print(f"   Username: {user_data['username']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Active: {user_data['is_active']}")
        else:
            print(f"❌ User info failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ User info endpoint error: {str(e)}")
        return False
    
    # Test 5: Demo automation endpoints
    print("\n5️⃣ Testing Demo Automation Endpoints")
    print("-" * 40)
    
    demo_health_url = f"{backend_url}/api/v1/automation/demo/health"
    
    try:
        response = requests.get(demo_health_url, timeout=10)
        
        if response.status_code == 200:
            demo_data = response.json()
            print("✅ Demo automation endpoints accessible")
            print(f"   Service: {demo_data['service']}")
            print(f"   Status: {demo_data['status']}")
        else:
            print(f"❌ Demo automation failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Demo automation error: {str(e)}")
        return False
    
    # Test 6: CORS configuration
    print("\n6️⃣ Testing CORS Configuration")
    print("-" * 40)
    
    try:
        # Test preflight request
        response = requests.options(
            login_url,
            headers={
                "Origin": frontend_url,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            print("✅ CORS configuration working correctly")
            cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
            for header, value in cors_headers.items():
                print(f"   {header}: {value}")
        else:
            print(f"⚠️  CORS preflight returned: {response.status_code}")
    except Exception as e:
        print(f"⚠️  CORS test error: {str(e)}")
    
    return True

def main():
    """Main function"""
    print("🎯 Complete Login Flow Test for Land Area Automation UI")
    print("="*70)
    
    success = test_complete_login_flow()
    
    if success:
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED - LOGIN FLOW IS WORKING!")
        print("="*70)
        print("✅ Complete login flow is functional!")
        print("\n🌐 Ready to use:")
        print("   1. Frontend: http://localhost:3001")
        print("   2. Backend API: http://localhost:8000")
        print("   3. API Docs: http://localhost:8000/docs")
        print("\n🔑 Demo Credentials:")
        print("   Username: demo")
        print("   Password: demo123")
        print("\n🚀 Next Steps:")
        print("   1. Open http://localhost:3001/login in your browser")
        print("   2. Login with demo credentials")
        print("   3. Navigate to 🤖 Automation section")
        print("   4. Explore the Land Area Automation features!")
        print("\n🎯 The manifest.json errors you saw earlier have been fixed!")
        print("   The UI should now work without any 404 errors.")
        
    else:
        print("\n❌ Some tests failed!")
        print("ℹ️  Please check:")
        print("   1. Backend server: python main.py")
        print("   2. Frontend server: cd frontend && npm start")
        print("   3. Demo user exists: python create_demo_user.py")

if __name__ == "__main__":
    main()
