import logging
import sys
from typing import Optional
from datetime import datetime

def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with console and optionally file output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def log_auth_event(
    logger: logging.Logger,
    event_type: str,
    user_id: str,
    details: dict,
    ip_address: Optional[str] = None
) -> None:
    """
    Log authentication-related events with structured data.
    """
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        **details
    }
    logger.info("Auth event", extra=log_data)
