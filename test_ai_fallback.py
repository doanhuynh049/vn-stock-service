#!/usr/bin/env python3
"""
Test AI fallback functionality for stock price retrieval
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_ai_fallback():
    """Test AI fallback price retrieval"""
    print("=== Testing AI Fallback for Stock Prices ===")
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Environment loaded")
    except ImportError:
        print("✗ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    
    # Test RealVNStockProvider with AI fallback
    try:
        from src.adapters.real_vn_provider import RealVNStockProvider
        
        provider = RealVNStockProvider()
        
        # Test AI fallback directly
        print("\n=== Testing AI Price Fallback ===")
        test_ticker = "FPT"
        
        try:
            # Force AI fallback by calling the method directly
            result = provider._get_quote_ai_fallback(test_ticker, "HOSE")
            print(f"✓ AI fallback successful for {test_ticker}")
            print(f"  Price: {result['price']:,.0f} VND")
            print(f"  Source: {result.get('source', 'Unknown')}")
            print(f"  Confidence: {result.get('confidence', 'Unknown')}")
            print(f"  Note: {result.get('note', 'No note')}")
            
        except Exception as e:
            print(f"✗ AI fallback failed: {e}")
            return False
            
        # Test basic estimate fallback
        print("\n=== Testing Basic Price Estimate ===")
        try:
            result = provider._get_basic_price_estimate(test_ticker, "HOSE")
            print(f"✓ Basic estimate successful for {test_ticker}")
            print(f"  Price: {result['price']:,.0f} VND")
            print(f"  Source: {result.get('source', 'Unknown')}")
            
        except Exception as e:
            print(f"✗ Basic estimate failed: {e}")
            return False
            
        print("\n✓ All AI fallback tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing AI fallback: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_ai_fallback()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
