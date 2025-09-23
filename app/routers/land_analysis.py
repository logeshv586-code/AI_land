from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import (
    AnalysisRequest, AnalysisResponse, QuickAnalysisResponse,
    BatchAnalysisRequest, BatchAnalysisResponse
)
from app.services.ai_analyzer import LandSuitabilityAnalyzer
from app.services.data_collector import DataCollector
from app.services.location_service import LocationService
from app.models import LandAnalysis, Location, User
from app.core.auth import get_current_user
from loguru import logger
import uuid

router = APIRouter()

# Initialize services
analyzer = LandSuitabilityAnalyzer()
data_collector = DataCollector()
location_service = LocationService()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_land(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive AI-powered land suitability analysis
    """
    try:
        # Get or create location
        location = await location_service.get_or_create_location(
            db, request.address, request.latitude, request.longitude
        )
        
        # Check if recent analysis exists
        existing_analysis = db.query(LandAnalysis).filter(
            LandAnalysis.location_id == location.id,
            LandAnalysis.user_id == current_user.id
        ).order_by(LandAnalysis.created_at.desc()).first()
        
        # If analysis is recent (less than 24 hours), return cached result
        if existing_analysis and analyzer.is_analysis_recent(existing_analysis):
            return analyzer.format_analysis_response(existing_analysis, location)
        
        # Collect fresh data in background if needed
        background_tasks.add_task(
            data_collector.update_location_data, location.id
        )
        
        # Perform AI analysis
        analysis_result = await analyzer.analyze_location(
            location, request, current_user.id, db
        )
        
        logger.info(f"Analysis completed for location {location.id} by user {current_user.id}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/quick-analyze", response_model=QuickAnalysisResponse)
async def quick_analyze(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform quick land analysis with basic scoring
    """
    try:
        location = await location_service.get_or_create_location(
            db, request.address, request.latitude, request.longitude
        )
        
        # Perform quick analysis using cached data
        quick_result = await analyzer.quick_analyze_location(location, request, db)
        
        logger.info(f"Quick analysis completed for location {location.id}")
        return quick_result
        
    except Exception as e:
        logger.error(f"Quick analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")

@router.post("/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform batch analysis for multiple locations
    """
    try:
        batch_id = str(uuid.uuid4())
        
        # Start batch processing in background
        background_tasks.add_task(
            analyzer.process_batch_analysis,
            batch_id, request.locations, current_user.id, db
        )
        
        return BatchAnalysisResponse(
            batch_id=batch_id,
            total_locations=len(request.locations),
            completed=0,
            failed=0,
            results=[]
        )
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.get("/batch-status/{batch_id}")
async def get_batch_status(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get status of batch analysis
    """
    # Implementation would track batch progress
    # For now, return a placeholder
    return {"batch_id": batch_id, "status": "processing"}

@router.get("/history", response_model=List[AnalysisResponse])
async def get_analysis_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's analysis history
    """
    analyses = db.query(LandAnalysis).filter(
        LandAnalysis.user_id == current_user.id
    ).order_by(LandAnalysis.created_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for analysis in analyses:
        location = db.query(Location).filter(Location.id == analysis.location_id).first()
        results.append(analyzer.format_analysis_response(analysis, location))
    
    return results

@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific analysis by ID
    """
    analysis = db.query(LandAnalysis).filter(
        LandAnalysis.id == analysis_id,
        LandAnalysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    location = db.query(Location).filter(Location.id == analysis.location_id).first()
    return analyzer.format_analysis_response(analysis, location)

@router.delete("/analysis/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an analysis
    """
    analysis = db.query(LandAnalysis).filter(
        LandAnalysis.id == analysis_id,
        LandAnalysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "Analysis deleted successfully"}

@router.get("/compare")
async def compare_locations(
    location_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare multiple locations side by side
    """
    if len(location_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 locations can be compared")
    
    analyses = db.query(LandAnalysis).filter(
        LandAnalysis.location_id.in_(location_ids),
        LandAnalysis.user_id == current_user.id
    ).all()
    
    comparison_data = analyzer.compare_analyses(analyses, db)
    return comparison_data

@router.get("/recommendations")
async def get_recommendations(
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    property_type: Optional[str] = None,
    min_score: float = 70.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered recommendations based on criteria
    """
    recommendations = await analyzer.get_personalized_recommendations(
        current_user.id, budget_min, budget_max, property_type, min_score, db
    )
    
    return recommendations