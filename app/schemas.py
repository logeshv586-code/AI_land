from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RecommendationType(str, Enum):
    BUY = "buy"
    HOLD = "hold"
    AVOID = "avoid"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    BUYER_AGENT = "buyer_agent"
    SELLER_AGENT = "seller_agent"

class SubscriptionPlan(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    PREMIUM = "premium"

class PropertyStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"

class MessageType(str, Enum):
    INQUIRY = "inquiry"
    RESPONSE = "response"
    FOLLOW_UP = "follow_up"
    OFFER = "offer"

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    user_role: UserRole = UserRole.BUYER
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    license_number: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    license_number: Optional[str] = None
    bio: Optional[str] = None
    commission_rate: Optional[float] = None
    years_experience: Optional[int] = None
    specializations: Optional[List[str]] = None
    service_areas: Optional[List[str]] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    subscription_plan: SubscriptionPlan
    subscription_expires_at: Optional[datetime] = None
    profile_image_url: Optional[str] = None
    commission_rate: Optional[float] = None
    years_experience: Optional[int] = None
    specializations: Optional[List[str]] = None
    service_areas: Optional[List[str]] = None
    subscription_status: str
    assigned_buyer_agent_id: Optional[int] = None
    assigned_seller_agent_id: Optional[int] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Location schemas
class LocationBase(BaseModel):
    address: str
    city: str
    state: str
    country: str
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    district: Optional[str] = None
    neighborhood: Optional[str] = None
    
    class Config:
        from_attributes = True

# Facility schemas
class FacilityBase(BaseModel):
    facility_type: str
    name: str
    distance_km: float
    rating: Optional[float] = None
    capacity: Optional[int] = None

class FacilityResponse(FacilityBase):
    id: int
    location_id: int
    
    class Config:
        from_attributes = True

# Analysis request schema
class AnalysisRequest(BaseModel):
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    property_type: str = "residential"  # residential, commercial, industrial
    investment_budget: Optional[float] = None
    investment_timeline: Optional[str] = "1-3 years"
    risk_tolerance: str = "medium"  # low, medium, high

# Analysis response schemas
class ScoreBreakdown(BaseModel):
    facility_score: float
    safety_score: float
    disaster_risk_score: float
    market_potential_score: float
    accessibility_score: float

class PredictionData(BaseModel):
    predicted_value_change_1y: float
    predicted_value_change_3y: float
    predicted_value_change_5y: float

class RiskFactor(BaseModel):
    factor: str
    severity: str
    description: str
    impact_score: float

class Opportunity(BaseModel):
    opportunity: str
    potential_impact: str
    description: str
    confidence: float

class NearbyFacility(BaseModel):
    type: str
    name: str
    distance: float
    rating: Optional[float] = None
    impact_on_score: float

class AnalysisResponse(BaseModel):
    id: int
    location: LocationResponse
    overall_score: float
    recommendation: RecommendationType
    confidence_level: float
    
    # Score breakdown
    scores: ScoreBreakdown
    
    # Predictions
    predictions: PredictionData
    
    # Detailed analysis
    risk_factors: List[RiskFactor]
    opportunities: List[Opportunity]
    nearby_facilities: List[NearbyFacility]
    
    # Market data
    avg_price_per_sqft: Optional[float] = None
    price_trend_6m: Optional[float] = None
    price_trend_1y: Optional[float] = None
    
    # Metadata
    created_at: datetime
    model_version: str
    
    class Config:
        from_attributes = True

# Quick analysis response (simplified)
class QuickAnalysisResponse(BaseModel):
    overall_score: float
    recommendation: RecommendationType
    confidence_level: float
    key_factors: List[str]
    summary: str

# Crime data schema
class CrimeDataResponse(BaseModel):
    crime_type: str
    incident_count: int
    crime_rate_per_1000: float
    severity_score: float
    year: int
    month: int
    
    class Config:
        from_attributes = True

# Disaster data schema
class DisasterDataResponse(BaseModel):
    disaster_type: str
    risk_level: RiskLevel
    probability: float
    last_occurrence: Optional[datetime] = None
    historical_frequency: float
    
    class Config:
        from_attributes = True

# Market data schema
class MarketDataResponse(BaseModel):
    property_type: str
    avg_price_per_sqft: float
    price_trend_6m: float
    price_trend_1y: float
    demand_score: float
    supply_score: float
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Batch analysis request
class BatchAnalysisRequest(BaseModel):
    locations: List[AnalysisRequest]
    analysis_name: Optional[str] = None

class BatchAnalysisResponse(BaseModel):
    batch_id: str
    total_locations: int
    completed: int
    failed: int
    results: List[AnalysisResponse]
    
# Data update schemas
class DataUpdateStatus(BaseModel):
    data_type: str
    last_update: datetime
    next_update: datetime
    status: str
    records_count: int

# Model performance schema
class ModelPerformance(BaseModel):
    model_name: str
    model_version: str
    accuracy_score: float
    precision: float
    recall: float
    f1_score: float
    training_date: datetime
    is_active: bool

# Property Valuation schemas
class PropertyValuationBase(BaseModel):
    property_type: str = "residential"
    beds: Optional[int] = None
    baths: Optional[int] = None
    sqft: Optional[int] = None
    year_built: Optional[int] = None
    lot_size: Optional[float] = None

class PropertyValuationCreate(PropertyValuationBase):
    location_id: int

class PropertyValuationResponse(PropertyValuationBase):
    id: int
    location_id: int
    current_value: Optional[float] = None
    predicted_value: Optional[float] = None
    value_uncertainty: Optional[float] = None
    price_per_sqft: Optional[float] = None
    comparable_sales_count: Optional[int] = None
    days_on_market_avg: Optional[float] = None
    valuation_date: datetime
    last_sale_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# Beneficiary Score schemas
class BeneficiaryScoreResponse(BaseModel):
    id: int
    location_id: int
    overall_score: float
    value_score: float
    school_score: float
    safety_score: float
    environmental_score: float
    accessibility_score: float
    scoring_weights: Dict[str, float]
    score_components: Dict[str, Any]
    calculated_at: datetime
    model_version: str

    class Config:
        from_attributes = True

class BeneficiaryScoreRequest(BaseModel):
    location_id: int
    property_valuation_id: Optional[int] = None
    custom_weights: Optional[Dict[str, float]] = None

# Property Recommendation schemas
class PropertyRecommendationResponse(BaseModel):
    id: int
    recommended_property: PropertyValuationResponse
    recommendation_type: str
    similarity_score: float
    confidence_score: float
    rank_position: int
    recommendation_reason: str
    created_at: datetime

    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    property_id: Optional[int] = None
    user_preferences: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, float]] = None  # {"lat": x, "lon": y}
    radius_km: Optional[float] = 10.0
    max_recommendations: int = 10
    recommendation_type: str = "hybrid"  # content_based, collaborative, hybrid

# Enhanced Analysis Request with AVM features
class EnhancedAnalysisRequest(AnalysisRequest):
    # Property characteristics for AVM
    beds: Optional[int] = None
    baths: Optional[int] = None
    sqft: Optional[int] = None
    year_built: Optional[int] = None
    lot_size: Optional[float] = None

    # Valuation preferences
    include_avm: bool = True
    include_beneficiary_score: bool = True
    include_recommendations: bool = True
    include_explanations: bool = True

    # Custom scoring weights
    custom_weights: Optional[Dict[str, float]] = None

# Enhanced Analysis Response with AVM and beneficiary data
class EnhancedAnalysisResponse(AnalysisResponse):
    # Property valuation data
    property_valuation: Optional[PropertyValuationResponse] = None
    beneficiary_score: Optional[BeneficiaryScoreResponse] = None

    # Recommendations
    similar_properties: List[PropertyRecommendationResponse] = []

    # Model explanations
    feature_explanations: Optional[Dict[str, Any]] = None

    # AVM specific data
    avm_confidence: Optional[float] = None
    comparable_properties: List[PropertyValuationResponse] = []

# User Interaction schemas
class UserInteractionCreate(BaseModel):
    property_valuation_id: int
    interaction_type: str
    search_query: Optional[str] = None
    referrer_source: Optional[str] = None
    device_type: Optional[str] = None
    session_duration: Optional[int] = None

class UserInteractionResponse(BaseModel):
    id: int
    user_id: int
    property_valuation_id: int
    interaction_type: str
    interaction_weight: float
    interaction_time: datetime

    class Config:
        from_attributes = True

# Model Explanation schemas
class FeatureAttribution(BaseModel):
    feature_name: str
    attribution_value: float
    feature_value: Any
    impact_description: str

class ModelExplanationResponse(BaseModel):
    id: int
    analysis_id: Optional[int] = None
    property_valuation_id: Optional[int] = None
    base_value: float
    prediction_value: float
    top_positive_features: List[FeatureAttribution]
    top_negative_features: List[FeatureAttribution]
    explanation_type: str
    model_version: str
    generated_at: datetime

    class Config:
        from_attributes = True

# Comprehensive analysis request for land area automation
class LandAreaAnalysisRequest(BaseModel):
    # Location data
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Property characteristics
    property_type: str = "residential"
    beds: Optional[int] = None
    baths: Optional[int] = None
    sqft: Optional[int] = None
    year_built: Optional[int] = None
    lot_size: Optional[float] = None

    # Analysis preferences
    investment_budget: Optional[float] = None
    investment_timeline: str = "1-3 years"
    risk_tolerance: str = "medium"

    # Feature toggles
    include_avm: bool = True
    include_beneficiary_score: bool = True
    include_recommendations: bool = True
    include_explanations: bool = True
    include_market_analysis: bool = True

    # Custom weights for scoring
    custom_weights: Optional[Dict[str, float]] = None

    # Recommendation parameters
    max_recommendations: int = 10
    recommendation_radius_km: float = 10.0

# Comprehensive response for land area automation
class LandAreaAnalysisResponse(BaseModel):
    # Basic analysis data
    analysis_id: int
    location: LocationResponse
    overall_score: float
    recommendation: RecommendationType
    confidence_level: float

    # Detailed scoring
    scores: ScoreBreakdown
    beneficiary_score: Optional[BeneficiaryScoreResponse] = None

    # Property valuation
    property_valuation: Optional[PropertyValuationResponse] = None
    avm_confidence: Optional[float] = None

    # Predictions and market data
    predictions: PredictionData
    market_data: Optional[MarketDataResponse] = None

    # Risk and opportunity analysis
    risk_factors: List[RiskFactor]
    opportunities: List[Opportunity]

    # Recommendations
    similar_properties: List[PropertyRecommendationResponse] = []
    nearby_facilities: List[NearbyFacility]

    # Model explanations
    feature_explanations: Optional[ModelExplanationResponse] = None

    # Metadata
    created_at: datetime
    model_version: str
    processing_time_ms: Optional[int] = None

# Property Listing schemas
class PropertyListingBase(BaseModel):
    title: str
    description: str
    property_type: str
    listing_type: str = "sale"
    price: float
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    sqft: Optional[int] = None
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    garage_spaces: Optional[int] = None
    features: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    appliances_included: Optional[List[str]] = None

class PropertyListingCreate(PropertyListingBase):
    address: str
    city: str
    state: str = "Illinois"
    country: str = "USA"
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PropertyListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    sqft: Optional[int] = None
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    garage_spaces: Optional[int] = None
    features: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    appliances_included: Optional[List[str]] = None
    status: Optional[PropertyStatus] = None
    is_featured: Optional[bool] = None

class PropertyListingResponse(PropertyListingBase):
    id: int
    owner_id: int
    agent_id: Optional[int] = None
    location: LocationResponse
    price_per_sqft: Optional[float] = None
    status: PropertyStatus
    is_featured: bool
    featured_until: Optional[datetime] = None
    views_count: int
    favorites_count: int
    images: Optional[List[str]] = None
    virtual_tour_url: Optional[str] = None
    video_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    listed_date: datetime

    # Illinois neighborhood quality scores
    neighborhood_quality_score: Optional[float] = None
    safety_crime_score: Optional[float] = None
    schools_education_score: Optional[float] = None
    cleanliness_sanitation_score: Optional[float] = None
    housing_quality_score: Optional[float] = None
    jobs_economy_score: Optional[float] = None
    transport_connectivity_score: Optional[float] = None
    walkability_infrastructure_score: Optional[float] = None
    healthcare_access_score: Optional[float] = None
    parks_green_spaces_score: Optional[float] = None
    shopping_amenities_score: Optional[float] = None
    community_engagement_score: Optional[float] = None
    noise_environment_score: Optional[float] = None
    diversity_inclusivity_score: Optional[float] = None
    future_development_score: Optional[float] = None
    neighbors_behavior_score: Optional[float] = None

    # Related data
    owner: Optional[UserResponse] = None
    agent: Optional[UserResponse] = None

    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    subject: str
    content: str
    message_type: MessageType = MessageType.INQUIRY
    priority: str = "normal"

class MessageCreate(MessageBase):
    recipient_id: int
    property_listing_id: int

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    recipient_id: int
    property_listing_id: int
    is_read: bool
    is_archived: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    # Related data
    sender: Optional[UserResponse] = None
    recipient: Optional[UserResponse] = None

    class Config:
        from_attributes = True

# Subscription schemas
class SubscriptionBase(BaseModel):
    plan_name: str
    plan_price: float
    billing_cycle: str = "monthly"
    payment_method: str

class SubscriptionCreate(SubscriptionBase):
    payment_id: str
    subscription_id: Optional[str] = None

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancelled_at: Optional[datetime] = None
    listings_used: int
    featured_listings_used: int
    analytics_views: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Illinois Neighborhood Quality Assessment
class NeighborhoodQualityFactors(BaseModel):
    safety_crime_rate: float
    schools_education_quality: float
    cleanliness_sanitation: float
    housing_quality_affordability: float
    access_jobs_economy: float
    public_transport_connectivity: float
    walkability_infrastructure: float
    healthcare_access: float
    parks_green_spaces: float
    shopping_amenities: float
    community_engagement: float
    noise_environment: float
    diversity_inclusivity: float
    future_development_property_values: float
    neighbors_behavior: float

class NeighborhoodQualityResponse(BaseModel):
    overall_score: float
    factors: NeighborhoodQualityFactors
    data_sources: Dict[str, str]  # Factor name to data source URL
    last_updated: datetime