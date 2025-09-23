from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from app.database import get_db
from app.models import User, PropertyListing, UserRole, SubscriptionPlan
from app.routers.auth import get_current_user, require_agent
from app.services.analytics_service import AnalyticsService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/property/{property_id}")
async def get_property_analytics(
    property_id: int,
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed analytics for a specific property"""
    
    try:
        analytics_service = AnalyticsService(db)
        analytics = analytics_service.get_property_analytics(property_id, current_user, days)
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=analytics["error"]
            )
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting property analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving property analytics"
        )

@router.get("/agent/dashboard")
async def get_agent_analytics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent)
):
    """Get analytics dashboard for agents"""
    
    try:
        analytics_service = AnalyticsService(db)
        analytics = analytics_service.get_agent_analytics(current_user, days)
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=analytics["error"]
            )
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving agent analytics"
        )

@router.get("/market")
async def get_market_analytics(
    location: str = Query(..., description="Location to analyze (city, neighborhood, etc.)"),
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get market analytics for a specific location"""
    
    try:
        analytics_service = AnalyticsService(db)
        analytics = analytics_service.get_market_analytics(location, days)
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=analytics["error"]
            )
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving market analytics"
        )

@router.get("/subscription/usage")
async def get_analytics_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent)
):
    """Get analytics usage statistics for current subscription"""
    
    try:
        # Check subscription status
        if current_user.subscription_plan not in [SubscriptionPlan.PRO, SubscriptionPlan.PREMIUM]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Analytics features require Pro or Premium subscription"
            )
        
        if current_user.subscription_status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active subscription required for analytics"
            )
        
        # Get subscription limits
        subscription_limits = {
            SubscriptionPlan.PRO: {
                "analytics_views": 1000,
                "detailed_reports": 10,
                "market_analysis": 5
            },
            SubscriptionPlan.PREMIUM: {
                "analytics_views": None,  # Unlimited
                "detailed_reports": None,  # Unlimited
                "market_analysis": None   # Unlimited
            }
        }
        
        limits = subscription_limits.get(current_user.subscription_plan, {})
        
        # In a real implementation, you would track actual usage
        # For now, return mock usage data
        current_usage = {
            "analytics_views": 750,
            "detailed_reports": 7,
            "market_analysis": 3
        }
        
        usage_report = {
            "subscription_plan": current_user.subscription_plan.value,
            "limits": limits,
            "current_usage": current_usage,
            "usage_percentage": {}
        }
        
        # Calculate usage percentages
        for metric, limit in limits.items():
            if limit is None:  # Unlimited
                usage_report["usage_percentage"][metric] = 0
            else:
                current = current_usage.get(metric, 0)
                usage_report["usage_percentage"][metric] = (current / limit * 100) if limit > 0 else 0
        
        return usage_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving analytics usage"
        )

@router.get("/features")
async def get_analytics_features():
    """Get list of available analytics features by subscription tier"""
    
    features = {
        "basic": {
            "name": "Basic Plan",
            "analytics_features": [],
            "description": "No analytics features included"
        },
        "pro": {
            "name": "Pro Plan",
            "analytics_features": [
                "Property view statistics",
                "Inquiry tracking",
                "Basic performance metrics",
                "30-day historical data",
                "Lead conversion tracking (buyer agents)",
                "Listing performance (seller agents)"
            ],
            "limits": {
                "analytics_views": 1000,
                "detailed_reports": 10,
                "market_analysis": 5
            },
            "description": "Advanced analytics for property and agent performance"
        },
        "premium": {
            "name": "Premium Plan",
            "analytics_features": [
                "All Pro features",
                "Unlimited analytics views",
                "Advanced market analysis",
                "Competitive analysis",
                "Custom reporting",
                "1-year historical data",
                "Predictive insights",
                "Export capabilities",
                "Priority data refresh"
            ],
            "limits": {
                "analytics_views": "unlimited",
                "detailed_reports": "unlimited",
                "market_analysis": "unlimited"
            },
            "description": "Comprehensive analytics suite with unlimited access"
        }
    }
    
    return {
        "analytics_features": features,
        "upgrade_benefits": {
            "pro_to_premium": [
                "Unlimited analytics views",
                "Advanced market analysis",
                "Custom reporting",
                "1-year historical data",
                "Predictive insights"
            ]
        }
    }

@router.post("/track-view")
async def track_property_view(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track a property view for analytics"""
    
    try:
        # Check if property exists
        property_listing = db.query(PropertyListing).filter(
            PropertyListing.id == property_id
        ).first()
        
        if not property_listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        # Create property view record
        from app.models import PropertyView
        from datetime import datetime
        
        property_view = PropertyView(
            property_id=property_id,
            user_id=current_user.id,
            viewed_at=datetime.utcnow()
        )
        
        db.add(property_view)
        db.commit()
        
        return {
            "message": "Property view tracked successfully",
            "property_id": property_id,
            "viewed_at": property_view.viewed_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking property view: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error tracking property view"
        )

@router.get("/insights/market-trends")
async def get_market_trends(
    location: Optional[str] = Query(None, description="Location filter"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent)
):
    """Get market trends and insights"""
    
    try:
        # Check subscription access
        if current_user.subscription_plan not in [SubscriptionPlan.PRO, SubscriptionPlan.PREMIUM]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Market trends require Pro or Premium subscription"
            )
        
        # Build query
        query = db.query(PropertyListing)
        
        if location:
            query = query.filter(
                PropertyListing.city.ilike(f"%{location}%")
            )
        
        if property_type:
            query = query.filter(
                PropertyListing.property_type == property_type
            )
        
        properties = query.all()
        
        if not properties:
            return {
                "message": "No properties found for the specified criteria",
                "trends": {}
            }
        
        # Calculate trends
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        last_month = now - timedelta(days=30)
        last_quarter = now - timedelta(days=90)
        
        recent_properties = [p for p in properties if p.created_at >= last_month]
        quarterly_properties = [p for p in properties if p.created_at >= last_quarter]
        
        trends = {
            "total_properties": len(properties),
            "recent_listings": len(recent_properties),
            "quarterly_listings": len(quarterly_properties),
            "average_price": sum(p.price for p in properties if p.price) / len(properties) if properties else 0,
            "price_ranges": {
                "under_300k": len([p for p in properties if p.price and p.price < 300000]),
                "300k_500k": len([p for p in properties if p.price and 300000 <= p.price < 500000]),
                "500k_plus": len([p for p in properties if p.price and p.price >= 500000])
            },
            "property_types": {}
        }
        
        # Property type distribution
        for prop in properties:
            prop_type = prop.property_type or "unknown"
            trends["property_types"][prop_type] = trends["property_types"].get(prop_type, 0) + 1
        
        return {
            "location": location or "All locations",
            "property_type": property_type or "All types",
            "trends": trends,
            "insights": [
                f"Average price: ${trends['average_price']:,.2f}",
                f"{len(recent_properties)} new listings in the last 30 days",
                f"Most common type: {max(trends['property_types'], key=trends['property_types'].get) if trends['property_types'] else 'N/A'}"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving market trends"
        )
