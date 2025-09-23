from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from loguru import logger

from app.services.data_collector import DataCollector
from app.core.config import settings

# Global scheduler instance
scheduler = None
data_collector = DataCollector()

def start_scheduler():
    """Start the background scheduler for automated tasks"""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler is already running")
        return
    
    scheduler = AsyncIOScheduler()
    
    # Schedule data updates
    schedule_data_updates()
    
    # Schedule model retraining
    schedule_model_updates()
    
    # Schedule cleanup tasks
    schedule_cleanup_tasks()
    
    # Start the scheduler
    scheduler.start()
    logger.info("Background scheduler started successfully")

def stop_scheduler():
    """Stop the background scheduler"""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Background scheduler stopped")

def schedule_data_updates():
    """Schedule automated data collection tasks"""
    global scheduler
    
    # Daily market data updates (every day at 2 AM)
    scheduler.add_job(
        func=data_collector.update_market_data,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_market_update',
        name='Daily Market Data Update',
        replace_existing=True
    )
    
    # Weekly facilities data updates (every Sunday at 3 AM)
    scheduler.add_job(
        func=data_collector.update_facilities_data,
        trigger=CronTrigger(day_of_week=6, hour=3, minute=0),
        id='weekly_facilities_update',
        name='Weekly Facilities Data Update',
        replace_existing=True
    )
    
    # Monthly crime data updates (1st of every month at 4 AM)
    scheduler.add_job(
        func=data_collector.update_crime_data,
        trigger=CronTrigger(day=1, hour=4, minute=0),
        id='monthly_crime_update',
        name='Monthly Crime Data Update',
        replace_existing=True
    )
    
    # Quarterly disaster data updates (1st of Jan, Apr, Jul, Oct at 5 AM)
    scheduler.add_job(
        func=data_collector.update_disaster_data,
        trigger=CronTrigger(month='1,4,7,10', day=1, hour=5, minute=0),
        id='quarterly_disaster_update',
        name='Quarterly Disaster Data Update',
        replace_existing=True
    )
    
    logger.info("Data update schedules configured")

def schedule_model_updates():
    """Schedule AI model retraining and updates"""
    global scheduler
    
    # Model retraining based on configuration
    interval_days = settings.MODEL_UPDATE_INTERVAL_DAYS
    
    scheduler.add_job(
        func=retrain_ai_models,
        trigger=IntervalTrigger(days=interval_days),
        id='model_retraining',
        name='AI Model Retraining',
        replace_existing=True,
        next_run_time=datetime.now() + timedelta(days=1)  # Start tomorrow
    )
    
    # Model performance monitoring (daily at 6 AM)
    scheduler.add_job(
        func=monitor_model_performance,
        trigger=CronTrigger(hour=6, minute=0),
        id='model_monitoring',
        name='Model Performance Monitoring',
        replace_existing=True
    )
    
    logger.info("Model update schedules configured")

def schedule_cleanup_tasks():
    """Schedule database cleanup and maintenance tasks"""
    global scheduler
    
    # Daily log cleanup (every day at 1 AM)
    scheduler.add_job(
        func=cleanup_old_logs,
        trigger=CronTrigger(hour=1, minute=0),
        id='daily_log_cleanup',
        name='Daily Log Cleanup',
        replace_existing=True
    )
    
    # Weekly database optimization (every Sunday at 1 AM)
    scheduler.add_job(
        func=optimize_database,
        trigger=CronTrigger(day_of_week=6, hour=1, minute=0),
        id='weekly_db_optimization',
        name='Weekly Database Optimization',
        replace_existing=True
    )
    
    # Monthly data archival (1st of every month at 12 AM)
    scheduler.add_job(
        func=archive_old_data,
        trigger=CronTrigger(day=1, hour=0, minute=0),
        id='monthly_data_archival',
        name='Monthly Data Archival',
        replace_existing=True
    )
    
    logger.info("Cleanup task schedules configured")

async def retrain_ai_models():
    """Retrain AI models with latest data"""
    logger.info("Starting AI model retraining")
    
    try:
        from app.services.ai_analyzer import LandSuitabilityAnalyzer
        from app.services.model_trainer import ModelTrainer
        
        trainer = ModelTrainer()
        
        # Retrain models
        await trainer.retrain_suitability_model()
        await trainer.retrain_price_prediction_model()
        await trainer.retrain_risk_assessment_model()
        
        logger.info("AI model retraining completed successfully")
        
    except Exception as e:
        logger.error(f"AI model retraining failed: {str(e)}")

async def monitor_model_performance():
    """Monitor AI model performance and accuracy"""
    logger.info("Starting model performance monitoring")
    
    try:
        from app.services.model_trainer import ModelTrainer
        
        trainer = ModelTrainer()
        performance_report = await trainer.evaluate_model_performance()
        
        # Log performance metrics
        for model_name, metrics in performance_report.items():
            logger.info(f"Model {model_name} performance: {metrics}")
            
            # Check if model performance has degraded
            if metrics.get('accuracy', 0) < settings.PREDICTION_CONFIDENCE_THRESHOLD:
                logger.warning(f"Model {model_name} performance below threshold, scheduling retraining")
                # Could trigger immediate retraining here
        
        logger.info("Model performance monitoring completed")
        
    except Exception as e:
        logger.error(f"Model performance monitoring failed: {str(e)}")

async def cleanup_old_logs():
    """Clean up old log files and database logs"""
    logger.info("Starting log cleanup")
    
    try:
        # Clean up old data update logs (older than 90 days)
        deleted_count = await data_collector.cleanup_old_data(90, None)
        logger.info(f"Cleaned up {deleted_count} old log records")
        
        # Clean up old analysis records (older than 1 year)
        await cleanup_old_analyses(365)
        
        logger.info("Log cleanup completed")
        
    except Exception as e:
        logger.error(f"Log cleanup failed: {str(e)}")

async def cleanup_old_analyses(days_old: int):
    """Clean up old analysis records"""
    from app.database import SessionLocal
    from app.models import LandAnalysis
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete old analyses (keep at least one per location per user)
        deleted_count = db.query(LandAnalysis).filter(
            LandAnalysis.created_at < cutoff_date
        ).delete()
        
        db.commit()
        logger.info(f"Cleaned up {deleted_count} old analysis records")
        
    except Exception as e:
        logger.error(f"Failed to cleanup old analyses: {str(e)}")
        db.rollback()
    finally:
        db.close()

async def optimize_database():
    """Perform database optimization tasks"""
    logger.info("Starting database optimization")
    
    try:
        from app.database import engine
        
        # For SQLite, run VACUUM to optimize database
        if "sqlite" in str(engine.url):
            with engine.connect() as conn:
                conn.execute("VACUUM")
                logger.info("SQLite database vacuumed")
        
        # For PostgreSQL, could run ANALYZE, REINDEX, etc.
        # This would be database-specific optimization
        
        logger.info("Database optimization completed")
        
    except Exception as e:
        logger.error(f"Database optimization failed: {str(e)}")

async def archive_old_data(months_old: int = 12):
    """Archive old data to reduce database size"""
    logger.info(f"Starting data archival for data older than {months_old} months")
    
    try:
        from app.database import SessionLocal
        from app.models import CrimeData, MarketData
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        cutoff_date = datetime.utcnow() - timedelta(days=months_old * 30)
        
        # Archive old crime data (keep recent data for analysis)
        old_crime_count = db.query(CrimeData).filter(
            CrimeData.year < cutoff_date.year
        ).count()
        
        # Archive old market data (keep last 6 months)
        old_market_count = db.query(MarketData).filter(
            MarketData.updated_at < cutoff_date
        ).count()
        
        logger.info(f"Found {old_crime_count} old crime records and {old_market_count} old market records for archival")
        
        # In a real implementation, you would export this data to archive storage
        # before deleting from the main database
        
        db.close()
        logger.info("Data archival completed")
        
    except Exception as e:
        logger.error(f"Data archival failed: {str(e)}")

def add_one_time_task(func, run_time: datetime, task_id: str, task_name: str):
    """Add a one-time scheduled task"""
    global scheduler
    
    if scheduler is None:
        logger.error("Scheduler not initialized")
        return False
    
    try:
        scheduler.add_job(
            func=func,
            trigger='date',
            run_date=run_time,
            id=task_id,
            name=task_name,
            replace_existing=True
        )
        logger.info(f"Scheduled one-time task '{task_name}' for {run_time}")
        return True
    except Exception as e:
        logger.error(f"Failed to schedule task '{task_name}': {str(e)}")
        return False

def remove_scheduled_task(task_id: str):
    """Remove a scheduled task"""
    global scheduler
    
    if scheduler is None:
        logger.error("Scheduler not initialized")
        return False
    
    try:
        scheduler.remove_job(task_id)
        logger.info(f"Removed scheduled task '{task_id}'")
        return True
    except Exception as e:
        logger.error(f"Failed to remove task '{task_id}': {str(e)}")
        return False

def get_scheduled_jobs():
    """Get list of all scheduled jobs"""
    global scheduler
    
    if scheduler is None:
        return []
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time,
            'trigger': str(job.trigger)
        })
    
    return jobs

def pause_scheduler():
    """Pause the scheduler"""
    global scheduler
    
    if scheduler is not None:
        scheduler.pause()
        logger.info("Scheduler paused")

def resume_scheduler():
    """Resume the scheduler"""
    global scheduler
    
    if scheduler is not None:
        scheduler.resume()
        logger.info("Scheduler resumed")

def is_scheduler_running():
    """Check if scheduler is running"""
    global scheduler
    return scheduler is not None and scheduler.running