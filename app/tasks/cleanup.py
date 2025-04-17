import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.token_service import clean_expired_tokens

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_job():
    """Cleanup expired tokens"""
    try:
        expired_count = clean_expired_tokens()
        logger.info(f"Cleaned up {expired_count} expired tokens")
    except Exception as e:
        logger.error(f"Error in cleanup job: {str(e)}")

def start_scheduler():
    """Start the background scheduler for cleanup tasks"""
    scheduler = BackgroundScheduler()
    # Run the cleanup job every hour
    scheduler.add_job(cleanup_job, 'interval', hours=1)
    scheduler.start()
    logger.info("Started background scheduler for token cleanup")
    return scheduler