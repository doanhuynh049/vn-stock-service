#!/usr/bin/env python3
"""
Test script for Gemini AI integration
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import Settings
from src.advisory.ai_advisor import AIAdvisor

async def test_gemini_connection():
    """Test basic Gemini API connection"""
    try:
        print("=== Testing Gemini AI Connection ===\n")
        
        # Load settings
        settings = Settings()
        
        print(f"LLM Provider URL: {settings.LLM_PROVIDER}")
        print(f"API Key: {settings.LLM_API_KEY[:20]}...")
        
        # Initialize AI advisor
        advisor = AIAdvisor(
            api_key=settings.LLM_API_KEY,
            api_url=settings.LLM_PROVIDER
        )
        
        # Test simple prompt
        test_prompt = """
        You are a Vietnam stock analyst. Respond in JSON format with the following structure:
        {
            "action": "hold",
            "rationale": "Test response",
            "key_signals": ["test"],
            "risk_notes": "Test risk note",
            "levels": {"add_zone": [100000, 110000], "take_profit_zone": [130000, 140000], "hard_stop": 90000},
            "next_checks": ["Monitor test conditions"]
        }
        
        Just return this exact JSON structure as a test.
        """
        
        print("\nSending test prompt to Gemini...")
        response = advisor._call_gemini(test_prompt)
        
        print("✓ Gemini API connection successful!")
        print("\nResponse:")
        print(json.dumps(response, indent=2))
        
        # Test with stock data
        print("\n=== Testing Stock Advisory Generation ===")
        
        sample_stock_data = {
            "ticker": "FPT",
            "exchange": "HOSE",
            "date": "2025-08-16T07:30:00+07:00",
            "price": 123000,
            "avg_price": 121000,
            "target_price": 145000,
            "pct_to_target": 17.9,
            "pl_pct_vs_avg": 1.65,
            "tech": {
                "rsi14": 62.4,
                "macd": {"value": 0.53, "signal": 0.41, "hist": 0.12, "crossover": "bullish"},
                "sma": {"sma20": 121500, "sma50": 118200, "sma200": 106000, "trend": "up"},
                "volume_vs_20d": 1.3
            },
            "fundamentals": {"pe_ttm": 20.4, "dividend_yield": 2.1},
            "news_sentiment": {"score": 0.21, "summary": "Positive tech outlook"},
            "risk": {"max_drawdown_pct": -12, "stop_suggest": 111000}
        }
        
        advisory = advisor.generate_advisory(sample_stock_data)
        
        print("✓ Stock advisory generated successfully!")
        print("\nStock Advisory:")
        print(json.dumps(advisory, indent=2))
        
        return True
        
    except Exception as e:
        print(f"✗ Gemini test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_portfolio_advisory():
    """Test portfolio advisory generation"""
    try:
        print("\n=== Testing Portfolio Advisory ===")
        
        settings = Settings()
        advisor = AIAdvisor(
            api_key=settings.LLM_API_KEY,
            api_url=settings.LLM_PROVIDER
        )
        
        portfolio_data = {
            "total_value": 157000000,  # 157 million VND
            "total_cost": 147500000,
            "total_pl": 9500000,
            "total_pl_pct": 6.44,
            "positions": [
                {
                    "ticker": "FPT",
                    "value": 61500000,
                    "weight": 39.17,
                    "pl_pct": 1.65
                },
                {
                    "ticker": "VNM", 
                    "value": 20400000,
                    "weight": 12.99,
                    "pl_pct": -2.35
                }
            ],
            "sectors": {"Technology": 1, "Consumer Staples": 1},
            "exchanges": {"HOSE": 2}
        }
        
        portfolio_advisory = advisor.generate_portfolio_advisory(portfolio_data)
        
        print("✓ Portfolio advisory generated successfully!")
        print("\nPortfolio Advisory:")
        print(json.dumps(portfolio_advisory, indent=2))
        
        return True
        
    except Exception as e:
        print(f"✗ Portfolio advisory test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=== Gemini AI Integration Tests ===\n")
    
    tests = [
        test_gemini_connection,
        test_portfolio_advisory
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
        
        print("-" * 60)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All Gemini tests passed!")
        return True
    else:
        print("✗ Some tests failed.")
        return False

if __name__ == "__main__":
    # Python 3.6 compatible asyncio
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(main())
    sys.exit(0 if success else 1)
