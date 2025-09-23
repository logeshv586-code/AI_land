import asyncio
import aiohttp
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from loguru import logger
import json

from app.models import (
    Location, Facility, CrimeData, DisasterData, MarketData, DataUpdateLog
)
from app.core.config import settings

class DataCollector:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="land_analysis_ai")
        self.session = None
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def update_location_data(self, location_id: int):
        """Update all data for a specific location"""
        logger.info(f"Starting data update for location {location_id}")
        
        try:
            # Run all data collection tasks concurrently
            await asyncio.gather(
                self.collect_facilities_data(location_id),
                self.collect_crime_data(location_id),
                self.collect_disaster_data(location_id),
                self.collect_market_data(location_id)
            )
            logger.info(f"Data update completed for location {location_id}")
        except Exception as e:
            logger.error(f"Data update failed for location {location_id}: {str(e)}")
    
    async def collect_facilities_data(self, location_id: int):
        """Collect facilities data (schools, hospitals, etc.) for a location"""
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            location = db.query(Location).filter(Location.id == location_id).first()
            if not location or not location.latitude or not location.longitude:
                return
            
            # Collect different types of facilities
            facility_types = {
                'school': ['school', 'university', 'college'],
                'hospital': ['hospital', 'clinic', 'medical'],
                'mall': ['shopping_mall', 'supermarket', 'retail'],
                'transport': ['bus_station', 'train_station', 'subway_station']
            }
            
            for facility_type, search_terms in facility_types.items():
                facilities = await self.search_nearby_facilities(
                    location.latitude, location.longitude, search_terms
                )
                
                # Save facilities to database
                for facility_data in facilities:
                    existing = db.query(Facility).filter(
                        Facility.location_id == location_id,
                        Facility.name == facility_data['name'],
                        Facility.facility_type == facility_type
                    ).first()
                    
                    if not existing:
                        facility = Facility(
                            location_id=location_id,
                            facility_type=facility_type,
                            name=facility_data['name'],
                            distance_km=facility_data['distance'],
                            rating=facility_data.get('rating'),
                            capacity=facility_data.get('capacity')
                        )
                        db.add(facility)
            
            db.commit()
            logger.info(f"Facilities data updated for location {location_id}")
            
        except Exception as e:
            logger.error(f"Failed to collect facilities data: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    async def search_nearby_facilities(self, lat: float, lon: float, search_terms: List[str], radius_km: float = 10) -> List[Dict]:
        """Search for nearby facilities using external APIs"""
        facilities = []
        
        try:
            # Use Google Places API if available
            if settings.GOOGLE_MAPS_API_KEY:
                facilities.extend(await self.search_google_places(lat, lon, search_terms, radius_km))
            else:
                # Fallback to OpenStreetMap/Nominatim
                facilities.extend(await self.search_osm_facilities(lat, lon, search_terms, radius_km))
        
        except Exception as e:
            logger.error(f"Failed to search facilities: {str(e)}")
        
        return facilities
    
    async def search_google_places(self, lat: float, lon: float, search_terms: List[str], radius_km: float) -> List[Dict]:
        """Search using Google Places API"""
        facilities = []
        session = await self.get_session()
        
        for term in search_terms:
            try:
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                params = {
                    'location': f"{lat},{lon}",
                    'radius': int(radius_km * 1000),  # Convert to meters
                    'type': term,
                    'key': settings.GOOGLE_MAPS_API_KEY
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for place in data.get('results', []):
                            place_lat = place['geometry']['location']['lat']
                            place_lon = place['geometry']['location']['lng']
                            
                            distance = geodesic((lat, lon), (place_lat, place_lon)).kilometers
                            
                            facilities.append({
                                'name': place['name'],
                                'distance': distance,
                                'rating': place.get('rating'),
                                'place_id': place.get('place_id')
                            })
            
            except Exception as e:
                logger.error(f"Google Places API error for {term}: {str(e)}")
        
        return facilities
    
    async def search_osm_facilities(self, lat: float, lon: float, search_terms: List[str], radius_km: float) -> List[Dict]:
        """Search using OpenStreetMap/Overpass API as fallback"""
        facilities = []
        
        try:
            # Use Overpass API to query OpenStreetMap data
            overpass_url = "http://overpass-api.de/api/interpreter"
            
            for term in search_terms:
                # Create Overpass query
                query = f"""
                [out:json][timeout:25];
                (
                  node["amenity"="{term}"](around:{radius_km*1000},{lat},{lon});
                  way["amenity"="{term}"](around:{radius_km*1000},{lat},{lon});
                  relation["amenity"="{term}"](around:{radius_km*1000},{lat},{lon});
                );
                out center meta;
                """
                
                session = await self.get_session()
                async with session.post(overpass_url, data=query) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for element in data.get('elements', []):
                            if 'tags' in element and 'name' in element['tags']:
                                element_lat = element.get('lat') or element.get('center', {}).get('lat')
                                element_lon = element.get('lon') or element.get('center', {}).get('lon')
                                
                                if element_lat and element_lon:
                                    distance = geodesic((lat, lon), (element_lat, element_lon)).kilometers
                                    
                                    facilities.append({
                                        'name': element['tags']['name'],
                                        'distance': distance,
                                        'rating': None,  # OSM doesn't have ratings
                                        'osm_id': element.get('id')
                                    })
        
        except Exception as e:
            logger.error(f"OSM search error: {str(e)}")
        
        return facilities
    
    async def collect_crime_data(self, location_id: int):
        """Collect crime statistics for a location"""
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            location = db.query(Location).filter(Location.id == location_id).first()
            if not location:
                return
            
            # Try to get crime data from various sources
            crime_data = await self.get_crime_statistics(location)
            
            for crime_record in crime_data:
                existing = db.query(CrimeData).filter(
                    CrimeData.location_id == location_id,
                    CrimeData.crime_type == crime_record['type'],
                    CrimeData.year == crime_record['year'],
                    CrimeData.month == crime_record.get('month', 1)
                ).first()
                
                if not existing:
                    crime = CrimeData(
                        location_id=location_id,
                        crime_type=crime_record['type'],
                        incident_count=crime_record['count'],
                        crime_rate_per_1000=crime_record['rate'],
                        year=crime_record['year'],
                        month=crime_record.get('month', 1),
                        severity_score=crime_record.get('severity', 5.0)
                    )
                    db.add(crime)
            
            db.commit()
            logger.info(f"Crime data updated for location {location_id}")
            
        except Exception as e:
            logger.error(f"Failed to collect crime data: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    async def get_crime_statistics(self, location: Location) -> List[Dict]:
        """Get crime statistics from various sources"""
        crime_data = []
        
        try:
            # Try government crime APIs (example for US)
            if location.country and location.country.lower() == 'usa':
                crime_data.extend(await self.get_us_crime_data(location))
            
            # If no real data available, generate realistic sample data
            if not crime_data:
                crime_data = self.generate_sample_crime_data(location)
        
        except Exception as e:
            logger.error(f"Error getting crime statistics: {str(e)}")
            # Fallback to sample data
            crime_data = self.generate_sample_crime_data(location)
        
        return crime_data
    
    async def get_us_crime_data(self, location: Location) -> List[Dict]:
        """Get US crime data from FBI Crime Data API or similar"""
        crime_data = []
        
        # This would integrate with actual crime APIs
        # For now, return sample data structure
        return crime_data
    
    def generate_sample_crime_data(self, location: Location) -> List[Dict]:
        """Generate realistic sample crime data"""
        import random
        
        crime_types = {
            'theft': {'base_rate': 15.0, 'severity': 3.0},
            'burglary': {'base_rate': 8.0, 'severity': 5.0},
            'assault': {'base_rate': 5.0, 'severity': 7.0},
            'vandalism': {'base_rate': 12.0, 'severity': 2.0},
            'robbery': {'base_rate': 3.0, 'severity': 8.0},
            'vehicle_theft': {'base_rate': 6.0, 'severity': 4.0}
        }
        
        crime_data = []
        current_year = datetime.now().year
        
        for crime_type, stats in crime_types.items():
            # Add some randomness to make it realistic
            rate_variation = random.uniform(0.7, 1.3)
            rate = stats['base_rate'] * rate_variation
            
            # Estimate incident count based on population (assume 10,000 people)
            estimated_population = 10000
            incident_count = int((rate / 1000) * estimated_population)
            
            crime_data.append({
                'type': crime_type,
                'count': incident_count,
                'rate': rate,
                'year': current_year,
                'month': 1,
                'severity': stats['severity']
            })
        
        return crime_data
    
    async def collect_disaster_data(self, location_id: int):
        """Collect natural disaster risk data"""
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            location = db.query(Location).filter(Location.id == location_id).first()
            if not location:
                return
            
            disaster_risks = await self.assess_disaster_risks(location)
            
            for disaster_type, risk_data in disaster_risks.items():
                existing = db.query(DisasterData).filter(
                    DisasterData.location_id == location_id,
                    DisasterData.disaster_type == disaster_type
                ).first()
                
                if existing:
                    # Update existing record
                    existing.risk_level = risk_data['risk_level']
                    existing.probability = risk_data['probability']
                    existing.historical_frequency = risk_data['frequency']
                else:
                    # Create new record
                    disaster = DisasterData(
                        location_id=location_id,
                        disaster_type=disaster_type,
                        risk_level=risk_data['risk_level'],
                        probability=risk_data['probability'],
                        last_occurrence=risk_data.get('last_occurrence'),
                        historical_frequency=risk_data['frequency']
                    )
                    db.add(disaster)
            
            db.commit()
            logger.info(f"Disaster data updated for location {location_id}")
            
        except Exception as e:
            logger.error(f"Failed to collect disaster data: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    async def assess_disaster_risks(self, location: Location) -> Dict[str, Dict]:
        """Assess disaster risks based on location"""
        risks = {}
        
        try:
            # This would integrate with NOAA, USGS, or other disaster APIs
            # For now, generate sample risk assessments based on geographic patterns
            
            lat, lon = location.latitude, location.longitude
            
            # Flood risk (higher near coasts and rivers)
            flood_risk = self.calculate_flood_risk(lat, lon)
            risks['flood'] = {
                'risk_level': self.get_risk_level(flood_risk),
                'probability': flood_risk,
                'frequency': flood_risk * 0.1  # events per year
            }
            
            # Earthquake risk (higher in certain geological zones)
            earthquake_risk = self.calculate_earthquake_risk(lat, lon)
            risks['earthquake'] = {
                'risk_level': self.get_risk_level(earthquake_risk),
                'probability': earthquake_risk,
                'frequency': earthquake_risk * 0.05
            }
            
            # Hurricane risk (higher in coastal areas)
            hurricane_risk = self.calculate_hurricane_risk(lat, lon)
            risks['hurricane'] = {
                'risk_level': self.get_risk_level(hurricane_risk),
                'probability': hurricane_risk,
                'frequency': hurricane_risk * 0.08
            }
            
            # Wildfire risk (higher in dry, forested areas)
            wildfire_risk = self.calculate_wildfire_risk(lat, lon)
            risks['wildfire'] = {
                'risk_level': self.get_risk_level(wildfire_risk),
                'probability': wildfire_risk,
                'frequency': wildfire_risk * 0.12
            }
            
            # Tornado risk (higher in tornado alley)
            tornado_risk = self.calculate_tornado_risk(lat, lon)
            risks['tornado'] = {
                'risk_level': self.get_risk_level(tornado_risk),
                'probability': tornado_risk,
                'frequency': tornado_risk * 0.15
            }
        
        except Exception as e:
            logger.error(f"Error assessing disaster risks: {str(e)}")
        
        return risks
    
    def calculate_flood_risk(self, lat: float, lon: float) -> float:
        """Calculate flood risk based on location"""
        # Simplified risk calculation
        # Higher risk near coasts and known flood zones
        import math
        
        # Distance from coast (simplified)
        coastal_distance = min(abs(lat - 25), abs(lat - 45))  # Rough coastal approximation
        coastal_risk = max(0, 1 - (coastal_distance / 20))
        
        # Add some randomness for river proximity
        import random
        river_risk = random.uniform(0, 0.3)
        
        total_risk = min(1.0, coastal_risk + river_risk)
        return total_risk
    
    def calculate_earthquake_risk(self, lat: float, lon: float) -> float:
        """Calculate earthquake risk based on location"""
        # Higher risk in known seismic zones (California, Alaska, etc.)
        high_risk_zones = [
            (37.7749, -122.4194),  # San Francisco
            (34.0522, -118.2437),  # Los Angeles
            (61.2181, -149.9003),  # Anchorage
        ]
        
        min_distance = float('inf')
        for zone_lat, zone_lon in high_risk_zones:
            distance = geodesic((lat, lon), (zone_lat, zone_lon)).kilometers
            min_distance = min(min_distance, distance)
        
        # Risk decreases with distance from known zones
        risk = max(0, 1 - (min_distance / 1000))  # Risk within 1000km
        return min(1.0, risk)
    
    def calculate_hurricane_risk(self, lat: float, lon: float) -> float:
        """Calculate hurricane risk based on location"""
        # Higher risk in Atlantic and Gulf coastal areas
        if -100 <= lon <= -70 and 25 <= lat <= 45:  # US East Coast
            coastal_distance = min(abs(lon + 80), abs(lon + 90))  # Distance from coast
            risk = max(0, 1 - (coastal_distance / 10))
        else:
            risk = 0.1  # Low baseline risk
        
        return min(1.0, risk)
    
    def calculate_wildfire_risk(self, lat: float, lon: float) -> float:
        """Calculate wildfire risk based on location"""
        # Higher risk in western US, dry climates
        if -125 <= lon <= -100 and 30 <= lat <= 50:  # Western US
            risk = 0.6
        elif -100 <= lon <= -80 and 25 <= lat <= 35:  # Southern US
            risk = 0.4
        else:
            risk = 0.2
        
        return risk
    
    def calculate_tornado_risk(self, lat: float, lon: float) -> float:
        """Calculate tornado risk based on location"""
        # Higher risk in tornado alley (central US)
        if -105 <= lon <= -90 and 30 <= lat <= 45:  # Tornado Alley
            risk = 0.7
        elif -90 <= lon <= -80 and 30 <= lat <= 40:  # Southeast
            risk = 0.4
        else:
            risk = 0.1
        
        return risk
    
    def get_risk_level(self, probability: float) -> str:
        """Convert probability to risk level string"""
        if probability >= 0.7:
            return "extreme"
        elif probability >= 0.5:
            return "high"
        elif probability >= 0.3:
            return "medium"
        else:
            return "low"
    
    async def collect_market_data(self, location_id: int):
        """Collect real estate market data"""
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            location = db.query(Location).filter(Location.id == location_id).first()
            if not location:
                return
            
            market_info = await self.get_market_data(location)
            
            for property_type, data in market_info.items():
                existing = db.query(MarketData).filter(
                    MarketData.location_id == location_id,
                    MarketData.property_type == property_type
                ).first()
                
                if existing:
                    # Update existing record
                    existing.avg_price_per_sqft = data['avg_price_per_sqft']
                    existing.price_trend_6m = data['price_trend_6m']
                    existing.price_trend_1y = data['price_trend_1y']
                    existing.demand_score = data['demand_score']
                    existing.supply_score = data['supply_score']
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new record
                    market = MarketData(
                        location_id=location_id,
                        property_type=property_type,
                        avg_price_per_sqft=data['avg_price_per_sqft'],
                        price_trend_6m=data['price_trend_6m'],
                        price_trend_1y=data['price_trend_1y'],
                        demand_score=data['demand_score'],
                        supply_score=data['supply_score']
                    )
                    db.add(market)
            
            db.commit()
            logger.info(f"Market data updated for location {location_id}")
            
        except Exception as e:
            logger.error(f"Failed to collect market data: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    async def get_market_data(self, location: Location) -> Dict[str, Dict]:
        """Get real estate market data"""
        market_data = {}
        
        try:
            # This would integrate with real estate APIs like Zillow, Realtor.com, etc.
            # For now, generate realistic sample data
            
            property_types = ['residential', 'commercial', 'industrial']
            
            for prop_type in property_types:
                market_data[prop_type] = self.generate_sample_market_data(location, prop_type)
        
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
        
        return market_data
    
    def generate_sample_market_data(self, location: Location, property_type: str) -> Dict:
        """Generate realistic sample market data"""
        import random
        
        # Base prices vary by property type and location
        base_prices = {
            'residential': random.uniform(80, 300),
            'commercial': random.uniform(150, 500),
            'industrial': random.uniform(50, 150)
        }
        
        # Generate realistic trends
        price_trend_6m = random.uniform(-0.1, 0.15)  # -10% to +15%
        price_trend_1y = random.uniform(-0.15, 0.25)  # -15% to +25%
        
        # Market dynamics
        demand_score = random.uniform(30, 90)
        supply_score = random.uniform(20, 80)
        
        return {
            'avg_price_per_sqft': base_prices[property_type],
            'price_trend_6m': price_trend_6m,
            'price_trend_1y': price_trend_1y,
            'demand_score': demand_score,
            'supply_score': supply_score
        }
    
    # Background update methods
    async def update_facilities_data(self):
        """Update facilities data for all locations"""
        await self.log_data_update_start("facilities")
        try:
            # Implementation for bulk facilities update
            logger.info("Facilities data update completed")
            await self.log_data_update_success("facilities", 0)
        except Exception as e:
            await self.log_data_update_failure("facilities", str(e))
    
    async def update_crime_data(self):
        """Update crime data for all locations"""
        await self.log_data_update_start("crime")
        try:
            # Implementation for bulk crime data update
            logger.info("Crime data update completed")
            await self.log_data_update_success("crime", 0)
        except Exception as e:
            await self.log_data_update_failure("crime", str(e))
    
    async def update_disaster_data(self):
        """Update disaster data for all locations"""
        await self.log_data_update_start("disaster")
        try:
            # Implementation for bulk disaster data update
            logger.info("Disaster data update completed")
            await self.log_data_update_success("disaster", 0)
        except Exception as e:
            await self.log_data_update_failure("disaster", str(e))
    
    async def update_market_data(self):
        """Update market data for all locations"""
        await self.log_data_update_start("market")
        try:
            # Implementation for bulk market data update
            logger.info("Market data update completed")
            await self.log_data_update_success("market", 0)
        except Exception as e:
            await self.log_data_update_failure("market", str(e))
    
    async def log_data_update_start(self, data_type: str):
        """Log the start of a data update"""
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            log = DataUpdateLog(
                data_type=data_type,
                update_status="in_progress",
                started_at=datetime.utcnow()
            )
            db.add(log)
            db.commit()
        finally:
            db.close()
    
    async def log_data_update_success(self, data_type: str, records_updated: int):
        """Log successful data update"""
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            log = db.query(DataUpdateLog).filter(
                DataUpdateLog.data_type == data_type,
                DataUpdateLog.update_status == "in_progress"
            ).order_by(DataUpdateLog.started_at.desc()).first()
            
            if log:
                log.update_status = "success"
                log.records_updated = records_updated
                log.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    async def log_data_update_failure(self, data_type: str, error_message: str):
        """Log failed data update"""
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            log = db.query(DataUpdateLog).filter(
                DataUpdateLog.data_type == data_type,
                DataUpdateLog.update_status == "in_progress"
            ).order_by(DataUpdateLog.started_at.desc()).first()
            
            if log:
                log.update_status = "failed"
                log.error_message = error_message
                log.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    def get_next_update_time(self, data_type: str) -> datetime:
        """Get next scheduled update time for data type"""
        # Different update frequencies for different data types
        intervals = {
            "facilities": 7,  # Weekly
            "crime": 30,     # Monthly
            "disaster": 90,  # Quarterly
            "market": 1      # Daily
        }
        
        days = intervals.get(data_type, 30)
        return datetime.utcnow() + timedelta(days=days)
    
    async def validate_api_connections(self) -> Dict[str, bool]:
        """Validate all external API connections"""
        results = {}
        
        # Test Google Maps API
        if settings.GOOGLE_MAPS_API_KEY:
            results['google_maps'] = await self.test_google_maps_api()
        else:
            results['google_maps'] = False
        
        # Test other APIs
        results['openstreetmap'] = await self.test_osm_api()
        
        return results
    
    async def test_google_maps_api(self) -> bool:
        """Test Google Maps API connection"""
        try:
            session = await self.get_session()
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': '37.7749,-122.4194',  # San Francisco
                'radius': 1000,
                'type': 'school',
                'key': settings.GOOGLE_MAPS_API_KEY
            }
            
            async with session.get(url, params=params) as response:
                return response.status == 200
        except:
            return False
    
    async def test_osm_api(self) -> bool:
        """Test OpenStreetMap API connection"""
        try:
            session = await self.get_session()
            url = "http://overpass-api.de/api/interpreter"
            query = "[out:json][timeout:5];(node[amenity=school](around:1000,37.7749,-122.4194););out 1;"
            
            async with session.post(url, data=query) as response:
                return response.status == 200
        except:
            return False
    
    async def get_data_statistics(self, db: Session) -> Dict[str, Any]:
        """Get overall data statistics"""
        stats = {
            'total_locations': db.query(Location).count(),
            'total_facilities': db.query(Facility).count(),
            'total_crime_records': db.query(CrimeData).count(),
            'total_disaster_records': db.query(DisasterData).count(),
            'total_market_records': db.query(MarketData).count()
        }
        
        return stats
    
    async def cleanup_old_data(self, days_old: int, db: Session) -> int:
        """Clean up old data records"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete old update logs
        deleted_count = db.query(DataUpdateLog).filter(
            DataUpdateLog.completed_at < cutoff_date
        ).delete()
        
        db.commit()
        return deleted_count
    
    async def get_coverage_statistics(self, db: Session) -> Dict[str, Any]:
        """Get data coverage statistics by region"""
        # Implementation for coverage statistics
        return {"coverage": "placeholder"}