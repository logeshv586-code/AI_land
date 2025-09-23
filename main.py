from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

from app.database import engine, get_db
from app.models import Base
from app.routers import land_analysis, auth, data_collection, land_area_automation, demo_automation, property_listings, illinois_neighborhood, messages, subscriptions, illinois_data, analytics, featured_listings, ai_automation
from app.core.config import settings
from app.services.scheduler import start_scheduler

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Land Analysis AI System")
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down Land Analysis AI System")

app = FastAPI(
    title="Land Suitability Analysis AI",
    description="AI-powered system for analyzing land suitability for real estate investment",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(land_analysis.router, prefix="/api/v1/analysis", tags=["Land Analysis"])
app.include_router(land_area_automation.router, prefix="/api/v1/automation", tags=["Land Area Automation"])
app.include_router(demo_automation.router, prefix="/api/v1/automation", tags=["Demo Automation"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(data_collection.router, prefix="/api/v1/data", tags=["Data Collection"])
app.include_router(property_listings.router, prefix="/api/v1/properties", tags=["Property Listings"])
app.include_router(illinois_neighborhood.router, prefix="/api/v1/illinois-neighborhood", tags=["Illinois Neighborhood Quality"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["Messages"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
app.include_router(illinois_data.router, prefix="/api/v1/illinois-data", tags=["Illinois Data Integration"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(featured_listings.router, prefix="/api/v1/featured-listings", tags=["Featured Listings"])
app.include_router(ai_automation.router)

# Mount static files for frontend (if build directory exists)
import os
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build"), name="static")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Land Suitability Analysis AI",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Land Analysis AI"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )