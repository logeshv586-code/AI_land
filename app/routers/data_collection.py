from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, DataUpdateLog
from app.schemas import DataUpdateStatus
from app.services.data_collector import DataCollector
from app.core.auth import get_current_user
from loguru import logger

router = APIRouter()
data_collector = DataCollector()

@router.post("/update-all")
async def trigger_full_data_update(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger full data update for all data sources
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Start background data collection tasks
    background_tasks.add_task(data_collector.update_facilities_data)
    background_tasks.add_task(data_collector.update_crime_data)
    background_tasks.add_task(data_collector.update_disaster_data)
    background_tasks.add_task(data_collector.update_market_data)
    
    logger.info(f"Full data update triggered by admin user {current_user.id}")
    return {"message": "Data update started in background"}

@router.post("/update-facilities")
async def update_facilities_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update facilities data (schools, hospitals, etc.)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    background_tasks.add_task(data_collector.update_facilities_data)
    return {"message": "Facilities data update started"}

@router.post("/update-crime")
async def update_crime_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update crime statistics data
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    background_tasks.add_task(data_collector.update_crime_data)
    return {"message": "Crime data update started"}

@router.post("/update-disasters")
async def update_disaster_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update natural disaster risk data
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    background_tasks.add_task(data_collector.update_disaster_data)
    return {"message": "Disaster data update started"}

@router.post("/update-market")
async def update_market_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update real estate market data
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    background_tasks.add_task(data_collector.update_market_data)
    return {"message": "Market data update started"}

@router.get("/status", response_model=List[DataUpdateStatus])
async def get_data_update_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get status of all data sources
    """
    # Get latest update logs for each data type
    data_types = ["facilities", "crime", "disaster", "market"]
    status_list = []
    
    for data_type in data_types:
        latest_log = db.query(DataUpdateLog).filter(
            DataUpdateLog.data_type == data_type
        ).order_by(DataUpdateLog.completed_at.desc()).first()
        
        if latest_log:
            status_list.append(DataUpdateStatus(
                data_type=data_type,
                last_update=latest_log.completed_at,
                next_update=data_collector.get_next_update_time(data_type),
                status=latest_log.update_status,
                records_count=latest_log.records_updated or 0
            ))
        else:
            status_list.append(DataUpdateStatus(
                data_type=data_type,
                last_update=None,
                next_update=data_collector.get_next_update_time(data_type),
                status="never_updated",
                records_count=0
            ))
    
    return status_list

@router.get("/logs")
async def get_update_logs(
    data_type: str = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get data update logs
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(DataUpdateLog)
    if data_type:
        query = query.filter(DataUpdateLog.data_type == data_type)
    
    logs = query.order_by(DataUpdateLog.started_at.desc()).limit(limit).all()
    return logs

@router.post("/validate-apis")
async def validate_external_apis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate all external API connections
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    validation_results = await data_collector.validate_api_connections()
    return validation_results

@router.post("/location/{location_id}/refresh")
async def refresh_location_data(
    location_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refresh data for a specific location
    """
    background_tasks.add_task(
        data_collector.update_location_data, location_id
    )
    
    return {"message": f"Data refresh started for location {location_id}"}

@router.get("/statistics")
async def get_data_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall data statistics
    """
    stats = await data_collector.get_data_statistics(db)
    return stats

@router.post("/cleanup")
async def cleanup_old_data(
    days_old: int = 365,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clean up old data records
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if days_old < 30:
        raise HTTPException(status_code=400, detail="Cannot delete data newer than 30 days")
    
    deleted_count = await data_collector.cleanup_old_data(days_old, db)
    return {"message": f"Deleted {deleted_count} old records"}

@router.get("/coverage")
async def get_data_coverage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get data coverage statistics by region
    """
    coverage_stats = await data_collector.get_coverage_statistics(db)
    return coverage_stats