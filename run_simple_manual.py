#!/usr/bin/env python3
"""
Simple Manual Advisory Run - Python 3.6 Compatible
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

def run_simple_advisory():
    """Run a simplified advisory process"""
    print("=== VN Stock Advisory - Simple Manual Run ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    setup_logging()
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Environment loaded")
    except ImportError:
        print("✗ python-dotenv not installed")
        return False
    
    # Ensure directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    try:
        # Import components
        from config.settings import Settings
        from models.holdings import Holdings
        from adapters.mock_provider import MockProvider
        from advisory.ai_advisor import AIAdvisor
        from advisory.engine import AdvisoryEngine
        
        print("✓ Components imported")
        
        # Load settings
        settings = Settings()
        print(f"✓ Settings loaded (LLM: {settings.LLM_PROVIDER[:50]}...)")
        
        # Load portfolio
        portfolio_file = Path("data/holdings.json")
        if not portfolio_file.exists():
            print("✗ Portfolio file not found")
            return False
        
        with open(portfolio_file) as f:
            portfolio_data = json.load(f)
        
        holdings = Holdings(**portfolio_data)
        print(f"✓ Portfolio loaded ({len(holdings.positions)} positions)")
        
        # Initialize components
        data_provider = MockProvider()
        ai_advisor = AIAdvisor(
            api_key=settings.LLM_API_KEY,
            api_url=settings.LLM_PROVIDER
        )
        advisory_engine = AdvisoryEngine(ai_advisor)
        
        print("✓ Advisory components initialized")
        
        print("\n=== Generating Advisories ===")
        
        # Process each position
        for position in holdings.positions:
            ticker = position.ticker
            print(f"\nProcessing {ticker}...")
            
            try:
                # Get market data
                market_data = data_provider.get_quote(ticker, position.exchange)
                print(f"  ✓ Market data: {market_data['price']:,} VND ({market_data['change_pct']:+.2f}%)")
                
                # Prepare data for AI
                stock_data = {
                    "ticker": ticker,
                    "exchange": position.exchange,
                    "date": datetime.now().isoformat(),
                    "price": market_data["price"],
                    "avg_price": position.avg_price,
                    "target_price": position.target_price,
                    "pct_to_target": ((position.target_price - market_data["price"]) / market_data["price"]) * 100,
                    "pl_pct_vs_avg": ((market_data["price"] - position.avg_price) / position.avg_price) * 100,
                    "tech": {
                        "rsi14": 50 + (market_data["change_pct"] * 2),  # Mock RSI
                        "volume_vs_20d": 1.2
                    },
                    "fundamentals": {"pe_ttm": 15.5, "dividend_yield": 2.5},
                    "news_sentiment": {"score": 0.1, "summary": "Neutral sentiment"},
                    "risk": {"max_drawdown_pct": position.max_drawdown_pct}
                }
                
                # Generate AI advisory
                advisory = ai_advisor.generate_advisory(stock_data)
                
                print(f"  ✓ Advisory generated")
                print(f"    Action: {advisory.get('action', 'N/A')}")
                print(f"    Rationale: {advisory.get('rationale', 'N/A')[:80]}...")
                
                # Save to output
                output_file = Path("output") / f"{ticker}_advisory.json"
                with open(output_file, 'w') as f:
                    json.dump({
                        "position": position.dict(),
                        "market_data": market_data,
                        "advisory": advisory,
                        "generated_at": datetime.now().isoformat()
                    }, f, indent=2)
                
                print(f"  ✓ Saved to {output_file}")
                
            except Exception as e:
                print(f"  ✗ Error processing {ticker}: {e}")
        
        print(f"\n=== Advisory Generation Complete ===")
        print(f"Check output/ directory for generated files")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = run_simple_advisory()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
