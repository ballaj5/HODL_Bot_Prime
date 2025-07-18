# src/scheduler/retrain_scheduler.py
import os
import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
# Use a relative import to get the train_predictor module
from ..models import train_predictor
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = os.getenv("SCHEDULER_LOG_PATH", "logs/scheduler.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()]
)
logger = logging.getLogger("Scheduler")

try:
    RETRAIN_INTERVAL_MINUTES = int(os.getenv("RETRAIN_INTERVAL_MINUTES", 30))
except (ValueError, TypeError):
    logger.error("Invalid RETRAIN_INTERVAL_MINUTES. Using default of 30.")
    RETRAIN_INTERVAL_MINUTES = 30

def retrain_job():
    """The job executed by the scheduler."""
    logger.info("🔁 Kicking off scheduled retraining job...")
    try:
        train_predictor.train_all()
        logger.info("✅ Scheduled retraining job completed successfully.")
    except Exception as e:
        logger.error(f"❌ Retraining job failed: {e}", exc_info=True)

def main():
    """Initializes and runs the scheduler."""
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(retrain_job, 'interval', minutes=RETRAIN_INTERVAL_MINUTES)
    
    try:
        scheduler.start()
        logger.info(f"✅ Scheduler started. Retraining every {RETRAIN_INTERVAL_MINUTES} minutes. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Shutdown signal received. Stopping scheduler...")
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}", exc_info=True)
    finally:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler has been shut down.")

if __name__ == "__main__":
    main()