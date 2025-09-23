"""
AI Automation API endpoints using CrewAI and NVAPI
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import User, PropertyListing, Message
from app.routers.auth import get_current_user, require_agent
from app.services.crewai_service import crewai_service

router = APIRouter(prefix="/api/v1/ai", tags=["AI Automation"])

# Pydantic models for requests/responses
class PropertyAnalysisRequest(BaseModel):
    address: str
    sqft: int
    bedrooms: int
    bathrooms: float
    year_built: int
    lot_size: Optional[float] = None
    property_type: str = "single_family"

class PropertyAnalysisResponse(BaseModel):
    estimated_value: int
    confidence: float
    value_range: Dict[str, int]
    factors: Dict[str, float]
    comparables: List[Dict[str, Any]]
    market_trends: Dict[str, Any]

class MarketAnalysisRequest(BaseModel):
    location: str
    property_type: Optional[str] = "single_family"
    timeframe: Optional[str] = "30d"

class MarketAnalysisResponse(BaseModel):
    location: str
    average_price: int
    price_trend: float
    market_velocity: int
    inventory_level: int
    buyer_demand: str
    seller_market: bool
    insights: List[str]
    predictions: List[Dict[str, Any]]

class LeadScoringRequest(BaseModel):
    leads: List[Dict[str, Any]]

class LeadScoringResponse(BaseModel):
    scored_leads: List[Dict[str, Any]]
    summary: Dict[str, Any]

class CommunicationRequest(BaseModel):
    lead_data: Dict[str, Any]
    message_type: str
    interaction_history: Optional[List[Dict[str, Any]]] = []

class CommunicationResponse(BaseModel):
    subject: str
    message: str
    recommended_timing: str
    follow_up_actions: List[str]

@router.post("/analyze-property", response_model=Dict[str, Any])
async def analyze_property(
    request: PropertyAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze property value using AI
    Available to all authenticated users
    """
    try:
        property_data = {
            "address": request.address,
            "sqft": request.sqft,
            "bedrooms": request.bedrooms,
            "bathrooms": request.bathrooms,
            "year_built": request.year_built,
            "lot_size": request.lot_size,
            "property_type": request.property_type
        }
        
        result = await crewai_service.analyze_property(property_data)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "analysis": result["result"],
            "agent": result["agent"],
            "timestamp": result["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Property analysis failed: {str(e)}")

@router.post("/analyze-market", response_model=Dict[str, Any])
async def analyze_market(
    request: MarketAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze market trends for a location using AI
    Available to all authenticated users
    """
    try:
        result = await crewai_service.analyze_market(request.location)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Generate additional insights using AI
        insights_task = {
            "type": "generate_market_insights",
            "location": request.location,
            "timeframe": request.timeframe
        }
        
        insights_result = await crewai_service.property_analyst.execute_task(insights_task)
        
        return {
            "success": True,
            "market_analysis": result["result"],
            "insights": insights_result["result"] if insights_result["success"] else {},
            "agent": result["agent"],
            "timestamp": result["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market analysis failed: {str(e)}")

@router.post("/score-leads", response_model=Dict[str, Any])
async def score_leads(
    request: LeadScoringRequest,
    current_user: User = Depends(require_agent),  # Only agents can score leads
    db: Session = Depends(get_db)
):
    """
    Score and prioritize leads using AI
    Available to agents only
    """
    try:
        result = await crewai_service.score_leads(request.leads)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        scored_leads = result["result"]
        
        # Generate summary statistics
        total_leads = len(scored_leads)
        high_priority = len([lead for lead in scored_leads if lead.get("priority") == "high"])
        medium_priority = len([lead for lead in scored_leads if lead.get("priority") == "medium"])
        low_priority = len([lead for lead in scored_leads if lead.get("priority") == "low"])
        
        avg_score = sum(lead.get("ai_score", 0) for lead in scored_leads) / total_leads if total_leads > 0 else 0
        
        summary = {
            "total_leads": total_leads,
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "average_score": round(avg_score, 1),
            "conversion_potential": "high" if avg_score > 60 else "medium" if avg_score > 40 else "low"
        }
        
        return {
            "success": True,
            "scored_leads": scored_leads,
            "summary": summary,
            "agent": result["agent"],
            "timestamp": result["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead scoring failed: {str(e)}")

@router.post("/generate-communication", response_model=Dict[str, Any])
async def generate_communication(
    request: CommunicationRequest,
    current_user: User = Depends(require_agent),  # Only agents can generate communications
    db: Session = Depends(get_db)
):
    """
    Generate personalized communication using AI
    Available to agents only
    """
    try:
        context = {
            "lead_data": request.lead_data,
            "message_type": request.message_type,
            "interaction_history": request.interaction_history
        }
        
        result = await crewai_service.generate_followup(context)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "communication": result["result"],
            "agent": result["agent"],
            "timestamp": result["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Communication generation failed: {str(e)}")

@router.get("/market-insights/{location}")
async def get_market_insights(
    location: str,
    timeframe: str = "30d",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive market insights for a location
    Available to all authenticated users
    """
    try:
        # Get market analysis
        market_result = await crewai_service.analyze_market(location)
        
        if not market_result["success"]:
            raise HTTPException(status_code=500, detail=market_result["error"])
        
        # Generate additional insights
        insights_task = {
            "type": "generate_market_insights",
            "location": location,
            "timeframe": timeframe
        }
        
        insights_result = await crewai_service.property_analyst.execute_task(insights_task)
        
        return {
            "success": True,
            "location": location,
            "timeframe": timeframe,
            "market_data": market_result["result"],
            "ai_insights": insights_result["result"] if insights_result["success"] else {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market insights failed: {str(e)}")

@router.get("/lead-recommendations/{lead_id}")
async def get_lead_recommendations(
    lead_id: str,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered recommendations for a specific lead
    Available to agents only
    """
    try:
        # In a real implementation, you would fetch lead data from database
        # For now, we'll use mock data
        lead_data = {
            "id": lead_id,
            "name": "Sample Lead",
            "budget": 400000,
            "preferred_location": "Chicago, IL",
            "preferences": {
                "bedrooms": 3,
                "bathrooms": 2,
                "property_type": "single_family"
            },
            "stage": "actively_searching",
            "communication_preferences": {
                "method": "email",
                "frequency": "weekly",
                "best_time": "morning"
            }
        }
        
        recommendations_task = {
            "type": "generate_recommendations",
            "lead_data": lead_data
        }
        
        result = await crewai_service.lead_manager.execute_task(recommendations_task)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "lead_id": lead_id,
            "recommendations": result["result"],
            "agent": result["agent"],
            "timestamp": result["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead recommendations failed: {str(e)}")

@router.post("/run-automation")
async def run_automation(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """
    Trigger AI automation tasks
    Available to agents only
    """
    try:
        # Run automation in background
        background_tasks.add_task(run_daily_automation_task)
        
        return {
            "success": True,
            "message": "AI automation tasks started in background",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automation trigger failed: {str(e)}")

async def run_daily_automation_task():
    """Background task for daily automation"""
    try:
        result = await crewai_service.run_daily_automation()
        print(f"Daily automation completed: {result}")
    except Exception as e:
        print(f"Daily automation failed: {str(e)}")

@router.get("/automation-status")
async def get_automation_status(
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """
    Get status of AI automation systems
    Available to agents only
    """
    return {
        "success": True,
        "status": "active",
        "agents": {
            "property_analyst": {
                "name": crewai_service.property_analyst.name,
                "role": crewai_service.property_analyst.role,
                "status": "active"
            },
            "lead_manager": {
                "name": crewai_service.lead_manager.name,
                "role": crewai_service.lead_manager.role,
                "status": "active"
            },
            "communication_agent": {
                "name": crewai_service.communication_agent.name,
                "role": crewai_service.communication_agent.role,
                "status": "active"
            }
        },
        "last_run": datetime.utcnow().isoformat(),
        "next_scheduled": datetime.utcnow().isoformat()
    }
