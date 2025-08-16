from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Exchange(str, Enum):
    HOSE = "HOSE"
    HNX = "HNX"
    UPCoM = "UPCoM"

class Quote(BaseModel):
    ticker: str
    exchange: Exchange
    price: float
    change: float = 0
    change_pct: float = 0
    volume: int = 0
    timestamp: datetime
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper()
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

class OHLCVData(BaseModel):
    dates: List[str]
    open: List[float]
    high: List[float]
    low: List[float]
    close: List[float]
    volume: List[int]
    
    @validator('dates', 'open', 'high', 'low', 'close', 'volume')
    def lists_must_have_same_length(cls, v, values):
        if 'dates' in values and len(v) != len(values['dates']):
            raise ValueError('All OHLCV lists must have the same length')
        return v
    
    def get_latest_close(self) -> Optional[float]:
        """Get the most recent closing price"""
        return self.close[-1] if self.close else None
    
    def get_price_range(self, days: int = None) -> Dict[str, float]:
        """Get high/low for specified days (or all data if None)"""
        if not self.high or not self.low:
            return {"high": 0, "low": 0}
        
        if days and days < len(self.high):
            highs = self.high[-days:]
            lows = self.low[-days:]
        else:
            highs = self.high
            lows = self.low
        
        return {"high": max(highs), "low": min(lows)}

class Fundamentals(BaseModel):
    ticker: str
    pe_ratio: float = 0
    eps: float = 0
    book_value: float = 0
    dividend_yield: float = 0
    market_cap: float = 0
    sector: str = "Unknown"
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    revenue_growth: Optional[float] = None
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper()

class NewsItem(BaseModel):
    title: str
    summary: str
    sentiment: float  # -1 to 1
    date: datetime
    source: str
    url: Optional[str] = None
    
    @validator('sentiment')
    def sentiment_must_be_in_range(cls, v):
        if not -1 <= v <= 1:
            raise ValueError('Sentiment must be between -1 and 1')
        return v

class NewsSentiment(BaseModel):
    ticker: str
    news: List[NewsItem]
    overall_sentiment: float
    sentiment_summary: Optional[str] = None
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper()
    
    @validator('overall_sentiment')
    def overall_sentiment_must_be_in_range(cls, v):
        if not -1 <= v <= 1:
            raise ValueError('Overall sentiment must be between -1 and 1')
        return v

class MarketData(BaseModel):
    ticker: str
    exchange: Exchange
    quote: Quote
    ohlcv: Optional[OHLCVData] = None
    fundamentals: Optional[Fundamentals] = None
    news_sentiment: Optional[NewsSentiment] = None
    last_updated: datetime = datetime.now()
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper()
    
    @property
    def price(self) -> float:
        """Convenience property for current price"""
        return self.quote.price
    
    @property
    def volume(self) -> int:
        """Convenience property for current volume"""
        return self.quote.volume
    
    def get_ohlcv_dict(self) -> Dict[str, List]:
        """Get OHLCV data as dictionary for technical analysis"""
        if not self.ohlcv:
            return {}
        
        return {
            "open": self.ohlcv.open,
            "high": self.ohlcv.high,
            "low": self.ohlcv.low,
            "close": self.ohlcv.close,
            "volume": self.ohlcv.volume,
            "dates": self.ohlcv.dates
        }
    
    def is_data_fresh(self, max_age_minutes: int = 15) -> bool:
        """Check if market data is fresh"""
        age = datetime.now() - self.last_updated
        return age.total_seconds() < (max_age_minutes * 60)
    
    def update_quote(self, new_quote: Quote) -> None:
        """Update quote data"""
        self.quote = new_quote
        self.last_updated = datetime.now()
    
    def update_fundamentals(self, new_fundamentals: Fundamentals) -> None:
        """Update fundamental data"""
        self.fundamentals = new_fundamentals
        self.last_updated = datetime.now()
    
    def update_news_sentiment(self, new_news: NewsSentiment) -> None:
        """Update news sentiment data"""
        self.news_sentiment = new_news
        self.last_updated = datetime.now()

class MarketDataCache(BaseModel):
    """Cache for market data to avoid excessive API calls"""
    data: Dict[str, MarketData] = {}
    cache_ttl_minutes: int = 5
    
    def get(self, ticker: str) -> Optional[MarketData]:
        """Get market data from cache if fresh"""
        ticker = ticker.upper()
        if ticker not in self.data:
            return None
        
        market_data = self.data[ticker]
        if market_data.is_data_fresh(self.cache_ttl_minutes):
            return market_data
        
        # Remove stale data
        del self.data[ticker]
        return None
    
    def set(self, ticker: str, market_data: MarketData) -> None:
        """Store market data in cache"""
        ticker = ticker.upper()
        self.data[ticker] = market_data
    
    def clear_stale(self) -> int:
        """Remove all stale entries and return count removed"""
        stale_tickers = []
        for ticker, market_data in self.data.items():
            if not market_data.is_data_fresh(self.cache_ttl_minutes):
                stale_tickers.append(ticker)
        
        for ticker in stale_tickers:
            del self.data[ticker]
        
        return len(stale_tickers)
    
    def clear_all(self) -> None:
        """Clear all cached data"""
        self.data.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics"""
        fresh_count = sum(1 for md in self.data.values() if md.is_data_fresh(self.cache_ttl_minutes))
        return {
            "total_entries": len(self.data),
            "fresh_entries": fresh_count,
            "stale_entries": len(self.data) - fresh_count,
            "tickers": list(self.data.keys())
        }

    def set_news_sentiment(self, sentiment_data):
        self.news_sentiment = sentiment_data

    def get_summary(self):
        return {
            "ticker": self.ticker,
            "exchange": self.exchange,
            "price": self.price,
            "volume": self.volume,
            "ohlc": self.ohlc,
            "fundamentals": self.fundamentals,
            "news_sentiment": self.news_sentiment,
        }