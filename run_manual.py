#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VN Stock Advisory - Manual Run
Run the advisory task once manually for testing
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_advisory_task():
    """Run the advisory task once"""
    print("=== VN Stock Advisory - Manual Run ===")
    print("Started at: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[OK] Environment loaded")
    except ImportError:
        print("[ERROR] python-dotenv not installed")
        return False
    
    # Ensure directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    try:
        # Import components
        from scheduler.jobs import StockAdvisoryScheduler
        
        print("[OK] Components loaded")
        
        # Create scheduler (but don't start it)
        scheduler = StockAdvisoryScheduler()
        
        # Run the task directly (it's not async)
        print("\n=== Running Advisory Task ===")
        
        # Run the daily advisory task
        scheduler.run_daily_advisory()
        
        print("[OK] Advisory task completed!")
        
        # Show output files
        output_dir = Path("output")
        if output_dir.exists():
            print("\nGenerated files in output/:")
            for file in output_dir.iterdir():
                if file.is_file():
                    print("  - {}".format(file.name))
        
        print("\nCheck logs/vn-stock-advisory.log for detailed logs")
        
        return True
        
    except Exception as e:
        print("[ERROR] Task failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = run_advisory_task()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[OK] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print("\n[ERROR] Unexpected error: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
