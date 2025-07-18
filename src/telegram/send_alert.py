# src/telegram/send_alert.py
import os
import json
import requests
import logging
from datetime import datetime
# Use relative imports for all local modules
from ..llm.service import generate_commentary
from ..utils.db import load_all_signals

# ... (rest of the send_alert.py code from the previous response)
# The logic inside this file was already correct. The main change is
# to call load_all_signals and process them in a batch.

def main():
    """Main entry point to fetch all signals and process them for alerting."""
    logging.info("--- Running Alert Generation ---")
    all_signals = load_all_signals()
    if not all_signals:
        logging.info("No signals found in the database to process.")
        return
    
    for signal_context in all_signals:
        process_signal(signal_context) # process_signal is the function from the previous response
    
    logging.info("--- Alert Generation Complete ---")

if __name__ == '__main__':
    main()