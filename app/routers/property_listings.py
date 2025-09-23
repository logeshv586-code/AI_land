from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.models import User, PropertyListing, Location, UserRole
from app.schemas import (
    PropertyListingCreate, PropertyListingUpdate, PropertyListingResponse,
    PropertyStatus, UserResponse, NeighborhoodQualityResponse
)
from app.routers.auth import get_current_user, require_seller, require_seller_agent, require_agent
from app.services.location_service import LocationService
from app.services.illinois_neighborhood_service import IllinoisNeighborhoodService

router = APIRouter()
location_service = LocationService()
neighborhood_service = IllinoisNeighborhoodService()

@router.post("/", response_model=PropertyListingResponse)
async def create_property_listing(
    listing_data: PropertyListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new property listing. Only sellers and seller agents can create listings."""
    
    # Check if user can create listings
    if current_user.user_role not in [UserRole.SELLER, UserRole.SELLER_AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers and seller agents can create property listings"
        )
    
    # For seller agents, check active subscription
    if current_user.user_role == UserRole.SELLER_AGENT:
        if current_user.subscription_status != "active":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Active subscription required to create listings"
            )
    
    # Get or create location
    location = await location_service.get_or_create_location(
        db, listing_data.address, listing_data.latitude, listing_data.longitude
    )
    
    # Calculate price per sqft if sqft is provided
    price_per_sqft = None
    if listing_data.sqft and listing_data.sqft > 0:
        price_per_sqft = listing_data.price / listing_data.sqft
    
    # Assess neighborhood quality for Illinois properties
    neighborhood_quality = None
    if location.state and location.state.lower() == "illinois":
        try:
            neighborhood_quality = await neighborhood_service.assess_neighborhood_quality(location, db)
        except Exception as e:
            # Log error but don't fail the listing creation
            print(f"Warning: Could not assess neighborhood quality: {str(e)}")

    # Create property listing
    db_listing = PropertyListing(
        owner_id=current_user.id if current_user.user_role == UserRole.SELLER else None,
        agent_id=current_user.id if current_user.user_role == UserRole.SELLER_AGENT else None,
        location_id=location.id,
        title=listing_data.title,
        description=listing_data.description,
        property_type=listing_data.property_type,
        listing_type=listing_data.listing_type,
        price=listing_data.price,
        price_per_sqft=price_per_sqft,
        bedrooms=listing_data.bedrooms,
        bathrooms=listing_data.bathrooms,
        sqft=listing_data.sqft,
        lot_size=listing_data.lot_size,
        year_built=listing_data.year_built,
        garage_spaces=listing_data.garage_spaces,
        features=listing_data.features or [],
        amenities=listing_data.amenities or [],
        appliances_included=listing_data.appliances_included or []
    )

    # Add neighborhood quality scores if available
    if neighborhood_quality:
        db_listing.neighborhood_quality_score = neighborhood_quality.overall_score
        db_listing.safety_crime_score = neighborhood_quality.factors.safety_crime_rate
        db_listing.schools_education_score = neighborhood_quality.factors.schools_education_quality
        db_listing.cleanliness_sanitation_score = neighborhood_quality.factors.cleanliness_sanitation
        db_listing.housing_quality_score = neighborhood_quality.factors.housing_quality_affordability
        db_listing.jobs_economy_score = neighborhood_quality.factors.access_jobs_economy
        db_listing.transport_connectivity_score = neighborhood_quality.factors.public_transport_connectivity
        db_listing.walkability_infrastructure_score = neighborhood_quality.factors.walkability_infrastructure
        db_listing.healthcare_access_score = neighborhood_quality.factors.healthcare_access
        db_listing.parks_green_spaces_score = neighborhood_quality.factors.parks_green_spaces
        db_listing.shopping_amenities_score = neighborhood_quality.factors.shopping_amenities
        db_listing.community_engagement_score = neighborhood_quality.factors.community_engagement
        db_listing.noise_environment_score = neighborhood_quality.factors.noise_environment
        db_listing.diversity_inclusivity_score = neighborhood_quality.factors.diversity_inclusivity
        db_listing.future_development_score = neighborhood_quality.factors.future_development_property_values
        db_listing.neighbors_behavior_score = neighborhood_quality.factors.neighbors_behavior

    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    
    return db_listing

@router.get("/", response_model=List[PropertyListingResponse])
async def get_property_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    property_type: Optional[str] = None,
    listing_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_bedrooms: Optional[int] = None,
    max_bedrooms: Optional[int] = None,
    min_bathrooms: Optional[float] = None,
    max_bathrooms: Optional[float] = None,
    min_sqft: Optional[int] = None,
    max_sqft: Optional[int] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    status: Optional[PropertyStatus] = PropertyStatus.ACTIVE,
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get property listings with filtering options"""
    
    query = db.query(PropertyListing).join(Location)
    
    # Apply filters
    if property_type:
        query = query.filter(PropertyListing.property_type == property_type)
    
    if listing_type:
        query = query.filter(PropertyListing.listing_type == listing_type)
    
    if min_price is not None:
        query = query.filter(PropertyListing.price >= min_price)
    
    if max_price is not None:
        query = query.filter(PropertyListing.price <= max_price)
    
    if min_bedrooms is not None:
        query = query.filter(PropertyListing.bedrooms >= min_bedrooms)
    
    if max_bedrooms is not None:
        query = query.filter(PropertyListing.bedrooms <= max_bedrooms)
    
    if min_bathrooms is not None:
        query = query.filter(PropertyListing.bathrooms >= min_bathrooms)
    
    if max_bathrooms is not None:
        query = query.filter(PropertyListing.bathrooms <= max_bathrooms)
    
    if min_sqft is not None:
        query = query.filter(PropertyListing.sqft >= min_sqft)
    
    if max_sqft is not None:
        query = query.filter(PropertyListing.sqft <= max_sqft)
    
    if city:
        query = query.filter(Location.city.ilike(f"%{city}%"))
    
    if state:
        query = query.filter(Location.state.ilike(f"%{state}%"))
    
    if status:
        query = query.filter(PropertyListing.status == status.value)
    
    if featured_only:
        query = query.filter(
            and_(
                PropertyListing.is_featured == True,
                or_(
                    PropertyListing.featured_until.is_(None),
                    PropertyListing.featured_until > datetime.utcnow()
                )
            )
        )
    
    # Order by featured first, then by creation date
    query = query.order_by(
        PropertyListing.is_featured.desc(),
        PropertyListing.created_at.desc()
    )
    
    listings = query.offset(skip).limit(limit).all()
    return listings

@router.get("/{listing_id}", response_model=PropertyListingResponse)
async def get_property_listing(
    listing_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific property listing by ID"""
    
    listing = db.query(PropertyListing).filter(PropertyListing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property listing not found"
        )
    
    # Increment view count
    listing.views_count += 1
    db.commit()
    
    return listing

@router.put("/{listing_id}", response_model=PropertyListingResponse)
async def update_property_listing(
    listing_id: int,
    listing_update: PropertyListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a property listing. Only the owner or agent can update."""
    
    listing = db.query(PropertyListing).filter(PropertyListing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property listing not found"
        )
    
    # Check permissions
    if listing.owner_id != current_user.id and listing.agent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own listings"
        )
    
    # Update fields
    update_data = listing_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)
    
    # Recalculate price per sqft if price or sqft changed
    if 'price' in update_data or 'sqft' in update_data:
        if listing.sqft and listing.sqft > 0:
            listing.price_per_sqft = listing.price / listing.sqft
    
    listing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(listing)
    
    return listing

@router.delete("/{listing_id}")
async def delete_property_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a property listing. Only the owner or agent can delete."""
    
    listing = db.query(PropertyListing).filter(PropertyListing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property listing not found"
        )
    
    # Check permissions
    if listing.owner_id != current_user.id and listing.agent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own listings"
        )
    
    db.delete(listing)
    db.commit()
    
    return {"message": "Property listing deleted successfully"}

@router.get("/my/listings", response_model=List[PropertyListingResponse])
async def get_my_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's property listings"""
    
    query = db.query(PropertyListing)
    
    if current_user.user_role == UserRole.SELLER:
        query = query.filter(PropertyListing.owner_id == current_user.id)
    elif current_user.user_role == UserRole.SELLER_AGENT:
        query = query.filter(PropertyListing.agent_id == current_user.id)
    else:
        # Buyers and buyer agents don't have listings
        return []
    
    query = query.order_by(PropertyListing.created_at.desc())
    listings = query.offset(skip).limit(limit).all()

    return listings

@router.get("/neighborhood-quality/{listing_id}", response_model=NeighborhoodQualityResponse)
async def get_neighborhood_quality(
    listing_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed neighborhood quality assessment for a property listing"""

    listing = db.query(PropertyListing).filter(PropertyListing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property listing not found"
        )

    # Get the location
    location = db.query(Location).filter(Location.id == listing.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    # Assess neighborhood quality
    if location.state and location.state.lower() == "illinois":
        neighborhood_quality = await neighborhood_service.assess_neighborhood_quality(location, db)
        return neighborhood_quality
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Neighborhood quality assessment is only available for Illinois properties"
        )
