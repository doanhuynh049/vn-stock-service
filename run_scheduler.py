#!/usr/bin/env python3
"""
VN Stock Advisory - Enhanced Scheduler Runner
Runs the enhanced AI-first daily advisory system with automated scheduling
"""

import os
import sys
import asyncio
import signal
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from advisory.enhanced_engine import EnhancedAdvisoryEngine
from advisory.enhanced_ai_advisor import AdvisoryMode
from email_service.sender import EmailSender

class GracefulKiller:
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.kill_now = True

class EnhancedScheduler:
    """Enhanced scheduler for AI-first advisory system"""
    
    def __init__(self):
        self.scheduler = None
        self.advisory_engine = None
        self.email_service = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize the enhanced advisory system"""
        try:
            from advisory.enhanced_engine import EnhancedAdvisoryEngine
            from email_service.sender import EmailSender
            
            # Initialize advisory engine
            self.advisory_engine = EnhancedAdvisoryEngine()
            self.logger.info("✓ Enhanced advisory engine initialized")
            
            # Initialize email service
            self.email_service = EmailSender()
            self.logger.info("✓ Email service initialized")
            
            # Initialize scheduler
            self.scheduler = AsyncIOScheduler()
            
            # Configure scheduling
            self._setup_jobs()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def _setup_jobs(self):
        """Setup scheduled jobs"""
        # Get schedule configuration
        schedule_cron = os.getenv('SCHEDULE_CRON', '30 7 * * 1-5')  # 7:30 AM Monday-Friday
        timezone = os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh')
        
        # Parse cron expression
        cron_parts = schedule_cron.split()
        if len(cron_parts) == 5:
            minute, hour, day, month, day_of_week = cron_parts
        else:
            # Default fallback
            minute, hour, day, month, day_of_week = "30", "7", "*", "*", "1-5"
        
        # Add daily advisory job
        self.scheduler.add_job(
            self.run_daily_advisory,
            CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                timezone=timezone
            ),
            id='daily_advisory',
            name='Daily Stock Advisory',
            misfire_grace_time=600  # 10 minutes grace time
        )
        
        self.logger.info(f"Daily advisory scheduled: {schedule_cron} ({timezone})")
        
        # Add weekly summary job (Fridays at 6 PM)
        self.scheduler.add_job(
            self.run_weekly_summary,
            CronTrigger(
                minute=0,
                hour=18,
                day_of_week='fri',
                timezone=timezone
            ),
            id='weekly_summary',
            name='Weekly Portfolio Summary',
            misfire_grace_time=1800  # 30 minutes grace time
        )
        
        self.logger.info("Weekly summary scheduled: Fridays 6:00 PM")
        
        # Add Entry & Exit Strategy analysis job (Mondays at 8 AM)
        self.scheduler.add_job(
            self.run_entry_exit_analysis,
            CronTrigger(
                minute=0,
                hour=8,
                day_of_week='mon',
                timezone=timezone
            ),
            id='entry_exit_strategy',
            name='Entry & Exit Strategy Analysis',
            misfire_grace_time=600  # 10 minutes grace time
        )
        
        self.logger.info("Entry & Exit Strategy analysis scheduled: Mondays 8:00 AM")
        
        # Add Dual Advisory job (send both emails sequentially) - Tuesdays at 8:30 AM
        self.scheduler.add_job(
            self.run_dual_advisory_sequential,
            CronTrigger(
                minute=30,
                hour=8,
                day_of_week='tue',
                timezone=timezone
            ),
            id='dual_advisory_sequential',
            name='Dual Advisory - Sequential Email Sending',
            misfire_grace_time=600  # 10 minutes grace time
        )
        
        self.logger.info("Dual Advisory (sequential emails) scheduled: Tuesdays 8:30 AM")
    
    async def run_daily_advisory(self):
        """Run daily advisory analysis and send notifications"""
        try:
            self.logger.info("Starting daily advisory analysis...")
            
            # Generate comprehensive advisory
            advisory = self.advisory_engine.generate_daily_advisory(save_to_history=True)
            
            if "error" in advisory:
                self.logger.error(f"Advisory generation failed: {advisory['error']}")
                return False
            
            self.logger.info("✓ Daily advisory generated successfully")
            
            # Prepare email data
            portfolio_summary = advisory['portfolio_summary']
            main_advisory = advisory['main_advisory']
            
            email_data = {
                "advisory_date": advisory['advisory_date'],
                "advisory_mode": advisory['advisory_mode'],
                "portfolio": portfolio_summary,
                "advisory": main_advisory,
                "additional_analyses": advisory.get('additional_analyses', {}),
                "user_preferences": advisory.get('user_preferences', {})
            }
            
            # Send email notification
            dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
            
            if dry_run:
                self.logger.info("DRY RUN MODE - Email would be sent with:")
                self.logger.info(f"  Portfolio positions: {portfolio_summary['total_positions']}")
                self.logger.info(f"  Total value: {portfolio_summary['total_invested_value']:,.0f} VND")
                self.logger.info(f"  Advisory mode: {advisory['advisory_mode']}")
                self.logger.info(f"  Action items: {len(main_advisory.get('action_items', []))}")
            else:
                # Send actual email
                success = await self.email_service.send_daily_advisory(email_data)
                if success:
                    self.logger.info("✓ Daily advisory email sent successfully")
                else:
                    self.logger.error("✗ Failed to send daily advisory email")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Daily advisory job failed: {e}")
            return False
    
    async def run_weekly_summary(self):
        """Run weekly portfolio summary"""
        try:
            self.logger.info("Starting weekly portfolio summary...")
            
            # Get portfolio evolution for the week
            evolution = self.advisory_engine.get_portfolio_evolution(days=7)
            
            if "error" in evolution:
                self.logger.error(f"Weekly summary failed: {evolution['error']}")
                return False
            
            # Generate weekly insights
            weekly_advisory = self.advisory_engine.generate_daily_advisory(save_to_history=True)
            
            email_data = {
                "summary_date": datetime.now().strftime('%Y-%m-%d'),
                "evolution": evolution,
                "weekly_advisory": weekly_advisory,
                "summary_type": "weekly"
            }
            
            dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
            
            if dry_run:
                self.logger.info("DRY RUN MODE - Weekly summary would be sent")
            else:
                success = await self.email_service.send_weekly_summary(email_data)
                if success:
                    self.logger.info("✓ Weekly summary email sent successfully")
                else:
                    self.logger.error("✗ Failed to send weekly summary email")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Weekly summary job failed: {e}")
            return False
    
    async def run_entry_exit_analysis(self):
        """Run Entry & Exit Strategy analysis task"""
        try:
            self.logger.info("🎯 Starting scheduled Entry & Exit Strategy analysis...")
            
            # Initialize engine with Entry & Exit Strategy mode
            engine = EnhancedAdvisoryEngine(
                gemini_api_key=os.getenv('GEMINI_API_KEY'),
                advisory_mode=AdvisoryMode.ENTRY_EXIT_STRATEGY,
                email_sender=self.email_service
            )
            
            # Generate and send analysis
            result = engine.generate_daily_advisory(
                save_to_history=True,
                send_email=True,
                email_recipient=os.getenv('NOTIFICATION_EMAIL')
            )
            
            if result.get("success"):
                self.logger.info("✅ Entry & Exit Strategy analysis completed successfully")
            else:
                self.logger.error("❌ Entry & Exit Strategy analysis failed")
            
            return result.get("success", False)
            
        except Exception as e:
            self.logger.error(f"Entry & Exit Strategy analysis job failed: {e}")
            return False
    
    async def run_dual_advisory_sequential(self):
        """Run Dual Advisory - send both emails sequentially (tuần tự)"""
        try:
            self.logger.info("📧 Starting scheduled Dual Advisory (sequential email sending)...")
            
            # Initialize engine
            engine = EnhancedAdvisoryEngine(
                gemini_api_key=os.getenv('GEMINI_API_KEY'),
                email_sender=self.email_service
            )
            
            # Generate and send both advisories sequentially
            result = engine.generate_dual_advisory_with_emails(
                save_to_history=True,
                email_recipient=os.getenv('NOTIFICATION_EMAIL')
            )
            
            if result.get("success"):
                emails_sent = result.get("emails_sent", {})
                total_sent = sum(emails_sent.values())
                self.logger.info(f"✅ Dual Advisory completed - {total_sent}/2 emails sent")
                self.logger.info(f"   📊 Regular advisory: {'✓' if emails_sent.get('regular') else '✗'}")
                self.logger.info(f"   🎯 Entry & Exit Strategy: {'✓' if emails_sent.get('entry_exit') else '✗'}")
            else:
                self.logger.error("❌ Dual Advisory failed")
            
            return result.get("success", False)
            
        except Exception as e:
            self.logger.error(f"Dual Advisory sequential job failed: {e}")
            return False

    def start(self):
        """Start the scheduler"""
        if self.scheduler:
            self.scheduler.start()
            self.logger.info("✓ Enhanced scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler:
            self.scheduler.shutdown()
            self.logger.info("✓ Enhanced scheduler stopped")

async def main():
    """Main scheduler function"""
    print("=== VN Stock Advisory - Enhanced Scheduler ===")
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
    os.makedirs("config", exist_ok=True)
    
    try:
        # Initialize enhanced scheduler
        enhanced_scheduler = EnhancedScheduler()
        killer = GracefulKiller()
        
        print("✓ Initializing enhanced advisory system...")
        
        success = await enhanced_scheduler.initialize()
        if not success:
            print("✗ Failed to initialize enhanced advisory system")
            return False
        
        # Get configuration info
        schedule_cron = os.getenv('SCHEDULE_CRON', '30 7 * * 1-5')
        timezone = os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh')
        dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        print(f"✓ Enhanced advisory system initialized")
        print(f"  Daily Schedule: {schedule_cron}")
        print(f"  Weekly Summary: Fridays 6:00 PM")
        print(f"  Timezone: {timezone}")
        print(f"  Dry Run: {dry_run}")
        
        if dry_run:
            print("  ⚠  DRY RUN MODE - No emails will be sent")
        
        # Start scheduler
        enhanced_scheduler.start()
        
        print("✓ Enhanced scheduler started successfully")
        print("\nFeatures enabled:")
        print("• AI-only analysis (no price fetching)")
        print("• Daily comprehensive advisory")
        print("• Weekly portfolio summaries")
        print("• Historical tracking and insights")
        print("• Scenario analysis integration")
        print("• User configuration management")
        
        print("\n  Press Ctrl+C to stop")
        
        # Keep running until interrupted
        while not killer.kill_now:
            await asyncio.sleep(1)
        
        print("\n✓ Stopping enhanced scheduler...")
        enhanced_scheduler.stop()
        print("✓ Enhanced scheduler stopped gracefully")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced scheduler error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        # Python 3.6+ compatible asyncio
        if sys.version_info >= (3, 7):
            success = asyncio.run(main())
        else:
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
