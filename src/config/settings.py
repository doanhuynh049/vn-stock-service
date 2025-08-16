import os
from typing import Optional
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Data Provider Settings
    VN_DATA_PROVIDER: str = "mock"
    VN_API_KEY: Optional[str] = None
    VN_BASE_URL: Optional[str] = None
    
    # Scheduler Settings
    SCHEDULE_CRON: str = "30 7 * * *"
    TIMEZONE: str = "Asia/Ho_Chi_Minh"
    
    # Email Settings
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    SMTP_TLS: bool = True
    MAIL_TO: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    
    # AI/LLM Settings
    LLM_PROVIDER: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    LLM_API_KEY: Optional[str] = None
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 500
    
    # Portfolio Settings
    HOLDINGS_FILE: str = "data/holdings.json"
    
    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_MINUTES: int = 5  # Cache market data for 5 minutes
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/vn-stock-advisory.log"
    
    # Risk Management
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30
    RATE_LIMIT_DELAY: float = 1.0
    
    # Development Settings
    DEBUG: bool = False
    DRY_RUN: bool = False  # If True, don't send emails
    
    # Database Settings (optional)
    DATABASE_URL: Optional[str] = None

    # FastConnect API Settings
    SSI_CONSUMER_ID: Optional[str] = None
    SSI_CONSUMER_SECRET: Optional[str] = None
    
    @validator('VN_DATA_PROVIDER')
    def validate_provider(cls, v):
        valid_providers = ['mock', 'vietcap', 'cafef']
        if v not in valid_providers:
            raise ValueError(f'VN_DATA_PROVIDER must be one of {valid_providers}')
        return v
    
    @validator('LLM_PROVIDER')
    def validate_llm_provider(cls, v):
        return v  # Simplified validation for now
    
    @validator('SMTP_HOST')
    def validate_smtp_settings(cls, v, values):
        """Validate SMTP settings if email is enabled"""
        if not values.get('DRY_RUN', False) and not v:
            raise ValueError('SMTP_HOST is required when DRY_RUN is False')
        return v
    
    @validator('MAIL_TO')
    def validate_email_recipient(cls, v, values):
        """Validate email recipient if email is enabled"""
        if not values.get('DRY_RUN', False) and not v:
            raise ValueError('MAIL_TO is required when DRY_RUN is False')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Logging configuration
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        }
    },
    'handlers': {
        'console': {
            'level': settings.LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': settings.LOG_LEVEL,
            'propagate': False
        }
    }
}

# Add file handler if log file is specified
if settings.LOG_FILE:
    LOGGING_CONFIG['handlers']['file'] = {
        'level': settings.LOG_LEVEL,
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': settings.LOG_FILE,
        'maxBytes': 10485760,  # 10MB
        'backupCount': 5,
        'formatter': 'json'
    }
    LOGGING_CONFIG['loggers']['']['handlers'].append('file')

logging.config.dictConfig(LOGGING_CONFIG)