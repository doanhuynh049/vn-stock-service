"""
Simplified Holdings-Only Data Provider
- Loads portfolio from holdings.json
- Passes data directly to AI for analysis
- No price fetching, no external APIs
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from adapters.base import DataProviderInterface, DataProviderError
from utils.api_logger import APILogger

logger = logging.getLogger(__name__)

class HoldingsOnlyProvider(DataProviderInterface):
    """
    Holdings-only provider that focuses on AI analysis
    - Loads portfolio from holdings.json
    - Provides AI-powered advisory without price fetching
    - Supports multiple advisory modes and scenarios
    """
    
    def __init__(self, holdings_file: str = "data/holdings.json"):
        self.holdings_file = Path(holdings_file)
        self.api_logger = APILogger()
        self.cached_holdings = None
        self.last_load_time = None
        
    def load_holdings(self) -> Dict[str, Any]:
        """Load portfolio holdings from JSON file"""
        try:
            if not self.holdings_file.exists():
                raise DataProviderError(f"Holdings file not found: {self.holdings_file}")
            
            with open(self.holdings_file, 'r', encoding='utf-8') as f:
                holdings = json.load(f)
            
            self.cached_holdings = holdings
            self.last_load_time = datetime.now()
            
            logger.info(f"Loaded portfolio with {len(holdings.get('positions', []))} positions")
            return holdings
            
        except json.JSONDecodeError as e:
            raise DataProviderError(f"Invalid JSON in holdings file: {e}")
        except Exception as e:
            raise DataProviderError(f"Error loading holdings: {e}")
    
    def get_holdings(self) -> Dict[str, Any]:
        """Get cached holdings or reload if needed"""
        if (self.cached_holdings is None or 
            self.last_load_time is None or 
            (datetime.now() - self.last_load_time).seconds > 300):  # Reload every 5 minutes
            return self.load_holdings()
        return self.cached_holdings
    
    def get_quote(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """
        Simplified quote method - returns basic info from holdings
        No external price fetching
        """
        holdings = self.get_holdings()
        
        # Find position in holdings
        for position in holdings.get("positions", []):
            if position.get("ticker") == ticker:
                return {
                    "ticker": ticker,
                    "exchange": exchange,
                    "shares": position.get("shares", 0),
                    "avg_price": position.get("avg_price", 0),
                    "target_price": position.get("target_price", 0),
                    "max_drawdown_pct": position.get("max_drawdown_pct", -15),
                    "notes": position.get("notes", ""),
                    "date_added": position.get("date_added", ""),
                    "timestamp": datetime.now().isoformat(),
                    "source": "Holdings_File"
                }
        
        # If not found in holdings, return minimal data
        return {
            "ticker": ticker,
            "exchange": exchange,
            "shares": 0,
            "avg_price": 0,
            "timestamp": datetime.now().isoformat(),
            "source": "Unknown"
        }
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary for AI analysis"""
        holdings = self.get_holdings()
        
        total_positions = len(holdings.get("positions", []))
        total_invested = sum(
            pos.get("shares", 0) * pos.get("avg_price", 0) 
            for pos in holdings.get("positions", [])
        )
        
        # Group by sector/exchange
        by_exchange = {}
        sectors = set()
        
        for position in holdings.get("positions", []):
            exchange = position.get("exchange", "HOSE")
            ticker = position.get("ticker", "")
            
            # Basic sector classification
            sector = self._classify_sector(ticker)
            sectors.add(sector)
            
            if exchange not in by_exchange:
                by_exchange[exchange] = []
            by_exchange[exchange].append(position)
        
        return {
            "owner": holdings.get("owner", ""),
            "currency": holdings.get("currency", "VND"),
            "timezone": holdings.get("timezone", "Asia/Ho_Chi_Minh"),
            "total_positions": total_positions,
            "total_invested_value": total_invested,
            "exchanges": by_exchange,
            "sectors": list(sectors),
            "positions": holdings.get("positions", []),
            "last_updated": holdings.get("last_updated", datetime.now().isoformat()),
            "version": holdings.get("version", "1.0")
        }
    
    def _classify_sector(self, ticker: str) -> str:
        """Basic sector classification for Vietnamese stocks"""
        sector_map = {
            # Banking
            "VCB": "Banking", "TCB": "Banking", "ACB": "Banking", "BID": "Banking",
            "CTG": "Banking", "EIB": "Banking", "HDB": "Banking", "LPB": "Banking",
            "MBB": "Banking", "MSB": "Banking", "STB": "Banking", "TPB": "Banking",
            "VIB": "Banking", "VPB": "Banking",
            
            # Technology
            "FPT": "Technology", "CMG": "Technology", "VGI": "Technology", 
            "ELC": "Technology", "ITD": "Technology",
            
            # Real Estate
            "VHM": "Real Estate", "VIC": "Real Estate", "KDH": "Real Estate",
            "NVL": "Real Estate", "PDR": "Real Estate", "DXG": "Real Estate",
            
            # Steel & Materials
            "HPG": "Steel & Materials", "HSG": "Steel & Materials", "NKG": "Steel & Materials",
            
            # Oil & Gas
            "GAS": "Oil & Gas", "PLX": "Oil & Gas", "PVS": "Oil & Gas",
            
            # Consumer Goods
            "MSN": "Consumer Goods", "VNM": "Consumer Goods", "SAB": "Consumer Goods",
            
            # Utilities
            "POW": "Utilities", "NT2": "Utilities"
        }
        
        return sector_map.get(ticker, "Other")
    
    def get_ohlcv(self, ticker: str, window: str = "1D", exchange: str = "HOSE") -> Dict[str, Any]:
        """Not needed - return empty data"""
        return {
            "ticker": ticker,
            "exchange": exchange,
            "data": {
                "dates": [],
                "open": [],
                "high": [],
                "low": [],
                "close": [],
                "volume": []
            },
            "note": "OHLCV data not available in holdings-only mode"
        }
    
    def get_fundamentals(self, ticker: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """Return basic info from holdings"""
        position_data = self.get_quote(ticker, exchange)
        sector = self._classify_sector(ticker)
        
        return {
            "ticker": ticker,
            "exchange": exchange,
            "sector": sector,
            "shares": position_data.get("shares", 0),
            "avg_price": position_data.get("avg_price", 0),
            "target_price": position_data.get("target_price", 0),
            "notes": position_data.get("notes", ""),
            "source": "Holdings_File"
        }
    
    def get_news(self, ticker: str, limit: int = 10) -> Dict[str, Any]:
        """Return empty news - not needed for holdings-only analysis"""
        return {
            "ticker": ticker,
            "news": [],
            "overall_sentiment": 0,
            "note": "News not available in holdings-only mode"
        }
    
    def health_check(self) -> bool:
        """Check if holdings file is accessible"""
        try:
            holdings = self.get_holdings()
            return len(holdings.get("positions", [])) > 0
        except Exception:
            return False
    
    def validate_holdings_file(self) -> Dict[str, Any]:
        """Validate holdings file structure and content"""
        try:
            holdings = self.load_holdings()
            
            errors = []
            warnings = []
            
            # Check required fields
            if "owner" not in holdings:
                warnings.append("Missing 'owner' field")
            if "positions" not in holdings:
                errors.append("Missing 'positions' array")
            elif not isinstance(holdings["positions"], list):
                errors.append("'positions' must be an array")
            
            # Validate each position
            for i, position in enumerate(holdings.get("positions", [])):
                pos_prefix = f"Position {i+1}"
                
                if "ticker" not in position:
                    errors.append(f"{pos_prefix}: Missing 'ticker'")
                if "shares" not in position:
                    errors.append(f"{pos_prefix}: Missing 'shares'")
                elif not isinstance(position["shares"], (int, float)) or position["shares"] <= 0:
                    errors.append(f"{pos_prefix}: 'shares' must be positive number")
                if "avg_price" not in position:
                    errors.append(f"{pos_prefix}: Missing 'avg_price'")
                elif not isinstance(position["avg_price"], (int, float)) or position["avg_price"] <= 0:
                    errors.append(f"{pos_prefix}: 'avg_price' must be positive number")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "positions_count": len(holdings.get("positions", [])),
                "file_path": str(self.holdings_file)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to load/parse holdings file: {e}"],
                "warnings": [],
                "positions_count": 0,
                "file_path": str(self.holdings_file)
            }
