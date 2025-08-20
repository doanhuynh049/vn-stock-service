import requests
import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re
from adapters.base import DataProviderInterface, DataProviderError, RateLimitError, DataNotFoundError
from utils.api_logger import APILogger

logger = logging.getLogger(__name__)

class RealVNStockProvider(DataProviderInterface):
    """
    Simplified Vietnamese stock data provider using AI analysis
    - Primary: AI-based stock analysis and price estimation
    - Focuses on portfolio analysis rather than real-time data fetching
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "VN-Stock-Advisory/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        # Initialize API logger
        self.api_logger = APILogger()
        
        # Rate limiting for AI requests
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between AI requests
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits for AI requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def get_quote(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """Get AI-based stock analysis and price estimate"""
        try:
            self._rate_limit()
            return self._get_ai_stock_analysis(ticker, exchange)
        except Exception as e:
            logger.error(f"AI analysis failed for {ticker}: {e}")
            return self._get_basic_price_estimate(ticker, exchange)

    def _get_ai_stock_analysis(self, ticker: str, exchange: str) -> Dict[str, Any]:
        """Get comprehensive AI analysis for a Vietnamese stock"""
        try:
            from src.config.settings import settings
            
            # Create comprehensive prompt for stock analysis
            prompt = f"""You are a Vietnamese stock market expert. Analyze {ticker} ({exchange}) and provide comprehensive information.

Please provide current market data and analysis in the following JSON format:
{{
    "price": <estimated_current_price_in_VND>,
    "change": <estimated_price_change_in_VND>,
    "change_pct": <estimated_percentage_change>,
    "volume": <estimated_trading_volume>,
    "market_cap": <market_capitalization_in_VND>,
    "pe_ratio": <price_to_earnings_ratio>,
    "sector": "<sector_name>",
    "analysis": {{
        "fundamental_strength": "<strong/moderate/weak>",
        "technical_outlook": "<bullish/neutral/bearish>",
        "recommendation": "<buy/hold/sell>",
        "key_factors": ["factor1", "factor2", "factor3"],
        "risk_level": "<low/medium/high>",
        "target_price": <target_price_in_VND>,
        "stop_loss": <stop_loss_price_in_VND>
    }},
    "confidence": <confidence_level_0_to_1>,
    "source": "AI Analysis",
    "note": "Brief explanation of current market conditions"
}}

Stock: {ticker}
Exchange: {exchange}
Date: {datetime.now().strftime('%Y-%m-%d')}

Please provide realistic data based on recent Vietnamese market conditions and fundamental analysis."""

            # Call AI model
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            # Add API key to URL for Gemini
            url = f"{settings.LLM_PROVIDER}?key={settings.LLM_API_KEY}"
            
            # Log the AI API request
            start_time = time.time()
            request_id = self.api_logger.log_ai_request(
                api_name="Gemini_Stock_Analysis",
                method="POST",
                url=url,
                prompt=prompt,
                model_config={"ticker": ticker, "exchange": exchange, "type": "comprehensive_analysis"}
            )
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            duration_ms = (time.time() - start_time) * 1000
            response.raise_for_status()
            
            data = response.json()
            
            # Extract response text
            if 'candidates' in data and data['candidates']:
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
                
                # Log successful AI response
                self.api_logger.log_ai_response(
                    request_id=request_id,
                    api_name="Gemini_Stock_Analysis",
                    status_code=response.status_code,
                    ai_response=ai_response,
                    response_headers=dict(response.headers),
                    duration_ms=duration_ms,
                    usage_stats=data.get('usageMetadata', {})
                )
                
                # Try to parse JSON from AI response
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    ai_data = json.loads(json_match.group())
                    
                    # Extract basic price data
                    price = float(ai_data.get('price', 50000))
                    change = float(ai_data.get('change', 0))
                    change_pct = float(ai_data.get('change_pct', 0))
                    volume = int(ai_data.get('volume', 100000))
                    
                    logger.info(f"AI analysis for {ticker}: {price} VND (confidence: {ai_data.get('confidence', 'unknown')})")
                    
                    # Store full analysis data for later use
                    result = {
                        "ticker": ticker,
                        "exchange": exchange,
                        "price": price,
                        "change": change,
                        "change_pct": change_pct,
                        "volume": volume,
                        "timestamp": datetime.now().isoformat(),
                        "source": "AI_Analysis",
                        "confidence": ai_data.get('confidence', 0.7),
                        "analysis": ai_data.get('analysis', {}),
                        "market_cap": ai_data.get('market_cap', 0),
                        "pe_ratio": ai_data.get('pe_ratio', 15.0),
                        "sector": ai_data.get('sector', 'Unknown'),
                        "note": ai_data.get('note', 'AI-generated comprehensive analysis')
                    }
                    
                    return result
            
            # If AI parsing fails, return a basic estimate
            raise Exception("Could not parse AI response")
            
        except Exception as e:
            logger.error(f"AI analysis failed for {ticker}: {e}")
            return self._get_basic_price_estimate(ticker, exchange)
    
    def _get_basic_price_estimate(self, ticker: str, exchange: str) -> Dict[str, Any]:
        """Basic price estimate with fundamental data as last resort"""
        # Enhanced price estimates based on common Vietnamese stocks
        stock_data = {
            "FPT": {"price": 125000, "sector": "Technology", "pe": 18.5, "recommendation": "buy"},
            "VCB": {"price": 65000, "sector": "Banking", "pe": 12.3, "recommendation": "hold"},
            "TCB": {"price": 40000, "sector": "Banking", "pe": 8.9, "recommendation": "hold"},
            "ACB": {"price": 25000, "sector": "Banking", "pe": 10.2, "recommendation": "hold"},
            "BID": {"price": 40000, "sector": "Banking", "pe": 11.5, "recommendation": "hold"},
            "HPG": {"price": 25000, "sector": "Steel & Materials", "pe": 7.8, "recommendation": "buy"},
            "MSN": {"price": 75000, "sector": "Consumer Goods", "pe": 22.1, "recommendation": "hold"},
            "VNM": {"price": 60000, "sector": "Food & Beverages", "pe": 16.3, "recommendation": "hold"},
            "KDH": {"price": 30000, "sector": "Real Estate", "pe": 9.4, "recommendation": "buy"},
            "HDG": {"price": 27000, "sector": "Construction", "pe": 8.2, "recommendation": "hold"},
            "CMG": {"price": 40000, "sector": "Steel & Materials", "pe": 9.1, "recommendation": "hold"}
        }
        
        data = stock_data.get(ticker, {
            "price": 50000, "sector": "Unknown", "pe": 15.0, "recommendation": "hold"
        })
        
        estimated_price = data["price"]
        
        logger.warning(f"Using basic estimate for {ticker}: {estimated_price} VND")
        
        return {
            "ticker": ticker,
            "exchange": exchange,
            "price": estimated_price,
            "change": 0,
            "change_pct": 0,
            "volume": 100000,
            "timestamp": datetime.now().isoformat(),
            "source": "Basic_Estimate",
            "confidence": 0.3,
            "pe_ratio": data["pe"],
            "sector": data["sector"],
            "analysis": {
                "fundamental_strength": "moderate",
                "technical_outlook": "neutral",
                "recommendation": data["recommendation"],
                "key_factors": ["Market volatility", "Economic conditions"],
                "risk_level": "medium"
            },
            "note": "Basic fallback estimate with fundamental data"
        }

    def get_ohlcv(self, ticker: str, window: str = "1D", exchange: str = "HOSE") -> Dict[str, Any]:
        """Simplified OHLCV - returns AI-generated historical patterns"""
        try:
            # Since we're focusing on AI analysis, generate simple historical data
            # This is mainly for technical indicators if needed
            current_quote = self.get_quote(ticker, exchange)
            current_price = current_quote["price"]
            
            # Generate simple historical data around current price
            days = {"1D": 1, "5D": 5, "1M": 22, "3M": 66, "6M": 132, "1Y": 252}.get(window, 22)
            
            dates = []
            opens, highs, lows, closes, volumes = [], [], [], [], []
            
            base_price = current_price
            for i in range(days):
                date = (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
                dates.append(date)
                
                # Simple price variation around base price
                variation = (i - days/2) / days * 0.1  # ±10% variation
                daily_price = base_price * (1 + variation)
                
                opens.append(daily_price * 0.999)
                highs.append(daily_price * 1.02)
                lows.append(daily_price * 0.98)
                closes.append(daily_price)
                volumes.append(100000 + (i * 10000))
            
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
            
        except Exception as e:
            logger.error(f"Error generating OHLCV for {ticker}: {e}")
            raise DataProviderError(f"Failed to generate OHLCV: {e}")
    
    def get_fundamentals(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """Get AI-powered fundamental analysis"""
        try:
            # Get comprehensive analysis from AI
            quote_data = self.get_quote(ticker, exchange)
            
            # Extract fundamental data from the AI analysis
            if 'analysis' in quote_data:
                return {
                    "ticker": ticker,
                    "pe_ratio": quote_data.get('pe_ratio', 15.0),
                    "eps": quote_data.get('price', 50000) / quote_data.get('pe_ratio', 15.0),
                    "book_value": quote_data.get('price', 50000) * 0.8,  # Estimate
                    "dividend_yield": 3.0,  # Default estimate
                    "market_cap": quote_data.get('market_cap', 50000000000),
                    "sector": quote_data.get('sector', 'Unknown'),
                    "analysis": quote_data.get('analysis', {})
                }
            else:
                return self._get_basic_fundamentals(ticker)
            
        except Exception as e:
            logger.warning(f"Error getting AI fundamentals for {ticker}: {e}")
            return self._get_basic_fundamentals(ticker)
    
    def _get_basic_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Basic fundamental data as fallback"""
        # Sector mapping for Vietnamese stocks
        fundamentals_map = {
            "FPT": {"pe": 18.5, "sector": "Technology", "dividend": 2.8, "market_cap": 180000000000},
            "VCB": {"pe": 12.3, "sector": "Banking", "dividend": 4.5, "market_cap": 520000000000},
            "TCB": {"pe": 8.9, "sector": "Banking", "dividend": 5.2, "market_cap": 280000000000},
            "ACB": {"pe": 10.2, "sector": "Banking", "dividend": 4.8, "market_cap": 120000000000},
            "BID": {"pe": 11.5, "sector": "Banking", "dividend": 4.0, "market_cap": 200000000000},
            "HPG": {"pe": 7.8, "sector": "Steel & Materials", "dividend": 3.5, "market_cap": 160000000000},
            "MSN": {"pe": 22.1, "sector": "Consumer Goods", "dividend": 2.2, "market_cap": 95000000000},
            "VNM": {"pe": 16.3, "sector": "Food & Beverages", "dividend": 3.8, "market_cap": 300000000000}
        }
        
        data = fundamentals_map.get(ticker, {
            "pe": 15.0, "sector": "Unknown", "dividend": 3.0, "market_cap": 50000000000
        })
        
        return {
            "ticker": ticker,
            "pe_ratio": data["pe"],
            "eps": 3000,  # Estimated EPS
            "book_value": 45000,  # Estimated book value
            "dividend_yield": data["dividend"],
            "market_cap": data["market_cap"],
            "sector": data["sector"]
        }

    def get_news(self, ticker: str, limit: int = 10) -> Dict[str, Any]:
        """Get AI-generated news and market sentiment"""
        try:
            from src.config.settings import settings
            
            prompt = f"""You are a Vietnamese stock market news analyst. Generate relevant news insights for {ticker}.

Please provide news analysis in the following JSON format:
{{
    "news": [
        {{
            "title": "News headline",
            "summary": "Brief news summary",
            "sentiment": <sentiment_score_-1_to_1>,
            "date": "<ISO_date>",
            "source": "Market Analysis",
            "impact": "<high/medium/low>"
        }}
    ],
    "overall_sentiment": <overall_sentiment_-1_to_1>,
    "market_outlook": "Brief market outlook for {ticker}",
    "key_themes": ["theme1", "theme2", "theme3"]
}}

Please provide realistic market news and sentiment for Vietnamese stock {ticker} as of {datetime.now().strftime('%Y-%m-%d')}."""

            # Call AI for news analysis
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            
            url = f"{settings.LLM_PROVIDER}?key={settings.LLM_API_KEY}"
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            if 'candidates' in data and data['candidates']:
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    news_data = json.loads(json_match.group())
                    return {
                        "ticker": ticker,
                        "news": news_data.get("news", [])[:limit],
                        "overall_sentiment": news_data.get("overall_sentiment", 0),
                        "market_outlook": news_data.get("market_outlook", ""),
                        "key_themes": news_data.get("key_themes", [])
                    }
            
            # Fallback to generic news
            return self._get_generic_news(ticker)
            
        except Exception as e:
            logger.error(f"Error getting AI news for {ticker}: {e}")
            return self._get_generic_news(ticker)
    
    def _get_generic_news(self, ticker: str) -> Dict[str, Any]:
        """Generate AI-enhanced generic news when real sources fail"""
        return {
            "ticker": ticker,
            "news": [
                {
                    "title": f"{ticker} - Daily Market Analysis",
                    "summary": f"AI-powered technical and fundamental analysis for {ticker} stock",
                    "sentiment": 0.05,
                    "date": datetime.now().isoformat(),
                    "source": "AI Market Analysis",
                    "impact": "medium"
                },
                {
                    "title": f"{ticker} - Portfolio Performance Review", 
                    "summary": f"Current trading activity and performance metrics for {ticker}",
                    "sentiment": 0.0,
                    "date": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "source": "Portfolio Analysis",
                    "impact": "low"
                },
                {
                    "title": f"Vietnamese Market Update - {ticker} Outlook",
                    "summary": f"General market conditions affecting {ticker} and sector trends",
                    "sentiment": 0.02,
                    "date": (datetime.now() - timedelta(hours=6)).isoformat(),
                    "source": "Market Overview",
                    "impact": "medium"
                }
            ],
            "overall_sentiment": 0.02,
            "market_outlook": f"Neutral to slightly positive outlook for {ticker} based on current market conditions",
            "key_themes": ["Market stability", "Sector performance", "Technical indicators"]
        }
    
    def health_check(self) -> bool:
        """Check if AI analysis system is available"""
        try:
            from src.config.settings import settings
            # Simple test call to verify AI access
            if not settings.LLM_API_KEY:
                return False
            
            # Test with a simple prompt
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": "Test connection. Respond with 'OK'."}]}]
            }
            url = f"{settings.LLM_PROVIDER}?key={settings.LLM_API_KEY}"
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    def get_portfolio_analysis(self, holdings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive AI analysis for entire portfolio"""
        try:
            from src.config.settings import settings
            
            # Create comprehensive portfolio analysis prompt
            portfolio_summary = {
                "total_positions": len(holdings_data.get("positions", [])),
                "owner": holdings_data.get("owner", ""),
                "positions": []
            }
            
            # Get individual stock data
            for position in holdings_data.get("positions", []):
                ticker = position.get("ticker")
                stock_data = self.get_quote(ticker, position.get("exchange", "HOSE"))
                portfolio_summary["positions"].append({
                    "ticker": ticker,
                    "shares": position.get("shares"),
                    "avg_price": position.get("avg_price"),
                    "current_price": stock_data.get("price"),
                    "sector": stock_data.get("sector", "Unknown"),
                    "analysis": stock_data.get("analysis", {})
                })
            
            prompt = f"""You are a Vietnamese portfolio advisor. Analyze this portfolio and provide comprehensive insights.

Portfolio Data:
{json.dumps(portfolio_summary, indent=2)}

Please provide portfolio analysis in the following JSON format:
{{
    "overall_health": "<excellent/good/fair/poor>",
    "total_value_vnd": <estimated_total_value>,
    "diversification_score": <0_to_10>,
    "risk_level": "<low/medium/high>",
    "recommendations": [
        {{
            "type": "<buy/sell/hold/rebalance>",
            "ticker": "<ticker_or_general>",
            "rationale": "Explanation",
            "priority": "<high/medium/low>"
        }}
    ],
    "sector_allocation": {{
        "Banking": <percentage>,
        "Technology": <percentage>,
        "Other": <percentage>
    }},
    "key_insights": ["insight1", "insight2", "insight3"],
    "risk_warnings": ["warning1", "warning2"],
    "performance_outlook": "Brief outlook for the portfolio"
}}

Date: {datetime.now().strftime('%Y-%m-%d')}
Please provide realistic analysis based on Vietnamese market conditions."""

            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            url = f"{settings.LLM_PROVIDER}?key={settings.LLM_API_KEY}"
            
            response = requests.post(url, json=payload, headers=headers, timeout=45)
            response.raise_for_status()
            
            data = response.json()
            if 'candidates' in data and data['candidates']:
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    return analysis
            
            return {"error": "Could not parse AI portfolio analysis"}
            
        except Exception as e:
            logger.error(f"Portfolio analysis failed: {e}")
            return {
                "overall_health": "fair",
                "total_value_vnd": 0,
                "diversification_score": 5,
                "risk_level": "medium",
                "recommendations": [],
                "key_insights": ["Analysis unavailable"],
                "error": str(e)
            }
