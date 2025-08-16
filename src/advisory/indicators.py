import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Calculate technical indicators for Vietnam stock analysis"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return {"value": 0, "signal": 0, "histogram": 0, "crossover": "neutral"}
        
        df = pd.DataFrame({'price': prices})
        df['ema_fast'] = df['price'].ewm(span=fast).mean()
        df['ema_slow'] = df['price'].ewm(span=slow).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['signal'] = df['macd'].ewm(span=signal).mean()
        df['histogram'] = df['macd'] - df['signal']
        
        current_macd = df['macd'].iloc[-1]
        current_signal = df['signal'].iloc[-1]
        current_hist = df['histogram'].iloc[-1]
        prev_hist = df['histogram'].iloc[-2] if len(df) > 1 else 0
        
        # Determine crossover
        crossover = "neutral"
        if current_hist > 0 and prev_hist <= 0:
            crossover = "bullish"
        elif current_hist < 0 and prev_hist >= 0:
            crossover = "bearish"
        
        return {
            "value": round(current_macd, 2),
            "signal": round(current_signal, 2),
            "histogram": round(current_hist, 2),
            "crossover": crossover
        }
    
    @staticmethod
    def calculate_sma(prices: List[float], periods: List[int] = [20, 50, 200]) -> Dict[str, Any]:
        """Calculate Simple Moving Averages"""
        result = {}
        
        for period in periods:
            if len(prices) >= period:
                sma_value = np.mean(prices[-period:])
                result[f'sma{period}'] = round(sma_value, 2)
            else:
                result[f'sma{period}'] = None
        
        # Determine trend
        current_price = prices[-1] if prices else 0
        trend = "neutral"
        
        if all(result.get(f'sma{p}') for p in periods):
            sma20 = result.get('sma20', 0)
            sma50 = result.get('sma50', 0)
            sma200 = result.get('sma200', 0)
            
            if current_price > sma20 > sma50 > sma200:
                trend = "strong_up"
            elif current_price > sma20 > sma50:
                trend = "up"
            elif current_price < sma20 < sma50 < sma200:
                trend = "strong_down"
            elif current_price < sma20 < sma50:
                trend = "down"
        
        result['trend'] = trend
        return result
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {"upper": 0, "middle": 0, "lower": 0, "position": 0}
        
        recent_prices = prices[-period:]
        sma = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        current_price = prices[-1]
        
        # Calculate position within bands (0 = lower band, 1 = upper band)
        if upper != lower:
            position = (current_price - lower) / (upper - lower)
        else:
            position = 0.5
        
        return {
            "upper": round(upper, 2),
            "middle": round(sma, 2),
            "lower": round(lower, 2),
            "position": round(position, 2)
        }
    
    @staticmethod
    def calculate_volume_indicators(volumes: List[float], prices: List[float]) -> Dict[str, Any]:
        """Calculate volume-based indicators"""
        if len(volumes) < 20:
            return {"avg_volume_20d": 0, "volume_ratio": 1.0, "volume_spike": False}
        
        avg_volume_20d = np.mean(volumes[-20:])
        current_volume = volumes[-1] if volumes else 0
        volume_ratio = current_volume / avg_volume_20d if avg_volume_20d > 0 else 1.0
        
        return {
            "avg_volume_20d": round(avg_volume_20d, 0),
            "volume_ratio": round(volume_ratio, 2),
            "volume_spike": volume_ratio > 2.0
        }
    
    @staticmethod
    def calculate_support_resistance(prices: List[float], period: int = 20) -> Dict[str, List[float]]:
        """Calculate basic support and resistance levels"""
        if len(prices) < period:
            return {"support": [], "resistance": []}
        
        recent_prices = prices[-period:]
        
        # Simple approach: use recent highs and lows
        sorted_prices = sorted(recent_prices)
        support_levels = sorted_prices[:3]  # Bottom 3 prices
        resistance_levels = sorted_prices[-3:]  # Top 3 prices
        
        return {
            "support": [round(p, 2) for p in support_levels],
            "resistance": [round(p, 2) for p in resistance_levels]
        }
    
    @classmethod
    def analyze_stock(cls, ohlcv_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Comprehensive technical analysis for a stock"""
        try:
            prices = ohlcv_data.get('close', [])
            volumes = ohlcv_data.get('volume', [])
            highs = ohlcv_data.get('high', [])
            lows = ohlcv_data.get('low', [])
            
            if not prices:
                return {}
            
            analysis = {
                "rsi14": cls.calculate_rsi(prices, 14),
                "macd": cls.calculate_macd(prices),
                "sma": cls.calculate_sma(prices),
                "bollinger": cls.calculate_bollinger_bands(prices),
                "volume": cls.calculate_volume_indicators(volumes, prices),
                "support_resistance": cls.calculate_support_resistance(prices)
            }
            
            # Add price change calculations
            if len(prices) >= 2:
                analysis["price_change"] = {
                    "1d_pct": round(((prices[-1] / prices[-2]) - 1) * 100, 2),
                    "5d_pct": round(((prices[-1] / prices[-5]) - 1) * 100, 2) if len(prices) >= 5 else 0,
                    "20d_pct": round(((prices[-1] / prices[-20]) - 1) * 100, 2) if len(prices) >= 20 else 0
                }
            
            # Calculate 52-week high/low if we have enough data
            if len(prices) >= 252:  # Approximately 1 year of trading days
                year_prices = prices[-252:]
                analysis["52_week"] = {
                    "high": max(year_prices),
                    "low": min(year_prices),
                    "position_pct": round(((prices[-1] - min(year_prices)) / (max(year_prices) - min(year_prices))) * 100, 2)
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            return {}

def calculate_ema(prices, window):
    if len(prices) < window:
        return None
    k = 2 / (window + 1)
    ema = [sum(prices[:window]) / window]
    for price in prices[window:]:
        ema.append((price - ema[-1]) * k + ema[-1])
    return ema

def calculate_sma(prices, window):
    if len(prices) < window:
        return None
    return sum(prices[-window:]) / window

def calculate_bollinger_bands(prices, window=20, num_std_dev=2):
    if len(prices) < window:
        return None, None
    sma = calculate_sma(prices, window)
    std_dev = (sum((x - sma) ** 2 for x in prices[-window:]) / window) ** 0.5
    upper_band = sma + (std_dev * num_std_dev)
    lower_band = sma - (std_dev * num_std_dev)
    return upper_band, lower_band

def calculate_volume_spike(current_volume, historical_volumes):
    if len(historical_volumes) == 0:
        return None
    average_volume = sum(historical_volumes) / len(historical_volumes)
    return current_volume / average_volume if average_volume > 0 else None

def calculate_drawdown(prices):
    if len(prices) == 0:
        return None
    peak = prices[0]
    max_drawdown = 0
    for price in prices:
        if price > peak:
            peak = price
        drawdown = (peak - price) / peak
        max_drawdown = max(max_drawdown, drawdown)
    return max_drawdown