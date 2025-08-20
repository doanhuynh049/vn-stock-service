#!/usr/bin/env python3
"""
VN Stock Advisory - Enhanced AI-First System
- No price fetching, pure AI analysis
- Holdings-only approach with comprehensive advisory
- Multiple analysis modes and scenarios
- Historical tracking and user configuration
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point for enhanced AI-first advisory system"""
    print("=== VN Stock Advisory - Enhanced AI System ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Environment loaded")
    except ImportError:
        print("✗ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    
    # Test system configuration
    try:
        print("\n=== System Configuration Test ===")
        if not test_configuration():
            return False
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False
    
    # Initialize enhanced advisory engine
    try:
        print("\n=== Initializing Enhanced Advisory Engine ===")
        engine = initialize_advisory_engine()
        if not engine:
            return False
        print("✓ Enhanced advisory engine initialized")
    except Exception as e:
        print(f"✗ Engine initialization failed: {e}")
        return False
    
    # Test holdings loading
    try:
        print("\n=== Testing Holdings Provider ===")
        if not test_holdings_provider():
            return False
    except Exception as e:
        print(f"✗ Holdings provider test failed: {e}")
        return False
    
    # Generate comprehensive advisory
    try:
        print("\n=== Generating Comprehensive Advisory ===")
        advisory = engine.generate_daily_advisory(save_to_history=False)
        
        if "error" in advisory:
            print(f"✗ Advisory generation failed: {advisory['error']}")
            return False
            
        print("✓ Comprehensive advisory generated successfully")
        print(f"  Advisory Mode: {advisory.get('advisory_mode', 'N/A')}")
        print(f"  Portfolio Positions: {advisory.get('portfolio_summary', {}).get('total_positions', 0)}")
        print(f"  Total Value: {advisory.get('portfolio_summary', {}).get('total_invested_value', 0):,.0f} VND")
        
        # Show sample advisory content
        main_advisory = advisory.get('main_advisory', {})
        if main_advisory:
            print(f"  Key Insights: {len(main_advisory.get('insights', []))} generated")
            print(f"  Action Items: {len(main_advisory.get('action_items', []))} identified")
        
    except Exception as e:
        print(f"✗ Advisory generation failed: {e}")
        return False
    
    # Test scenario analysis
    try:
        print("\n=== Testing Scenario Analysis ===")
        scenario_result = engine.analyze_scenario("What if the banking sector declines by 15%?")
        
        if "error" in scenario_result:
            print(f"⚠ Scenario analysis warning: {scenario_result['error']}")
        else:
            print("✓ Scenario analysis working")
            
    except Exception as e:
        print(f"⚠ Scenario analysis test failed: {e}")
    
    # Test historical tracking
    try:
        print("\n=== Testing Historical Tracking ===")
        evolution = engine.get_portfolio_evolution(days=7)
        
        if "error" in evolution:
            print(f"⚠ Historical tracking warning: {evolution['error']}")
        else:
            print("✓ Historical tracking available")
            print(f"  Historical snapshots: {evolution.get('historical_snapshots', 0)}")
            
    except Exception as e:
        print(f"⚠ Historical tracking test failed: {e}")
    
    print("\n✓ Enhanced AI-First Advisory System Operational!")
    print("\nSystem Features:")
    print("• AI-only analysis (no price fetching)")
    print("• Multiple advisory modes (long-term, swing trading, etc.)")
    print("• Scenario analysis and what-if planning")
    print("• Historical portfolio tracking")
    print("• User configuration management")
    print("• Risk management recommendations")
    
    print("\nNext Steps:")
    print("1. Customize your advisory preferences in config/user_config.yaml")
    print("2. Set up email notifications in .env")
    print("3. Run the scheduler: python3 run_scheduler.py")
    print("4. Access web dashboard (coming soon)")
    
    return True

def test_configuration():
    """Test system configuration"""
    
    # Test Gemini AI API
    api_key = os.getenv('LLM_API_KEY')
    api_url = os.getenv('LLM_PROVIDER')
    
    if not api_key or not api_url:
        print("✗ Gemini AI configuration missing")
        print("  Please set LLM_API_KEY and LLM_PROVIDER in .env")
        return False
    
    print("✓ Gemini AI configuration found")
    
    # Test basic API connectivity
    try:
        import requests
        
        test_prompt = "Respond with exactly: 'API_OK'"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": test_prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 10}
        }
        
        url = f"{api_url}?key={api_key}"
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print("✓ Gemini AI API connectivity confirmed")
            return True
        else:
            print(f"✗ Gemini AI API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Gemini AI API test failed: {e}")
        return False

def initialize_advisory_engine():
    """Initialize the enhanced advisory engine"""
    try:
        from advisory.enhanced_engine import EnhancedAdvisoryEngine
        
        # Check if holdings file exists, create sample if not
        holdings_file = "data/holdings.json"
        if not os.path.exists(holdings_file):
            create_sample_holdings()
        
        # Initialize engine
        engine = EnhancedAdvisoryEngine(holdings_file)
        return engine
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Make sure all required modules are available")
        return None
    except Exception as e:
        print(f"✗ Engine initialization error: {e}")
        return None

def test_holdings_provider():
    """Test the holdings provider"""
    try:
        from adapters.holdings_provider import HoldingsOnlyProvider
        
        provider = HoldingsOnlyProvider("data/holdings.json")
        
        # Validate holdings file
        validation = provider.validate_holdings_file()
        if not validation['valid']:
            print(f"✗ Holdings validation failed: {validation['errors']}")
            return False
        
        # Get portfolio summary
        summary = provider.get_portfolio_summary()
        print(f"✓ Portfolio loaded: {summary['total_positions']} positions")
        print(f"  Owner: {summary['owner']}")
        print(f"  Total invested: {summary['total_invested_value']:,.0f} VND")
        
        # Show positions
        for i, pos in enumerate(summary['positions'][:3], 1):  # Show first 3
            print(f"  {i}. {pos['ticker']}: {pos['shares']} shares @ {pos['avg_price']:,.0f} VND")
        
        if len(summary['positions']) > 3:
            print(f"  ... and {len(summary['positions']) - 3} more positions")
        
        return True
        
    except Exception as e:
        print(f"✗ Holdings provider test failed: {e}")
        return False

def create_sample_holdings():
    """Create sample holdings file if it doesn't exist"""
    sample_portfolio = {
        "owner": "Quat",
        "currency": "VND",
        "timezone": "Asia/Ho_Chi_Minh",
        "last_updated": datetime.now().isoformat(),
        "positions": [
            {
                "ticker": "FPT",
                "exchange": "HOSE",
                "shares": 500,
                "avg_price": 121000,
                "target_price": 145000,
                "max_drawdown_pct": -12,
                "notes": "Technology leader in Vietnam"
            },
            {
                "ticker": "VNM",
                "exchange": "HOSE",
                "shares": 300,
                "avg_price": 68000,
                "target_price": 80000,
                "max_drawdown_pct": -10,
                "notes": "Leading dairy and beverage company"
            },
            {
                "ticker": "VCB",
                "exchange": "HOSE",
                "shares": 200,
                "avg_price": 95000,
                "target_price": 110000,
                "max_drawdown_pct": -15,
                "notes": "Top banking stock"
            },
            {
                "ticker": "HPG",
                "exchange": "HOSE",
                "shares": 800,
                "avg_price": 32000,
                "target_price": 38000,
                "max_drawdown_pct": -18,
                "notes": "Steel industry leader"
            }
        ]
    }
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Save sample portfolio
    with open("data/holdings.json", 'w', encoding='utf-8') as f:
        json.dump(sample_portfolio, f, indent=2, ensure_ascii=False)
    
    print("✓ Sample holdings file created")

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
