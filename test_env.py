#!/usr/bin/env python3

import os
import sys

print("=== Environment Test ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Check if .env file exists
env_file = ".env"
if os.path.exists(env_file):
    print(f"✓ Found .env file")
    with open(env_file, 'r') as f:
        content = f.read()
        print(f"Content preview: {content[:200]}...")
else:
    print("✗ No .env file found")

# Try to load dotenv
try:
    from dotenv import load_dotenv
    result = load_dotenv()
    print(f"✓ Dotenv loaded: {result}")
    
    # Check specific variables
    llm_provider = os.getenv('LLM_PROVIDER')
    llm_api_key = os.getenv('LLM_API_KEY')
    
    print(f"LLM_PROVIDER: {llm_provider}")
    print(f"LLM_API_KEY: {llm_api_key[:20] if llm_api_key else 'None'}...")
    
except ImportError as e:
    print(f"✗ Could not import dotenv: {e}")
except Exception as e:
    print(f"✗ Error loading dotenv: {e}")

# Try to load settings
try:
    sys.path.insert(0, '.')
    from src.config.settings import Settings
    settings = Settings()
    print("✓ Settings loaded successfully")
    print(f"LLM Provider from settings: {settings.LLM_PROVIDER}")
    
except Exception as e:
    print(f"✗ Settings loading failed: {e}")
    import traceback
    traceback.print_exc()

print("=== End Test ===")
