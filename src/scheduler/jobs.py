import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore

from config.settings import settings
from models.holdings import Holdings
from models.market_data import MarketDataCache
from adapters.vn_data_provider import DataProviderFactory
from advisory.engine import AdvisoryEngine
from advisory.ai_advisor import AIAdvisor
from email_service.sender import EmailSender, DryRunEmailSender

logger = logging.getLogger(__name__)

class StockAdvisoryScheduler:
    """Main scheduler for stock advisory notifications"""
    
    def __init__(self):
        # Setup scheduler
        jobstores = {'default': MemoryJobStore()}
        executors = {'default': ThreadPoolExecutor(20)}
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=pytz.timezone(settings.TIMEZONE)
        )
        
        # Initialize components
        self.data_provider = DataProviderFactory.create_provider(
            settings.VN_DATA_PROVIDER,
            api_key=settings.VN_API_KEY,
            base_url=settings.VN_BASE_URL
        )
        
        self.ai_advisor = AIAdvisor(
            api_key=settings.LLM_API_KEY,
            api_url=settings.LLM_PROVIDER
        )
        
        self.advisory_engine = AdvisoryEngine(self.ai_advisor)
        
        # Email sender
        if settings.DRY_RUN:
            self.email_sender = DryRunEmailSender()
        else:
            self.email_sender = EmailSender(
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_user=settings.SMTP_USER,
                smtp_pass=settings.SMTP_PASS,
                mail_from=settings.MAIL_FROM,
                smtp_tls=settings.SMTP_TLS
            )
        
        self.market_cache = MarketDataCache(cache_ttl_minutes=settings.CACHE_TTL_MINUTES)
        
    def start(self):
        """Start the scheduler"""
        try:
            # Add the daily job
            self.add_daily_advisory_job()
            
            # Start scheduler
            self.scheduler.start()
            logger.info("Stock advisory scheduler started")
            
            # Test email connection
            if not settings.DRY_RUN:
                if self.email_sender.test_connection():
                    logger.info("Email connection test successful")
                else:
                    logger.warning("Email connection test failed")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Stock advisory scheduler stopped")
    
    def add_daily_advisory_job(self):
        """Add the daily advisory job to scheduler"""
        # Parse cron expression
        cron_parts = settings.SCHEDULE_CRON.split()
        if len(cron_parts) != 5:
            raise ValueError(f"Invalid cron expression: {settings.SCHEDULE_CRON}")
        
        minute, hour, day, month, day_of_week = cron_parts
        
        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            timezone=pytz.timezone(settings.TIMEZONE)
        )
        
        self.scheduler.add_job(
            func=self.run_daily_advisory,
            trigger=trigger,
            id='daily_advisory',
            name='Daily Stock Advisory',
            replace_existing=True
        )
        
        logger.info(f"Daily advisory job scheduled: {settings.SCHEDULE_CRON} {settings.TIMEZONE}")
    
    def run_daily_advisory(self):
        """Main job function that runs daily advisory"""
        start_time = datetime.now()
        logger.info("=== Starting Daily Stock Advisory Analysis ===")
        
        try:
            # Load holdings
            holdings = self.load_holdings()
            logger.info(f"Loaded {len(holdings.positions)} positions")
            
            # Fetch market data for all positions
            market_data = self.fetch_market_data(holdings)
            logger.info(f"Fetched market data for {len(market_data)} positions")
            
            # Generate individual stock advisories
            stock_advisories = self.generate_stock_advisories(holdings, market_data)
            logger.info(f"Generated {len(stock_advisories)} stock advisories")
            
            # Generate portfolio advisory
            portfolio_advisory = self.generate_portfolio_advisory(holdings, market_data)
            logger.info("Generated portfolio advisory")
            
            # Send emails
            self.send_advisory_emails(stock_advisories, portfolio_advisory, holdings)
            
            # Log completion
            duration = datetime.now() - start_time
            logger.info(f"=== Daily advisory completed in {duration.total_seconds():.2f} seconds ===")
            
        except Exception as e:
            logger.error(f"Daily advisory job failed: {e}", exc_info=True)
            
            # Send error notification
            self.send_error_notification(str(e))
    
    def load_holdings(self) -> Holdings:
        """Load holdings from file"""
        try:
            return Holdings.from_json_file(settings.HOLDINGS_FILE)
        except Exception as e:
            logger.error(f"Failed to load holdings from {settings.HOLDINGS_FILE}: {e}")
            raise
    
    def fetch_market_data(self, holdings: Holdings) -> Dict[str, Dict[str, Any]]:
        """Fetch market data for all positions"""
        market_data = {}
        
        for position in holdings.positions:
            ticker = position.ticker
            
            try:
                # Check cache first
                cached_data = self.market_cache.get(ticker)
                if cached_data and settings.CACHE_ENABLED:
                    logger.debug(f"Using cached data for {ticker}")
                    market_data[ticker] = cached_data.dict()
                    continue
                
                # Fetch fresh data
                logger.debug(f"Fetching fresh data for {ticker}")
                
                # Get quote
                quote_data = self.data_provider.get_quote(ticker, position.exchange)
                
                # Get OHLCV data for multiple timeframes
                ohlcv_data = {}
                for window in ["5D", "1M", "3M"]:
                    try:
                        ohlcv = self.data_provider.get_ohlcv(ticker, window, position.exchange)
                        if ohlcv and ohlcv.get("data"):
                            ohlcv_data = ohlcv["data"]  # Use the most recent successful fetch
                            break
                    except Exception as e:
                        logger.warning(f"Failed to fetch {window} OHLCV for {ticker}: {e}")
                
                # Get fundamentals
                fundamentals_data = {}
                try:
                    fundamentals_data = self.data_provider.get_fundamentals(ticker, position.exchange)
                except Exception as e:
                    logger.warning(f"Failed to fetch fundamentals for {ticker}: {e}")
                
                # Get news sentiment
                news_data = {}
                try:
                    news_data = self.data_provider.get_news(ticker)
                except Exception as e:
                    logger.warning(f"Failed to fetch news for {ticker}: {e}")
                
                # Combine all data
                combined_data = {
                    "ticker": ticker,
                    "exchange": position.exchange,
                    "price": quote_data.get("price", 0),
                    "change": quote_data.get("change", 0),
                    "change_pct": quote_data.get("change_pct", 0),
                    "volume": quote_data.get("volume", 0),
                    "timestamp": quote_data.get("timestamp", datetime.now().isoformat()),
                    "ohlcv": ohlcv_data,
                    "fundamentals": fundamentals_data,
                    "news_sentiment": news_data
                }
                
                market_data[ticker] = combined_data
                
                # Cache the data
                if settings.CACHE_ENABLED:
                    # Would need to convert to MarketData model for caching
                    pass
                
            except Exception as e:
                logger.error(f"Failed to fetch market data for {ticker}: {e}")
                # Use fallback data
                market_data[ticker] = {
                    "ticker": ticker,
                    "exchange": position.exchange,
                    "price": position.avg_price,  # Fallback to avg price
                    "change": 0,
                    "change_pct": 0,
                    "volume": 0,
                    "timestamp": datetime.now().isoformat(),
                    "ohlcv": {},
                    "fundamentals": {},
                    "news_sentiment": {}
                }
        
        return market_data
    
    def generate_stock_advisories(self, holdings: Holdings, 
                                  market_data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate advisory for each stock position"""
        advisories = []
        
        for position in holdings.positions:
            ticker = position.ticker
            
            if ticker not in market_data:
                logger.warning(f"No market data available for {ticker}, skipping advisory")
                continue
            
            try:
                advisory = self.advisory_engine.generate_stock_advisory(
                    position.dict(), 
                    market_data[ticker]
                )
                advisories.append(advisory)
                logger.debug(f"Generated advisory for {ticker}: {advisory['advisory']['action']}")
                
            except Exception as e:
                logger.error(f"Failed to generate advisory for {ticker}: {e}")
        
        return advisories
    
    def generate_portfolio_advisory(self, holdings: Holdings, 
                                   market_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate portfolio-level advisory"""
        try:
            return self.advisory_engine.generate_portfolio_advisory(
                [pos.dict() for pos in holdings.positions],
                market_data
            )
        except Exception as e:
            logger.error(f"Failed to generate portfolio advisory: {e}")
            return {
                "portfolio_metrics": {},
                "advisory": {"priority_todos": ["Check system errors"]},
                "generated_at": datetime.now().isoformat()
            }
    
    def send_advisory_emails(self, stock_advisories: List[Dict[str, Any]], 
                            portfolio_advisory: Dict[str, Any], holdings: Holdings):
        """Send all advisory emails"""
        logger.info("Sending advisory emails")
        if not stock_advisories:
            logger.warning("No stock advisories to send")
            return
        if not portfolio_advisory:
            logger.warning("No portfolio advisory to send")
            return
        try:
            # Send consolidated all-stocks advisory email
            success = self.email_sender.send_all_stocks_advisory_email(
                stock_advisories,
                holdings.dict(),
                portfolio_advisory["portfolio_metrics"],
                settings.MAIL_TO
            )
            if success:
                logger.info(f"Sent consolidated stock advisory email for {len(stock_advisories)} positions")
            else:
                logger.error("Failed to send consolidated stock advisory email")
            
            # Still send portfolio overview email for high-level summary
            success = self.email_sender.send_portfolio_overview_email(
                portfolio_advisory, 
                holdings.dict(), 
                settings.MAIL_TO
            )
            if success:
                logger.info("Sent portfolio overview email")
            else:
                logger.error("Failed to send portfolio overview email")
                
        except Exception as e:
            logger.error(f"Error sending advisory emails: {e}")
    
    def send_error_notification(self, error_message: str):
        """Send error notification email"""
        try:
            subject = f"🚨 VN Stock Advisory Error - {datetime.now().strftime('%Y-%m-%d')}"
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="background-color: #f8d7da; padding: 20px; border-radius: 5px;">
                    <h2 style="color: #721c24;">Stock Advisory System Error</h2>
                    <p><strong>Time:</strong> {datetime.now().isoformat()}</p>
                    <p><strong>Error:</strong> {error_message}</p>
                    <p>Please check the system logs for more details.</p>
                </div>
            </body>
            </html>
            """
            
            self.email_sender.send_email(settings.MAIL_TO, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
    
    def run_manual_advisory(self) -> Dict[str, Any]:
        """Run advisory manually (for testing)"""
        logger.info("Running manual advisory analysis")
        
        import asyncio
        return asyncio.run(self.run_daily_advisory())
    
    def get_job_status(self) -> Dict[str, Any]:
        """Get status of scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": self.scheduler.running,
            "timezone": settings.TIMEZONE,
            "jobs": jobs,
            "cache_info": self.market_cache.get_cache_info() if settings.CACHE_ENABLED else None
        }

