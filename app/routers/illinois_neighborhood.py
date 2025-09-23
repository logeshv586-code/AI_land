from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Location
from app.schemas import NeighborhoodQualityResponse, LocationCreate, LocationResponse
from app.services.illinois_neighborhood_service import IllinoisNeighborhoodService
from app.services.location_service import LocationService
from app.routers.auth import get_current_user

router = APIRouter()
neighborhood_service = IllinoisNeighborhoodService()
location_service = LocationService()

@router.post("/assess", response_model=NeighborhoodQualityResponse)
async def assess_neighborhood_quality(
    address: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    city: Optional[str] = None,
    state: str = "Illinois",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Assess neighborhood quality for a given location in Illinois.
    Requires either address or latitude/longitude coordinates.
    """
    
    if not address and (not latitude or not longitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either address or latitude/longitude coordinates are required"
        )
    
    if state.lower() != "illinois":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Neighborhood quality assessment is only available for Illinois locations"
        )
    
    # Get or create location
    location = await location_service.get_or_create_location(
        db, address, latitude, longitude, city, state
    )
    
    # Assess neighborhood quality
    try:
        assessment = await neighborhood_service.assess_neighborhood_quality(location, db)
        return assessment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assessing neighborhood quality: {str(e)}"
        )

@router.get("/factors", response_model=dict)
async def get_neighborhood_factors():
    """
    Get information about the 15 neighborhood quality factors used in assessment.
    """
    
    factors_info = {
        "factors": [
            {
                "name": "Safety & Crime Rate",
                "description": "Low crime, good street lighting, visible community policing",
                "data_source": "Illinois Uniform Crime Reporting (I-UCR) Program",
                "weight": 0.15
            },
            {
                "name": "Schools & Education Quality",
                "description": "Presence of good schools, libraries, after-school programs",
                "data_source": "Illinois Report Card - Illinois State Board of Education",
                "weight": 0.12
            },
            {
                "name": "Cleanliness & Sanitation",
                "description": "Trash management, clean streets, air and noise pollution levels",
                "data_source": "Chicago Bureau of Sanitation",
                "weight": 0.05
            },
            {
                "name": "Housing Quality & Affordability",
                "description": "Well-maintained homes vs. abandoned or overcrowded buildings",
                "data_source": "Illinois Housing Development Authority (IHDA)",
                "weight": 0.10
            },
            {
                "name": "Access to Jobs & Economy",
                "description": "Proximity to employment opportunities and strong local economy",
                "data_source": "Illinois Dept. of Employment Security (IDES)",
                "weight": 0.08
            },
            {
                "name": "Public Transport & Connectivity",
                "description": "Bus, metro, bike lanes, and access to main roads",
                "data_source": "Illinois Department of Transportation (IDOT)",
                "weight": 0.08
            },
            {
                "name": "Walkability & Infrastructure",
                "description": "Sidewalks, streetlights, pedestrian safety, traffic control",
                "data_source": "CMAP Non-Motorized Transportation Report",
                "weight": 0.07
            },
            {
                "name": "Healthcare Access",
                "description": "Nearby hospitals, clinics, pharmacies",
                "data_source": "Illinois Hospital Report Card",
                "weight": 0.07
            },
            {
                "name": "Parks & Green Spaces",
                "description": "Availability of parks, playgrounds, community gardens",
                "data_source": "Illinois Dept. of Natural Resources",
                "weight": 0.06
            },
            {
                "name": "Shopping & Amenities",
                "description": "Grocery stores, markets, cafes, and other daily needs",
                "data_source": "Enjoy Illinois Tourism Guide",
                "weight": 0.06
            },
            {
                "name": "Community Engagement",
                "description": "Active neighborhood associations, events, sense of belonging",
                "data_source": "Nicor Illinois Community Investment (NICI)",
                "weight": 0.05
            },
            {
                "name": "Noise & Environment",
                "description": "Quiet residential streets vs. constant traffic/industrial noise",
                "data_source": "Illinois EPA - Noise Pollution",
                "weight": 0.03
            },
            {
                "name": "Diversity & Inclusivity",
                "description": "Welcoming of different cultures, age groups, and backgrounds",
                "data_source": "CMAP Northeastern Illinois Census Report",
                "weight": 0.02
            },
            {
                "name": "Future Development & Property Values",
                "description": "Growth potential, city investment, rising or declining value",
                "data_source": "Illinois REALTORS® Market Statistics",
                "weight": 0.04
            },
            {
                "name": "Neighbors' Behavior",
                "description": "Friendly/helpful vs. neglectful, hostile, or isolated neighbors",
                "data_source": "Neighborhood Watch Programs",
                "weight": 0.02
            }
        ],
        "total_weight": 1.0,
        "scoring_range": "0-100 (higher is better)",
        "assessment_method": "Weighted average of all factors"
    }
    
    return factors_info

@router.get("/data-sources", response_model=dict)
async def get_data_sources():
    """
    Get information about the Illinois-specific data sources used for assessment.
    """
    
    data_sources = {
        "primary_sources": [
            {
                "name": "Illinois Uniform Crime Reporting (I-UCR) Program",
                "url": "https://ilucr.nibrs.com/",
                "description": "Official statewide crime data portal",
                "factors": ["Safety & Crime Rate"]
            },
            {
                "name": "Illinois Report Card",
                "url": "https://www.illinoisreportcard.com/",
                "description": "Illinois State Board of Education's official school performance site",
                "factors": ["Schools & Education Quality"]
            },
            {
                "name": "Chicago Bureau of Sanitation",
                "url": "https://www.chicago.gov/city/en/depts/streets/provdrs/streets_san.html",
                "description": "City of Chicago's sanitation department",
                "factors": ["Cleanliness & Sanitation"]
            },
            {
                "name": "Illinois Housing Development Authority (IHDA)",
                "url": "https://www.ihda.org/",
                "description": "State agency for affordable housing",
                "factors": ["Housing Quality & Affordability"]
            },
            {
                "name": "Illinois Dept. of Employment Security (IDES)",
                "url": "https://ides.illinois.gov/resources/labor-market-information.html",
                "description": "State labor market statistics",
                "factors": ["Access to Jobs & Economy"]
            },
            {
                "name": "Illinois Department of Transportation (IDOT)",
                "url": "https://idot.illinois.gov/transportation-system/network-overview/transit-system.html",
                "description": "Statewide transit system overview",
                "factors": ["Public Transport & Connectivity"]
            },
            {
                "name": "CMAP Non-Motorized Transportation Report",
                "url": "https://cmap.illinois.gov/wp-content/uploads/Non-motorized-transportation-report.pdf",
                "description": "Regional planning study on walking/biking infrastructure",
                "factors": ["Walkability & Infrastructure"]
            },
            {
                "name": "Illinois Hospital Report Card",
                "url": "https://healthcarereportcard.illinois.gov/",
                "description": "State-run data site for hospitals/surgery centers",
                "factors": ["Healthcare Access"]
            },
            {
                "name": "Illinois Dept. of Natural Resources",
                "url": "https://dnr.illinois.gov/parks.html",
                "description": "Official info on state parks and recreation areas",
                "factors": ["Parks & Green Spaces"]
            },
            {
                "name": "Enjoy Illinois Tourism",
                "url": "https://www.enjoyillinois.com/things-to-do/shopping/",
                "description": "State tourism site with shopping guide",
                "factors": ["Shopping & Amenities"]
            }
        ],
        "secondary_sources": [
            {
                "name": "University of Chicago Crime Lab",
                "url": "https://crimelab.uchicago.edu/",
                "description": "Research reports on Chicago crime trends"
            },
            {
                "name": "Chicago Metropolitan Agency for Planning (CMAP)",
                "url": "https://cmap.illinois.gov/",
                "description": "Regional planning and housing data"
            },
            {
                "name": "Institute for Housing Studies (DePaul University)",
                "url": "https://www.housingstudies.org/",
                "description": "Chicago-area housing market analysis"
            }
        ],
        "update_frequency": "Data sources are checked every 24 hours for updates",
        "coverage_area": "Statewide Illinois with enhanced coverage for Chicago metropolitan area"
    }
    
    return data_sources

@router.get("/compare")
async def compare_neighborhoods(
    address1: str,
    address2: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Compare neighborhood quality between two Illinois locations.
    """
    
    try:
        # Get locations
        location1 = await location_service.get_or_create_location(db, address1, state="Illinois")
        location2 = await location_service.get_or_create_location(db, address2, state="Illinois")
        
        # Assess both neighborhoods
        assessment1 = await neighborhood_service.assess_neighborhood_quality(location1, db)
        assessment2 = await neighborhood_service.assess_neighborhood_quality(location2, db)
        
        # Calculate differences
        factor_differences = {}
        for factor_name in assessment1.factors.__dict__.keys():
            value1 = getattr(assessment1.factors, factor_name)
            value2 = getattr(assessment2.factors, factor_name)
            factor_differences[factor_name] = {
                "location1_score": value1,
                "location2_score": value2,
                "difference": value2 - value1,
                "better_location": "location2" if value2 > value1 else "location1" if value1 > value2 else "tie"
            }
        
        return {
            "location1": {
                "address": address1,
                "assessment": assessment1
            },
            "location2": {
                "address": address2,
                "assessment": assessment2
            },
            "comparison": {
                "overall_score_difference": assessment2.overall_score - assessment1.overall_score,
                "better_overall": "location2" if assessment2.overall_score > assessment1.overall_score else "location1" if assessment1.overall_score > assessment2.overall_score else "tie",
                "factor_differences": factor_differences
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing neighborhoods: {str(e)}"
        )
