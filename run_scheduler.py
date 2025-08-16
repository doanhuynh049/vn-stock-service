#!/usr/bin/env python3
"""
VN Stock Advisory - Scheduler Runner
Runs the daily notification scheduler
"""

import os
import sys
import asyncio
import signal
import logging
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class GracefulKiller:
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.kill_now = True

async def main():
    """Run the scheduler"""
    print("=== VN Stock Advisory - Scheduler ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Environment loaded")
    except ImportError:
        print("✗ python-dotenv not installed")
        return False
    
    # Setup logging
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/scheduler.log')
        ] if os.getenv('LOG_FILE') else [logging.StreamHandler()]
    )
    
    # Ensure directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    try:
        # Import scheduler components
        from scheduler.jobs import StockAdvisoryScheduler
        
        print("✓ Scheduler components loaded")
        
        # Create scheduler
        scheduler = StockAdvisoryScheduler()
        killer = GracefulKiller()
        
        print("✓ Starting scheduler...")
        
        # Get schedule info
        schedule_cron = os.getenv('SCHEDULE_CRON', '30 7 * * *')
        timezone = os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh')
        dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        print(f"  Schedule: {schedule_cron}")
        print(f"  Timezone: {timezone}")
        print(f"  Dry Run: {dry_run}")
        
        if dry_run:
            print("  ⚠  DRY RUN MODE - No emails will be sent")
        
        # Start scheduler
        scheduler.start()
        
        print("✓ Scheduler started successfully")
        print("  Press Ctrl+C to stop")
        
        # Keep running until interrupted
        while not killer.kill_now:
            await asyncio.sleep(1)
        
        print("\n✓ Stopping scheduler...")
        scheduler.stop()
        print("✓ Scheduler stopped gracefully")
        
        return True
        
    except Exception as e:
        print(f"✗ Scheduler error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        # Python 3.6 compatible asyncio
        loop = asyncio.get_event_loop()
        success = loop.run_until_complete(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
