from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import asyncio
import logging

from app.database import get_db
from app.models import Location, User
from app.schemas import LocationCreate
from app.routers.auth import get_current_user
from app.services.illinois_data_integration import IllinoisDataIntegration

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize data integration service
data_integration = IllinoisDataIntegration()

@router.get("/sources/status")
async def get_data_sources_status():
    """Get status of all Illinois data sources"""
    try:
        status = await data_integration.get_data_source_status()
        return status
    except Exception as e:
        logger.error(f"Error getting data sources status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving data sources status"
        )

@router.get("/sources")
async def get_available_data_sources(
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get list of available Illinois data sources"""
    try:
        status = await data_integration.get_data_source_status()
        sources = status["sources"]
        
        if category:
            sources = {
                key: source for key, source in sources.items()
                if source["category"] == category
            }
        
        return {
            "sources": sources,
            "categories": list(status["categories"].keys()),
            "total_sources": len(sources)
        }
    except Exception as e:
        logger.error(f"Error getting data sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving data sources"
        )

@router.post("/fetch-comprehensive")
async def fetch_comprehensive_data(
    location: LocationCreate,
    categories: Optional[List[str]] = Query(None, description="Categories to fetch data for"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch comprehensive data from all Illinois sources for a location"""
    
    try:
        # Create location object
        location_obj = Location(
            address=location.address,
            city=location.city,
            state=location.state,
            zip_code=location.zip_code,
            latitude=location.latitude,
            longitude=location.longitude
        )
        
        # Fetch data from all sources
        comprehensive_data = await data_integration.fetch_comprehensive_data(
            location_obj, categories
        )
        
        # Process and structure the response
        response = {
            "location": {
                "address": location.address,
                "city": location.city,
                "state": location.state,
                "coordinates": {
                    "latitude": location.latitude,
                    "longitude": location.longitude
                }
            },
            "data_sources": len(comprehensive_data),
            "categories_fetched": categories or ["all"],
            "data": comprehensive_data,
            "summary": _generate_data_summary(comprehensive_data)
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching comprehensive data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching comprehensive data: {str(e)}"
        )

@router.post("/fetch-category")
async def fetch_category_data(
    location: LocationCreate,
    category: str = Query(..., description="Category to fetch data for"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch data from Illinois sources for a specific category"""
    
    valid_categories = [
        "crime", "education", "housing", "employment", "transportation",
        "infrastructure", "healthcare", "recreation", "amenities",
        "community", "environment", "demographics", "market"
    ]
    
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Valid categories: {valid_categories}"
        )
    
    try:
        # Create location object
        location_obj = Location(
            address=location.address,
            city=location.city,
            state=location.state,
            zip_code=location.zip_code,
            latitude=location.latitude,
            longitude=location.longitude
        )
        
        # Fetch data for specific category
        category_data = await data_integration.fetch_comprehensive_data(
            location_obj, [category]
        )
        
        # Filter only sources from the requested category
        filtered_data = {
            key: value for key, value in category_data.items()
            if value.get("category") == category
        }
        
        response = {
            "location": {
                "address": location.address,
                "city": location.city,
                "state": location.state,
                "coordinates": {
                    "latitude": location.latitude,
                    "longitude": location.longitude
                }
            },
            "category": category,
            "data_sources": len(filtered_data),
            "data": filtered_data,
            "summary": _generate_category_summary(filtered_data, category)
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching category data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching category data: {str(e)}"
        )

@router.get("/categories")
async def get_data_categories():
    """Get list of available data categories"""
    categories = {
        "crime": {
            "name": "Crime & Safety",
            "description": "Crime statistics, safety ratings, police presence",
            "sources": ["illinois_ucr", "chicago_crime", "uchicago_crime_lab"]
        },
        "education": {
            "name": "Education Quality",
            "description": "School ratings, test scores, educational resources",
            "sources": ["illinois_report_card", "greatschools_illinois"]
        },
        "housing": {
            "name": "Housing & Development",
            "description": "Housing market data, development projects, affordability",
            "sources": ["cmap_housing", "ihda", "depaul_housing_studies"]
        },
        "employment": {
            "name": "Employment & Economy",
            "description": "Job market, unemployment rates, economic indicators",
            "sources": ["ides", "dceo"]
        },
        "transportation": {
            "name": "Transportation",
            "description": "Public transit, walkability, commute times",
            "sources": ["idot_transit", "cta", "metra"]
        },
        "infrastructure": {
            "name": "Infrastructure",
            "description": "Roads, utilities, walkability scores",
            "sources": ["cmap_walkability"]
        },
        "healthcare": {
            "name": "Healthcare Access",
            "description": "Hospital quality, healthcare facility access",
            "sources": ["illinois_hospital_report"]
        },
        "recreation": {
            "name": "Parks & Recreation",
            "description": "Parks, recreational facilities, outdoor activities",
            "sources": ["illinois_dnr", "chicago_parks"]
        },
        "amenities": {
            "name": "Shopping & Amenities",
            "description": "Shopping centers, restaurants, entertainment",
            "sources": ["enjoy_illinois"]
        },
        "community": {
            "name": "Community Investment",
            "description": "Community programs, local investments",
            "sources": ["nici"]
        },
        "environment": {
            "name": "Environmental Quality",
            "description": "Air quality, noise pollution, environmental health",
            "sources": ["illinois_epa", "wbez_environment"]
        },
        "demographics": {
            "name": "Demographics & Diversity",
            "description": "Population demographics, diversity indices",
            "sources": ["cmap_census", "illinois_extension"]
        },
        "market": {
            "name": "Real Estate Market",
            "description": "Market trends, property values, sales data",
            "sources": ["illinois_realtors"]
        }
    }
    
    return {
        "categories": categories,
        "total_categories": len(categories)
    }

def _generate_data_summary(comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a summary of the comprehensive data"""
    
    summary = {
        "total_sources": len(comprehensive_data),
        "successful_fetches": 0,
        "failed_fetches": 0,
        "categories_covered": set(),
        "data_quality": "good"
    }
    
    for source_key, source_data in comprehensive_data.items():
        if source_data.get("error"):
            summary["failed_fetches"] += 1
        else:
            summary["successful_fetches"] += 1
            if "category" in source_data:
                summary["categories_covered"].add(source_data["category"])
    
    summary["categories_covered"] = list(summary["categories_covered"])
    
    # Determine data quality
    success_rate = summary["successful_fetches"] / summary["total_sources"] if summary["total_sources"] > 0 else 0
    if success_rate >= 0.8:
        summary["data_quality"] = "excellent"
    elif success_rate >= 0.6:
        summary["data_quality"] = "good"
    elif success_rate >= 0.4:
        summary["data_quality"] = "fair"
    else:
        summary["data_quality"] = "poor"
    
    return summary

def _generate_category_summary(category_data: Dict[str, Any], category: str) -> Dict[str, Any]:
    """Generate a summary for category-specific data"""
    
    summary = {
        "category": category,
        "sources_available": len(category_data),
        "successful_fetches": 0,
        "failed_fetches": 0,
        "data_points": 0
    }
    
    for source_key, source_data in category_data.items():
        if source_data.get("error"):
            summary["failed_fetches"] += 1
        else:
            summary["successful_fetches"] += 1
            # Count data points if available
            if isinstance(source_data.get("data"), list):
                summary["data_points"] += len(source_data["data"])
            elif isinstance(source_data.get("data"), dict):
                summary["data_points"] += len(source_data["data"])
    
    return summary
