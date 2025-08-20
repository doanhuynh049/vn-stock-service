#!/usr/bin/env python3
"""
VN Stock Advisory Notifier - Enhanced AI-First System
Enhanced background app for Vietnam stock analysis with AI-only advisory.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn

from .config.settings import settings
from .advisory.enhanced_engine import EnhancedAdvisoryEngine
from .config.user_config import get_user_config
from .data.historical_store import historical_store

# Setup logging
logger = logging.getLogger(__name__)

# Global advisory engine instance
advisory_engine: EnhancedAdvisoryEngine = None

# FastAPI app for API endpoints and dashboard
app = FastAPI(
    title="VN Stock Advisory - Enhanced AI System",
    description="Vietnam Stock Advisory with AI-Only Analysis",
    version="2.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize the enhanced advisory system"""
    global advisory_engine
    
    try:
        logger.info("Starting Enhanced VN Stock Advisory System...")
        
        # Ensure required directories exist
        Path("logs").mkdir(exist_ok=True)
        Path("output").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        Path("config").mkdir(exist_ok=True)
        
        # Initialize advisory engine
        advisory_engine = EnhancedAdvisoryEngine()
        
        # Initialize historical database
        historical_store.initialize_database()
        
        logger.info("Enhanced VN Stock Advisory System started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown the system"""
    logger.info("Shutting down Enhanced VN Stock Advisory System...")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with system info"""
    return {
        "service": "VN Stock Advisory - Enhanced AI System", 
        "version": "2.0.0",
        "features": [
            "AI-only analysis (no price fetching)",
            "Multiple advisory modes",
            "Scenario analysis",
            "Historical tracking",
            "User configuration management"
        ],
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not advisory_engine:
        raise HTTPException(status_code=503, detail="Advisory engine not initialized")
    
    # Test AI connectivity
    try:
        portfolio = advisory_engine.holdings_provider.get_portfolio_summary()
        ai_status = "healthy" if portfolio['total_positions'] > 0 else "no_positions"
    except Exception as e:
        ai_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if ai_status == "healthy" else "degraded",
        "ai_engine_status": ai_status,
        "timestamp": "2025-01-21T10:00:00Z"
    }

@app.get("/portfolio")
async def get_portfolio():
    """Get portfolio summary"""
    if not advisory_engine:
        raise HTTPException(status_code=503, detail="Advisory engine not initialized")
    
    try:
        portfolio = advisory_engine.holdings_provider.get_portfolio_summary()
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load portfolio: {e}")

@app.get("/advisory/daily")
async def get_daily_advisory():
    """Get daily advisory analysis"""
    if not advisory_engine:
        raise HTTPException(status_code=503, detail="Advisory engine not initialized")
    
    try:
        advisory = advisory_engine.generate_daily_advisory(save_to_history=False)
        
        if "error" in advisory:
            raise HTTPException(status_code=500, detail=advisory["error"])
        
        return advisory
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advisory generation failed: {e}")

@app.post("/advisory/daily")
async def generate_daily_advisory(background_tasks: BackgroundTasks, save_history: bool = True):
    """Generate and save daily advisory analysis"""
    if not advisory_engine:
        raise HTTPException(status_code=503, detail="Advisory engine not initialized")
    
    def _generate_advisory():
        try:
            advisory = advisory_engine.generate_daily_advisory(save_to_history=save_history)
            logger.info("Daily advisory generated via API")
            return advisory
        except Exception as e:
            logger.error(f"Background advisory generation failed: {e}")
    
    background_tasks.add_task(_generate_advisory)
    return {"status": "started", "message": "Daily advisory generation started in background"}

@app.post("/scenario/analyze")
async def analyze_scenario(scenario: dict):
    """Analyze a what-if scenario"""
    if not advisory_engine:
        raise HTTPException(status_code=503, detail="Advisory engine not initialized")
    
    scenario_description = scenario.get("description")
    if not scenario_description:
        raise HTTPException(status_code=400, detail="Scenario description required")
    
    try:
        result = advisory_engine.analyze_scenario(scenario_description)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario analysis failed: {e}")

@app.get("/position/{ticker}")
async def get_position_analysis(ticker: str):
    """Get detailed analysis for a specific position"""
    if not advisory_engine:
        raise HTTPException(status_code=503, detail="Advisory engine not initialized")
    
    try:
        analysis = advisory_engine.get_position_analysis(ticker.upper())
        
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Position analysis failed: {e}")

@app.get("/history/evolution")
async def get_portfolio_evolution(days: int = 30):
    """Get portfolio evolution over time"""
    if not advisory_engine:
        raise HTTPException(status_code=503, detail="Advisory engine not initialized")
    
    try:
        evolution = advisory_engine.get_portfolio_evolution(days)
        
        if "error" in evolution:
            raise HTTPException(status_code=500, detail=evolution["error"])
        
        return evolution
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio evolution failed: {e}")

@app.get("/config/user")
async def get_user_config():
    """Get user configuration"""
    try:
        config = get_user_config()
        return {
            "advisory": config.advisory.__dict__,
            "risk": config.risk.__dict__,
            "email": {
                "enabled": config.email.enabled,
                "recipients": config.email.recipients,
                "schedule": config.email.schedule
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load user config: {e}")

@app.post("/config/advisory_mode")
async def update_advisory_mode(mode_data: dict):
    """Update advisory mode"""
    if not advisory_engine:
        raise HTTPException(status_code=503, detail="Advisory engine not initialized")
    
    new_mode = mode_data.get("mode")
    if not new_mode:
        raise HTTPException(status_code=400, detail="Advisory mode required")
    
    valid_modes = ["long_term", "swing_trader", "dividend_focused", "growth_oriented", "value_investor", "conservative"]
    if new_mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Must be one of: {valid_modes}")
    
    try:
        success = advisory_engine.update_advisory_mode(new_mode)
        if success:
            return {"status": "success", "new_mode": new_mode}
        else:
            raise HTTPException(status_code=500, detail="Failed to update advisory mode")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mode update failed: {e}")

@app.post("/recommendation/explain")
async def explain_recommendation(data: dict):
    """Get explanation for a recommendation"""
    if not advisory_engine:
        raise HTTPException(status_code=503, detail="Advisory engine not initialized")
    
    recommendation = data.get("recommendation")
    ticker = data.get("ticker")
    
    if not recommendation:
        raise HTTPException(status_code=400, detail="Recommendation text required")
    
    try:
        explanation = advisory_engine.explain_recommendation(recommendation, ticker)
        return {"recommendation": recommendation, "explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {e}")

# CLI Functions

def run_daily_advisory():
    """Run a single advisory analysis manually"""
    logger.info("Running manual advisory analysis")
    
    try:
        engine = EnhancedAdvisoryEngine()
        advisory = engine.generate_daily_advisory(save_to_history=True)
        
        if "error" in advisory:
            logger.error(f"Advisory generation failed: {advisory['error']}")
            sys.exit(1)
        
        logger.info("Manual advisory analysis completed successfully")
        print(f"Advisory generated for {advisory['portfolio_summary']['total_positions']} positions")
        print(f"Total portfolio value: {advisory['portfolio_summary']['total_invested_value']:,.0f} VND")
        
    except Exception as e:
        logger.error(f"Manual analysis failed: {e}")
        sys.exit(1)

def run_scenario_analysis(scenario: str):
    """Run scenario analysis manually"""
    logger.info(f"Running scenario analysis: {scenario}")
    
    try:
        engine = EnhancedAdvisoryEngine()
        result = engine.analyze_scenario(scenario)
        
        if "error" in result:
            logger.error(f"Scenario analysis failed: {result['error']}")
            sys.exit(1)
        
        logger.info("Scenario analysis completed successfully")
        print(f"Scenario: {scenario}")
        print(f"Analysis completed at: {result['analyzed_at']}")
        
    except Exception as e:
        logger.error(f"Scenario analysis failed: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced VN Stock Advisory System")
    parser.add_argument("--mode", choices=["api", "advisory", "scenario"], 
                       default="api", help="Run mode")
    parser.add_argument("--host", default="0.0.0.0", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (dev only)")
    parser.add_argument("--scenario", type=str, help="Scenario description for scenario mode")
    
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
    elif args.mode == "advisory":
        # Run manual advisory
        run_daily_advisory()
    elif args.mode == "scenario":
        # Run scenario analysis
        if not args.scenario:
            print("--scenario is required for scenario mode")
            sys.exit(1)
        run_scenario_analysis(args.scenario)

if __name__ == "__main__":
    main()