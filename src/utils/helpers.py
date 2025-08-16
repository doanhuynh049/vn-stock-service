import json
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union
import pytz
from pathlib import Path

def format_currency(value: Union[int, float], currency: str = 'VND', 
                   show_decimals: bool = False) -> str:
    """
    Format a numeric value as currency with proper formatting for Vietnamese Dong
    
    Args:
        value: Numeric value to format
        currency: Currency code (default: VND)
        show_decimals: Whether to show decimal places
    
    Returns:
        Formatted currency string
    """
    if show_decimals:
        return f"{value:,.2f} {currency}"
    else:
        return f"{value:,.0f} {currency}"

def format_percentage(value: Union[int, float], decimals: int = 2) -> str:
    """Format a value as percentage with proper sign"""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100

def normalize_ticker(ticker: str) -> str:
    """Normalize ticker symbol to uppercase and remove extra spaces"""
    return ticker.upper().strip()

def validate_exchange(exchange: str) -> bool:
    """Validate if exchange is a valid Vietnamese exchange"""
    valid_exchanges = {'HOSE', 'HNX', 'UPCoM'}
    return exchange in valid_exchanges

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    if denominator == 0:
        return default
    return numerator / denominator

def convert_timezone(dt: datetime, target_tz: str = "Asia/Ho_Chi_Minh") -> datetime:
    """Convert datetime to target timezone"""
    target_timezone = pytz.timezone(target_tz)
    
    # If datetime is naive, assume UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    return dt.astimezone(target_timezone)

def get_vietnam_time() -> datetime:
    """Get current time in Vietnam timezone"""
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(vn_tz)

def is_market_hours(dt: Optional[datetime] = None) -> bool:
    """
    Check if given time (or current time) is within Vietnamese market hours
    HOSE: 9:00-11:30, 13:00-15:00 (GMT+7)
    """
    if dt is None:
        dt = get_vietnam_time()
    
    # Convert to Vietnam time if not already
    if dt.tzinfo != pytz.timezone("Asia/Ho_Chi_Minh"):
        dt = convert_timezone(dt)
    
    # Check if it's a weekday
    if dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    time_only = dt.time()
    morning_start = datetime.strptime("09:00", "%H:%M").time()
    morning_end = datetime.strptime("11:30", "%H:%M").time()
    afternoon_start = datetime.strptime("13:00", "%H:%M").time()
    afternoon_end = datetime.strptime("15:00", "%H:%M").time()
    
    return (morning_start <= time_only <= morning_end) or \
           (afternoon_start <= time_only <= afternoon_end)

def generate_email_subject(ticker: str, action: str, date: Optional[datetime] = None) -> str:
    """Generate email subject line for stock advisory"""
    if date is None:
        date = get_vietnam_time()
    
    date_str = date.strftime("%Y-%m-%d")
    action_emoji = {
        "buy": "🚀",
        "add": "📈", 
        "add_small": "📊",
        "hold": "⚖️",
        "trim": "📉",
        "reduce": "⚠️",
        "exit": "🚨",
        "take_profit": "💰"
    }
    
    emoji = action_emoji.get(action.lower(), "📊")
    return f"{emoji} {ticker} Advisory: {action.title()} - {date_str}"

def parse_cron_expression(cron_expr: str) -> Dict[str, str]:
    """Parse cron expression into components"""
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {cron_expr}")
    
    return {
        "minute": parts[0],
        "hour": parts[1], 
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4]
    }

def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra spaces and normalize
    sanitized = ' '.join(sanitized.split())
    # Limit length
    return sanitized[:255]

def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0, 
                      backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Retry function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry on
    """
    import time
    import logging
    
    logger = logging.getLogger(__name__)
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries:
                logger.error(f"Function failed after {max_retries + 1} attempts: {e}")
                raise
            
            delay = initial_delay * (backoff_factor ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
            time.sleep(delay)

def load_json_file(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Safely load JSON file with error handling
    
    Args:
        file_path: Path to JSON file
        default: Default value to return if file doesn't exist or is invalid
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if default is not None:
            return default
        raise

def save_json_file(data: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """
    Safely save data to JSON file
    
    Args:
        data: Data to save
        file_path: Path to save JSON file
        indent: JSON indentation level
    """
    # Ensure directory exists
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)

def calculate_risk_score(pl_pct: float, volatility: float, max_drawdown: float) -> str:
    """
    Calculate risk score based on various factors
    
    Args:
        pl_pct: Current P/L percentage
        volatility: Estimated volatility (0-1 scale)
        max_drawdown: Maximum allowed drawdown percentage
        
    Returns:
        Risk score: "LOW", "MEDIUM", "HIGH", "CRITICAL"
    """
    risk_score = 0
    
    # P/L factor
    if pl_pct < max_drawdown * 0.8:  # Close to max drawdown
        risk_score += 3
    elif pl_pct < 0:  # In loss
        risk_score += 1
    
    # Volatility factor
    if volatility > 0.3:  # High volatility
        risk_score += 2
    elif volatility > 0.2:  # Medium volatility
        risk_score += 1
    
    # Drawdown proximity
    if pl_pct < max_drawdown * 0.5:  # Very close to max drawdown
        risk_score += 2
    
    if risk_score >= 5:
        return "CRITICAL"
    elif risk_score >= 3:
        return "HIGH"
    elif risk_score >= 1:
        return "MEDIUM"
    else:
        return "LOW"

def format_large_number(value: Union[int, float], suffix_map: Optional[Dict[int, str]] = None) -> str:
    """
    Format large numbers with appropriate suffixes (K, M, B)
    
    Args:
        value: Number to format
        suffix_map: Custom suffix mapping
        
    Returns:
        Formatted number string
    """
    if suffix_map is None:
        suffix_map = {
            9: 'B',   # Billion
            6: 'M',   # Million
            3: 'K'    # Thousand
        }
    
    if abs(value) < 1000:
        return str(int(value))
    
    for exp, suffix in sorted(suffix_map.items(), reverse=True):
        threshold = 10 ** exp
        if abs(value) >= threshold:
            formatted = value / threshold
            if formatted == int(formatted):
                return f"{int(formatted)}{suffix}"
            else:
                return f"{formatted:.1f}{suffix}"
    
    return str(int(value))

def validate_holdings_structure(holdings_data: Dict[str, Any]) -> List[str]:
    """
    Validate holdings JSON structure and return list of errors
    
    Args:
        holdings_data: Holdings data dictionary
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Check required top-level fields
    required_fields = ['owner', 'currency', 'timezone', 'positions']
    for field in required_fields:
        if field not in holdings_data:
            errors.append(f"Missing required field: {field}")
    
    # Check currency
    if holdings_data.get('currency') != 'VND':
        errors.append("Currency must be 'VND'")
    
    # Check positions
    positions = holdings_data.get('positions', [])
    if not isinstance(positions, list):
        errors.append("Positions must be a list")
    elif not positions:
        errors.append("At least one position is required")
    else:
        for i, position in enumerate(positions):
            position_errors = validate_position_structure(position, i)
            errors.extend(position_errors)
    
    return errors

def validate_position_structure(position: Dict[str, Any], index: int) -> List[str]:
    """Validate individual position structure"""
    errors = []
    prefix = f"Position {index + 1}"
    
    required_fields = ['ticker', 'exchange', 'shares', 'avg_price', 'target_price']
    for field in required_fields:
        if field not in position:
            errors.append(f"{prefix}: Missing required field '{field}'")
    
    # Validate ticker
    ticker = position.get('ticker', '')
    if not ticker or not isinstance(ticker, str):
        errors.append(f"{prefix}: Invalid ticker")
    
    # Validate exchange
    exchange = position.get('exchange', '')
    if not validate_exchange(exchange):
        errors.append(f"{prefix}: Invalid exchange '{exchange}'. Must be HOSE, HNX, or UPCoM")
    
    # Validate numeric fields
    numeric_fields = ['shares', 'avg_price', 'target_price']
    for field in numeric_fields:
        value = position.get(field)
        if not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"{prefix}: {field} must be a positive number")
    
    # Validate max_drawdown_pct if present
    max_drawdown = position.get('max_drawdown_pct')
    if max_drawdown is not None:
        if not isinstance(max_drawdown, (int, float)) or max_drawdown >= 0:
            errors.append(f"{prefix}: max_drawdown_pct must be a negative number")
    
    return errors
    required_keys = {'ticker', 'exchange', 'shares', 'avg_price', 'target_price', 'max_drawdown_pct'}
    for position in holdings.get('positions', []):
        if not required_keys.issubset(position.keys()):
            raise ValueError(f"Missing required keys in position: {position}")