"""
Featured Listings Service

Manages premium featured listings functionality for paid subscribers.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models import (
    PropertyListing, User, Subscription, 
    UserRole, SubscriptionPlan
)

logger = logging.getLogger(__name__)

class FeaturedListingsService:
    """Service for managing featured listings"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Featured listing limits by subscription plan
        self.plan_limits = {
            SubscriptionPlan.BASIC: 0,      # No featured listings
            SubscriptionPlan.PRO: 5,        # Up to 5 featured listings
            SubscriptionPlan.PREMIUM: 20    # Up to 20 featured listings
        }
        
        # Featured listing duration by plan (in days)
        self.plan_durations = {
            SubscriptionPlan.PRO: 30,       # 30 days
            SubscriptionPlan.PREMIUM: 60    # 60 days
        }
    
    def make_listing_featured(
        self, 
        property_id: int, 
        user: User,
        duration_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make a property listing featured"""
        
        # Check if user has permission
        if user.user_role not in [UserRole.SELLER, UserRole.SELLER_AGENT]:
            return {"error": "Only sellers and seller agents can feature listings"}
        
        # Check subscription status
        if not self._has_featured_access(user):
            return {"error": "Featured listings require Pro or Premium subscription"}
        
        # Get the property listing
        property_listing = self.db.query(PropertyListing).filter(
            PropertyListing.id == property_id
        ).first()
        
        if not property_listing:
            return {"error": "Property listing not found"}
        
        # Check ownership/authorization
        if user.user_role == UserRole.SELLER and property_listing.owner_id != user.id:
            return {"error": "You can only feature your own listings"}
        elif user.user_role == UserRole.SELLER_AGENT and property_listing.agent_id != user.id:
            return {"error": "You can only feature listings you represent"}
        
        # Check if already featured
        if property_listing.is_featured and property_listing.featured_until > datetime.utcnow():
            return {"error": "Property is already featured"}
        
        # Check subscription limits
        current_featured_count = self._get_user_featured_count(user)
        plan_limit = self.plan_limits.get(user.subscription_plan, 0)
        
        if current_featured_count >= plan_limit:
            return {
                "error": f"Featured listing limit reached. Your {user.subscription_plan.value} plan allows {plan_limit} featured listings."
            }
        
        # Set duration based on plan or custom duration
        if duration_days is None:
            duration_days = self.plan_durations.get(user.subscription_plan, 30)
        
        # Update the listing
        property_listing.is_featured = True
        property_listing.featured_until = datetime.utcnow() + timedelta(days=duration_days)
        
        # Update subscription usage
        subscription = self.db.query(Subscription).filter(
            and_(
                Subscription.user_id == user.id,
                Subscription.status == "active"
            )
        ).first()
        
        if subscription:
            subscription.featured_listings_used += 1
        
        self.db.commit()
        
        return {
            "message": "Property listing featured successfully",
            "property_id": property_id,
            "featured_until": property_listing.featured_until,
            "duration_days": duration_days,
            "remaining_featured_slots": plan_limit - (current_featured_count + 1)
        }
    
    def remove_featured_status(
        self, 
        property_id: int, 
        user: User
    ) -> Dict[str, Any]:
        """Remove featured status from a property listing"""
        
        # Get the property listing
        property_listing = self.db.query(PropertyListing).filter(
            PropertyListing.id == property_id
        ).first()
        
        if not property_listing:
            return {"error": "Property listing not found"}
        
        # Check ownership/authorization
        if user.user_role == UserRole.SELLER and property_listing.owner_id != user.id:
            return {"error": "You can only modify your own listings"}
        elif user.user_role == UserRole.SELLER_AGENT and property_listing.agent_id != user.id:
            return {"error": "You can only modify listings you represent"}
        
        if not property_listing.is_featured:
            return {"error": "Property is not currently featured"}
        
        # Remove featured status
        property_listing.is_featured = False
        property_listing.featured_until = None
        
        # Update subscription usage
        subscription = self.db.query(Subscription).filter(
            and_(
                Subscription.user_id == user.id,
                Subscription.status == "active"
            )
        ).first()
        
        if subscription and subscription.featured_listings_used > 0:
            subscription.featured_listings_used -= 1
        
        self.db.commit()
        
        return {
            "message": "Featured status removed successfully",
            "property_id": property_id
        }
    
    def get_featured_listings(
        self, 
        limit: int = 20,
        location: Optional[str] = None,
        property_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[PropertyListing]:
        """Get current featured listings with optional filters"""
        
        query = self.db.query(PropertyListing).filter(
            and_(
                PropertyListing.is_featured == True,
                PropertyListing.featured_until > datetime.utcnow(),
                PropertyListing.status == "active"
            )
        )
        
        # Apply filters
        if location:
            query = query.filter(
                or_(
                    PropertyListing.city.ilike(f"%{location}%"),
                    PropertyListing.address.ilike(f"%{location}%")
                )
            )
        
        if property_type:
            query = query.filter(PropertyListing.property_type == property_type)
        
        if min_price:
            query = query.filter(PropertyListing.price >= min_price)
        
        if max_price:
            query = query.filter(PropertyListing.price <= max_price)
        
        # Order by featured date (most recent first) and then by price
        query = query.order_by(desc(PropertyListing.featured_until), PropertyListing.price)
        
        return query.limit(limit).all()
    
    def get_user_featured_listings(self, user: User) -> List[PropertyListing]:
        """Get user's current featured listings"""
        
        if user.user_role == UserRole.SELLER:
            query = self.db.query(PropertyListing).filter(
                and_(
                    PropertyListing.owner_id == user.id,
                    PropertyListing.is_featured == True,
                    PropertyListing.featured_until > datetime.utcnow()
                )
            )
        elif user.user_role == UserRole.SELLER_AGENT:
            query = self.db.query(PropertyListing).filter(
                and_(
                    PropertyListing.agent_id == user.id,
                    PropertyListing.is_featured == True,
                    PropertyListing.featured_until > datetime.utcnow()
                )
            )
        else:
            return []
        
        return query.order_by(desc(PropertyListing.featured_until)).all()
    
    def get_featured_stats(self, user: User) -> Dict[str, Any]:
        """Get featured listings statistics for a user"""
        
        if not self._has_featured_access(user):
            return {"error": "Featured listings require Pro or Premium subscription"}
        
        current_featured = self._get_user_featured_count(user)
        plan_limit = self.plan_limits.get(user.subscription_plan, 0)
        
        # Get expiring soon (within 7 days)
        expiring_soon = self.db.query(PropertyListing).filter(
            and_(
                PropertyListing.is_featured == True,
                PropertyListing.featured_until > datetime.utcnow(),
                PropertyListing.featured_until <= datetime.utcnow() + timedelta(days=7),
                PropertyListing.owner_id == user.id if user.user_role == UserRole.SELLER else PropertyListing.agent_id == user.id
            )
        ).count()
        
        # Get total views for featured listings
        featured_listings = self.get_user_featured_listings(user)
        total_featured_views = sum(listing.views_count for listing in featured_listings)
        
        return {
            "current_featured": current_featured,
            "plan_limit": plan_limit,
            "remaining_slots": plan_limit - current_featured,
            "expiring_soon": expiring_soon,
            "total_featured_views": total_featured_views,
            "plan_duration_days": self.plan_durations.get(user.subscription_plan, 30),
            "featured_listings": [
                {
                    "id": listing.id,
                    "title": listing.title,
                    "price": listing.price,
                    "featured_until": listing.featured_until,
                    "views_count": listing.views_count,
                    "days_remaining": (listing.featured_until - datetime.utcnow()).days
                }
                for listing in featured_listings
            ]
        }
    
    def extend_featured_duration(
        self, 
        property_id: int, 
        user: User,
        additional_days: int
    ) -> Dict[str, Any]:
        """Extend the featured duration of a listing (Premium feature)"""
        
        if user.subscription_plan != SubscriptionPlan.PREMIUM:
            return {"error": "Duration extension is a Premium feature"}
        
        property_listing = self.db.query(PropertyListing).filter(
            PropertyListing.id == property_id
        ).first()
        
        if not property_listing:
            return {"error": "Property listing not found"}
        
        # Check ownership/authorization
        if user.user_role == UserRole.SELLER and property_listing.owner_id != user.id:
            return {"error": "You can only modify your own listings"}
        elif user.user_role == UserRole.SELLER_AGENT and property_listing.agent_id != user.id:
            return {"error": "You can only modify listings you represent"}
        
        if not property_listing.is_featured:
            return {"error": "Property is not currently featured"}
        
        # Extend the duration
        property_listing.featured_until += timedelta(days=additional_days)
        self.db.commit()
        
        return {
            "message": f"Featured duration extended by {additional_days} days",
            "property_id": property_id,
            "new_featured_until": property_listing.featured_until
        }
    
    def _has_featured_access(self, user: User) -> bool:
        """Check if user has access to featured listings"""
        return (
            user.subscription_plan in [SubscriptionPlan.PRO, SubscriptionPlan.PREMIUM] and
            user.subscription_status == "active"
        )
    
    def _get_user_featured_count(self, user: User) -> int:
        """Get current count of user's featured listings"""
        
        if user.user_role == UserRole.SELLER:
            return self.db.query(PropertyListing).filter(
                and_(
                    PropertyListing.owner_id == user.id,
                    PropertyListing.is_featured == True,
                    PropertyListing.featured_until > datetime.utcnow()
                )
            ).count()
        elif user.user_role == UserRole.SELLER_AGENT:
            return self.db.query(PropertyListing).filter(
                and_(
                    PropertyListing.agent_id == user.id,
                    PropertyListing.is_featured == True,
                    PropertyListing.featured_until > datetime.utcnow()
                )
            ).count()
        
        return 0
    
    def cleanup_expired_featured(self):
        """Clean up expired featured listings (run as scheduled task)"""
        
        expired_listings = self.db.query(PropertyListing).filter(
            and_(
                PropertyListing.is_featured == True,
                PropertyListing.featured_until <= datetime.utcnow()
            )
        ).all()
        
        for listing in expired_listings:
            listing.is_featured = False
            listing.featured_until = None
        
        self.db.commit()
        
        logger.info(f"Cleaned up {len(expired_listings)} expired featured listings")
        
        return len(expired_listings)
