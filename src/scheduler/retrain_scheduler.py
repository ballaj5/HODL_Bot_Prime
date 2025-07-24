# src/scheduler/retrain_scheduler.py
import os
import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
from ..models import train_predictor
from ..telegram.send_alert import process_and_send_alerts # Import the new alert function

# --- Logging Setup ---
LOG_PATH = "logs/scheduler.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()]
)
logger = logging.getLogger("Scheduler")

# --- Job Functions ---
def model_retrain_job():
    """Job to retrain the predictive models."""
    logger.info("🔁 Kicking off scheduled model retraining job...")
    try:
        # CORRECTED: Called the correct function `train_all` instead of `main`
        train_predictor.train_all() 
        logger.info("✅ Model retraining job completed successfully.")
    except Exception as e:
        logger.error(f"❌ Model retraining job failed: {e}", exc_info=True)

def alert_sending_job():
    """Job to check for and send new alerts."""
    logger.info("📨 Kicking off scheduled alert sending job...")
    try:
        process_and_send_alerts()
        logger.info("✅ Alert sending job completed successfully.")
    except Exception as e:
        logger.error(f"❌ Alert sending job failed: {e}", exc_info=True)

# --- Main Scheduler Logic ---
def main():
    """Initializes and runs the scheduler for all background tasks."""
    scheduler = BackgroundScheduler(timezone="UTC")
    
    # Schedule model retraining every 30 minutes
    scheduler.add_job(model_retrain_job, 'interval', minutes=30, id='retrain_job')
    
    # Schedule alert checking every 5 minutes
    scheduler.add_job(alert_sending_job, 'interval', minutes=5, id='alert_job')
    
    try:
        scheduler.start()
        logger.info("✅ Scheduler started with all jobs. Press Ctrl+C to exit.")
        # Keep the script running
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Shutdown signal received. Stopping scheduler...")
    finally:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler has been shut down.")

if __name__ == "__main__":
    main()