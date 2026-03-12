import sys
from loguru import logger
import os

def setup_logging():
    """
    Configures Loguru for structured JSON logging in production
    and human-readable colored logging in development.
    """
    # Remove default handler
    logger.remove()

    # Determine log level
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # JSON formatting for production/containers
    # In development, we use a clean colored format
    is_production = os.getenv("ENV", "development").lower() == "production"

    if is_production:
        # Structured JSON logging
        logger.add(
            sys.stdout,
            format="{message}",
            level=log_level,
            serialize=True,
        )
    else:
        # Human-readable colored logging
        # Format: Time | Level | SessionID | Message
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[session_id]}</cyan> - "
            "<level>{message}</level>"
        )
        logger.add(
            sys.stdout,
            format=log_format,
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    # Bind a default session_id to avoid KeyError in dev format
    return logger.bind(session_id="SYSTEM")

# Global logger instance
logger = setup_logging()
