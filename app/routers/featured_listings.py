from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.models import User, PropertyListing, UserRole
from app.schemas import PropertyListingResponse
from app.routers.auth import get_current_user, require_seller_or_agent
from app.services.featured_listings_service import FeaturedListingsService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/make-featured/{property_id}")
async def make_listing_featured(
    property_id: int,
    duration_days: Optional[int] = Query(None, description="Custom duration in days (Premium feature)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller_or_agent)
):
    """Make a property listing featured"""
    
    try:
        featured_service = FeaturedListingsService(db)
        result = featured_service.make_listing_featured(property_id, current_user, duration_days)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making listing featured: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error making listing featured"
        )

@router.delete("/remove-featured/{property_id}")
async def remove_featured_status(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller_or_agent)
):
    """Remove featured status from a property listing"""
    
    try:
        featured_service = FeaturedListingsService(db)
        result = featured_service.remove_featured_status(property_id, current_user)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing featured status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error removing featured status"
        )

@router.get("/", response_model=List[PropertyListingResponse])
async def get_featured_listings(
    limit: int = Query(20, description="Maximum number of listings to return", ge=1, le=100),
    location: Optional[str] = Query(None, description="Filter by location"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    db: Session = Depends(get_db)
):
    """Get current featured listings with optional filters"""
    
    try:
        featured_service = FeaturedListingsService(db)
        featured_listings = featured_service.get_featured_listings(
            limit=limit,
            location=location,
            property_type=property_type,
            min_price=min_price,
            max_price=max_price
        )
        
        return featured_listings
        
    except Exception as e:
        logger.error(f"Error getting featured listings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving featured listings"
        )

@router.get("/my-featured", response_model=List[PropertyListingResponse])
async def get_my_featured_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller_or_agent)
):
    """Get current user's featured listings"""
    
    try:
        featured_service = FeaturedListingsService(db)
        featured_listings = featured_service.get_user_featured_listings(current_user)
        
        return featured_listings
        
    except Exception as e:
        logger.error(f"Error getting user's featured listings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving your featured listings"
        )

@router.get("/stats")
async def get_featured_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller_or_agent)
):
    """Get featured listings statistics for current user"""
    
    try:
        featured_service = FeaturedListingsService(db)
        stats = featured_service.get_featured_stats(current_user)
        
        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=stats["error"]
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting featured stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving featured statistics"
        )

@router.post("/extend-duration/{property_id}")
async def extend_featured_duration(
    property_id: int,
    additional_days: int = Query(..., description="Number of additional days", ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller_or_agent)
):
    """Extend the featured duration of a listing (Premium feature)"""
    
    try:
        featured_service = FeaturedListingsService(db)
        result = featured_service.extend_featured_duration(property_id, current_user, additional_days)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extending featured duration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error extending featured duration"
        )

@router.get("/pricing")
async def get_featured_pricing():
    """Get featured listings pricing and plan information"""
    
    pricing_info = {
        "plans": {
            "basic": {
                "name": "Basic Plan",
                "price": 49.00,
                "featured_listings": 0,
                "duration_days": 0,
                "description": "No featured listings included"
            },
            "pro": {
                "name": "Pro Plan", 
                "price": 99.00,
                "featured_listings": 5,
                "duration_days": 30,
                "description": "Up to 5 featured listings for 30 days each"
            },
            "premium": {
                "name": "Premium Plan",
                "price": 199.00,
                "featured_listings": 20,
                "duration_days": 60,
                "description": "Up to 20 featured listings for 60 days each",
                "premium_features": [
                    "Custom duration extension",
                    "Priority placement",
                    "Advanced analytics",
                    "Banner placement on homepage"
                ]
            }
        },
        "benefits": {
            "featured_listings": [
                "3x more visibility than regular listings",
                "Priority placement in search results",
                "Highlighted display with special badge",
                "Featured section on homepage",
                "Enhanced listing details",
                "Priority in email notifications to buyers"
            ]
        },
        "upgrade_cta": {
            "message": "Upgrade your subscription to feature your listings and get more visibility",
            "upgrade_url": "/subscriptions/upgrade"
        }
    }
    
    return pricing_info

@router.get("/performance")
async def get_featured_performance(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller_or_agent)
):
    """Get performance comparison between featured and regular listings"""
    
    try:
        # Get user's listings
        if current_user.user_role == UserRole.SELLER:
            user_listings = db.query(PropertyListing).filter(
                PropertyListing.owner_id == current_user.id
            ).all()
        else:  # SELLER_AGENT
            user_listings = db.query(PropertyListing).filter(
                PropertyListing.agent_id == current_user.id
            ).all()
        
        if not user_listings:
            return {
                "message": "No listings found",
                "performance": {}
            }
        
        # Separate featured and regular listings
        featured_listings = [l for l in user_listings if l.is_featured]
        regular_listings = [l for l in user_listings if not l.is_featured]
        
        # Calculate performance metrics
        def calculate_metrics(listings):
            if not listings:
                return {"count": 0, "avg_views": 0, "avg_favorites": 0, "total_inquiries": 0}
            
            total_views = sum(l.views_count for l in listings)
            total_favorites = sum(l.favorites_count for l in listings)
            
            # Count inquiries (messages about these properties)
            from app.models import Message
            listing_ids = [l.id for l in listings]
            total_inquiries = db.query(Message).filter(
                Message.property_listing_id.in_(listing_ids)
            ).count()
            
            return {
                "count": len(listings),
                "avg_views": total_views / len(listings),
                "avg_favorites": total_favorites / len(listings),
                "total_inquiries": total_inquiries,
                "avg_inquiries": total_inquiries / len(listings)
            }
        
        featured_metrics = calculate_metrics(featured_listings)
        regular_metrics = calculate_metrics(regular_listings)
        
        # Calculate performance improvement
        performance_improvement = {}
        if regular_metrics["avg_views"] > 0:
            performance_improvement["views_improvement"] = (
                (featured_metrics["avg_views"] - regular_metrics["avg_views"]) / 
                regular_metrics["avg_views"] * 100
            )
        
        if regular_metrics["avg_favorites"] > 0:
            performance_improvement["favorites_improvement"] = (
                (featured_metrics["avg_favorites"] - regular_metrics["avg_favorites"]) / 
                regular_metrics["avg_favorites"] * 100
            )
        
        if regular_metrics["avg_inquiries"] > 0:
            performance_improvement["inquiries_improvement"] = (
                (featured_metrics["avg_inquiries"] - regular_metrics["avg_inquiries"]) / 
                regular_metrics["avg_inquiries"] * 100
            )
        
        return {
            "period_days": days,
            "featured_listings": featured_metrics,
            "regular_listings": regular_metrics,
            "performance_improvement": performance_improvement,
            "insights": [
                f"You have {featured_metrics['count']} featured listings and {regular_metrics['count']} regular listings",
                f"Featured listings average {featured_metrics['avg_views']:.1f} views vs {regular_metrics['avg_views']:.1f} for regular listings",
                f"Featured listings get {featured_metrics['avg_inquiries']:.1f} inquiries on average vs {regular_metrics['avg_inquiries']:.1f} for regular listings"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting featured performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving performance data"
        )
