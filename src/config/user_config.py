"""
User Configuration Management System
- YAML/TOML based configuration
- Advisory mode preferences
- Email template customization
- Risk tolerance settings
- Scheduling preferences
"""

import yaml
import tomli
import tomli_w
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigFormat(Enum):
    YAML = "yaml"
    TOML = "toml"

@dataclass
class EmailConfig:
    """Email configuration settings"""
    enabled: bool = True
    recipients: List[str] = None
    schedule: Dict[str, Any] = None
    template_style: str = "professional"  # professional, casual, detailed
    include_charts: bool = False
    include_explanations: bool = True
    include_detailed_analysis: bool = True
    include_scenarios: bool = False
    language: str = "english"  # english, vietnamese, both
    frequency: str = "daily"  # daily, weekly, monthly
    time_preference: str = "07:30"
    timezone: str = "Asia/Ho_Chi_Minh"
    
    def __post_init__(self):
        if self.recipients is None:
            self.recipients = []
        if self.schedule is None:
            self.schedule = {"time": "08:00", "days": [0, 1, 2, 3, 4]}

@dataclass
class RiskConfig:
    """Risk management configuration"""
    risk_tolerance: str = "medium"  # low, medium, high
    max_position_size: float = 15.0  # percentage
    max_sector_concentration: float = 40.0  # percentage
    default_stop_loss: float = -15.0  # percentage
    position_sizing: str = "risk_weighted"  # equal_weight, risk_weighted, conviction_weighted
    enable_stop_loss_alerts: bool = True
    stop_loss_threshold: float = -15.0  # percentage
    rebalancing_threshold: float = 5.0  # percentage deviation

@dataclass
class AdvisoryConfig:
    """Advisory preferences configuration"""
    primary_mode: str = "long_term"  # long_term, swing_trader, dividend_focused, etc.
    secondary_modes: List[str] = None
    benchmark_comparisons: List[str] = None
    enable_scenario_analysis: bool = True
    enable_sector_rotation_alerts: bool = True
    custom_instructions: Optional[str] = None
    
    def __post_init__(self):
        if self.secondary_modes is None:
            self.secondary_modes = []
        if self.benchmark_comparisons is None:
            self.benchmark_comparisons = ["VN-Index", "VN30"]

@dataclass
class NotificationConfig:
    """Notification preferences"""
    enable_email: bool = True
    enable_webhooks: bool = False
    urgent_alert_threshold: str = "high"  # high, medium, low
    daily_summary: bool = True
    weekly_summary: bool = True
    monthly_summary: bool = True
    webhook_urls: List[str] = None
    
    def __post_init__(self):
        if self.webhook_urls is None:
            self.webhook_urls = []

@dataclass
class DataConfig:
    """Data and caching configuration"""
    enable_historical_storage: bool = True
    storage_backend: str = "sqlite"  # sqlite, postgresql, file
    cache_duration_minutes: int = 60
    backup_frequency: str = "weekly"  # daily, weekly, monthly
    max_history_days: int = 365

@dataclass
class UserConfiguration:
    """Complete user configuration"""
    user_name: str = "User"
    created_at: str = ""
    last_updated: str = ""
    version: str = "1.0"
    
    email: EmailConfig = None
    risk: RiskConfig = None
    advisory: AdvisoryConfig = None
    notifications: NotificationConfig = None
    data: DataConfig = None
    
    def __post_init__(self):
        if self.email is None:
            self.email = EmailConfig()
        if self.risk is None:
            self.risk = RiskConfig()
        if self.advisory is None:
            self.advisory = AdvisoryConfig()
        if self.notifications is None:
            self.notifications = NotificationConfig()
        if self.data is None:
            self.data = DataConfig()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()

class ConfigManager:
    """
    Configuration Manager for user preferences and settings
    """
    
    def __init__(self, config_file: str = "config/user_config.yaml", 
                 format_type: ConfigFormat = ConfigFormat.YAML):
        self.config_file = Path(config_file)
        self.format_type = format_type
        self.config: Optional[UserConfiguration] = None
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> UserConfiguration:
        """Load configuration from file"""
        try:
            if not self.config_file.exists():
                logger.info(f"Config file not found, creating default: {self.config_file}")
                return self.create_default_config()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                if self.format_type == ConfigFormat.YAML:
                    data = yaml.safe_load(f)
                elif self.format_type == ConfigFormat.TOML:
                    data = tomli.load(f)
                else:
                    raise ValueError(f"Unsupported format: {self.format_type}")
            
            # Convert to UserConfiguration object
            self.config = self._dict_to_config(data)
            logger.info(f"Loaded configuration from {self.config_file}")
            return self.config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.info("Using default configuration")
            return self.create_default_config()
    
    def save_config(self, config: UserConfiguration) -> bool:
        """Save configuration to file"""
        try:
            config.last_updated = datetime.now().isoformat()
            data = asdict(config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.format_type == ConfigFormat.YAML:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
                elif self.format_type == ConfigFormat.TOML:
                    tomli_w.dump(data, f)
                else:
                    raise ValueError(f"Unsupported format: {self.format_type}")
            
            self.config = config
            logger.info(f"Saved configuration to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def create_default_config(self) -> UserConfiguration:
        """Create default configuration"""
        config = UserConfiguration()
        self.save_config(config)
        return config
    
    def update_advisory_mode(self, primary_mode: str, secondary_modes: List[str] = None) -> bool:
        """Update advisory mode preferences"""
        try:
            if not self.config:
                self.config = self.load_config()
            
            self.config.advisory.primary_mode = primary_mode
            if secondary_modes:
                self.config.advisory.secondary_modes = secondary_modes
            
            return self.save_config(self.config)
            
        except Exception as e:
            logger.error(f"Error updating advisory mode: {e}")
            return False
    
    def update_risk_settings(self, risk_tolerance: str = None, 
                           max_position_size: float = None,
                           stop_loss_threshold: float = None) -> bool:
        """Update risk management settings"""
        try:
            if not self.config:
                self.config = self.load_config()
            
            if risk_tolerance:
                self.config.risk.risk_tolerance = risk_tolerance
            if max_position_size:
                self.config.risk.max_position_size = max_position_size
            if stop_loss_threshold:
                self.config.risk.stop_loss_threshold = stop_loss_threshold
            
            return self.save_config(self.config)
            
        except Exception as e:
            logger.error(f"Error updating risk settings: {e}")
            return False
    
    def update_email_preferences(self, template_style: str = None,
                               language: str = None,
                               include_explanations: bool = None) -> bool:
        """Update email preferences"""
        try:
            if not self.config:
                self.config = self.load_config()
            
            if template_style:
                self.config.email.template_style = template_style
            if language:
                self.config.email.language = language
            if include_explanations is not None:
                self.config.email.include_explanations = include_explanations
            
            return self.save_config(self.config)
            
        except Exception as e:
            logger.error(f"Error updating email preferences: {e}")
            return False
    
    def get_config(self) -> UserConfiguration:
        """Get current configuration"""
        if not self.config:
            self.config = self.load_config()
        return self.config
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration settings"""
        if not self.config:
            self.config = self.load_config()
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate advisory mode
        valid_modes = ["long_term", "swing_trader", "dividend_focused", "growth_oriented", "value_investor", "conservative"]
        if self.config.advisory.primary_mode not in valid_modes:
            validation_results["errors"].append(f"Invalid primary advisory mode: {self.config.advisory.primary_mode}")
            validation_results["valid"] = False
        
        # Validate risk settings
        if not 0 < self.config.risk.max_position_size <= 100:
            validation_results["errors"].append("Max position size must be between 0 and 100%")
            validation_results["valid"] = False
        
        if not -50 <= self.config.risk.stop_loss_threshold <= 0:
            validation_results["warnings"].append("Stop loss threshold should typically be between -50% and 0%")
        
        # Validate email settings
        valid_languages = ["english", "vietnamese", "both"]
        if self.config.email.language not in valid_languages:
            validation_results["warnings"].append(f"Unusual language setting: {self.config.email.language}")
        
        return validation_results
    
    def export_config(self, export_path: str, format_type: ConfigFormat = None) -> bool:
        """Export configuration to different file/format"""
        try:
            if not self.config:
                self.config = self.load_config()
            
            export_file = Path(export_path)
            export_format = format_type or self.format_type
            
            data = asdict(self.config)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                if export_format == ConfigFormat.YAML:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
                elif export_format == ConfigFormat.TOML:
                    tomli_w.dump(data, f)
            
            logger.info(f"Exported configuration to {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            return False
    
    def _dict_to_config(self, data: Dict[str, Any]) -> UserConfiguration:
        """Convert dictionary to UserConfiguration object"""
        try:
            # Create config objects from dictionaries
            email_config = EmailConfig(**data.get('email', {}))
            risk_config = RiskConfig(**data.get('risk', {}))
            advisory_config = AdvisoryConfig(**data.get('advisory', {}))
            notification_config = NotificationConfig(**data.get('notifications', {}))
            data_config = DataConfig(**data.get('data', {}))
            
            # Create main config
            config = UserConfiguration(
                user_name=data.get('user_name', 'User'),
                created_at=data.get('created_at', ''),
                last_updated=data.get('last_updated', ''),
                version=data.get('version', '1.0'),
                email=email_config,
                risk=risk_config,
                advisory=advisory_config,
                notifications=notification_config,
                data=data_config
            )
            
            return config
            
        except Exception as e:
            logger.error(f"Error converting dict to config: {e}")
            return UserConfiguration()

# Global configuration manager instance
config_manager = ConfigManager()

def get_user_config() -> UserConfiguration:
    """Get current user configuration"""
    return config_manager.get_config()

def update_user_config(config: UserConfiguration) -> bool:
    """Update user configuration"""
    return config_manager.save_config(config)
