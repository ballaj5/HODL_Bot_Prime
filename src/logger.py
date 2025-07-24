import logging
import json
from config import config

class JsonFormatter(logging.Formatter):
    """
    Formats log records as JSON.
    """
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger():
    """
    Sets up a logger with a JSON formatter and a configurable log level.
    """
    logger = logging.getLogger("HODL_Bot_Prime")
    logger.setLevel(config.LOG_LEVEL)

    # Prevent duplicate logs if already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# Instantiate the logger
logger = setup_logger()