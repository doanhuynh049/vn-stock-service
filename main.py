#!/usr/bin/env python3
"""
VN Stock Advisory - Main Entry Point
Simplified version focused on Gemini AI integration
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point"""
    print("=== VN Stock Advisory System ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Environment loaded")
    except ImportError:
        print("✗ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    
    # Test Gemini API
    try:
        print("\n=== Testing Gemini AI ===")
        success = test_gemini_integration()
        if not success:
            return False
    except Exception as e:
        print(f"✗ Gemini test failed: {e}")
        return False
    
    # Load sample holdings
    try:
        print("\n=== Loading Portfolio ===")
        portfolio = load_sample_portfolio()
        print(f"✓ Portfolio loaded: {len(portfolio['positions'])} positions")
    except Exception as e:
        print(f"✗ Portfolio loading failed: {e}")
        return False
    
    # Generate sample advisory
    try:
        print("\n=== Generating Sample Advisory ===")
        advisory = generate_sample_advisory(portfolio)
        print("✓ Sample advisory generated")
        print(f"  Action: {advisory.get('action', 'N/A')}")
        print(f"  Rationale: {advisory.get('rationale', 'N/A')[:60]}...")
    except Exception as e:
        print(f"✗ Advisory generation failed: {e}")
        return False
    
    print("\n✓ All systems working!")
    print("\nNext steps:")
    print("1. Configure your email settings in .env")
    print("2. Set DRY_RUN=false to send real emails")
    print("3. Run the scheduler: python3 run_scheduler.py")
    
    return True

def test_gemini_integration():
    """Test Gemini API integration"""
    import requests
    
    api_key = os.getenv('LLM_API_KEY')
    api_url = os.getenv('LLM_PROVIDER')
    
    if not api_key or not api_url:
        print("✗ Gemini API configuration missing")
        return False
    
    # Simple test prompt
    prompt = "Respond with this exact JSON: {'status': 'ok', 'message': 'Gemini API working'}"
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 100}
    }
    
    try:
        url = f"{api_url}?key={api_key}"
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result:
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"✓ Gemini API working: {content[:50]}...")
                return True
        
        print(f"✗ Gemini API error: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"✗ Gemini API exception: {e}")
        return False

def load_sample_portfolio():
    """Load sample portfolio data"""
    portfolio_file = "data/holdings.json"
    
    if os.path.exists(portfolio_file):
        with open(portfolio_file, 'r') as f:
            return json.load(f)
    
    # Create sample portfolio if not exists
    sample_portfolio = {
        "owner": "Quat",
        "currency": "VND",
        "timezone": "Asia/Ho_Chi_Minh",
        "positions": [
            {
                "ticker": "FPT",
                "exchange": "HOSE",
                "shares": 500,
                "avg_price": 121000,
                "target_price": 145000,
                "max_drawdown_pct": -12
            },
            {
                "ticker": "VNM",
                "exchange": "HOSE", 
                "shares": 300,
                "avg_price": 68000,
                "target_price": 80000,
                "max_drawdown_pct": -10
            }
        ]
    }
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Save sample portfolio
    with open(portfolio_file, 'w') as f:
        json.dump(sample_portfolio, f, indent=2)
    
    return sample_portfolio

def generate_sample_advisory(portfolio):
    """Generate sample advisory using Gemini"""
    import requests
    
    # Use first position for test
    position = portfolio["positions"][0]
    
    # Create advisory prompt
    prompt = f"""
    You are a Vietnam stock analyst. Analyze this position and respond in JSON format:
    
    Ticker: {position["ticker"]}
    Current Holdings: {position["shares"]} shares
    Average Price: {position["avg_price"]:,} VND
    Target Price: {position["target_price"]:,} VND
    
    Respond with this JSON structure:
    {{
        "action": "hold",
        "rationale": "Brief analysis of the position",
        "key_signals": ["signal1", "signal2"],
        "risk_notes": "Risk assessment",
        "levels": {{
            "add_zone": [120000, 125000],
            "take_profit_zone": [140000, 150000],
            "hard_stop": 110000
        }}
    }}
    """
    
    api_key = os.getenv('LLM_API_KEY')
    api_url = os.getenv('LLM_PROVIDER')
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 400}
    }
    
    try:
        url = f"{api_url}?key={api_key}"
        response = requests.post(url, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result:
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Try to parse JSON response
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Extract JSON from text if needed
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    
                    # Fallback response
                    return {
                        "action": "hold",
                        "rationale": "AI response could not be parsed as JSON",
                        "key_signals": ["API_RESPONSE_UNPARSED"],
                        "risk_notes": "Manual review recommended"
                    }
        
        # Fallback response for API errors
        return {
            "action": "hold", 
            "rationale": "API request failed - manual review needed",
            "key_signals": ["API_ERROR"],
            "risk_notes": "Check API configuration"
        }
        
    except Exception as e:
        return {
            "action": "hold",
            "rationale": f"Exception occurred: {str(e)[:50]}...",
            "key_signals": ["EXCEPTION"],
            "risk_notes": "System error - manual review required"
        }

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
