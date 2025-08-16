from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
from advisory.indicators import TechnicalIndicators
from advisory.ai_advisor import AIAdvisor

logger = logging.getLogger(__name__)

class AdvisoryEngine:
    def __init__(self, ai_advisor: AIAdvisor):
        self.ai_advisor = ai_advisor
        self.indicators = TechnicalIndicators()

    def generate_stock_advisory(self, position: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive advisory for a single stock position"""
        try:
            # Calculate basic performance metrics
            performance = self.calculate_performance(
                position['avg_price'], 
                market_data['price'], 
                position['shares']
            )
            
            # Calculate technical indicators
            tech_analysis = self.indicators.analyze_stock(market_data.get('ohlcv', {}))
            
            # Calculate risk metrics
            risk_metrics = self.calculate_risk_metrics(position, market_data, tech_analysis)
            
            # Prepare data for AI analysis
            stock_data = {
                "ticker": position['ticker'],
                "exchange": position['exchange'],
                "date": datetime.now(timezone.utc).isoformat(),
                "price": market_data['price'],
                "avg_price": position['avg_price'],
                "target_price": position['target_price'],
                "shares": position['shares'],
                "pct_to_target": ((position['target_price'] / market_data['price']) - 1) * 100,
                "pl_pct_vs_avg": performance['pl_pct'],
                "total_value": market_data['price'] * position['shares'],
                "tech": tech_analysis,
                "fundamentals": market_data.get('fundamentals', {}),
                "news_sentiment": market_data.get('news_sentiment', {}),
                "risk": risk_metrics
            }
            
            # Get AI advisory
            ai_advisory = self.ai_advisor.generate_advisory(stock_data)
            
            return {
                "position": position,
                "market_data": market_data,
                "performance": performance,
                "technical": tech_analysis,
                "risk": risk_metrics,
                "advisory": ai_advisory,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating advisory for {position.get('ticker')}: {e}")
            return self._fallback_advisory(position, market_data)

    def generate_portfolio_advisory(self, positions: List[Dict[str, Any]], market_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate portfolio-level advisory"""
        try:
            portfolio_metrics = self.calculate_portfolio_metrics(positions, market_data)
            ai_portfolio_advisory = self.ai_advisor.generate_portfolio_advisory(portfolio_metrics)
            
            return {
                "portfolio_metrics": portfolio_metrics,
                "advisory": ai_portfolio_advisory,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating portfolio advisory: {e}")
            return self._fallback_portfolio_advisory(positions, market_data)

    def calculate_performance(self, avg_price: float, current_price: float, shares: int) -> Dict[str, float]:
        """Calculate position performance metrics"""
        pl = (current_price - avg_price) * shares
        pl_pct = ((current_price / avg_price) - 1) * 100 if avg_price > 0 else 0
        total_value = current_price * shares
        total_cost = avg_price * shares
        
        return {
            "pl": round(pl, 2),
            "pl_pct": round(pl_pct, 2),
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "current_price": current_price,
            "avg_price": avg_price
        }

    def calculate_risk_metrics(self, position: Dict[str, Any], market_data: Dict[str, Any], tech_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk-related metrics"""
        current_price = market_data['price']
        avg_price = position['avg_price']
        max_drawdown_pct = position.get('max_drawdown_pct', -15)
        
        # Calculate current drawdown
        current_drawdown_pct = ((current_price / avg_price) - 1) * 100
        
        # Calculate stop loss level
        stop_loss_price = avg_price * (1 + max_drawdown_pct / 100)
        
        # Volatility estimate (basic)
        volatility_estimate = "medium"  # Default
        if tech_analysis.get('bollinger', {}).get('position', 0.5) > 0.8:
            volatility_estimate = "high"
        elif tech_analysis.get('bollinger', {}).get('position', 0.5) < 0.2:
            volatility_estimate = "low"
        
        # Risk level assessment
        risk_level = "medium"
        if current_drawdown_pct < max_drawdown_pct * 0.8:  # Close to max drawdown
            risk_level = "high"
        elif current_drawdown_pct > 5:  # In profit
            risk_level = "low"
        
        return {
            "max_drawdown_pct": max_drawdown_pct,
            "current_drawdown_pct": round(current_drawdown_pct, 2),
            "stop_loss_price": round(stop_loss_price, 2),
            "is_stop_breached": current_price < stop_loss_price,
            "volatility_estimate": volatility_estimate,
            "risk_level": risk_level,
            "position_size_pct": 0  # Will be calculated at portfolio level
        }

    def calculate_portfolio_metrics(self, positions: List[Dict[str, Any]], market_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate portfolio-level metrics"""
        total_value = 0
        total_cost = 0
        total_pl = 0
        position_details = []
        
        for position in positions:
            ticker = position['ticker']
            if ticker in market_data:
                price = market_data[ticker]['price']
                performance = self.calculate_performance(
                    position['avg_price'], 
                    price, 
                    position['shares']
                )
                
                total_value += performance['total_value']
                total_cost += performance['total_cost']
                total_pl += performance['pl']
                
                position_details.append({
                    "ticker": ticker,
                    "value": performance['total_value'],
                    "pl": performance['pl'],
                    "pl_pct": performance['pl_pct'],
                    "weight_pct": 0  # Will calculate after total_value is known
                })
        
        # Calculate position weights
        for detail in position_details:
            detail['weight_pct'] = round((detail['value'] / total_value) * 100, 2) if total_value > 0 else 0
        
        # Portfolio-level calculations
        total_pl_pct = ((total_value / total_cost) - 1) * 100 if total_cost > 0 else 0
        
        # Risk assessments
        concentration_risks = []
        for detail in position_details:
            if detail['weight_pct'] > 30:
                concentration_risks.append(f"{detail['ticker']} represents {detail['weight_pct']}% of portfolio")
        
        # Top movers (biggest gains/losses)
        sorted_positions = sorted(position_details, key=lambda x: x['pl_pct'], reverse=True)
        top_gainers = [p['ticker'] for p in sorted_positions[:3] if p['pl_pct'] > 0]
        top_losers = [p['ticker'] for p in sorted_positions[-3:] if p['pl_pct'] < 0]
        
        return {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_pl": round(total_pl, 2),
            "total_pl_pct": round(total_pl_pct, 2),
            "position_count": len(positions),
            "positions": position_details,
            "concentration_risks": concentration_risks,
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "max_position_weight": max([p['weight_pct'] for p in position_details]) if position_details else 0
        }

    def _fallback_advisory(self, position: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback advisory when main analysis fails"""
        performance = self.calculate_performance(
            position['avg_price'], 
            market_data['price'], 
            position['shares']
        )
        
        return {
            "position": position,
            "market_data": market_data,
            "performance": performance,
            "technical": {},
            "risk": {"risk_level": "unknown"},
            "advisory": {
                "action": "hold",
                "rationale": "Technical analysis unavailable - holding position",
                "key_signals": ["SYSTEM_ERROR"],
                "risk_notes": "Unable to perform full analysis",
                "levels": {},
                "next_checks": ["Retry analysis when system is available"]
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def _fallback_portfolio_advisory(self, positions: List[Dict[str, Any]], market_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback portfolio advisory"""
        return {
            "portfolio_metrics": {"total_pl_pct": 0, "position_count": len(positions)},
            "advisory": {
                "total_pl_pct": 0,
                "risk_alerts": ["System error - manual review required"],
                "top_movers": [],
                "concentration_risks": [],
                "priority_todos": ["Check system health", "Perform manual analysis"]
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def calculate_technical_indicators(self, price_data: List[float]) -> Dict[str, Any]:
        # Placeholder for actual indicator calculations
        return {
            "rsi": self.calculate_rsi(price_data),
            "macd": self.calculate_macd(price_data),
            "sma": {
                "sma20": self.calculate_sma(price_data, 20),
                "sma50": self.calculate_sma(price_data, 50),
                "sma200": self.calculate_sma(price_data, 200),
            }
        }

    def calculate_rsi(self, price_data: List[float]) -> float:
        # Implement RSI calculation logic
        return 0.0

    def calculate_macd(self, price_data: List[float]) -> Dict[str, float]:
        # Implement MACD calculation logic
        return {"value": 0.0, "signal": 0.0, "hist": 0.0}

    def calculate_sma(self, price_data: List[float], period: int) -> float:
        if len(price_data) < period:
            return 0.0
        return sum(price_data[-period:]) / period

    def generate_advisory(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        performance = self.calculate_performance(stock_data['avg_price'], stock_data['price'], stock_data['shares'])
        technical_indicators = self.calculate_technical_indicators(stock_data['price_history'])

        advisory = {
            "ticker": stock_data['ticker'],
            "performance": performance,
            "technical_indicators": technical_indicators,
            "risk": self.evaluate_risk(stock_data),
            "action": self.determine_action(performance, technical_indicators)
        }
        return advisory

    def evaluate_risk(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implement risk evaluation logic
        return {"max_drawdown": stock_data.get('max_drawdown_pct', 0)}

    def determine_action(self, performance: Dict[str, float], technical_indicators: Dict[str, Any]) -> str:
        # Implement logic to determine action based on performance and indicators
        return "hold"  # Placeholder action

    def process_portfolio(self, holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        advisories = []
        for holding in holdings:
            advisory = self.generate_advisory(holding)
            advisories.append(advisory)
        return advisories