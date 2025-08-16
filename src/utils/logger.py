import logging
import logging.config
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None, 
                  enable_json: bool = False) -> logging.Logger:
    """
    Setup application logging with console and optional file output
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (optional)
        enable_json: Whether to use JSON format for structured logging
    
    Returns:
        Configured logger instance
    """
    
    # Ensure logs directory exists
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Define formatters
    formatters = {
        'standard': {
            'format': '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)8s] %(name)s [%(filename)s:%(lineno)d]: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "module": "%(filename)s", "line": %(lineno)d, "message": "%(message)s"}',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    }
    
    # Select formatter
    formatter_name = 'json' if enable_json else 'standard'
    file_formatter = 'json' if enable_json else 'detailed'
    
    # Configure handlers
    handlers = {
        'console': {
            'level': log_level,
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': formatter_name
        }
    }
    
    # Add file handler if specified
    if log_file:
        handlers['file'] = {
            'level': log_level,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file,
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': file_formatter,
            'encoding': 'utf-8'
        }
    
    # Logging configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': formatters,
        'handlers': handlers,
        'root': {
            'level': log_level,
            'handlers': list(handlers.keys())
        },
        'loggers': {
            # Reduce noise from third-party libraries
            'urllib3': {'level': 'WARNING'},
            'requests': {'level': 'WARNING'},
            'httpx': {'level': 'WARNING'},
            'apscheduler': {'level': 'INFO'},
            'pydantic': {'level': 'WARNING'}
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Get root logger
    logger = logging.getLogger()
    
    # Log initial message
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file or 'None'}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)

def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func_name} failed: {e}", exc_info=True)
                raise
        return wrapper
    return decorator

def log_execution_time(func):
    """Decorator to log function execution time"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {e}")
            raise
    return wrapper

class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(self.__class__.__module__ + '.' + self.__class__.__name__)

# Default logger instance
logger = get_logger(__name__)
    logger.info(message)

def log_warning(message):
    logger.warning(message)

def log_error(message):
    logger.error(message)

def log_debug(message):
    logger.debug(message)

def log_exception(exc):
    logger.exception(f"Exception occurred: {exc}")