#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VN Stock Advisory - Manual Run (Enhanced AI-First Version)
Run the enhanced AI advisory task once manually for testing.
Uses holdings-only data with advanced AI analysis.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_advisory_task():
    """Run the enhanced AI advisory task once for manual testing"""
    print("=== VN Stock Advisory - Enhanced Manual Run ===")
    print("Started at: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    # Configure debug logging
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
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
        # Import components for enhanced AI-first system
        from adapters.holdings_provider import HoldingsOnlyProvider
        from advisory.enhanced_ai_advisor import EnhancedAIAdvisor, AdvisoryMode
        from advisory.enhanced_engine import EnhancedAdvisoryEngine
        from config.user_config import ConfigManager
        from config.settings import Settings
        from email_service.sender import EmailSender, DryRunEmailSender
        from data.historical_store import HistoricalDataStore
        
        print("[OK] Enhanced components loaded")
        
        # Load settings
        settings = Settings()
        
        # Initialize configuration
        print("\n=== Initializing Enhanced Advisory Engine ===")
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize components
        holdings_provider = HoldingsOnlyProvider()
        ai_advisor = EnhancedAIAdvisor(
            api_key=settings.LLM_API_KEY,
            api_url=settings.LLM_PROVIDER
        )
        
        # Email sender - use real sender if SMTP is configured
        if settings.DRY_RUN or not settings.SMTP_HOST:
            email_sender = DryRunEmailSender()
            print("[INFO] Using DryRunEmailSender (no actual emails will be sent)")
        else:
            email_sender = EmailSender(
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_user=settings.SMTP_USER,
                smtp_pass=settings.SMTP_PASS,
                mail_from=settings.MAIL_FROM,
                smtp_tls=settings.SMTP_TLS
            )
            print(f"[INFO] Using EmailSender (will send emails to {settings.MAIL_TO})")
        historical_store = HistoricalDataStore()
        
        # Create enhanced engine with just the holdings file path
        # Create enhanced engine with email sender
        engine = EnhancedAdvisoryEngine(
            holdings_file=settings.HOLDINGS_FILE,
            email_sender=email_sender
        )
        
        print("[OK] Enhanced advisory engine initialized")
        
        # Run the enhanced advisory task
        print("\n=== Running Enhanced AI Advisory Task ===")
        result = engine.generate_daily_advisory()
        
        if result.get("success"):
            print("[OK] Enhanced advisory task completed!")
            
            # Show summary
            summary = result.get("summary", {})
            print(f"\nAdvisory Summary:")
            print(f"  - Holdings processed: {summary.get('holdings_count', 0)}")
            print(f"  - Advisory mode: {summary.get('advisory_mode', 'N/A')}")
            print(f"  - Email sent: {summary.get('email_sent', False)}")
            print(f"  - Duration: {summary.get('duration_seconds', 0):.2f}s")
        else:
            print(f"[ERROR] Advisory task failed: {result.get('error', 'Unknown error')}")
            return False
        
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
