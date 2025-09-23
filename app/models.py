from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class UserRole(enum.Enum):
    BUYER = "buyer"
    SELLER = "seller"
    BUYER_AGENT = "buyer_agent"
    SELLER_AGENT = "seller_agent"

class SubscriptionPlan(enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    PREMIUM = "premium"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # New role-based fields
    user_role = Column(Enum(UserRole), default=UserRole.BUYER)
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    subscription_expires_at = Column(DateTime)

    # Profile information
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    company_name = Column(String)  # For agents
    license_number = Column(String)  # For agents
    bio = Column(Text)
    profile_image_url = Column(String)

    # Agent assignment fields
    assigned_buyer_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For buyers
    assigned_seller_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For sellers
    
    # Agent-specific fields
    commission_rate = Column(Float)  # For agents
    years_experience = Column(Integer)  # For agents
    specializations = Column(JSON)  # List of specializations for agents
    service_areas = Column(JSON)  # List of service areas for agents

    # Subscription and payment
    stripe_customer_id = Column(String)
    paypal_customer_id = Column(String)
    subscription_status = Column(String, default="inactive")  # active, inactive, cancelled, past_due

    # Relationships
    analyses = relationship("LandAnalysis", back_populates="user")
    property_listings = relationship("PropertyListing", back_populates="owner", foreign_keys="PropertyListing.owner_id")
    agent_listings = relationship("PropertyListing", back_populates="agent", foreign_keys="PropertyListing.agent_id")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    received_messages = relationship("Message", back_populates="recipient", foreign_keys="Message.recipient_id")
    subscriptions = relationship("Subscription", back_populates="user")
    
    # Agent assignment relationships
    assigned_buyer_agent = relationship("User", remote_side="User.id", foreign_keys=[assigned_buyer_agent_id], post_update=True)
    assigned_seller_agent = relationship("User", remote_side="User.id", foreign_keys=[assigned_seller_agent_id], post_update=True)
    buyer_clients = relationship("User", foreign_keys="User.assigned_buyer_agent_id", back_populates="assigned_buyer_agent")
    seller_clients = relationship("User", foreign_keys="User.assigned_seller_agent_id", back_populates="assigned_seller_agent")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    city = Column(String, index=True)
    state = Column(String, index=True)
    country = Column(String, index=True)
    postal_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Geographic and administrative data
    district = Column(String)
    neighborhood = Column(String)
    
    # Relationships
    analyses = relationship("LandAnalysis", back_populates="location")
    facilities = relationship("Facility", back_populates="location")
    crime_data = relationship("CrimeData", back_populates="location")
    disaster_data = relationship("DisasterData", back_populates="location")

class Facility(Base):
    __tablename__ = "facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    facility_type = Column(String)  # school, hospital, mall, transport, etc.
    name = Column(String)
    distance_km = Column(Float)
    rating = Column(Float)  # Quality rating if available
    capacity = Column(Integer)  # For schools, hospitals
    
    # Relationships
    location = relationship("Location", back_populates="facilities")

class CrimeData(Base):
    __tablename__ = "crime_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    crime_type = Column(String)
    incident_count = Column(Integer)
    crime_rate_per_1000 = Column(Float)
    year = Column(Integer)
    month = Column(Integer)
    severity_score = Column(Float)  # Calculated severity
    
    # Relationships
    location = relationship("Location", back_populates="crime_data")

class DisasterData(Base):
    __tablename__ = "disaster_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    disaster_type = Column(String)  # flood, earthquake, hurricane, etc.
    risk_level = Column(String)  # low, medium, high, extreme
    probability = Column(Float)  # 0-1 probability
    last_occurrence = Column(DateTime)
    historical_frequency = Column(Float)  # events per year
    
    # Relationships
    location = relationship("Location", back_populates="disaster_data")

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    property_type = Column(String)  # residential, commercial, industrial
    avg_price_per_sqft = Column(Float)
    price_trend_6m = Column(Float)  # % change in 6 months
    price_trend_1y = Column(Float)  # % change in 1 year
    demand_score = Column(Float)  # 0-100 demand score
    supply_score = Column(Float)  # 0-100 supply score
    updated_at = Column(DateTime, default=datetime.utcnow)

class LandAnalysis(Base):
    __tablename__ = "land_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    
    # Analysis results
    overall_score = Column(Float)  # 0-100 suitability score
    recommendation = Column(String)  # buy, hold, avoid
    confidence_level = Column(Float)  # 0-1 confidence
    
    # Individual factor scores
    facility_score = Column(Float)
    safety_score = Column(Float)
    disaster_risk_score = Column(Float)
    market_potential_score = Column(Float)
    accessibility_score = Column(Float)
    
    # Detailed analysis
    analysis_details = Column(JSON)  # Detailed breakdown
    risk_factors = Column(JSON)  # List of risk factors
    opportunities = Column(JSON)  # List of opportunities
    
    # Prediction data
    predicted_value_change_1y = Column(Float)
    predicted_value_change_3y = Column(Float)
    predicted_value_change_5y = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    location = relationship("Location", back_populates="analyses")

class DataUpdateLog(Base):
    __tablename__ = "data_update_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String)  # facilities, crime, disaster, market
    update_status = Column(String)  # success, failed, in_progress
    records_updated = Column(Integer)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String)
    model_version = Column(String)
    model_type = Column(String)  # classification, regression, ensemble
    accuracy_score = Column(Float)
    training_data_size = Column(Integer)
    feature_importance = Column(JSON)
    model_path = Column(String)  # Path to saved model file
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    performance_metrics = Column(JSON)

class PropertyValuation(Base):
    __tablename__ = "property_valuations"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    property_type = Column(String)  # residential, commercial, industrial

    # Property characteristics
    beds = Column(Integer)
    baths = Column(Integer)
    sqft = Column(Integer)
    year_built = Column(Integer)
    lot_size = Column(Float)

    # Valuation data
    current_value = Column(Float)
    predicted_value = Column(Float)
    value_uncertainty = Column(Float)  # Standard deviation from AVM
    price_per_sqft = Column(Float)

    # Market data
    comparable_sales_count = Column(Integer)
    days_on_market_avg = Column(Float)
    sale_price_variance = Column(Float)

    # Timestamps
    valuation_date = Column(DateTime, default=datetime.utcnow)
    last_sale_date = Column(DateTime)

    # Relationships
    location = relationship("Location")

class BeneficiaryScore(Base):
    __tablename__ = "beneficiary_scores"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    property_valuation_id = Column(Integer, ForeignKey("property_valuations.id"))

    # Overall beneficiary score (0-100)
    overall_score = Column(Float)

    # Component scores (0-100 each)
    value_score = Column(Float)
    school_score = Column(Float)
    safety_score = Column(Float)
    environmental_score = Column(Float)
    accessibility_score = Column(Float)

    # Weights used in calculation
    scoring_weights = Column(JSON)

    # Score breakdown details
    score_components = Column(JSON)

    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String)

    # Relationships
    location = relationship("Location")
    property_valuation = relationship("PropertyValuation")

class PropertyRecommendation(Base):
    __tablename__ = "property_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    source_property_id = Column(Integer, ForeignKey("property_valuations.id"))
    recommended_property_id = Column(Integer, ForeignKey("property_valuations.id"))

    # Recommendation details
    recommendation_type = Column(String)  # content_based, collaborative, hybrid
    similarity_score = Column(Float)
    confidence_score = Column(Float)

    # Ranking and filtering
    rank_position = Column(Integer)
    recommendation_reason = Column(Text)

    # User interaction tracking
    viewed = Column(Boolean, default=False)
    saved = Column(Boolean, default=False)
    contacted = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    viewed_at = Column(DateTime)

    # Relationships
    user = relationship("User")
    source_property = relationship("PropertyValuation", foreign_keys=[source_property_id])
    recommended_property = relationship("PropertyValuation", foreign_keys=[recommended_property_id])

class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    property_valuation_id = Column(Integer, ForeignKey("property_valuations.id"))

    # Interaction details
    interaction_type = Column(String)  # view, save, contact, share
    interaction_weight = Column(Float)  # Weighted importance for recommendations
    session_id = Column(String)

    # Context data
    search_query = Column(String)
    referrer_source = Column(String)
    device_type = Column(String)

    # Timestamps
    interaction_time = Column(DateTime, default=datetime.utcnow)
    session_duration = Column(Integer)  # seconds

    # Relationships
    user = relationship("User")
    property_valuation = relationship("PropertyValuation")

# New models for Illinois Real Estate Application

class PropertyListing(Base):
    __tablename__ = "property_listings"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))  # Seller
    agent_id = Column(Integer, ForeignKey("users.id"))  # Seller Agent
    location_id = Column(Integer, ForeignKey("locations.id"))

    # Basic property information
    title = Column(String, index=True)
    description = Column(Text)
    property_type = Column(String)  # house, condo, townhouse, land, commercial
    listing_type = Column(String)  # sale, rent
    price = Column(Float)
    price_per_sqft = Column(Float)

    # Property details
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    sqft = Column(Integer)
    lot_size = Column(Float)
    year_built = Column(Integer)
    garage_spaces = Column(Integer)

    # Property features
    features = Column(JSON)  # List of features
    amenities = Column(JSON)  # List of amenities
    appliances_included = Column(JSON)  # List of included appliances

    # Listing status and metadata
    status = Column(String, default="active")  # active, pending, sold, withdrawn
    is_featured = Column(Boolean, default=False)  # Premium feature
    featured_until = Column(DateTime)  # When featured status expires
    views_count = Column(Integer, default=0)
    favorites_count = Column(Integer, default=0)

    # Images and media
    images = Column(JSON)  # List of image URLs
    virtual_tour_url = Column(String)
    video_url = Column(String)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    listed_date = Column(DateTime, default=datetime.utcnow)

    # Illinois-specific neighborhood quality data
    neighborhood_quality_score = Column(Float)  # Overall score 0-100
    safety_crime_score = Column(Float)
    schools_education_score = Column(Float)
    cleanliness_sanitation_score = Column(Float)
    housing_quality_score = Column(Float)
    jobs_economy_score = Column(Float)
    transport_connectivity_score = Column(Float)
    walkability_infrastructure_score = Column(Float)
    healthcare_access_score = Column(Float)
    parks_green_spaces_score = Column(Float)
    shopping_amenities_score = Column(Float)
    community_engagement_score = Column(Float)
    noise_environment_score = Column(Float)
    diversity_inclusivity_score = Column(Float)
    future_development_score = Column(Float)
    neighbors_behavior_score = Column(Float)

    # Relationships
    owner = relationship("User", back_populates="property_listings", foreign_keys=[owner_id])
    agent = relationship("User", back_populates="agent_listings", foreign_keys=[agent_id])
    location = relationship("Location")
    messages = relationship("Message", back_populates="property_listing")
    favorites = relationship("PropertyFavorite", back_populates="property_listing")
    views = relationship("PropertyView", back_populates="property")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    property_listing_id = Column(Integer, ForeignKey("property_listings.id"))

    # Message content
    subject = Column(String)
    content = Column(Text)
    message_type = Column(String, default="inquiry")  # inquiry, response, follow_up, offer

    # Message status
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    priority = Column(String, default="normal")  # low, normal, high, urgent

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)

    # Relationships
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])
    recipient = relationship("User", back_populates="received_messages", foreign_keys=[recipient_id])
    property_listing = relationship("PropertyListing", back_populates="messages")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Subscription details
    plan_name = Column(String)  # basic, pro, premium
    plan_price = Column(Float)
    billing_cycle = Column(String)  # monthly, annual

    # Payment information
    payment_method = Column(String)  # stripe, paypal
    payment_id = Column(String)  # External payment ID
    subscription_id = Column(String)  # External subscription ID

    # Status and dates
    status = Column(String)  # active, cancelled, past_due, unpaid
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancelled_at = Column(DateTime)

    # Usage tracking
    listings_used = Column(Integer, default=0)
    featured_listings_used = Column(Integer, default=0)
    analytics_views = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscriptions")

class PropertyView(Base):
    """Track property views for analytics"""
    __tablename__ = "property_views"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("property_listings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous views
    viewed_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)  # For anonymous tracking
    user_agent = Column(Text, nullable=True)

    # Relationships
    property = relationship("PropertyListing", back_populates="views")
    user = relationship("User")

class PropertyFavorite(Base):
    __tablename__ = "property_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    property_listing_id = Column(Integer, ForeignKey("property_listings.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    property_listing = relationship("PropertyListing", back_populates="favorites")

class ModelExplanation(Base):
    __tablename__ = "model_explanations"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("land_analyses.id"))
    property_valuation_id = Column(Integer, ForeignKey("property_valuations.id"))

    # SHAP explanation data
    feature_attributions = Column(JSON)  # SHAP values for each feature
    base_value = Column(Float)  # Model's base prediction
    prediction_value = Column(Float)  # Actual prediction

    # Top contributing features
    top_positive_features = Column(JSON)  # Features that increase prediction
    top_negative_features = Column(JSON)  # Features that decrease prediction

    # Explanation metadata
    explanation_type = Column(String)  # shap_tree, shap_linear, etc.
    model_version = Column(String)
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    analysis = relationship("LandAnalysis")
    property_valuation = relationship("PropertyValuation")