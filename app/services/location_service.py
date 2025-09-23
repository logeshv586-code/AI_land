from typing import Optional, Tuple
from sqlalchemy.orm import Session
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from loguru import logger

from app.models import Location

class LocationService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="land_analysis_ai")
    
    async def get_or_create_location(
        self, 
        db: Session, 
        address: Optional[str] = None, 
        latitude: Optional[float] = None, 
        longitude: Optional[float] = None
    ) -> Location:
        """
        Get existing location or create new one from address or coordinates
        """
        
        # If coordinates provided, try to find existing location
        if latitude and longitude:
            existing = self.find_nearby_location(db, latitude, longitude)
            if existing:
                return existing
        
        # If address provided, geocode it
        if address and not (latitude and longitude):
            try:
                geocoded = await self.geocode_address(address)
                if geocoded:
                    latitude, longitude = geocoded
                else:
                    raise ValueError(f"Could not geocode address: {address}")
            except Exception as e:
                logger.error(f"Geocoding failed for address '{address}': {str(e)}")
                raise ValueError(f"Geocoding failed: {str(e)}")
        
        # If still no coordinates, raise error
        if not latitude or not longitude:
            raise ValueError("Either address or coordinates must be provided")
        
        # Check again for existing location with the geocoded coordinates
        existing = self.find_nearby_location(db, latitude, longitude)
        if existing:
            return existing
        
        # Create new location
        location_data = await self.get_location_details(latitude, longitude, address)
        
        location = Location(
            address=location_data['address'],
            city=location_data['city'],
            state=location_data['state'],
            country=location_data['country'],
            postal_code=location_data.get('postal_code'),
            latitude=latitude,
            longitude=longitude,
            district=location_data.get('district'),
            neighborhood=location_data.get('neighborhood')
        )
        
        db.add(location)
        db.commit()
        db.refresh(location)
        
        logger.info(f"Created new location: {location.address}")
        return location
    
    def find_nearby_location(self, db: Session, latitude: float, longitude: float, radius_km: float = 1.0) -> Optional[Location]:
        """
        Find existing location within specified radius
        """
        # Simple distance calculation (for more accuracy, use PostGIS or similar)
        # This is a rough approximation: 1 degree ≈ 111 km
        lat_range = radius_km / 111.0
        lon_range = radius_km / (111.0 * abs(latitude) / 90.0) if latitude != 0 else radius_km / 111.0
        
        existing = db.query(Location).filter(
            Location.latitude.between(latitude - lat_range, latitude + lat_range),
            Location.longitude.between(longitude - lon_range, longitude + lon_range)
        ).first()
        
        return existing
    
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates using geocoding service
        """
        try:
            location = self.geolocator.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
            return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding service error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected geocoding error: {str(e)}")
            return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[dict]:
        """
        Convert coordinates to address information
        """
        try:
            location = self.geolocator.reverse((latitude, longitude), timeout=10)
            if location and location.raw:
                return location.raw.get('address', {})
            return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Reverse geocoding service error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected reverse geocoding error: {str(e)}")
            return None
    
    async def get_location_details(self, latitude: float, longitude: float, provided_address: Optional[str] = None) -> dict:
        """
        Get detailed location information from coordinates
        """
        location_data = {
            'address': provided_address or f"{latitude}, {longitude}",
            'city': '',
            'state': '',
            'country': '',
            'postal_code': None,
            'district': None,
            'neighborhood': None
        }
        
        try:
            # Try reverse geocoding to get detailed address info
            address_info = await self.reverse_geocode(latitude, longitude)
            
            if address_info:
                location_data.update({
                    'address': provided_address or self.format_address(address_info),
                    'city': address_info.get('city') or address_info.get('town') or address_info.get('village', ''),
                    'state': address_info.get('state') or address_info.get('province', ''),
                    'country': address_info.get('country', ''),
                    'postal_code': address_info.get('postcode'),
                    'district': address_info.get('county') or address_info.get('district'),
                    'neighborhood': address_info.get('neighbourhood') or address_info.get('suburb')
                })
        
        except Exception as e:
            logger.warning(f"Could not get detailed location info: {str(e)}")
        
        return location_data
    
    def format_address(self, address_info: dict) -> str:
        """
        Format address components into a readable address string
        """
        components = []
        
        # Add house number and street
        house_number = address_info.get('house_number', '')
        road = address_info.get('road', '')
        if house_number and road:
            components.append(f"{house_number} {road}")
        elif road:
            components.append(road)
        
        # Add city
        city = address_info.get('city') or address_info.get('town') or address_info.get('village')
        if city:
            components.append(city)
        
        # Add state
        state = address_info.get('state') or address_info.get('province')
        if state:
            components.append(state)
        
        # Add postal code
        postcode = address_info.get('postcode')
        if postcode:
            components.append(postcode)
        
        # Add country
        country = address_info.get('country')
        if country:
            components.append(country)
        
        return ', '.join(filter(None, components))
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate that coordinates are within valid ranges
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    async def get_location_by_id(self, db: Session, location_id: int) -> Optional[Location]:
        """
        Get location by ID
        """
        return db.query(Location).filter(Location.id == location_id).first()
    
    async def search_locations(self, db: Session, query: str, limit: int = 10) -> list[Location]:
        """
        Search locations by address, city, or other fields
        """
        locations = db.query(Location).filter(
            Location.address.ilike(f"%{query}%") |
            Location.city.ilike(f"%{query}%") |
            Location.state.ilike(f"%{query}%")
        ).limit(limit).all()
        
        return locations
    
    async def get_locations_in_radius(self, db: Session, center_lat: float, center_lon: float, radius_km: float) -> list[Location]:
        """
        Get all locations within specified radius of center point
        """
        # Simple bounding box calculation
        lat_range = radius_km / 111.0
        lon_range = radius_km / (111.0 * abs(center_lat) / 90.0) if center_lat != 0 else radius_km / 111.0
        
        locations = db.query(Location).filter(
            Location.latitude.between(center_lat - lat_range, center_lat + lat_range),
            Location.longitude.between(center_lon - lon_range, center_lon + lon_range)
        ).all()
        
        # Filter by actual distance (more accurate)
        from geopy.distance import geodesic
        filtered_locations = []
        
        for location in locations:
            if location.latitude and location.longitude:
                distance = geodesic(
                    (center_lat, center_lon),
                    (location.latitude, location.longitude)
                ).kilometers
                
                if distance <= radius_km:
                    filtered_locations.append(location)
        
        return filtered_locations
    
    async def update_location_info(self, db: Session, location_id: int) -> Optional[Location]:
        """
        Update location information with fresh geocoding data
        """
        location = await self.get_location_by_id(db, location_id)
        if not location or not location.latitude or not location.longitude:
            return None
        
        try:
            # Get fresh location details
            updated_data = await self.get_location_details(
                location.latitude, location.longitude
            )
            
            # Update location fields
            location.city = updated_data['city']
            location.state = updated_data['state']
            location.country = updated_data['country']
            location.postal_code = updated_data.get('postal_code')
            location.district = updated_data.get('district')
            location.neighborhood = updated_data.get('neighborhood')
            
            db.commit()
            db.refresh(location)
            
            logger.info(f"Updated location info for location {location_id}")
            return location
        
        except Exception as e:
            logger.error(f"Failed to update location {location_id}: {str(e)}")
            db.rollback()
            return None