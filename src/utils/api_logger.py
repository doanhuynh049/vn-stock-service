import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import uuid

class APILogger:
    """
    Comprehensive API logging system for tracking all API requests and responses
    Logs to both file and structured JSON format for easy analysis
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create separate loggers for different purposes
        self.setup_loggers()
    
    def setup_loggers(self):
        """Setup different loggers for API tracking"""
        
        # Main API logger (detailed logs)
        self.api_logger = logging.getLogger('api_requests')
        self.api_logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.api_logger.handlers[:]:
            self.api_logger.removeHandler(handler)
        
        # File handler for detailed API logs
        api_log_file = self.log_dir / "api_requests.log"
        api_handler = logging.FileHandler(api_log_file, encoding='utf-8')
        api_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        api_handler.setFormatter(api_formatter)
        self.api_logger.addHandler(api_handler)
        
        # JSON logger for structured data
        self.json_logger = logging.getLogger('api_json')
        self.json_logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in self.json_logger.handlers[:]:
            self.json_logger.removeHandler(handler)
        
        # JSON file handler
        json_log_file = self.log_dir / "api_requests.jsonl"
        json_handler = logging.FileHandler(json_log_file, encoding='utf-8')
        json_formatter = logging.Formatter('%(message)s')
        json_handler.setFormatter(json_formatter)
        self.json_logger.addHandler(json_handler)
        
        # Error logger for API failures
        self.error_logger = logging.getLogger('api_errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # Remove existing handlers
        for handler in self.error_logger.handlers[:]:
            self.error_logger.removeHandler(handler)
        
        # Error file handler
        error_log_file = self.log_dir / "api_errors.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_formatter = logging.Formatter(
            '%(asctime)s | ERROR | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)
    
    def log_request(self, 
                   api_name: str,
                   method: str,
                   url: str,
                   headers: Optional[Dict] = None,
                   params: Optional[Dict] = None,
                   payload: Optional[Dict] = None,
                   request_id: Optional[str] = None) -> str:
        """
        Log an outgoing API request
        
        Args:
            api_name: Name of the API (e.g., 'SSI', 'Gemini', 'CafeF')
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers (sensitive data will be masked)
            params: URL parameters
            payload: Request body/payload
            request_id: Optional request ID for correlation
        
        Returns:
            Request ID for correlation with response
        """
        if not request_id:
            request_id = str(uuid.uuid4())[:8]
        
        # Mask sensitive data in headers
        safe_headers = self._mask_sensitive_data(headers) if headers else None
        safe_payload = self._mask_sensitive_data(payload) if payload else None
        
        # Create request log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "type": "REQUEST",
            "api_name": api_name,
            "method": method,
            "url": self._mask_url_credentials(url),
            "headers": safe_headers,
            "params": params,
            "payload": safe_payload,
            "payload_size": len(json.dumps(payload)) if payload else 0
        }
        
        # Log to both structured and human-readable formats
        self.api_logger.info(f"REQUEST | {api_name} | {method} {url} | ID: {request_id}")
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        return request_id
    
    def log_response(self,
                    request_id: str,
                    api_name: str,
                    status_code: int,
                    response_data: Optional[Any] = None,
                    response_headers: Optional[Dict] = None,
                    duration_ms: Optional[float] = None,
                    error: Optional[str] = None) -> None:
        """
        Log an API response
        
        Args:
            request_id: Request ID from log_request
            api_name: Name of the API
            status_code: HTTP status code
            response_data: Response body/data
            response_headers: Response headers
            duration_ms: Request duration in milliseconds
            error: Error message if request failed
        """
        
        # Determine response size
        response_size = 0
        if response_data:
            try:
                response_size = len(json.dumps(response_data)) if isinstance(response_data, (dict, list)) else len(str(response_data))
            except:
                response_size = len(str(response_data))
        
        # Create response log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "type": "RESPONSE",
            "api_name": api_name,
            "status_code": status_code,
            "response_size": response_size,
            "duration_ms": duration_ms,
            "success": 200 <= status_code < 300,
            "error": error,
            "response_headers": self._mask_sensitive_data(response_headers) if response_headers else None
        }
        
        # Add response data if not too large
        if response_size < 10000:  # Less than 10KB
            log_entry["response_data"] = response_data
        else:
            log_entry["response_data"] = f"<Large response: {response_size} bytes>"
        
        # Log to different files based on success/failure
        status_emoji = "✅" if log_entry["success"] else "❌"
        duration_str = f" | {duration_ms:.0f}ms" if duration_ms else ""
        
        self.api_logger.info(
            f"RESPONSE | {api_name} | {status_emoji} {status_code} | ID: {request_id}{duration_str}"
        )
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        # Log errors separately
        if error or not log_entry["success"]:
            error_msg = f"API_ERROR | {api_name} | {status_code} | {error or 'HTTP Error'} | ID: {request_id}"
            self.error_logger.error(error_msg)
    
    def log_ai_request(self,
                      provider: str,
                      model: str,
                      prompt: str,
                      request_id: Optional[str] = None) -> str:
        """
        Log AI/LLM API request with special handling for prompts
        
        Args:
            provider: AI provider (e.g., 'Gemini', 'OpenAI')
            model: Model name
            prompt: AI prompt text
            request_id: Optional request ID
        
        Returns:
            Request ID for correlation
        """
        if not request_id:
            request_id = str(uuid.uuid4())[:8]
        
        # Truncate very long prompts for logging
        prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "type": "AI_REQUEST",
            "provider": provider,
            "model": model,
            "prompt_length": len(prompt),
            "prompt_preview": prompt_preview
        }
        
        self.api_logger.info(f"AI_REQUEST | {provider} | {model} | {len(prompt)} chars | ID: {request_id}")
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        return request_id
    
    def log_ai_response(self,
                       request_id: str,
                       provider: str,
                       response_text: str,
                       tokens_used: Optional[int] = None,
                       duration_ms: Optional[float] = None,
                       error: Optional[str] = None) -> None:
        """
        Log AI/LLM API response
        
        Args:
            request_id: Request ID from log_ai_request
            provider: AI provider name
            response_text: AI response text
            tokens_used: Number of tokens consumed
            duration_ms: Request duration
            error: Error message if failed
        """
        
        # Truncate long responses for logging
        response_preview = response_text[:1000] + "..." if len(response_text) > 1000 else response_text
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "type": "AI_RESPONSE",
            "provider": provider,
            "response_length": len(response_text),
            "response_preview": response_preview,
            "tokens_used": tokens_used,
            "duration_ms": duration_ms,
            "success": error is None,
            "error": error
        }
        
        status_emoji = "✅" if not error else "❌"
        duration_str = f" | {duration_ms:.0f}ms" if duration_ms else ""
        tokens_str = f" | {tokens_used} tokens" if tokens_used else ""
        
        self.api_logger.info(
            f"AI_RESPONSE | {provider} | {status_emoji} {len(response_text)} chars | ID: {request_id}{duration_str}{tokens_str}"
        )
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        if error:
            self.error_logger.error(f"AI_ERROR | {provider} | {error} | ID: {request_id}")
    
    def _mask_sensitive_data(self, data: Dict) -> Dict:
        """Mask sensitive information in API data"""
        if not data:
            return data
        
        sensitive_keys = {
            'authorization', 'auth', 'token', 'key', 'secret', 'password', 'pass',
            'api_key', 'apikey', 'api-key', 'bearer', 'x-api-key'
        }
        
        masked_data = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                masked_data[key] = "***MASKED***"
            else:
                masked_data[key] = value
        
        return masked_data
    
    def _mask_url_credentials(self, url: str) -> str:
        """Mask credentials in URLs"""
        import re
        # Mask API keys in URLs
        return re.sub(r'[?&]key=([^&]+)', r'?key=***MASKED***', url)
    
    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get API usage statistics for the last N hours
        
        Args:
            hours: Number of hours to analyze
        
        Returns:
            Dictionary with usage statistics
        """
        stats = {
            "period_hours": hours,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "apis": {},
            "avg_duration_ms": 0,
            "error_rate": 0
        }
        
        try:
            json_log_file = self.log_dir / "api_requests.jsonl"
            if not json_log_file.exists():
                return stats
            
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            durations = []
            
            with open(json_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(entry["timestamp"]).timestamp()
                        
                        if entry_time < cutoff_time:
                            continue
                        
                        if entry["type"] == "RESPONSE":
                            api_name = entry["api_name"]
                            stats["total_requests"] += 1
                            
                            if api_name not in stats["apis"]:
                                stats["apis"][api_name] = {
                                    "total": 0, "success": 0, "errors": 0
                                }
                            
                            stats["apis"][api_name]["total"] += 1
                            
                            if entry["success"]:
                                stats["successful_requests"] += 1
                                stats["apis"][api_name]["success"] += 1
                            else:
                                stats["failed_requests"] += 1
                                stats["apis"][api_name]["errors"] += 1
                            
                            if entry.get("duration_ms"):
                                durations.append(entry["duration_ms"])
                    
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            # Calculate averages
            if stats["total_requests"] > 0:
                stats["error_rate"] = stats["failed_requests"] / stats["total_requests"]
            
            if durations:
                stats["avg_duration_ms"] = sum(durations) / len(durations)
        
        except Exception as e:
            self.error_logger.error(f"Error calculating statistics: {e}")
        
        return stats
    
    def cleanup_old_logs(self, days: int = 30) -> None:
        """Remove log files older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.api_logger.info(f"Cleaned up old log file: {log_file}")
        
        except Exception as e:
            self.error_logger.error(f"Error cleaning up logs: {e}")

# Global API logger instance
api_logger = APILogger()

def log_api_call(api_name: str, method: str, url: str, **kwargs):
    """Decorator for logging API calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            request_id = api_logger.log_request(api_name, method, url, **kwargs)
            
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Assume success if no exception
                api_logger.log_response(
                    request_id=request_id,
                    api_name=api_name,
                    status_code=200,
                    response_data=result,
                    duration_ms=duration
                )
                return result
            
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                api_logger.log_response(
                    request_id=request_id,
                    api_name=api_name,
                    status_code=500,
                    duration_ms=duration,
                    error=str(e)
                )
                raise
        
        return wrapper
    return decorator
