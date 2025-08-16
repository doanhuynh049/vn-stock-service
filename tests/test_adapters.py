import pytest
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.mock_provider import MockProvider
from src.adapters.vn_data_provider import DataProviderFactory
from src.adapters.base import DataProviderError, RateLimitError, DataNotFoundError


class TestMockProvider(unittest.TestCase):
    def setUp(self):
        self.provider = MockProvider()

    def test_get_quote(self):
        """Test getting quote data"""
        ticker = "FPT"
        quote = self.provider.get_quote(ticker, "HOSE")
        
        self.assertIn("ticker", quote)
        self.assertIn("price", quote)
        self.assertIn("change", quote)
        self.assertIn("change_pct", quote)
        self.assertIn("volume", quote)
        self.assertIn("timestamp", quote)
        self.assertEqual(quote["ticker"], ticker)
        self.assertEqual(quote["exchange"], "HOSE")
        self.assertIsInstance(quote["price"], (int, float))
        self.assertGreater(quote["price"], 0)

    def test_get_ohlcv(self):
        """Test getting OHLCV data"""
        ticker = "FPT"
        ohlcv = self.provider.get_ohlcv(ticker, "1M", "HOSE")
        
        self.assertIn("ticker", ohlcv)
        self.assertIn("exchange", ohlcv)
        self.assertIn("data", ohlcv)
        
        data = ohlcv["data"]
        self.assertIn("dates", data)
        self.assertIn("open", data)
        self.assertIn("high", data)
        self.assertIn("low", data)
        self.assertIn("close", data)
        self.assertIn("volume", data)
        
        # All lists should have same length
        length = len(data["dates"])
        self.assertEqual(len(data["open"]), length)
        self.assertEqual(len(data["high"]), length)
        self.assertEqual(len(data["low"]), length)
        self.assertEqual(len(data["close"]), length)
        self.assertEqual(len(data["volume"]), length)
        
        # Check OHLC relationships
        for i in range(length):
            high = data["high"][i]
            low = data["low"][i]
            open_price = data["open"][i]
            close = data["close"][i]
            
            self.assertGreaterEqual(high, max(open_price, close))
            self.assertLessEqual(low, min(open_price, close))

    def test_get_fundamentals(self):
        """Test getting fundamental data"""
        ticker = "FPT"
        fundamentals = self.provider.get_fundamentals(ticker, "HOSE")
        
        required_fields = ["ticker", "pe_ratio", "eps", "book_value", 
                          "dividend_yield", "market_cap", "sector"]
        
        for field in required_fields:
            self.assertIn(field, fundamentals)
        
        self.assertEqual(fundamentals["ticker"], ticker)
        self.assertIsInstance(fundamentals["pe_ratio"], (int, float))
        self.assertIsInstance(fundamentals["market_cap"], (int, float))

    def test_get_news(self):
        """Test getting news data"""
        ticker = "FPT"
        news = self.provider.get_news(ticker, limit=5)
        
        self.assertIn("ticker", news)
        self.assertIn("news", news)
        self.assertIn("overall_sentiment", news)
        
        self.assertEqual(news["ticker"], ticker)
        self.assertIsInstance(news["news"], list)
        self.assertLessEqual(len(news["news"]), 5)
        self.assertTrue(-1 <= news["overall_sentiment"] <= 1)
        
        # Check news item structure
        for news_item in news["news"]:
            required_fields = ["title", "summary", "sentiment", "date", "source"]
            for field in required_fields:
                self.assertIn(field, news_item)
            
            self.assertTrue(-1 <= news_item["sentiment"] <= 1)

    def test_health_check(self):
        """Test health check"""
        self.assertTrue(self.provider.health_check())

    def test_different_timeframes(self):
        """Test different time windows"""
        ticker = "VNM"
        windows = ["1D", "5D", "1M", "3M", "6M", "1Y"]
        
        for window in windows:
            ohlcv = self.provider.get_ohlcv(ticker, window, "HOSE")
            self.assertIn("data", ohlcv)
            self.assertGreater(len(ohlcv["data"]["dates"]), 0)


class TestDataProviderFactory(unittest.TestCase):
    def test_create_mock_provider(self):
        """Test creating mock provider"""
        provider = DataProviderFactory.create_provider("mock")
        self.assertIsInstance(provider, MockProvider)

    def test_invalid_provider_type(self):
        """Test invalid provider type raises error"""
        with self.assertRaises(ValueError):
            DataProviderFactory.create_provider("invalid_provider")

    def test_get_available_providers(self):
        """Test getting list of available providers"""
        providers = DataProviderFactory.get_available_providers()
        self.assertIn("mock", providers)
        self.assertIsInstance(providers, list)


class TestDataProviderInterface(unittest.TestCase):
    def setUp(self):
        self.provider = MockProvider()

    def test_ticker_normalization(self):
        """Test that tickers are normalized to uppercase"""
        quote = self.provider.get_quote("fpt", "HOSE")
        self.assertEqual(quote["ticker"], "FPT")

    def test_exchange_validation(self):
        """Test exchange validation"""
        valid_exchanges = ["HOSE", "HNX", "UPCoM"]
        for exchange in valid_exchanges:
            quote = self.provider.get_quote("FPT", exchange)
            self.assertEqual(quote["exchange"], exchange)

    def test_price_consistency(self):
        """Test that prices are reasonable and consistent"""
        ticker = "FPT"
        
        # Get multiple quotes
        quotes = [self.provider.get_quote(ticker) for _ in range(5)]
        
        for quote in quotes:
            self.assertGreater(quote["price"], 0)
            self.assertIsInstance(quote["price"], (int, float))
        
        # Prices should be within reasonable range for VN market
        prices = [q["price"] for q in quotes]
        avg_price = sum(prices) / len(prices)
        
        for price in prices:
            # Should be within ±10% of average (reasonable volatility)
            self.assertLess(abs(price - avg_price) / avg_price, 0.1)


class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.provider = MockProvider()

    def test_empty_ticker(self):
        """Test handling of empty ticker"""
        # Mock provider should handle empty tickers gracefully
        quote = self.provider.get_quote("", "HOSE")
        self.assertIn("ticker", quote)

    def test_invalid_window(self):
        """Test handling of invalid time window"""
        ohlcv = self.provider.get_ohlcv("FPT", "invalid_window", "HOSE")
        # Should return some default data
        self.assertIn("data", ohlcv)

    @patch('src.adapters.mock_provider.random.uniform')
    def test_deterministic_output(self, mock_random):
        """Test deterministic output for testing"""
        mock_random.return_value = 0.05  # Fixed 5% variation
        
        quote1 = self.provider.get_quote("FPT")
        quote2 = self.provider.get_quote("FPT")
        
        # With fixed random seed, prices should be identical
        self.assertEqual(quote1["price"], quote2["price"])


if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMockProvider,
        TestDataProviderFactory,
        TestDataProviderInterface,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
        self.assertIn("volume", ohlc)

    def test_get_fundamentals(self):
        ticker = "FPT"
        fundamentals = self.provider.get_fundamentals(ticker)
        self.assertIn("pe_ttm", fundamentals)
        self.assertIn("dividend_yield", fundamentals)

    def test_get_news(self):
        ticker = "FPT"
        news = self.provider.get_news(ticker)
        self.assertIsInstance(news, list)

if __name__ == "__main__":
    unittest.main()