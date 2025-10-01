"""
Backend scheduler for automated forecast data updates.
Runs independently to update forecast data every 12 hours.
"""

import time
import schedule
import logging
from datetime import datetime
from pathlib import Path

from backend.data_processor import get_processor


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend/scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def update_forecast_data():
    """Update forecast data and log the result."""
    try:
        logger.info("Starting scheduled forecast data update...")
        processor = get_processor()
        
        # Force refresh to get new data
        data = processor.get_forecast_data(force_refresh=True)
        
        spots_count = len(data.get('spots_processed', []))
        logger.info(f"Successfully updated forecast data for {spots_count} spots")
        
        # Log cache status
        status = processor.get_cache_status()
        logger.info(f"Next update scheduled for: {status['next_update']}")
        
    except Exception as e:
        logger.error(f"Failed to update forecast data: {e}")


def main():
    """Main scheduler loop."""
    logger.info("Starting forecast data scheduler...")
    
    # Schedule updates every 12 hours
    schedule.every(12).hours.do(update_forecast_data)
    
    # Also run an initial update if no cache exists
    processor = get_processor()
    if not processor._is_cache_valid():
        logger.info("No valid cache found, running initial update...")
        update_forecast_data()
    
    logger.info("Scheduler started. Updates will run every 12 hours.")
    
    # Keep the scheduler running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)  # Wait before retrying


if __name__ == "__main__":
    main()
