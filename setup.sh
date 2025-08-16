#!/bin/bash

# VN Stock Advisory - Setup and Test Script

set -e  # Exit on any error

echo "=== VN Stock Advisory Setup ==="
echo

# Check Python version
echo "Checking Python version..."
python3 --version
echo

# Install core dependencies
echo "Installing core dependencies..."
python3 -m pip install --user requests python-dotenv pydantic fastapi uvicorn tenacity
echo "✓ Core dependencies installed"
echo

# Check .env file
echo "Checking configuration..."
if [ -f ".env" ]; then
    echo "✓ .env file found"
    if grep -q "LLM_API_KEY" .env; then
        echo "✓ LLM_API_KEY found in .env"
    else
        echo "✗ LLM_API_KEY not found in .env"
        exit 1
    fi
    if grep -q "LLM_PROVIDER" .env; then
        echo "✓ LLM_PROVIDER found in .env"
    else
        echo "✗ LLM_PROVIDER not found in .env"
        exit 1
    fi
else
    echo "✗ .env file not found"
    echo "Please copy .env.example to .env and configure your API key"
    exit 1
fi
echo

# Test Gemini API
echo "Testing Gemini API..."
python3 simple_gemini_test.py
echo

echo "=== Setup Complete ==="
echo "You can now run the stock advisory system with:"
echo "  python3 src/app.py"
echo
