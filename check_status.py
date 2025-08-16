#!/usr/bin/env python3
"""
VN Stock Advisory - System Status Check
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def check_system_status():
    """Check overall system status"""
    print("=== VN Stock Advisory System Status ===")
    print(f"Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    status = {"overall": True, "components": {}}
    
    # Check environment file
    env_file = Path(".env")
    if env_file.exists():
        print("✓ Environment file (.env) exists")
        status["components"]["env_file"] = True
    else:
        print("✗ Environment file (.env) missing")
        status["components"]["env_file"] = False
        status["overall"] = False
    
    # Check portfolio file
    portfolio_file = Path("data/holdings.json")
    if portfolio_file.exists():
        try:
            with open(portfolio_file) as f:
                portfolio = json.load(f)
            positions = len(portfolio.get("positions", []))
            print(f"✓ Portfolio file exists ({positions} positions)")
            status["components"]["portfolio"] = True
        except Exception as e:
            print(f"✗ Portfolio file corrupted: {e}")
            status["components"]["portfolio"] = False
            status["overall"] = False
    else:
        print("✗ Portfolio file (data/holdings.json) missing")
        status["components"]["portfolio"] = False
        status["overall"] = False
    
    # Check directories
    dirs = ["logs", "output", "data"]
    for dir_name in dirs:
        if Path(dir_name).exists():
            print(f"✓ Directory {dir_name}/ exists")
            status["components"][f"dir_{dir_name}"] = True
        else:
            print(f"✗ Directory {dir_name}/ missing")
            status["components"][f"dir_{dir_name}"] = False
    
    # Check Python dependencies
    try:
        import requests
        import pydantic
        from dotenv import load_dotenv
        print("✓ Core Python dependencies available")
        status["components"]["python_deps"] = True
    except ImportError as e:
        print(f"✗ Missing Python dependencies: {e}")
        status["components"]["python_deps"] = False
        status["overall"] = False
    
    # Check environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            "LLM_PROVIDER", "LLM_API_KEY", 
            "SMTP_HOST", "SMTP_USER", "SMTP_PASS", "MAIL_TO"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
            status["components"]["env_vars"] = False
            status["overall"] = False
        else:
            print("✓ All required environment variables set")
            status["components"]["env_vars"] = True
            
    except Exception as e:
        print(f"✗ Error checking environment: {e}")
        status["components"]["env_vars"] = False
        status["overall"] = False
    
    # Test Gemini API
    if status["components"].get("env_vars", False):
        try:
            import requests
            api_key = os.getenv('LLM_API_KEY')
            api_url = os.getenv('LLM_PROVIDER')
            
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": "Test"}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 10}
            }
            
            url = f"{api_url}?key={api_key}"
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                print("✓ Gemini API connection successful")
                status["components"]["gemini_api"] = True
            else:
                print(f"✗ Gemini API error: {response.status_code}")
                status["components"]["gemini_api"] = False
        except Exception as e:
            print(f"✗ Gemini API test failed: {e}")
            status["components"]["gemini_api"] = False
    else:
        print("⚠ Skipping Gemini API test (missing environment)")
        status["components"]["gemini_api"] = None
    
    # Summary
    print("\n" + "="*50)
    if status["overall"]:
        print("✓ SYSTEM READY")
        print("\nYou can now run:")
        print("  python3 main.py          # Test system")
        print("  python3 run_scheduler.py # Start scheduler")
        print("  python3 run_manual.py    # Manual run")
    else:
        print("✗ SYSTEM NOT READY")
        print("\nPlease fix the issues above before running.")
        
        # Provide specific guidance
        if not status["components"].get("env_file", False):
            print("\n1. Copy .env.example to .env and configure it")
        
        if not status["components"].get("portfolio", False):
            print("\n2. Create data/holdings.json with your portfolio")
        
        if not status["components"].get("env_vars", False):
            print("\n3. Set required environment variables in .env")
    
    print()
    return status["overall"]

if __name__ == "__main__":
    success = check_system_status()
    sys.exit(0 if success else 1)
