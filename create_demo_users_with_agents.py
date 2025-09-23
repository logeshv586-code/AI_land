"""
Script to create demo users for all roles with agent assignments
"""
import asyncio
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import User, UserRole, SubscriptionPlan
from app.core.auth import get_password_hash
from app.services.agent_assignment_service import AgentAssignmentService

def create_demo_users():
    """Create demo users for all roles"""
    
    # Create database session
    db = Session(bind=engine)
    
    try:
        # Demo users data
        demo_users = [
            # Buyer Agents
            {
                "username": "demo_buyer_agent",
                "email": "buyer.agent@demo.com",
                "password": "agent123",
                "user_role": UserRole.BUYER_AGENT,
                "first_name": "John",
                "last_name": "Smith",
                "company_name": "Smith Real Estate",
                "license_number": "BA123456",
                "bio": "Experienced buyer agent helping clients find their dream homes",
                "phone": "+1-555-0101",
                "years_experience": 8,
                "specializations": ["Residential", "First-time buyers", "Investment properties"],
                "service_areas": ["Chicago", "Naperville", "Oak Park"],
                "subscription_status": "active"
            },
            {
                "username": "sarah_buyer_agent",
                "email": "sarah.johnson@demo.com",
                "password": "agent123",
                "user_role": UserRole.BUYER_AGENT,
                "first_name": "Sarah",
                "last_name": "Johnson",
                "company_name": "Johnson Properties",
                "license_number": "BA789012",
                "bio": "Specializing in luxury homes and investment properties",
                "phone": "+1-555-0102",
                "years_experience": 12,
                "specializations": ["Luxury homes", "Investment properties", "Condos"],
                "service_areas": ["Chicago", "Evanston", "Highland Park"],
                "subscription_status": "active"
            },
            
            # Seller Agents
            {
                "username": "demo_seller_agent",
                "email": "seller.agent@demo.com",
                "password": "agent123",
                "user_role": UserRole.SELLER_AGENT,
                "first_name": "Michael",
                "last_name": "Davis",
                "company_name": "Davis Realty Group",
                "license_number": "SA123456",
                "bio": "Top-performing seller agent maximizing property values",
                "phone": "+1-555-0201",
                "years_experience": 10,
                "specializations": ["Luxury listings", "Commercial", "Property staging"],
                "service_areas": ["Chicago", "Schaumburg", "Arlington Heights"],
                "subscription_status": "active"
            },
            {
                "username": "emma_seller_agent",
                "email": "emma.wilson@demo.com",
                "password": "agent123",
                "user_role": UserRole.SELLER_AGENT,
                "first_name": "Emma",
                "last_name": "Wilson",
                "company_name": "Wilson & Associates",
                "license_number": "SA789012",
                "bio": "Expert in residential sales and market analysis",
                "phone": "+1-555-0202",
                "years_experience": 7,
                "specializations": ["Residential", "Market analysis", "Home staging"],
                "service_areas": ["Chicago", "Oak Lawn", "Orland Park"],
                "subscription_status": "active"
            },
            
            # Buyers
            {
                "username": "demo_buyer",
                "email": "buyer@demo.com",
                "password": "buyer123",
                "user_role": UserRole.BUYER,
                "first_name": "Alice",
                "last_name": "Brown",
                "phone": "+1-555-0301",
                "bio": "Looking for my first home in Chicago area"
            },
            {
                "username": "james_buyer",
                "email": "james.buyer@demo.com",
                "password": "buyer123",
                "user_role": UserRole.BUYER,
                "first_name": "James",
                "last_name": "Miller",
                "phone": "+1-555-0302",
                "bio": "Seeking investment properties in prime locations"
            },
            
            # Sellers
            {
                "username": "demo_seller",
                "email": "seller@demo.com",
                "password": "seller123",
                "user_role": UserRole.SELLER,
                "first_name": "Robert",
                "last_name": "Garcia",
                "phone": "+1-555-0401",
                "bio": "Selling my family home after 20 years"
            },
            {
                "username": "lisa_seller",
                "email": "lisa.seller@demo.com",
                "password": "seller123",
                "user_role": UserRole.SELLER,
                "first_name": "Lisa",
                "last_name": "Taylor",
                "phone": "+1-555-0402",
                "bio": "Downsizing and selling multiple properties"
            }
        ]
        
        created_users = []
        
        # Create users
        for user_data in demo_users:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == user_data["email"]) | (User.username == user_data["username"])
            ).first()
            
            if existing_user:
                print(f"User {user_data['username']} already exists, skipping...")
                created_users.append(existing_user)
                continue
            
            # Create new user
            password = user_data.pop("password")
            hashed_password = get_password_hash(password)
            
            new_user = User(
                hashed_password=hashed_password,
                is_active=True,
                **user_data
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            created_users.append(new_user)
            
            print(f"Created user: {new_user.username} ({new_user.user_role.value})")
        
        # Now assign agents to buyers and sellers
        agent_service = AgentAssignmentService(db)
        
        # Get agents
        buyer_agents = [user for user in created_users if user.user_role == UserRole.BUYER_AGENT]
        seller_agents = [user for user in created_users if user.user_role == UserRole.SELLER_AGENT]
        
        # Assign agents to buyers
        buyers = [user for user in created_users if user.user_role == UserRole.BUYER]
        for i, buyer in enumerate(buyers):
            if buyer_agents:
                agent = buyer_agents[i % len(buyer_agents)]  # Round-robin assignment
                buyer.assigned_buyer_agent_id = agent.id
                db.commit()
                print(f"Assigned buyer agent {agent.username} to buyer {buyer.username}")
        
        # Assign agents to sellers
        sellers = [user for user in created_users if user.user_role == UserRole.SELLER]
        for i, seller in enumerate(sellers):
            if seller_agents:
                agent = seller_agents[i % len(seller_agents)]  # Round-robin assignment
                seller.assigned_seller_agent_id = agent.id
                db.commit()
                print(f"Assigned seller agent {agent.username} to seller {seller.username}")
        
        print("\n✅ Demo users created successfully!")
        print("\n📋 Demo Credentials:")
        print("=" * 50)
        
        for user in created_users:
            role_name = user.user_role.value if hasattr(user.user_role, 'value') else str(user.user_role)
            print(f"{role_name.replace('_', ' ').title()}: {user.username}")
        
        print("\n🔐 All passwords: agent123 (for agents), buyer123 (for buyers), seller123 (for sellers)")
        print("\n🔗 Agent Assignments:")
        print("-" * 30)
        
        for buyer in buyers:
            if buyer.assigned_buyer_agent_id:
                agent = db.query(User).filter(User.id == buyer.assigned_buyer_agent_id).first()
                print(f"Buyer {buyer.username} → Agent {agent.username}")
        
        for seller in sellers:
            if seller.assigned_seller_agent_id:
                agent = db.query(User).filter(User.id == seller.assigned_seller_agent_id).first()
                print(f"Seller {seller.username} → Agent {agent.username}")
        
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_users()