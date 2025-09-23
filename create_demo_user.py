#!/usr/bin/env python3
"""
🚀 Create Demo User Script
Creates a demo user with credentials: demo/demo123 for testing the Land Area Automation UI
"""

import sys
import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, User
from app.core.auth import get_password_hash

def create_demo_user():
    """Create a demo user for testing"""
    
    print("🚀 Creating Demo User for Land Area Automation UI")
    print("="*60)
    
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if demo user already exists
        existing_user = db.query(User).filter(User.username == "demo").first()
        
        if existing_user:
            print("ℹ️  Demo user already exists!")
            print(f"   Username: {existing_user.username}")
            print(f"   Email: {existing_user.email}")
            print(f"   Created: {existing_user.created_at}")
            print(f"   Active: {existing_user.is_active}")
            
            # Update password to ensure it's correct
            existing_user.hashed_password = get_password_hash("demo123")
            db.commit()
            print("✅ Demo user password updated to 'demo123'")
            
        else:
            # Create new demo user
            demo_user = User(
                email="demo@landanalysis.ai",
                username="demo",
                hashed_password=get_password_hash("demo123"),
                is_active=True,
                is_admin=False
            )
            
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            
            print("✅ Demo user created successfully!")
            print(f"   Username: {demo_user.username}")
            print(f"   Email: {demo_user.email}")
            print(f"   Created: {demo_user.created_at}")
            print(f"   Active: {demo_user.is_active}")
        
        print("\n🎯 Demo Credentials:")
        print("   Username: demo")
        print("   Password: demo123")
        print("\n🌐 Login URL: http://localhost:3001/login")
        print("🔧 API Docs: http://localhost:8000/docs")
        
        # Test authentication
        print("\n🧪 Testing authentication...")
        from app.core.auth import authenticate_user
        
        auth_result = authenticate_user(db, "demo", "demo123")
        if auth_result:
            print("✅ Authentication test passed!")
            print("🎉 Demo user is ready for login!")
        else:
            print("❌ Authentication test failed!")
            
    except Exception as e:
        print(f"❌ Error creating demo user: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()
    
    return True

def main():
    """Main function"""
    success = create_demo_user()
    
    if success:
        print("\n" + "="*60)
        print("🎉 DEMO USER SETUP COMPLETE!")
        print("="*60)
        print("✅ You can now login to the UI with:")
        print("   👤 Username: demo")
        print("   🔑 Password: demo123")
        print("\n🚀 Next Steps:")
        print("   1. Make sure backend is running: python main.py")
        print("   2. Make sure frontend is running: cd frontend && npm start")
        print("   3. Open browser: http://localhost:3001/login")
        print("   4. Login with demo credentials")
        print("   5. Explore the Land Area Automation features!")
    else:
        print("\n❌ Demo user setup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
