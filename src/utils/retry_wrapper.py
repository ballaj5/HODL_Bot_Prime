# utils/retry_wrapper.py

import time
import logging

logging.basicConfig(level=logging.INFO)

def retry(operation, label="Operation", attempts=3, delay=2):
    """
    Retry a callable function up to N times with delay.
    Args:
        operation: a function with no arguments
        label: string used in logs
        attempts: number of retry attempts
        delay: seconds to wait between attempts
    Returns:
        Result of operation() if successful, else raises the last exception.
    """
    for i in range(1, attempts + 1):
        try:
            logging.info(f"🔁 Attempt {i}/{attempts}: {label}")
            return operation()
        except Exception as e:
            logging.error(f"⚠️ {label} failed on attempt {i}: {e}")
            if i < attempts:
                time.sleep(delay)
            else:
                logging.critical(f"❌ {label} failed after {attempts} attempts.")
                raise e
