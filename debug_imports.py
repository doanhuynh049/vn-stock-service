#!/usr/bin/env python3
"""
Debug Manual Run - with detailed error reporting
"""

import os
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_imports():
    """Debug import issues"""
    print("=== Debug Imports ===")
    
    try:
        from dotenv import load_dotenv
        print("✓ dotenv imported")
        
        load_dotenv()
        print("✓ .env loaded")
        
        # Check key environment variables
        print(f"LLM_API_KEY: {'✓' if os.getenv('LLM_API_KEY') else '✗'}")
        print(f"LLM_PROVIDER: {'✓' if os.getenv('LLM_PROVIDER') else '✗'}")
        
    except Exception as e:
        print(f"✗ Dotenv error: {e}")
        return False
    
    try:
        from config.settings import Settings
        settings = Settings()
        print("✓ Settings imported and created")
    except Exception as e:
        print(f"✗ Settings error: {e}")
        traceback.print_exc()
        return False
    
    try:
        from models.holdings import Holdings
        print("✓ Holdings model imported")
    except Exception as e:
        print(f"✗ Holdings model error: {e}")
        traceback.print_exc()
        return False
    
    try:
        from adapters.mock_provider import MockDataProvider
        provider = MockDataProvider()
        print("✓ Mock provider imported and created")
    except Exception as e:
        print(f"✗ Mock provider error: {e}")
        traceback.print_exc()
        return False
    
    try:
        from advisory.ai_advisor import AIAdvisor
        advisor = AIAdvisor(
            api_key=settings.LLM_API_KEY,
            api_url=settings.LLM_PROVIDER
        )
        print("✓ AI advisor imported and created")
    except Exception as e:
        print(f"✗ AI advisor error: {e}")
        traceback.print_exc()
        return False
    
    try:
        from advisory.engine import AdvisoryEngine
        engine = AdvisoryEngine(advisor)
        print("✓ Advisory engine imported and created")
    except Exception as e:
        print(f"✗ Advisory engine error: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = debug_imports()
        if success:
            print("\n✓ All imports successful!")
        else:
            print("\n✗ Some imports failed")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
