import requests
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
from adapters.base import DataProviderInterface, DataProviderError, RateLimitError, DataNotFoundError

logger = logging.getLogger(__name__)

class VietCapitalProvider(DataProviderInterface):
    """
    Vietnam stock data provider using VietCapital API
    NOTE: This is a sample implementation. Replace with actual API endpoints.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.vietcap.com.vn"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "VN-Stock-Advisory/1.0",
            "Accept": "application/json"
        })
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def get_quote(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """Get current quote from VietCapital API"""
        try:
            url = f"{self.base_url}/securities/{ticker}/quote"
            params = {"exchange": exchange}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 404:
                raise DataNotFoundError(f"Ticker {ticker} not found")
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "ticker": ticker,
                "exchange": exchange,
                "price": data.get("last_price", 0),
                "change": data.get("change", 0),
                "change_pct": data.get("change_percent", 0),
                "volume": data.get("volume", 0),
                "timestamp": data.get("timestamp", datetime.now().isoformat())
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching quote for {ticker}: {e}")
            raise DataProviderError(f"Failed to fetch quote: {e}")
    
    def get_ohlcv(self, ticker: str, window: str = "1D", exchange: str = "HOSE") -> Dict[str, Any]:
        """Get OHLCV data from VietCapital API"""
        try:
            url = f"{self.base_url}/securities/{ticker}/ohlcv"
            params = {
                "exchange": exchange,
                "period": window,
                "limit": self._get_limit_for_window(window)
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 404:
                raise DataNotFoundError(f"OHLCV data for {ticker} not found")
                
            response.raise_for_status()
            data = response.json()
            
            return {
                "ticker": ticker,
                "exchange": exchange,
                "data": {
                    "dates": [item["date"] for item in data.get("data", [])],
                    "open": [item["open"] for item in data.get("data", [])],
                    "high": [item["high"] for item in data.get("data", [])],
                    "low": [item["low"] for item in data.get("data", [])],
                    "close": [item["close"] for item in data.get("data", [])],
                    "volume": [item["volume"] for item in data.get("data", [])]
                }
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching OHLCV for {ticker}: {e}")
            raise DataProviderError(f"Failed to fetch OHLCV: {e}")
    
    def get_fundamentals(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """Get fundamental data from VietCapital API"""
        try:
            url = f"{self.base_url}/securities/{ticker}/fundamentals"
            params = {"exchange": exchange}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 404:
                raise DataNotFoundError(f"Fundamentals for {ticker} not found")
                
            response.raise_for_status()
            data = response.json()
            
            return {
                "ticker": ticker,
                "pe_ratio": data.get("pe_ratio", 0),
                "eps": data.get("eps", 0),
                "book_value": data.get("book_value", 0),
                "dividend_yield": data.get("dividend_yield", 0),
                "market_cap": data.get("market_cap", 0),
                "sector": data.get("sector", "Unknown")
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching fundamentals for {ticker}: {e}")
            return {"ticker": ticker, "pe_ratio": 0, "eps": 0, "book_value": 0, 
                   "dividend_yield": 0, "market_cap": 0, "sector": "Unknown"}
    
    def get_news(self, ticker: str, limit: int = 10) -> Dict[str, Any]:
        """Get news from VietCapital API"""
        try:
            url = f"{self.base_url}/securities/{ticker}/news"
            params = {"limit": limit}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
                
            response.raise_for_status()
            data = response.json()
            
            news_items = []
            for item in data.get("news", []):
                news_items.append({
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "sentiment": item.get("sentiment", 0),
                    "date": item.get("date", ""),
                    "source": item.get("source", "Unknown")
                })
            
            overall_sentiment = sum([item["sentiment"] for item in news_items]) / len(news_items) if news_items else 0
            
            return {
                "ticker": ticker,
                "news": news_items,
                "overall_sentiment": round(overall_sentiment, 2)
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return {"ticker": ticker, "news": [], "overall_sentiment": 0}
    
    def health_check(self) -> bool:
        """Check if the API is available"""
        try:
            url = f"{self.base_url}/health"
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_limit_for_window(self, window: str) -> int:
        """Get appropriate data limit for time window"""
        limits = {
            "1D": 1,
            "5D": 5,
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365
        }
        return limits.get(window, 30)


class CafeFinanceProvider(DataProviderInterface):
    """
    Alternative provider using CafeF.vn (web scraping)
    WARNING: Web scraping should comply with Terms of Service
    """
    
    def __init__(self):
        self.base_url = "https://s.cafef.vn"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_quote(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """
        Scrape quote data from CafeF
        NOTE: This is for demonstration. Ensure compliance with ToS
        """
        try:
            url = f"{self.base_url}/Gia.chn/{ticker}-{exchange}.chn"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML (simplified example)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # This would need actual CSS selectors for CafeF's layout
            price_element = soup.find("div", {"class": "price"})  # Example selector
            
            if not price_element:
                raise DataNotFoundError(f"Could not find price data for {ticker}")
            
            # Extract price data (this is simplified)
            price = float(price_element.text.replace(",", "")) if price_element else 0
            
            return {
                "ticker": ticker,
                "exchange": exchange,
                "price": price,
                "change": 0,  # Would need to parse change
                "change_pct": 0,  # Would need to parse change %
                "volume": 0,  # Would need to parse volume
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping quote for {ticker}: {e}")
            raise DataProviderError(f"Failed to scrape quote: {e}")
    
    def get_ohlcv(self, ticker: str, window: str = "1D", exchange: str = "HOSE") -> Dict[str, Any]:
        """Scrape OHLCV data (placeholder implementation)"""
        # This would require more complex scraping
        raise NotImplementedError("OHLCV scraping not implemented yet")
    
    def get_fundamentals(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """Scrape fundamental data (placeholder implementation)"""
        # This would require scraping fundamental data pages
        return {
            "ticker": ticker,
            "pe_ratio": 0,
            "eps": 0,
            "book_value": 0,
            "dividend_yield": 0,
            "market_cap": 0,
            "sector": "Unknown"
        }
    
    def get_news(self, ticker: str, limit: int = 10) -> Dict[str, Any]:
        """Scrape news data (placeholder implementation)"""
        return {"ticker": ticker, "news": [], "overall_sentiment": 0}
    
    def health_check(self) -> bool:
        """Check if CafeF is accessible"""
        try:
            response = self.session.get(self.base_url, timeout=5)
            return response.status_code == 200
        except:
            return False


class DataProviderFactory:
    """Factory for creating data providers"""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> DataProviderInterface:
        """Create a data provider instance"""
        if provider_type == "mock":
            from adapters.mock_provider import MockProvider
            return MockProvider()
        elif provider_type == "vietcap":
            # Use the new real VN provider instead of placeholder
            from adapters.real_vn_provider import RealVNStockProvider
            return RealVNStockProvider(**kwargs)
        elif provider_type == "cafef":
            return CafeFinanceProvider()
        elif provider_type == "real":
            from adapters.real_vn_provider import RealVNStockProvider
            return RealVNStockProvider(**kwargs)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available provider types"""
        return ["mock", "vietcap", "cafef", "real"]