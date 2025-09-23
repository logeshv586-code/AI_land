from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import asyncio
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Message, PropertyListing, UserRole, LandAnalysis, Location
from app.schemas import MessageCreate, MessageResponse, MessageType
from app.routers.auth import get_current_user
from app.services.communication_validator import communication_validator
from app.services.agent_assignment_service import AgentAssignmentService

router = APIRouter()

# Enhanced schemas for AI integration
class LandAnalysisRequest(BaseModel):
    property_id: Optional[int] = None
    location: str
    message_content: str
    analysis_type: str = "comprehensive"  # comprehensive, quick, market_focused

class AIEnhancedMessageCreate(BaseModel):
    recipient_id: int
    property_listing_id: Optional[int] = None
    subject: Optional[str] = None
    content: str
    message_type: str = "inquiry"
    priority: str = "normal"
    request_ai_analysis: bool = False
    analysis_preferences: Optional[Dict[str, Any]] = None

class MessageEnhancementResponse(BaseModel):
    has_land_analysis: bool = False
    has_price_analysis: bool = False
    has_market_trends: bool = False
    suggested_responses: List[str] = []
    ai_insights: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None

@router.post("/", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message following agent-mediated communication rules:
    - Buyers can only contact seller agents
    - Sellers can only contact buyer agents
    - Agents can contact anyone
    """
    
    # Get recipient user
    recipient = db.query(User).filter(User.id == message_data.recipient_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )
    
    # Get property listing
    property_listing = db.query(PropertyListing).filter(
        PropertyListing.id == message_data.property_listing_id
    ).first()
    if not property_listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property listing not found"
        )
    
    # Validate communication rules using agent assignment service
    agent_service = AgentAssignmentService(db)
    if not agent_service.can_communicate(current_user.id, message_data.recipient_id):
        # Get communication path suggestion
        communication_path = agent_service.get_communication_path(current_user.id, message_data.recipient_id)
        if len(communication_path) > 2:
            # There's an agent mediation path available
            suggested_recipient_id = communication_path[1] if len(communication_path) > 1 else message_data.recipient_id
            suggested_recipient = db.query(User).filter(User.id == suggested_recipient_id).first()
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": _get_communication_error_message(current_user.user_role, recipient.user_role),
                    "suggested_recipient_id": suggested_recipient_id,
                    "suggested_recipient_name": f"{suggested_recipient.first_name} {suggested_recipient.last_name}" if suggested_recipient else None,
                    "communication_path": communication_path
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=_get_communication_error_message(current_user.user_role, recipient.user_role)
            )
    
    # Create message
    db_message = Message(
        sender_id=current_user.id,
        recipient_id=message_data.recipient_id,
        property_listing_id=message_data.property_listing_id,
        subject=message_data.subject,
        content=message_data.content,
        message_type=message_data.message_type,
        priority=message_data.priority
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message

@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    message_type: Optional[MessageType] = None,
    is_read: Optional[bool] = None,
    property_listing_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages for the current user (both sent and received)"""
    
    query = db.query(Message).filter(
        or_(
            Message.sender_id == current_user.id,
            Message.recipient_id == current_user.id
        )
    )
    
    # Apply filters
    if message_type:
        query = query.filter(Message.message_type == message_type.value)
    
    if is_read is not None:
        query = query.filter(Message.is_read == is_read)
    
    if property_listing_id:
        query = query.filter(Message.property_listing_id == property_listing_id)
    
    # Order by creation date (newest first)
    query = query.order_by(Message.created_at.desc())
    
    messages = query.offset(skip).limit(limit).all()
    return messages

@router.get("/inbox", response_model=List[MessageResponse])
async def get_inbox(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get received messages (inbox)"""
    
    query = db.query(Message).filter(Message.recipient_id == current_user.id)
    
    if unread_only:
        query = query.filter(Message.is_read == False)
    
    query = query.order_by(Message.created_at.desc())
    messages = query.offset(skip).limit(limit).all()
    
    return messages

@router.get("/sent", response_model=List[MessageResponse])
async def get_sent_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sent messages"""
    
    query = db.query(Message).filter(Message.sender_id == current_user.id)
    query = query.order_by(Message.created_at.desc())
    messages = query.offset(skip).limit(limit).all()
    
    return messages

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific message"""
    
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user has access to this message
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this message"
        )
    
    # Mark as read if user is the recipient
    if message.recipient_id == current_user.id and not message.is_read:
        message.is_read = True
        message.read_at = datetime.utcnow()
        db.commit()
    
    return message

@router.put("/{message_id}/read")
async def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a message as read"""
    
    message = db.query(Message).filter(
        and_(
            Message.id == message_id,
            Message.recipient_id == current_user.id
        )
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or you're not the recipient"
        )
    
    message.is_read = True
    message.read_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Message marked as read"}

@router.put("/{message_id}/archive")
async def archive_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive a message"""
    
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user has access to this message
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this message"
        )
    
    message.is_archived = True
    db.commit()
    
    return {"message": "Message archived"}

@router.get("/stats/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread messages"""
    
    unread_count = db.query(Message).filter(
        and_(
            Message.recipient_id == current_user.id,
            Message.is_read == False
        )
    ).count()
    
    return {"unread_count": unread_count}

@router.get("/property/{property_id}/conversation", response_model=List[MessageResponse])
async def get_property_conversation(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages related to a specific property"""
    
    # Check if property exists
    property_listing = db.query(PropertyListing).filter(PropertyListing.id == property_id).first()
    if not property_listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property listing not found"
        )
    
    # Get messages where user is either sender or recipient
    messages = db.query(Message).filter(
        and_(
            Message.property_listing_id == property_id,
            or_(
                Message.sender_id == current_user.id,
                Message.recipient_id == current_user.id
            )
        )
    ).order_by(Message.created_at.asc()).all()
    
    return messages

def _can_send_message(sender: User, recipient: User, property_listing: PropertyListing) -> bool:
    """
    Check if sender can send message to recipient based on agent-mediated rules
    """
    sender_role = sender.user_role
    recipient_role = recipient.user_role
    
    # Agents can contact anyone
    if sender_role in [UserRole.BUYER_AGENT, UserRole.SELLER_AGENT]:
        return True
    
    # Buyers can only contact seller agents
    if sender_role == UserRole.BUYER:
        return recipient_role == UserRole.SELLER_AGENT
    
    # Sellers can only contact buyer agents
    if sender_role == UserRole.SELLER:
        return recipient_role == UserRole.BUYER_AGENT
    
    return False

def _get_communication_error_message(sender_role: UserRole, recipient_role: UserRole) -> str:
    """Get appropriate error message for communication rule violation"""
    
    if sender_role == UserRole.BUYER:
        if recipient_role == UserRole.SELLER:
            return "Buyers cannot contact sellers directly. Please contact the seller's agent."
        elif recipient_role == UserRole.BUYER_AGENT:
            return "Buyers should contact seller agents, not buyer agents."
        else:
            return "Buyers can only contact seller agents."
    
    elif sender_role == UserRole.SELLER:
        if recipient_role == UserRole.BUYER:
            return "Sellers cannot contact buyers directly. Please contact a buyer's agent."
        elif recipient_role == UserRole.SELLER_AGENT:
            return "Sellers should contact buyer agents, not seller agents."
        else:
            return "Sellers can only contact buyer agents."
    
    return "Communication not allowed between these user types."

@router.post("/validate-communication/{recipient_id}")
async def validate_communication(
    recipient_id: int,
    property_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate if communication is allowed between current user and recipient
    """
    # Get recipient
    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    # Prepare context
    context = {}
    if property_id:
        property_listing = db.query(PropertyListing).filter(PropertyListing.id == property_id).first()
        if property_listing:
            context["property_id"] = property_id
            context["property_title"] = property_listing.title

    # Validate communication
    is_allowed, message, suggestions = communication_validator.validate_communication(
        sender=current_user,
        recipient=recipient,
        context=context
    )

    # Get communication path suggestions if needed
    communication_path = communication_validator.suggest_communication_path(
        sender=current_user,
        target_recipient=recipient,
        db=db
    )

    return {
        "is_allowed": is_allowed,
        "message": message,
        "suggestions": suggestions,
        "communication_path": communication_path,
        "sender_role": current_user.user_role.value if hasattr(current_user.user_role, 'value') else current_user.user_role,
        "recipient_role": recipient.user_role.value if hasattr(recipient.user_role, 'value') else recipient.user_role
    }

@router.get("/communication-guidelines")
async def get_communication_guidelines(
    current_user: User = Depends(get_current_user)
):
    """
    Get communication guidelines for the current user's role
    """
    user_role = current_user.user_role.value if hasattr(current_user.user_role, 'value') else current_user.user_role
    guidelines = communication_validator.get_communication_guidelines(user_role)

    return {
        "user_role": user_role,
        "guidelines": guidelines,
        "platform_rules": {
            "buyer_rules": [
                "Browse properties freely",
                "Contact seller agents directly for property inquiries",
                "Work with buyer agents for negotiations and offers",
                "No direct communication with sellers"
            ],
            "seller_rules": [
                "List and manage properties",
                "Work with seller agents for buyer communications",
                "Track property performance and inquiries",
                "No direct communication with buyers"
            ],
            "agent_rules": [
                "Represent clients professionally",
                "Communicate with other agents and clients",
                "Handle negotiations and transactions",
                "Provide market expertise and guidance"
            ]
        }
    }

@router.get("/agent-info")
async def get_agent_assignment_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get agent assignment information for the current user
    """
    agent_service = AgentAssignmentService(db)
    
    info = {
        "user_role": current_user.user_role.value if hasattr(current_user.user_role, 'value') else current_user.user_role,
        "user_id": current_user.id,
        "assigned_buyer_agent_id": current_user.assigned_buyer_agent_id,
        "assigned_seller_agent_id": current_user.assigned_seller_agent_id,
    }
    
    # Get assigned agent details
    if current_user.user_role == UserRole.BUYER and current_user.assigned_buyer_agent_id:
        assigned_agent = db.query(User).filter(User.id == current_user.assigned_buyer_agent_id).first()
        if assigned_agent:
            info["assigned_buyer_agent"] = {
                "id": assigned_agent.id,
                "name": f"{assigned_agent.first_name} {assigned_agent.last_name}" if assigned_agent.first_name else assigned_agent.username,
                "company_name": assigned_agent.company_name,
                "phone": assigned_agent.phone,
                "email": assigned_agent.email
            }
    
    if current_user.user_role == UserRole.SELLER and current_user.assigned_seller_agent_id:
        assigned_agent = db.query(User).filter(User.id == current_user.assigned_seller_agent_id).first()
        if assigned_agent:
            info["assigned_seller_agent"] = {
                "id": assigned_agent.id,
                "name": f"{assigned_agent.first_name} {assigned_agent.last_name}" if assigned_agent.first_name else assigned_agent.username,
                "company_name": assigned_agent.company_name,
                "phone": assigned_agent.phone,
                "email": assigned_agent.email
            }
    
    # Get client list for agents
    if current_user.user_role in [UserRole.BUYER_AGENT, UserRole.SELLER_AGENT]:
        clients = agent_service.get_client_list(current_user.id)
        info["clients"] = [
            {
                "id": client.id,
                "name": f"{client.first_name} {client.last_name}" if client.first_name else client.username,
                "role": client.user_role.value if hasattr(client.user_role, 'value') else client.user_role,
                "email": client.email,
                "phone": client.phone
            }
            for client in clients
        ]
    
    return info

@router.post("/route-message")
async def get_message_routing(
    recipient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the proper routing for a message to ensure it goes through the correct agents
    """
    agent_service = AgentAssignmentService(db)
    
    # Check if direct communication is allowed
    can_communicate_directly = agent_service.can_communicate(current_user.id, recipient_id)
    
    # Get communication path
    communication_path = agent_service.get_communication_path(current_user.id, recipient_id)
    
    # Get recipient info
    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )
    
    # Build routing information
    routing_info = {
        "can_communicate_directly": can_communicate_directly,
        "communication_path": communication_path,
        "recipient": {
            "id": recipient.id,
            "name": f"{recipient.first_name} {recipient.last_name}" if recipient.first_name else recipient.username,
            "role": recipient.user_role.value if hasattr(recipient.user_role, 'value') else recipient.user_role
        }
    }
    
    if not can_communicate_directly and len(communication_path) > 2:
        # Need to route through agent(s)
        next_recipient_id = communication_path[1]
        next_recipient = db.query(User).filter(User.id == next_recipient_id).first()
        
        if next_recipient:
            routing_info["suggested_action"] = {
                "message": "Please send your message through your assigned agent",
                "next_recipient": {
                    "id": next_recipient.id,
                    "name": f"{next_recipient.first_name} {next_recipient.last_name}" if next_recipient.first_name else next_recipient.username,
                    "role": next_recipient.user_role.value if hasattr(next_recipient.user_role, 'value') else next_recipient.user_role,
                    "is_agent": next_recipient.user_role in [UserRole.BUYER_AGENT, UserRole.SELLER_AGENT]
                }
            }
    
    return routing_info

# AI Helper Functions

async def generate_ai_analysis_response(
    message_id: int,
    property_listing: PropertyListing,
    sender: User,
    recipient: User,
    analysis_preferences: Dict[str, Any]
):
    """
    Background task to generate AI analysis and send follow-up message
    """
    try:
        # Simulate AI analysis generation
        await asyncio.sleep(2)  # Simulate processing time
        
        analysis_data = await _generate_mock_land_analysis(
            property_listing.location.address if property_listing.location else "Unknown Location",
            analysis_preferences.get('analysis_type', 'comprehensive')
        )
        
        # Create follow-up message with analysis
        ai_response = f"""AI Analysis Complete for {property_listing.title}:
        
📊 Overall Score: {analysis_data['overall_score']}/100
🎯 Recommendation: {analysis_data['recommendation'].upper()}
🔍 Confidence: {analysis_data['confidence_level']:.1%}

Key Highlights:
• Safety Score: {analysis_data.get('safety_score', 85)}/100
• Market Potential: {analysis_data.get('market_potential_score', 78)}/100
• Accessibility: {analysis_data.get('accessibility_score', 82)}/100

Predicted Value Growth:
📈 1 Year: +{analysis_data.get('predicted_value_change_1y', 5.2):.1f}%
📈 3 Years: +{analysis_data.get('predicted_value_change_3y', 16.8):.1f}%
📈 5 Years: +{analysis_data.get('predicted_value_change_5y', 28.5):.1f}%

This analysis was generated using NVIDIA AI technology for comprehensive real estate insights."""
        
        # Store AI response message
        # Note: In a real implementation, you'd use the database session here
        print(f"AI Analysis generated for message {message_id}: {ai_response[:100]}...")
        
    except Exception as e:
        print(f"Error generating AI analysis: {e}")

def _generate_role_based_suggestions(user_role: UserRole, message_content: str, property_id: Optional[int]) -> List[str]:
    """
    Generate suggested responses based on user role and message context
    """
    base_suggestions = [
        "Would you like me to provide a detailed market analysis for this area?",
        "I can share recent comparable sales data if that would be helpful.",
        "Let me know if you'd like to schedule a property viewing.",
        "I can provide more information about the neighborhood amenities."
    ]
    
    role_specific = {
        UserRole.BUYER: [
            "I'm interested in learning more about the investment potential.",
            "Can you provide information about the local schools and safety ratings?",
            "What's the current market trend for this type of property?"
        ],
        UserRole.SELLER: [
            "I'd like to understand the competitive landscape for my property.",
            "Can you provide a comprehensive market analysis for pricing?",
            "What marketing strategies would work best for this property?"
        ],
        UserRole.BUYER_AGENT: [
            "I can prepare a comprehensive CMA for your client.",
            "Would you like me to run financing scenarios?",
            "I can provide investment analysis and market projections."
        ],
        UserRole.SELLER_AGENT: [
            "I can provide a detailed property valuation report.",
            "Let me share the latest market trends for optimal pricing.",
            "I can analyze the competition and suggest positioning strategies."
        ]
    }
    
    suggestions = base_suggestions.copy()
    if user_role in role_specific:
        suggestions.extend(role_specific[user_role])
    
    return suggestions

async def _generate_property_insights(property_listing: PropertyListing, db: Session) -> Dict[str, Any]:
    """
    Generate AI insights for a specific property
    """
    insights = {
        "property_analysis": {
            "price_per_sqft": property_listing.price / property_listing.sqft if property_listing.sqft else 0,
            "market_position": "competitive",  # This would be calculated based on comparables
            "investment_grade": "A-",  # This would be AI-generated
        },
        "market_context": {
            "appreciation_trend": "+8.2% YoY",
            "inventory_level": "Low",
            "demand_indicator": "High"
        },
        "ai_recommendations": [
            "Strong buy signal based on current market conditions",
            "Property is priced competitively for the area",
            "Expected appreciation above market average"
        ]
    }
    
    return insights

def _calculate_enhancement_confidence(enhancement: MessageEnhancementResponse) -> float:
    """
    Calculate confidence score for message enhancement
    """
    confidence = 0.5  # Base confidence
    
    if enhancement.has_land_analysis:
        confidence += 0.2
    if enhancement.has_price_analysis:
        confidence += 0.2
    if enhancement.has_market_trends:
        confidence += 0.1
    
    return min(confidence, 1.0)

async def _generate_mock_land_analysis(location: str, analysis_type: str) -> Dict[str, Any]:
    """
    Generate mock land analysis data (replace with actual NVIDIA API calls)
    """
    import random
    
    # Simulate processing time
    await asyncio.sleep(1)
    
    base_score = random.randint(60, 95)
    
    return {
        "analysis_id": f"analysis_{int(datetime.utcnow().timestamp())}",
        "location": location,
        "overall_score": base_score,
        "recommendation": "buy" if base_score >= 80 else "hold" if base_score >= 65 else "avoid",
        "confidence_level": random.uniform(0.75, 0.95),
        "facility_score": random.randint(70, 95),
        "safety_score": random.randint(75, 95),
        "disaster_risk_score": random.randint(60, 90),
        "market_potential_score": random.randint(65, 90),
        "accessibility_score": random.randint(70, 90),
        "analysis_details": {
            "methodology": "NVIDIA AI-powered comprehensive analysis",
            "data_sources": ["Crime statistics", "School ratings", "Market trends", "Demographics"],
            "last_updated": datetime.utcnow().isoformat()
        },
        "risk_factors": [
            "Property taxes may increase due to rising assessed values",
            "Traffic congestion during peak hours",
            "Limited parking in downtown areas"
        ],
        "opportunities": [
            "Upcoming transit expansion will improve connectivity",
            "New shopping center development planned",
            "Strong job growth in tech sector"
        ],
        "predicted_value_change_1y": random.uniform(3.0, 8.0),
        "predicted_value_change_3y": random.uniform(12.0, 25.0),
        "predicted_value_change_5y": random.uniform(20.0, 40.0),
        "comparable_properties": [
            {
                "address": f"{random.randint(1000, 9999)} Example St",
                "price": random.randint(300000, 600000),
                "score": random.randint(75, 95),
                "distance": random.uniform(0.1, 2.0)
            }
            for _ in range(4)
        ]
    }
