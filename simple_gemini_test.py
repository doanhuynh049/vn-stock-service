#!/usr/bin/env python3
"""
Simple Gemini API test without complex dependencies
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API directly"""
    print("=== Testing Gemini API ===")
    
    # Get configuration
    api_key = os.getenv('LLM_API_KEY')
    api_url = os.getenv('LLM_PROVIDER')
    
    if not api_key:
        print("✗ LLM_API_KEY not found in environment")
        return False
        
    if not api_url:
        print("✗ LLM_PROVIDER not found in environment") 
        return False
        
    print(f"✓ API Key: {api_key[:20]}...")
    print(f"✓ API URL: {api_url}")
    
    # Create test prompt
    test_prompt = """
    You are a Vietnam stock analyst. Analyze the following data and respond in JSON format:

    Stock: FPT
    Current Price: 123,000 VND
    Average Cost: 121,000 VND
    Target Price: 145,000 VND

    Please respond with this exact JSON structure:
    {
        "action": "hold",
        "rationale": "Stock is trading above average cost with good upside potential",
        "key_signals": ["positive momentum", "above average cost"],
        "risk_notes": "Monitor for any reversal signals",
        "levels": {
            "add_zone": [120000, 122000],
            "take_profit_zone": [142000, 146000], 
            "hard_stop": 115000
        },
        "next_checks": ["RSI levels", "volume confirmation"]
    }
    """
    
    # Prepare request
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": test_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 500
        }
    }
    
    url = f"{api_url}?key={api_key}"
    
    try:
        print("\n=== Sending request to Gemini ===")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Request successful!")
            
            # Extract content
            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"\n=== Gemini Response ===")
                print(content)
                
                # Try to parse as JSON
                try:
                    parsed = json.loads(content)
                    print("\n✓ Response parsed as JSON successfully!")
                    print(json.dumps(parsed, indent=2))
                    return True
                except json.JSONDecodeError:
                    print("\n⚠ Response is not valid JSON, but API call succeeded")
                    return True
            else:
                print("✗ No candidates in response")
                print("Response:", json.dumps(result, indent=2))
                return False
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print("Response:", response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if success:
        print("\n✓ Gemini API test completed successfully!")
    else:
        print("\n✗ Gemini API test failed!")
