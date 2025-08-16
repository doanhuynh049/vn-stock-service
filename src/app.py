#!/usr/bin/env python3
"""
VN Stock Advisory Notifier
A production-ready background app for Vietnam stock analysis and daily email notifications.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from .config.settings import settings
from .scheduler.jobs import StockAdvisoryScheduler
from .models.holdings import Holdings

# Setup logging
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: StockAdvisoryScheduler = None

# FastAPI app for optional API endpoints
app = FastAPI(
    title="VN Stock Advisory Notifier",
    description="Vietnam Stock Advisory and Email Notification System",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize and start the scheduler"""
    global scheduler
    
    try:
        logger.info("Starting VN Stock Advisory Notifier...")
        
        # Ensure required directories exist
        Path("logs").mkdir(exist_ok=True)
        Path("output").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        
        # Initialize scheduler
        scheduler = StockAdvisoryScheduler()
        scheduler.start()
        
        logger.info("VN Stock Advisory Notifier started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown the scheduler"""
    global scheduler
    
    if scheduler:
        logger.info("Shutting down VN Stock Advisory Notifier...")
        scheduler.stop()
        logger.info("Scheduler stopped")

# API Endpoints for monitoring and manual operations

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "service": "VN Stock Advisory Notifier", 
        "version": "1.0.0",
        "status": "running" if scheduler and scheduler.scheduler.running else "stopped"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    return {
        "status": "healthy" if scheduler.scheduler.running else "unhealthy",
        "scheduler_running": scheduler.scheduler.running,
        "timestamp": "2025-01-21T10:00:00Z"  # Would use actual timestamp
    }

@app.get("/status")
async def get_status():
    """Get detailed status information"""
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    return scheduler.get_job_status()

@app.post("/run-advisory")
async def run_manual_advisory():
    """Manually trigger advisory analysis"""
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    try:
        logger.info("Manual advisory triggered via API")
        await scheduler.run_daily_advisory()
        return {"status": "success", "message": "Advisory analysis completed"}
    except Exception as e:
        logger.error(f"Manual advisory failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/holdings")
async def get_holdings():
    """Get current holdings"""
    try:
        holdings = Holdings.from_json_file(settings.HOLDINGS_FILE)
        return holdings.dict()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to load holdings: {e}")

@app.get("/config")
async def get_config():
    """Get current configuration (sensitive data masked)"""
    config = {
        "VN_DATA_PROVIDER": settings.VN_DATA_PROVIDER,
        "SCHEDULE_CRON": settings.SCHEDULE_CRON,
        "TIMEZONE": settings.TIMEZONE,
        "LLM_PROVIDER": settings.LLM_PROVIDER,
        "CACHE_ENABLED": settings.CACHE_ENABLED,
        "DRY_RUN": settings.DRY_RUN,
        "DEBUG": settings.DEBUG
    }
    return config

# CLI Functions

def run_scheduler_only():
    """Run the scheduler without FastAPI (for production deployment)"""
    logger.info("Starting VN Stock Advisory Notifier (scheduler only)")
    
    # Global scheduler
    global scheduler
    scheduler = StockAdvisoryScheduler()
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        if scheduler:
            scheduler.stop()
        sys.exit(0)
    
    # Handle shutdown signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        scheduler.start()
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            import time
            time.sleep(60)  # Sleep for 1 minute
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        if scheduler:
            scheduler.stop()

def run_manual_analysis():
    """Run a single advisory analysis manually"""
    logger.info("Running manual stock advisory analysis")
    
    scheduler = StockAdvisoryScheduler()
    
    try:
        asyncio.run(scheduler.run_daily_advisory())
        logger.info("Manual analysis completed successfully")
    except Exception as e:
        logger.error(f"Manual analysis failed: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VN Stock Advisory Notifier")
    parser.add_argument("--mode", choices=["api", "scheduler", "manual"], 
                       default="scheduler", help="Run mode")
    parser.add_argument("--host", default="0.0.0.0", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (dev only)")
    
    args = parser.parse_args()
    
    if args.mode == "api":
        # Run with FastAPI
        uvicorn.run(
            "src.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    elif args.mode == "scheduler":
        # Run scheduler only
        run_scheduler_only()
    elif args.mode == "manual":
        # Run manual analysis
        run_manual_analysis()

if __name__ == "__main__":
    main()