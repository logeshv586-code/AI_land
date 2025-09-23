#!/usr/bin/env python3
"""
🚀 Test Demo Login Script
Tests the demo user login functionality for the Land Area Automation UI
"""

import requests
import json

def test_demo_login():
    """Test demo user login"""
    
    print("🚀 Testing Demo User Login")
    print("="*50)
    
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/api/v1/auth/token"
    
    # Demo credentials
    credentials = {
        "username": "demo",
        "password": "demo123"
    }
    
    try:
        print("ℹ️  Attempting login with demo credentials...")
        print(f"   Username: {credentials['username']}")
        print(f"   Password: {credentials['password']}")
        
        # Send login request
        response = requests.post(
            login_url,
            data=credentials,  # OAuth2PasswordRequestForm expects form data
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            print(f"   Access Token: {token_data['access_token'][:50]}...")
            print(f"   Token Type: {token_data['token_type']}")
            
            # Test authenticated endpoint
            print("\n🧪 Testing authenticated endpoint...")
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}"
            }
            
            # Try to access a protected endpoint
            protected_url = f"{base_url}/api/v1/automation/health"
            protected_response = requests.get(protected_url, headers=headers, timeout=10)
            
            if protected_response.status_code == 200:
                print("✅ Authenticated endpoint access successful!")
                print(f"   Response: {protected_response.json()}")
            else:
                print(f"⚠️  Authenticated endpoint returned: {protected_response.status_code}")
                print(f"   Response: {protected_response.text}")
            
            return True
            
        else:
            print(f"❌ Login failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed!")
        print("ℹ️  Make sure the backend server is running: python main.py")
        return False
        
    except Exception as e:
        print(f"❌ Login test failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("🎯 Demo Login Test for Land Area Automation UI")
    print("="*60)
    
    success = test_demo_login()
    
    if success:
        print("\n" + "="*60)
        print("🎉 DEMO LOGIN TEST PASSED!")
        print("="*60)
        print("✅ Demo credentials are working correctly!")
        print("\n🌐 You can now login to the UI:")
        print("   1. Open: http://localhost:3001/login")
        print("   2. Enter Username: demo")
        print("   3. Enter Password: demo123")
        print("   4. Click Login")
        print("   5. Explore the automation features!")
        
    else:
        print("\n❌ Demo login test failed!")
        print("ℹ️  Please check:")
        print("   1. Backend server is running: python main.py")
        print("   2. Demo user was created: python create_demo_user.py")
        print("   3. Database is accessible")

if __name__ == "__main__":
    main()
