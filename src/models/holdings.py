from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

class Position(BaseModel):
    ticker: str
    exchange: str
    shares: int
    avg_price: float
    target_price: float
    max_drawdown_pct: float = -15.0  # Default max drawdown
    notes: Optional[str] = None
    date_added: Optional[datetime] = None
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper()
    
    @validator('exchange')
    def exchange_must_be_valid(cls, v):
        valid_exchanges = ['HOSE', 'HNX', 'UPCoM']
        if v not in valid_exchanges:
            raise ValueError(f'Exchange must be one of {valid_exchanges}')
        return v
    
    @validator('shares')
    def shares_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Shares must be positive')
        return v
    
    @validator('avg_price', 'target_price')
    def prices_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Prices must be positive')
        return v
    
    @validator('max_drawdown_pct')
    def max_drawdown_must_be_negative(cls, v):
        if v > 0:
            raise ValueError('Max drawdown percentage must be negative')
        return v

class Holdings(BaseModel):
    owner: str
    currency: str = "VND"
    timezone: str = "Asia/Ho_Chi_Minh"
    positions: List[Position]
    last_updated: Optional[datetime] = None
    version: str = "1.0"
    
    @validator('currency')
    def currency_must_be_vnd(cls, v):
        if v != "VND":
            raise ValueError('Only VND currency is supported')
        return v
    
    @validator('positions')
    def positions_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Holdings must contain at least one position')
        return v
    
    def get_position(self, ticker: str) -> Optional[Position]:
        """Get position by ticker"""
        for position in self.positions:
            if position.ticker == ticker.upper():
                return position
        return None
    
    def add_position(self, position: Position) -> None:
        """Add a new position"""
        # Check if ticker already exists
        existing = self.get_position(position.ticker)
        if existing:
            raise ValueError(f"Position for {position.ticker} already exists")
        
        self.positions.append(position)
        self.last_updated = datetime.now()
    
    def update_position(self, ticker: str, **updates) -> bool:
        """Update an existing position"""
        position = self.get_position(ticker)
        if not position:
            return False
        
        for field, value in updates.items():
            if hasattr(position, field):
                setattr(position, field, value)
        
        self.last_updated = datetime.now()
        return True
    
    def remove_position(self, ticker: str) -> bool:
        """Remove a position"""
        for i, position in enumerate(self.positions):
            if position.ticker == ticker.upper():
                del self.positions[i]
                self.last_updated = datetime.now()
                return True
        return False
    
    def get_total_value_at_prices(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value at given prices"""
        total = 0
        for position in self.positions:
            price = current_prices.get(position.ticker, position.avg_price)
            total += position.shares * price
        return total
    
    def get_total_cost(self) -> float:
        """Calculate total cost basis of portfolio"""
        return sum(position.shares * position.avg_price for position in self.positions)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return self.json(indent=2, default=str)
    
    @classmethod
    def from_json_file(cls, file_path: str) -> 'Holdings':
        """Load holdings from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)
    
    def save_to_json_file(self, file_path: str) -> None:
        """Save holdings to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

class PortfolioSummary(BaseModel):
    """Summary statistics for a portfolio"""
    total_positions: int
    total_value: float
    total_cost: float
    total_pl: float
    total_pl_pct: float
    largest_position: Optional[str] = None
    largest_position_pct: float = 0
    sectors: Dict[str, int] = {}
    exchanges: Dict[str, int] = {}
    
    @classmethod
    def from_holdings(cls, holdings: Holdings, current_prices: Dict[str, float], 
                     fundamentals: Dict[str, Dict[str, Any]] = {}) -> 'PortfolioSummary':
        """Create portfolio summary from holdings"""
        total_cost = holdings.get_total_cost()
        total_value = holdings.get_total_value_at_prices(current_prices)
        total_pl = total_value - total_cost
        total_pl_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0
        
        # Find largest position
        largest_position = None
        largest_value = 0
        
        # Count by exchange
        exchanges = {}
        sectors = {}
        
        for position in holdings.positions:
            # Position value
            price = current_prices.get(position.ticker, position.avg_price)
            position_value = position.shares * price
            
            if position_value > largest_value:
                largest_value = position_value
                largest_position = position.ticker
            
            # Count exchanges
            exchanges[position.exchange] = exchanges.get(position.exchange, 0) + 1
            
            # Count sectors if available
            if position.ticker in fundamentals:
                sector = fundamentals[position.ticker].get('sector', 'Unknown')
                sectors[sector] = sectors.get(sector, 0) + 1
        
        largest_position_pct = (largest_value / total_value * 100) if total_value > 0 else 0
        
        return cls(
            total_positions=len(holdings.positions),
            total_value=total_value,
            total_cost=total_cost,
            total_pl=total_pl,
            total_pl_pct=total_pl_pct,
            largest_position=largest_position,
            largest_position_pct=largest_position_pct,
            sectors=sectors,
            exchanges=exchanges
        )