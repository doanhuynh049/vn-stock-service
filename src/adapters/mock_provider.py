import random
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from adapters.base import DataProviderInterface

logger = logging.getLogger(__name__)

class MockProvider(DataProviderInterface):
    """Mock data provider for testing and development"""
    
    def __init__(self):
        # Updated with more realistic current market prices (August 2025)
        self.base_prices = {
            "FPT": 101000,  # Current market price ~101K
            "VCB": 55500,   # Current market price ~55.5K  
            "TCB": 23000,   # Current market price ~23K
            "ACB": 21800,   # Current market price ~21.8K
            "BID": 33500,   # Current market price ~33.5K
            "HPG": 20500,   # Current market price ~20.5K
            "MSN": 68000,   # Current market price ~68K
            "VNM": 54000,   # Current market price ~54K
            "KDH": 25500,   # Current market price ~25.5K
            "HDG": 23200,   # Current market price ~23.2K
            "CMG": 34500,   # Current market price ~34.5K
            # Keep existing ones for backward compatibility
            "VIC": 85000,
            "VHM": 65000,
            "GVR": 18000,
            "NVL": 12000,
            "POW": 11000
        }
        
    def get_quote(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """Generate mock quote data"""
        base_price = self.base_prices.get(ticker, 50000)
        
        # Add some realistic daily price variation
        price_variation = random.uniform(-0.03, 0.03)  # ±3% daily (more realistic)
        current_price = base_price * (1 + price_variation)
        
        change = current_price - base_price
        change_pct = (change / base_price) * 100
        
        volume = random.randint(10000, 1000000)
        
        return {
            "ticker": ticker,
            "exchange": exchange,
            "price": round(current_price, 0),
            "change": round(change, 0),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "timestamp": datetime.now().isoformat()
        }

    def get_ohlcv(self, ticker: str, window: str = "1D", exchange: str = "HOSE") -> Dict[str, Any]:
        """Generate mock OHLCV data"""
        base_price = self.base_prices.get(ticker, 50000)
        
        # Determine number of data points based on window
        window_map = {
            "1D": 1,
            "5D": 5,
            "1M": 20,
            "3M": 60,
            "6M": 120,
            "1Y": 252
        }
        
        num_points = window_map.get(window, 20)
        
        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        current_price = base_price
        
        for i in range(num_points):
            date = datetime.now() - timedelta(days=num_points-i-1)
            dates.append(date.strftime("%Y-%m-%d"))
            
            # Generate realistic OHLC data
            daily_change = random.uniform(-0.03, 0.03)  # ±3% daily
            open_price = current_price
            
            high_price = open_price * (1 + random.uniform(0, 0.02))  # Up to 2% higher
            low_price = open_price * (1 - random.uniform(0, 0.02))   # Up to 2% lower
            close_price = open_price * (1 + daily_change)
            
            # Ensure OHLC relationships are valid
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            opens.append(round(open_price, 0))
            highs.append(round(high_price, 0))
            lows.append(round(low_price, 0))
            closes.append(round(close_price, 0))
            volumes.append(random.randint(50000, 500000))
            
            current_price = close_price
        
        return {
            "ticker": ticker,
            "exchange": exchange,
            "data": {
                "dates": dates,
                "open": opens,
                "high": highs,
                "low": lows,
                "close": closes,
                "volume": volumes
            }
        }

    def get_fundamentals(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """Generate mock fundamental data"""
        # Mock fundamental ratios based on typical VN market values
        fundamentals_data = {
            "FPT": {"pe_ratio": 20.4, "eps": 5932, "dividend_yield": 2.1, "sector": "Technology"},
            "VNM": {"pe_ratio": 18.2, "eps": 3740, "dividend_yield": 4.5, "sector": "Consumer Staples"},
            "VIC": {"pe_ratio": 15.8, "eps": 5380, "dividend_yield": 1.8, "sector": "Real Estate"},
            "HPG": {"pe_ratio": 8.5, "eps": 2941, "dividend_yield": 3.2, "sector": "Materials"},
            "TCB": {"pe_ratio": 7.2, "eps": 3194, "dividend_yield": 5.1, "sector": "Banking"}
        }
        
        default_data = {"pe_ratio": 15.0, "eps": 3000, "dividend_yield": 3.0, "sector": "Unknown"}
        data = fundamentals_data.get(ticker, default_data)
        
        return {
            "ticker": ticker,
            "pe_ratio": data["pe_ratio"],
            "eps": data["eps"],
            "book_value": data["eps"] * data["pe_ratio"] * random.uniform(0.8, 1.2),
            "dividend_yield": data["dividend_yield"],
            "market_cap": random.randint(10000, 500000) * 1e9,  # Billion VND
            "sector": data["sector"]
        }

    def get_news(self, ticker: str, limit: int = 10) -> Dict[str, Any]:
        """Generate mock news data"""
        sample_news = [
            {
                "title": f"{ticker} announces Q3 earnings results",
                "summary": f"{ticker} reported strong quarterly performance with revenue growth",
                "sentiment": random.uniform(-0.2, 0.8),
                "date": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                "source": "VnExpress"
            },
            {
                "title": f"Market analysis: {ticker} outlook for next quarter",
                "summary": f"Analysts provide mixed outlook for {ticker} based on market conditions",
                "sentiment": random.uniform(-0.5, 0.5),
                "date": (datetime.now() - timedelta(days=random.randint(1, 14))).isoformat(),
                "source": "CafeF"
            },
            {
                "title": f"{ticker} board meeting scheduled",
                "summary": f"{ticker} announces upcoming board meeting to discuss strategic initiatives",
                "sentiment": random.uniform(0, 0.3),
                "date": (datetime.now() - timedelta(days=random.randint(2, 21))).isoformat(),
                "source": "StockBiz"
            }
        ]
        
        # Randomly select news items
        selected_news = random.sample(sample_news, min(limit, len(sample_news)))
        overall_sentiment = sum([news["sentiment"] for news in selected_news]) / len(selected_news)
        
        return {
            "ticker": ticker,
            "news": selected_news,
            "overall_sentiment": round(overall_sentiment, 2)
        }

    def health_check(self) -> bool:
        """Mock provider is always available"""
        return True