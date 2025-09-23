"""
Analytics Service for Illinois Real Estate Platform

Provides advanced analytics for property listings, user behavior,
and market insights for premium subscribers.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models import (
    PropertyListing, User, Message, Subscription, 
    PropertyView, PropertyFavorite, UserRole, SubscriptionPlan
)

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for generating analytics and insights"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_property_analytics(
        self, 
        property_id: int, 
        user: User,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get detailed analytics for a specific property"""
        
        # Check if user has access to analytics
        if not self._has_analytics_access(user):
            return {"error": "Analytics access requires Pro or Premium subscription"}
        
        property_listing = self.db.query(PropertyListing).filter(
            PropertyListing.id == property_id
        ).first()
        
        if not property_listing:
            return {"error": "Property not found"}
        
        # Check if user owns this property or is authorized
        if property_listing.seller_id != user.id and user.user_role not in [UserRole.BUYER_AGENT, UserRole.SELLER_AGENT]:
            return {"error": "Unauthorized access to property analytics"}
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get view analytics
        views_query = self.db.query(PropertyView).filter(
            and_(
                PropertyView.property_id == property_id,
                PropertyView.viewed_at >= start_date,
                PropertyView.viewed_at <= end_date
            )
        )
        
        total_views = views_query.count()
        unique_viewers = views_query.distinct(PropertyView.user_id).count()
        
        # Daily views breakdown
        daily_views = self.db.query(
            func.date(PropertyView.viewed_at).label('date'),
            func.count(PropertyView.id).label('views')
        ).filter(
            and_(
                PropertyView.property_id == property_id,
                PropertyView.viewed_at >= start_date
            )
        ).group_by(func.date(PropertyView.viewed_at)).all()
        
        # Get favorites count
        favorites_count = self.db.query(PropertyFavorite).filter(
            PropertyFavorite.property_id == property_id
        ).count()
        
        # Get inquiries (messages about this property)
        inquiries_count = self.db.query(Message).filter(
            and_(
                Message.property_id == property_id,
                Message.created_at >= start_date
            )
        ).count()
        
        # Calculate engagement metrics
        engagement_rate = (favorites_count + inquiries_count) / max(total_views, 1) * 100
        
        # Get viewer demographics (if available)
        viewer_roles = self.db.query(
            User.user_role,
            func.count(PropertyView.id).label('count')
        ).join(PropertyView, User.id == PropertyView.user_id).filter(
            and_(
                PropertyView.property_id == property_id,
                PropertyView.viewed_at >= start_date
            )
        ).group_by(User.user_role).all()
        
        return {
            "property_id": property_id,
            "property_title": property_listing.title,
            "period": f"{days} days",
            "overview": {
                "total_views": total_views,
                "unique_viewers": unique_viewers,
                "favorites": favorites_count,
                "inquiries": inquiries_count,
                "engagement_rate": round(engagement_rate, 2)
            },
            "daily_views": [
                {"date": str(day.date), "views": day.views}
                for day in daily_views
            ],
            "viewer_demographics": [
                {"role": role.value, "count": count}
                for role, count in viewer_roles
            ],
            "performance_insights": self._generate_performance_insights(
                total_views, unique_viewers, favorites_count, inquiries_count, days
            )
        }
    
    def get_agent_analytics(
        self, 
        user: User,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics dashboard for agents"""
        
        if user.user_role not in [UserRole.BUYER_AGENT, UserRole.SELLER_AGENT]:
            return {"error": "Agent analytics only available for agents"}
        
        if not self._has_analytics_access(user):
            return {"error": "Analytics access requires Pro or Premium subscription"}
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if user.user_role == UserRole.SELLER_AGENT:
            return self._get_seller_agent_analytics(user, start_date, end_date, days)
        else:
            return self._get_buyer_agent_analytics(user, start_date, end_date, days)
    
    def _get_seller_agent_analytics(
        self, 
        user: User, 
        start_date: datetime, 
        end_date: datetime,
        days: int
    ) -> Dict[str, Any]:
        """Analytics for seller agents"""
        
        # Get agent's client listings
        client_listings = self.db.query(PropertyListing).filter(
            PropertyListing.seller_agent_id == user.id
        ).all()
        
        listing_ids = [listing.id for listing in client_listings]
        
        if not listing_ids:
            return {
                "agent_type": "seller_agent",
                "period": f"{days} days",
                "overview": {
                    "total_listings": 0,
                    "total_views": 0,
                    "total_inquiries": 0,
                    "avg_days_on_market": 0
                },
                "listings_performance": [],
                "insights": ["No active listings found"]
            }
        
        # Total views across all listings
        total_views = self.db.query(PropertyView).filter(
            and_(
                PropertyView.property_id.in_(listing_ids),
                PropertyView.viewed_at >= start_date
            )
        ).count()
        
        # Total inquiries
        total_inquiries = self.db.query(Message).filter(
            and_(
                Message.property_id.in_(listing_ids),
                Message.created_at >= start_date
            )
        ).count()
        
        # Average days on market
        avg_days_on_market = self.db.query(
            func.avg(func.julianday('now') - func.julianday(PropertyListing.created_at))
        ).filter(
            PropertyListing.id.in_(listing_ids)
        ).scalar() or 0
        
        # Individual listing performance
        listings_performance = []
        for listing in client_listings:
            listing_views = self.db.query(PropertyView).filter(
                and_(
                    PropertyView.property_id == listing.id,
                    PropertyView.viewed_at >= start_date
                )
            ).count()
            
            listing_inquiries = self.db.query(Message).filter(
                and_(
                    Message.property_id == listing.id,
                    Message.created_at >= start_date
                )
            ).count()
            
            listings_performance.append({
                "listing_id": listing.id,
                "title": listing.title,
                "price": listing.price,
                "views": listing_views,
                "inquiries": listing_inquiries,
                "days_on_market": (datetime.utcnow() - listing.created_at).days
            })
        
        return {
            "agent_type": "seller_agent",
            "period": f"{days} days",
            "overview": {
                "total_listings": len(client_listings),
                "total_views": total_views,
                "total_inquiries": total_inquiries,
                "avg_days_on_market": round(avg_days_on_market, 1)
            },
            "listings_performance": listings_performance,
            "insights": self._generate_seller_agent_insights(
                len(client_listings), total_views, total_inquiries, avg_days_on_market
            )
        }
    
    def _get_buyer_agent_analytics(
        self, 
        user: User, 
        start_date: datetime, 
        end_date: datetime,
        days: int
    ) -> Dict[str, Any]:
        """Analytics for buyer agents"""
        
        # Get leads (messages to this buyer agent)
        leads = self.db.query(Message).filter(
            and_(
                Message.recipient_id == user.id,
                Message.created_at >= start_date
            )
        ).all()
        
        # Response time analysis
        response_times = []
        for lead in leads:
            # Find first response from agent
            response = self.db.query(Message).filter(
                and_(
                    Message.sender_id == user.id,
                    Message.recipient_id == lead.sender_id,
                    Message.created_at > lead.created_at
                )
            ).first()
            
            if response:
                response_time = (response.created_at - lead.created_at).total_seconds() / 3600  # hours
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Lead conversion (simplified - based on continued conversation)
        converted_leads = 0
        for lead in leads:
            conversation_count = self.db.query(Message).filter(
                or_(
                    and_(Message.sender_id == user.id, Message.recipient_id == lead.sender_id),
                    and_(Message.sender_id == lead.sender_id, Message.recipient_id == user.id)
                )
            ).count()
            
            if conversation_count >= 3:  # At least 3 messages exchanged
                converted_leads += 1
        
        conversion_rate = (converted_leads / len(leads) * 100) if leads else 0
        
        return {
            "agent_type": "buyer_agent",
            "period": f"{days} days",
            "overview": {
                "total_leads": len(leads),
                "converted_leads": converted_leads,
                "conversion_rate": round(conversion_rate, 1),
                "avg_response_time_hours": round(avg_response_time, 1)
            },
            "lead_sources": self._analyze_lead_sources(leads),
            "insights": self._generate_buyer_agent_insights(
                len(leads), converted_leads, avg_response_time
            )
        }
    
    def get_market_analytics(self, location: str, days: int = 30) -> Dict[str, Any]:
        """Get market analytics for a specific location"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get properties in the area
        properties = self.db.query(PropertyListing).filter(
            or_(
                PropertyListing.city.ilike(f"%{location}%"),
                PropertyListing.address.ilike(f"%{location}%")
            )
        ).all()
        
        if not properties:
            return {"error": f"No properties found in {location}"}
        
        # Calculate market metrics
        prices = [p.price for p in properties if p.price]
        avg_price = sum(prices) / len(prices) if prices else 0
        median_price = sorted(prices)[len(prices)//2] if prices else 0
        
        # Recent listings
        recent_listings = [p for p in properties if p.created_at >= start_date]
        
        # Price trends (simplified)
        older_properties = [p for p in properties if p.created_at < start_date]
        older_avg_price = sum(p.price for p in older_properties if p.price) / len(older_properties) if older_properties else avg_price
        
        price_trend = ((avg_price - older_avg_price) / older_avg_price * 100) if older_avg_price > 0 else 0
        
        return {
            "location": location,
            "period": f"{days} days",
            "market_overview": {
                "total_properties": len(properties),
                "recent_listings": len(recent_listings),
                "average_price": round(avg_price, 2),
                "median_price": round(median_price, 2),
                "price_trend_percent": round(price_trend, 2)
            },
            "price_distribution": self._calculate_price_distribution(prices),
            "property_types": self._analyze_property_types(properties)
        }
    
    def _has_analytics_access(self, user: User) -> bool:
        """Check if user has access to analytics features"""
        if user.user_role in [UserRole.BUYER, UserRole.SELLER]:
            return False  # Basic users don't get analytics
        
        # Agents need Pro or Premium subscription
        if user.subscription_plan in [SubscriptionPlan.PRO, SubscriptionPlan.PREMIUM]:
            return user.subscription_status == "active"
        
        return False
    
    def _generate_performance_insights(
        self, 
        views: int, 
        unique_viewers: int, 
        favorites: int, 
        inquiries: int, 
        days: int
    ) -> List[str]:
        """Generate performance insights for a property"""
        insights = []
        
        daily_avg_views = views / days if days > 0 else 0
        
        if daily_avg_views > 10:
            insights.append("🔥 High visibility - getting excellent exposure")
        elif daily_avg_views > 5:
            insights.append("👍 Good visibility - steady interest")
        else:
            insights.append("📈 Consider improving photos or description to increase views")
        
        if inquiries > 0:
            inquiry_rate = (inquiries / views * 100) if views > 0 else 0
            if inquiry_rate > 5:
                insights.append("💬 Excellent inquiry rate - buyers are very interested")
            elif inquiry_rate > 2:
                insights.append("💬 Good inquiry rate - generating solid interest")
        else:
            insights.append("💬 No inquiries yet - consider adjusting price or improving listing")
        
        return insights
    
    def _generate_seller_agent_insights(
        self, 
        listings: int, 
        views: int, 
        inquiries: int, 
        avg_days: float
    ) -> List[str]:
        """Generate insights for seller agents"""
        insights = []
        
        if avg_days < 30:
            insights.append("⚡ Properties selling quickly - great market positioning")
        elif avg_days > 60:
            insights.append("📊 Properties taking longer to sell - consider pricing review")
        
        if inquiries > 0:
            inquiry_rate = inquiries / max(views, 1) * 100
            if inquiry_rate > 3:
                insights.append("🎯 High inquiry rate - listings are well-targeted")
        
        return insights
    
    def _generate_buyer_agent_insights(
        self, 
        leads: int, 
        converted: int, 
        response_time: float
    ) -> List[str]:
        """Generate insights for buyer agents"""
        insights = []
        
        if response_time < 2:
            insights.append("⚡ Excellent response time - leads are getting quick attention")
        elif response_time > 24:
            insights.append("⏰ Consider faster response times to improve conversion")
        
        if converted > 0:
            conversion_rate = converted / leads * 100
            if conversion_rate > 30:
                insights.append("🎯 High conversion rate - excellent lead nurturing")
        
        return insights
    
    def _analyze_lead_sources(self, leads: List[Message]) -> Dict[str, int]:
        """Analyze where leads are coming from"""
        # Simplified analysis - in production would track actual sources
        return {
            "property_inquiries": len([l for l in leads if l.property_id]),
            "direct_contact": len([l for l in leads if not l.property_id])
        }
    
    def _calculate_price_distribution(self, prices: List[float]) -> Dict[str, int]:
        """Calculate price distribution"""
        if not prices:
            return {}
        
        ranges = {
            "under_200k": len([p for p in prices if p < 200000]),
            "200k_400k": len([p for p in prices if 200000 <= p < 400000]),
            "400k_600k": len([p for p in prices if 400000 <= p < 600000]),
            "600k_800k": len([p for p in prices if 600000 <= p < 800000]),
            "over_800k": len([p for p in prices if p >= 800000])
        }
        
        return ranges
    
    def _analyze_property_types(self, properties: List[PropertyListing]) -> Dict[str, int]:
        """Analyze property types distribution"""
        types = {}
        for prop in properties:
            prop_type = prop.property_type or "unknown"
            types[prop_type] = types.get(prop_type, 0) + 1
        
        return types
