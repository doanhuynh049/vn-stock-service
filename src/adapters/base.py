from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class DataProviderInterface(ABC):
    """Base interface for Vietnam stock market data providers"""
    
    @abstractmethod
    def get_quote(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """
        Get current quote for a ticker
        Returns: {
            "ticker": str,
            "exchange": str,
            "price": float,
            "change": float,
            "change_pct": float,
            "volume": int,
            "timestamp": str
        }
        """
        pass

    @abstractmethod
    def get_ohlcv(self, ticker: str, window: str = "1D", exchange: str = "HOSE") -> Dict[str, Any]:
        """
        Get OHLCV data for a ticker
        Args:
            window: "1D", "5D", "1M", "3M", "6M", "1Y"
        Returns: {
            "ticker": str,
            "exchange": str,
            "data": {
                "dates": List[str],
                "open": List[float],
                "high": List[float], 
                "low": List[float],
                "close": List[float],
                "volume": List[int]
            }
        }
        """
        pass

    @abstractmethod
    def get_fundamentals(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """
        Get fundamental data for a ticker
        Returns: {
            "ticker": str,
            "pe_ratio": float,
            "eps": float,
            "book_value": float,
            "dividend_yield": float,
            "market_cap": float,
            "sector": str
        }
        """
        pass

    @abstractmethod
    def get_news(self, ticker: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent news for a ticker
        Returns: {
            "ticker": str,
            "news": List[{
                "title": str,
                "summary": str,
                "sentiment": float,  # -1 to 1
                "date": str,
                "source": str
            }],
            "overall_sentiment": float
        }
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the data provider is available"""
        pass

class DataProviderError(Exception):
    """Custom exception for data provider errors"""
    pass

class RateLimitError(DataProviderError):
    """Exception for rate limit exceeded"""
    pass

class DataNotFoundError(DataProviderError):
    """Exception for when ticker data is not found"""
    pass