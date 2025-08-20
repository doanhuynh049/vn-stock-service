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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from adapters.holdings_provider import HoldingsOnlyProvider
from advisory.enhanced_ai_advisor import EnhancedAIAdvisor, AdvisoryMode
from advisory.enhanced_engine import EnhancedAdvisoryEngine
from config.user_config import ConfigManager, get_user_config
from email_service.sender import EmailSender, DryRunEmailSender
from data.historical_store import HistoricalDataStore

def run_advisory_task():
    """Run the Entry & Exit Strategy + Risk & Volatility advisory task"""
    
    # Get environment variables directly from .env
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    mail_from = os.getenv('MAIL_FROM')
    notification_email = os.getenv('MAIL_TO')
    smtp_tls = os.getenv('SMTP_TLS', 'true').lower() == 'true'
    dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
    
    # Initialize email sender - always use real sender for actual email delivery
    if dry_run or not smtp_host:
        email_sender = DryRunEmailSender()
        print("[INFO] Using DryRunEmailSender (no actual emails will be sent)")
    else:
        email_sender = EmailSender(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
            smtp_tls=smtp_tls
        )
        print(f"[INFO] Using real EmailSender - will send emails to {notification_email}")
    
    # Initialize enhanced advisory engine with email sender
    engine = EnhancedAdvisoryEngine(email_sender=email_sender)
    
    # Use notification email from .env
    recipient_email = notification_email
        
    print("🚀 Running Entry & Exit Strategy + Risk & Volatility Advisory...")
    print(f"📧 Email recipient: {recipient_email}")
        
    # Generate Entry & Exit Strategy + Risk & Volatility analysis and send emails
    result = engine.generate_entry_exit_and_risk_analysis(
        save_to_history=True,
        email_recipient=recipient_email
    )
        
    if result.get("success"):
        print(f"✅ Analysis completed successfully!")
            
        # Entry & Exit results
        entry_exit = result.get("entry_exit_advisory", {})
        if entry_exit.get("success"):
            print(f"📊 Entry & Exit Strategy - Holdings: {entry_exit.get('holdings_count', 0)}")
            
        # Risk & Volatility results  
        risk_volatility = result.get("risk_volatility_advisory", {})
        if risk_volatility.get("success"):
            print(f"📊 Risk & Volatility - Holdings: {risk_volatility.get('holdings_count', 0)}")
            
        # Email status
        emails_sent = result.get("emails_sent", {})
        print(f"📧 Entry & Exit Strategy email sent: {emails_sent.get('entry_exit', False)}")
        print(f"� Risk & Volatility email sent: {emails_sent.get('risk_volatility', False)}")
            
    else:
        print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        

if __name__ == "__main__":
    run_advisory_task()
