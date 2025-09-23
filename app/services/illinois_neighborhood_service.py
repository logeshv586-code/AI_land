"""
Illinois Neighborhood Quality Assessment Service

This service integrates with Illinois-specific data sources to assess
the 15 neighborhood quality factors for real estate evaluation.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import Location, PropertyListing
from app.schemas import NeighborhoodQualityFactors, NeighborhoodQualityResponse
from app.core.config import settings
from app.services.illinois_data_integration import IllinoisDataIntegration

logger = logging.getLogger(__name__)

class IllinoisNeighborhoodService:
    """Service for assessing Illinois neighborhood quality factors"""
    
    def __init__(self):
        # Initialize the comprehensive data integration service
        self.data_integration = IllinoisDataIntegration()

        self.data_sources = {
            "safety_crime_rate": "https://ilucr.nibrs.com/",
            "schools_education_quality": "https://www.illinoisreportcard.com/",
            "cleanliness_sanitation": "https://www.chicago.gov/city/en/depts/streets/provdrs/streets_san.html",
            "housing_quality_affordability": "https://www.ihda.org/",
            "access_jobs_economy": "https://ides.illinois.gov/resources/labor-market-information.html",
            "public_transport_connectivity": "https://idot.illinois.gov/transportation-system/network-overview/transit-system.html",
            "walkability_infrastructure": "https://cmap.illinois.gov/wp-content/uploads/Non-motorized-transportation-report.pdf",
            "healthcare_access": "https://healthcarereportcard.illinois.gov/",
            "parks_green_spaces": "https://dnr.illinois.gov/parks.html",
            "shopping_amenities": "https://www.enjoyillinois.com/things-to-do/shopping/",
            "community_engagement": "https://www.nici-il.org/community-engagement",
            "noise_environment": "https://epa.illinois.gov/pollution-complaint/noise.html",
            "diversity_inclusivity": "https://cmap.illinois.gov/news-updates/2020-census-reveals-slow-population-growth-increased-diversity-in-northeastern-illinois/",
            "future_development_property_values": "https://www.illinoisrealtors.org/marketstats/",
            "neighbors_behavior": "https://www.naperville.il.us/services/naperville-police-department/community-education-and-crime-prevention/neighborhood-watch/"
        }
        
        # Cache for neighborhood assessments (24 hour TTL)
        self._cache = {}
        self._cache_ttl = timedelta(hours=24)
    
    async def assess_neighborhood_quality(
        self, 
        location: Location, 
        db: Session
    ) -> NeighborhoodQualityResponse:
        """
        Assess all 15 neighborhood quality factors for a given location
        """
        cache_key = f"{location.latitude}_{location.longitude}"
        
        # Check cache first
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.utcnow() - timestamp < self._cache_ttl:
                return cached_data
        
        try:
            # Assess all factors concurrently
            factors = await self._assess_all_factors(location, db)
            
            # Calculate overall score (weighted average)
            overall_score = self._calculate_overall_score(factors)
            
            response = NeighborhoodQualityResponse(
                overall_score=overall_score,
                factors=factors,
                data_sources=self.data_sources,
                last_updated=datetime.utcnow()
            )
            
            # Cache the result
            self._cache[cache_key] = (response, datetime.utcnow())
            
            return response
            
        except Exception as e:
            logger.error(f"Error assessing neighborhood quality: {str(e)}")
            # Return default scores if assessment fails
            return self._get_default_assessment()
    
    async def _assess_all_factors(
        self, 
        location: Location, 
        db: Session
    ) -> NeighborhoodQualityFactors:
        """Assess all 15 neighborhood quality factors"""
        
        # Run all assessments concurrently
        tasks = [
            self._assess_safety_crime_rate(location, db),
            self._assess_schools_education_quality(location, db),
            self._assess_cleanliness_sanitation(location, db),
            self._assess_housing_quality_affordability(location, db),
            self._assess_access_jobs_economy(location, db),
            self._assess_public_transport_connectivity(location, db),
            self._assess_walkability_infrastructure(location, db),
            self._assess_healthcare_access(location, db),
            self._assess_parks_green_spaces(location, db),
            self._assess_shopping_amenities(location, db),
            self._assess_community_engagement(location, db),
            self._assess_noise_environment(location, db),
            self._assess_diversity_inclusivity(location, db),
            self._assess_future_development_property_values(location, db),
            self._assess_neighbors_behavior(location, db)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions and provide default scores
        scores = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Factor assessment {i} failed: {str(result)}")
                scores.append(50.0)  # Default neutral score
            else:
                scores.append(result)
        
        return NeighborhoodQualityFactors(
            safety_crime_rate=scores[0],
            schools_education_quality=scores[1],
            cleanliness_sanitation=scores[2],
            housing_quality_affordability=scores[3],
            access_jobs_economy=scores[4],
            public_transport_connectivity=scores[5],
            walkability_infrastructure=scores[6],
            healthcare_access=scores[7],
            parks_green_spaces=scores[8],
            shopping_amenities=scores[9],
            community_engagement=scores[10],
            noise_environment=scores[11],
            diversity_inclusivity=scores[12],
            future_development_property_values=scores[13],
            neighbors_behavior=scores[14]
        )
    
    def _calculate_overall_score(self, factors: NeighborhoodQualityFactors) -> float:
        """Calculate weighted overall neighborhood quality score"""
        
        # Define weights for each factor (total should equal 1.0)
        weights = {
            'safety_crime_rate': 0.15,
            'schools_education_quality': 0.12,
            'housing_quality_affordability': 0.10,
            'access_jobs_economy': 0.08,
            'public_transport_connectivity': 0.08,
            'walkability_infrastructure': 0.07,
            'healthcare_access': 0.07,
            'parks_green_spaces': 0.06,
            'shopping_amenities': 0.06,
            'cleanliness_sanitation': 0.05,
            'community_engagement': 0.05,
            'future_development_property_values': 0.04,
            'noise_environment': 0.03,
            'diversity_inclusivity': 0.02,
            'neighbors_behavior': 0.02
        }
        
        weighted_sum = 0.0
        for factor_name, weight in weights.items():
            factor_value = getattr(factors, factor_name)
            weighted_sum += factor_value * weight
        
        return round(weighted_sum, 2)
    
    async def _assess_safety_crime_rate(self, location: Location, db: Session) -> float:
        """Assess safety and crime rate (0-100, higher is better)"""
        try:
            # In a real implementation, this would query Illinois UCR data
            # For now, we'll use a mock assessment based on location
            
            # Mock logic: Urban areas might have higher crime, suburban areas lower
            if location.city and location.city.lower() in ['chicago']:
                base_score = 60.0
            elif location.city and 'suburb' in location.city.lower():
                base_score = 80.0
            else:
                base_score = 70.0
            
            # Add some variation based on coordinates
            if location.latitude and location.longitude:
                coord_factor = (abs(location.latitude) + abs(location.longitude)) % 20
                base_score += coord_factor - 10
            
            return max(0.0, min(100.0, base_score))
            
        except Exception as e:
            logger.error(f"Error assessing safety/crime rate: {str(e)}")
            return 50.0
    
    async def _assess_schools_education_quality(self, location: Location, db: Session) -> float:
        """Assess schools and education quality (0-100, higher is better)"""
        try:
            # Mock assessment - in reality would query Illinois Report Card API
            base_score = 75.0
            
            # Suburban areas typically have better schools
            if location.city and any(suburb in location.city.lower() for suburb in ['naperville', 'schaumburg', 'evanston']):
                base_score = 90.0
            elif location.city and location.city.lower() == 'chicago':
                base_score = 65.0
            
            return max(0.0, min(100.0, base_score))
            
        except Exception as e:
            logger.error(f"Error assessing schools/education: {str(e)}")
            return 50.0
    
    async def _assess_cleanliness_sanitation(self, location: Location, db: Session) -> float:
        """Assess cleanliness and sanitation (0-100, higher is better)"""
        try:
            # Mock assessment
            base_score = 70.0
            
            # Newer developments and suburbs tend to be cleaner
            if location.city and any(clean_area in location.city.lower() for clean_area in ['naperville', 'oak brook']):
                base_score = 85.0
            
            return max(0.0, min(100.0, base_score))
            
        except Exception as e:
            logger.error(f"Error assessing cleanliness/sanitation: {str(e)}")
            return 50.0
    
    async def _assess_housing_quality_affordability(self, location: Location, db: Session) -> float:
        """Assess housing quality and affordability (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with IHDA data
            base_score = 65.0
            
            # Balance quality vs affordability
            if location.city:
                if location.city.lower() in ['chicago']:
                    base_score = 60.0  # High quality but expensive
                elif 'suburb' in location.city.lower():
                    base_score = 75.0  # Good balance
            
            return max(0.0, min(100.0, base_score))
            
        except Exception as e:
            logger.error(f"Error assessing housing quality/affordability: {str(e)}")
            return 50.0
    
    def _get_default_assessment(self) -> NeighborhoodQualityResponse:
        """Return default assessment when data is unavailable"""
        factors = NeighborhoodQualityFactors(
            safety_crime_rate=50.0,
            schools_education_quality=50.0,
            cleanliness_sanitation=50.0,
            housing_quality_affordability=50.0,
            access_jobs_economy=50.0,
            public_transport_connectivity=50.0,
            walkability_infrastructure=50.0,
            healthcare_access=50.0,
            parks_green_spaces=50.0,
            shopping_amenities=50.0,
            community_engagement=50.0,
            noise_environment=50.0,
            diversity_inclusivity=50.0,
            future_development_property_values=50.0,
            neighbors_behavior=50.0
        )
        
        return NeighborhoodQualityResponse(
            overall_score=50.0,
            factors=factors,
            data_sources=self.data_sources,
            last_updated=datetime.utcnow()
        )
    
    async def _assess_access_jobs_economy(self, location: Location, db: Session) -> float:
        """Assess access to jobs and economic opportunities (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with IDES labor market data
            base_score = 70.0

            # Chicago and suburbs have better job access
            if location.city:
                if location.city.lower() == 'chicago':
                    base_score = 85.0  # Major employment hub
                elif any(suburb in location.city.lower() for suburb in ['schaumburg', 'naperville', 'oak brook']):
                    base_score = 80.0  # Corporate suburbs
                elif 'rural' in location.city.lower():
                    base_score = 45.0  # Limited job opportunities

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing jobs/economy access: {str(e)}")
            return 50.0

    async def _assess_public_transport_connectivity(self, location: Location, db: Session) -> float:
        """Assess public transportation connectivity (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with CTA, Metra, Pace data
            base_score = 65.0

            if location.city:
                if location.city.lower() == 'chicago':
                    base_score = 90.0  # Excellent CTA coverage
                elif any(suburb in location.city.lower() for suburb in ['evanston', 'oak park']):
                    base_score = 85.0  # Good CTA/Metra access
                elif 'suburb' in location.city.lower():
                    base_score = 60.0  # Limited to Metra/Pace
                else:
                    base_score = 30.0  # Rural areas with limited transit

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing public transport: {str(e)}")
            return 50.0

    async def _assess_walkability_infrastructure(self, location: Location, db: Session) -> float:
        """Assess walkability and infrastructure (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with CMAP walkability data
            base_score = 60.0

            if location.city:
                if location.city.lower() in ['chicago', 'evanston']:
                    base_score = 85.0  # Dense, walkable areas
                elif any(suburb in location.city.lower() for suburb in ['naperville', 'schaumburg']):
                    base_score = 70.0  # Planned communities with sidewalks
                elif 'rural' in location.city.lower():
                    base_score = 35.0  # Limited pedestrian infrastructure

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing walkability: {str(e)}")
            return 50.0

    async def _assess_healthcare_access(self, location: Location, db: Session) -> float:
        """Assess healthcare access (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with Illinois Hospital Report Card
            base_score = 75.0

            if location.city:
                if location.city.lower() == 'chicago':
                    base_score = 95.0  # Major medical centers
                elif any(suburb in location.city.lower() for suburb in ['evanston', 'oak park']):
                    base_score = 85.0  # Good hospital access
                elif 'rural' in location.city.lower():
                    base_score = 50.0  # Limited healthcare facilities

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing healthcare access: {str(e)}")
            return 50.0

    async def _assess_parks_green_spaces(self, location: Location, db: Session) -> float:
        """Assess parks and green spaces (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with Illinois DNR and Chicago Parks data
            base_score = 70.0

            if location.city:
                if location.city.lower() == 'chicago':
                    base_score = 80.0  # Extensive park system
                elif any(suburb in location.city.lower() for suburb in ['naperville', 'schaumburg']):
                    base_score = 85.0  # Well-planned green spaces
                elif 'rural' in location.city.lower():
                    base_score = 90.0  # Natural areas and open space

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing parks/green spaces: {str(e)}")
            return 50.0

    async def _assess_shopping_amenities(self, location: Location, db: Session) -> float:
        """Assess shopping and amenities (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with retail location data
            base_score = 65.0

            if location.city:
                if location.city.lower() == 'chicago':
                    base_score = 90.0  # Magnificent Mile and diverse shopping
                elif any(suburb in location.city.lower() for suburb in ['schaumburg', 'oak brook']):
                    base_score = 85.0  # Major shopping centers
                elif 'rural' in location.city.lower():
                    base_score = 40.0  # Limited shopping options

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing shopping/amenities: {str(e)}")
            return 50.0

    async def _assess_community_engagement(self, location: Location, db: Session) -> float:
        """Assess community engagement (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with community organization data
            base_score = 60.0

            # Suburban communities often have higher engagement
            if location.city and any(suburb in location.city.lower() for suburb in ['naperville', 'evanston']):
                base_score = 80.0
            elif location.city and location.city.lower() == 'chicago':
                base_score = 70.0  # Varies by neighborhood

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing community engagement: {str(e)}")
            return 50.0

    async def _assess_noise_environment(self, location: Location, db: Session) -> float:
        """Assess noise and environmental quality (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with EPA noise data
            base_score = 70.0

            if location.city:
                if location.city.lower() == 'chicago':
                    base_score = 55.0  # Urban noise issues
                elif 'suburb' in location.city.lower():
                    base_score = 80.0  # Quieter residential areas
                elif 'rural' in location.city.lower():
                    base_score = 90.0  # Very quiet

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing noise/environment: {str(e)}")
            return 50.0

    async def _assess_diversity_inclusivity(self, location: Location, db: Session) -> float:
        """Assess diversity and inclusivity (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with census diversity data
            base_score = 75.0

            if location.city:
                if location.city.lower() == 'chicago':
                    base_score = 90.0  # Very diverse
                elif any(suburb in location.city.lower() for suburb in ['evanston', 'oak park']):
                    base_score = 85.0  # Historically diverse suburbs

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing diversity/inclusivity: {str(e)}")
            return 50.0

    async def _assess_future_development_property_values(self, location: Location, db: Session) -> float:
        """Assess future development and property value trends (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with Illinois REALTORS market data
            base_score = 65.0

            if location.city:
                if any(growth_area in location.city.lower() for growth_area in ['naperville', 'schaumburg']):
                    base_score = 80.0  # Strong growth areas
                elif location.city.lower() == 'chicago':
                    base_score = 70.0  # Mixed, depends on neighborhood

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing future development: {str(e)}")
            return 50.0

    async def _assess_neighbors_behavior(self, location: Location, db: Session) -> float:
        """Assess neighbors' behavior and community cohesion (0-100, higher is better)"""
        try:
            # Mock assessment - would integrate with neighborhood watch and community data
            base_score = 70.0

            # Suburban areas often have better neighbor relations
            if location.city and any(suburb in location.city.lower() for suburb in ['naperville', 'schaumburg']):
                base_score = 80.0

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Error assessing neighbors' behavior: {str(e)}")
            return 50.0
