"""
Enhanced Advisory Engine - Holdings + AI Only
- No price fetching, pure AI analysis
- Multiple advisory modes
- Scenario analysis
- Risk management
- Historical tracking
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from adapters.holdings_provider import HoldingsOnlyProvider
from advisory.enhanced_ai_advisor import EnhancedAIAdvisor, AdvisoryMode
from config.user_config import get_user_config, UserConfiguration
from data.historical_store import historical_store

logger = logging.getLogger(__name__)

class EnhancedAdvisoryEngine:
    """
    Enhanced advisory engine that focuses on AI analysis without price fetching
    """
    
    def __init__(self, holdings_file: str = "data/holdings.json", email_sender=None, advisory_mode: Optional[AdvisoryMode] = None):
        self.holdings_provider = HoldingsOnlyProvider(holdings_file)
        self.email_sender = email_sender  # Optional email sender
        self.override_advisory_mode = advisory_mode  # Override mode for specific analysis
        
        # Initialize AI advisor (will be configured based on user preferences)
        self.ai_advisor = None
        self.user_config = get_user_config()
        self._initialize_ai_advisor()
    
    def _initialize_ai_advisor(self, mode: Optional[AdvisoryMode] = None):
        """Initialize AI advisor with user configuration"""
        try:
            from config.settings import Settings
            settings = Settings()
            
            # Map user config to advisory mode
            mode_mapping = {
                "long_term": AdvisoryMode.LONG_TERM,
                "swing_trader": AdvisoryMode.SWING_TRADER,
                "dividend_focused": AdvisoryMode.DIVIDEND_FOCUSED,
                "growth_oriented": AdvisoryMode.GROWTH_ORIENTED,
                "value_investor": AdvisoryMode.VALUE_INVESTOR,
                "conservative": AdvisoryMode.CONSERVATIVE,
                "entry_exit_strategy": AdvisoryMode.ENTRY_EXIT_STRATEGY
            }
            
            # Use provided mode first, then override mode, otherwise use user config
            if mode:
                advisory_mode = mode
                logger.info(f"Using provided advisory mode: {advisory_mode.value}")
            elif self.override_advisory_mode:
                advisory_mode = self.override_advisory_mode
                logger.info(f"Using override advisory mode: {advisory_mode.value}")
            else:
                advisory_mode = mode_mapping.get(
                    self.user_config.advisory.primary_mode, 
                    AdvisoryMode.LONG_TERM
                )
                logger.info(f"Using user config advisory mode: {advisory_mode.value}")
            
            self.ai_advisor = EnhancedAIAdvisor(
                api_key=settings.LLM_API_KEY,
                api_url=settings.LLM_PROVIDER,
                mode=advisory_mode
            )
            
            logger.info(f"AI advisor initialized with mode: {advisory_mode.value}")
            
        except Exception as e:
            logger.error(f"Error initializing AI advisor: {e}")
            raise
    
    def generate_daily_advisory(self, save_to_history: bool = True, send_email: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive daily advisory analysis
        """
        try:
            logger.info("Starting daily advisory generation")
            
            # Validate holdings file
            validation = self.holdings_provider.validate_holdings_file()
            if not validation['valid']:
                return {
                    "error": "Invalid holdings file",
                    "validation_errors": validation['errors'],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Load portfolio data
            portfolio_summary = self.holdings_provider.get_portfolio_summary()
            
            if portfolio_summary['total_positions'] == 0:
                return {
                    "error": "No positions found in portfolio",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate main advisory analysis
            advisory_result = self.ai_advisor.generate_portfolio_advisory(
                portfolio_data=portfolio_summary,
                benchmark=self.user_config.advisory.benchmark_comparisons[0] if self.user_config.advisory.benchmark_comparisons else "VN-Index",
                custom_instructions=self.user_config.advisory.custom_instructions
            )
            
            # Use single AI call - disable additional analyses for performance
            additional_analyses = {
                'risk_analysis': {
                    'risk_metrics': {
                        'estimated_portfolio_beta': 1.0,
                        'concentration_risk_score': 5,
                        'single_stock_risk': {
                            'largest_position': 'N/A',
                            'percentage': '0%',
                            'risk_level': 'medium'
                        }
                    },
                    'risk_factors': {
                        'systematic_risks': [
                            {
                                'factor': 'Vietnam Market Risk',
                                'impact': 'medium',
                                'description': 'General market volatility',
                                'mitigation': 'Maintain diversified portfolio'
                            }
                        ],
                        'unsystematic_risks': [
                            {
                                'factor': 'Sector Concentration',
                                'impact': 'medium', 
                                'description': 'Portfolio concentration in specific sectors',
                                'mitigation': 'Monitor sector allocation'
                            }
                        ]
                    }
                },
                'benchmark_comparison': {
                    'benchmark_comparison': {
                        'VN-Index': {
                            'correlation': 'high',
                            'beta': 1.0,
                            'expected_outperformance': 'market-level',
                            'risk_vs_return': 'similar'
                        }
                    }
                }
            }
            
            # Ensure main_advisory has risk_assessment for template compatibility
            if 'risk_assessment' not in advisory_result:
                advisory_result['risk_assessment'] = {
                    'overall_risk': 'medium',
                    'sector_risk': {'Banking': 'medium', 'Technology': 'medium'},
                    'position_sizing_issues': [],
                    'suggested_risk_controls': ['Monitor portfolio regularly', 'Maintain diversification']
                }
            
            # Combine all results
            complete_analysis = {
                "success": True,
                "advisory_date": datetime.now().strftime('%Y-%m-%d'),
                "advisory_mode": self.ai_advisor.mode.value,
                "portfolio_summary": portfolio_summary,
                "main_advisory": advisory_result,
                "additional_analyses": additional_analyses,
                "user_preferences": {
                    "risk_tolerance": self.user_config.risk.risk_tolerance,
                    "max_position_size": self.user_config.risk.max_position_size,
                    "advisory_mode": self.user_config.advisory.primary_mode
                },
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "holdings_count": portfolio_summary['total_positions'],
                    "advisory_mode": self.ai_advisor.mode.value,
                    "email_sent": False,  # Will be updated if email is sent
                    "duration_seconds": 0  # Will be calculated later
                }
            }
            
            # Save to historical database if requested
            if save_to_history:
                self._save_to_history(portfolio_summary, complete_analysis)
            
            # Send email if email sender is configured and user wants emails
            email_sent = False
            if send_email and self.email_sender and self.user_config.email.enabled:
                email_sent = self._send_advisory_email(complete_analysis)
                complete_analysis["summary"]["email_sent"] = email_sent
            
            logger.info("Daily advisory generation completed successfully")
            return complete_analysis
            
        except Exception as e:
            logger.error(f"Error generating daily advisory: {e}")
            return {
                "error": f"Advisory generation failed: {e}",
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_scenario(self, scenario_description: str) -> Dict[str, Any]:
        """
        Analyze a specific what-if scenario
        """
        try:
            portfolio_summary = self.holdings_provider.get_portfolio_summary()
            scenario_result = self.ai_advisor.generate_scenario_analysis(
                portfolio_summary, scenario_description
            )
            
            return {
                "scenario": scenario_description,
                "analysis": scenario_result,
                "portfolio_context": portfolio_summary,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing scenario: {e}")
            return {"error": f"Scenario analysis failed: {e}"}
    
    def get_position_analysis(self, ticker: str) -> Dict[str, Any]:
        """
        Get detailed analysis for a specific position
        """
        try:
            portfolio_summary = self.holdings_provider.get_portfolio_summary()
            
            # Find the position
            position = None
            for pos in portfolio_summary['positions']:
                if pos['ticker'] == ticker:
                    position = pos
                    break
            
            if not position:
                return {"error": f"Position {ticker} not found in portfolio"}
            
            # Get AI analysis for this specific position
            position_context = {
                "ticker": ticker,
                "position_data": position,
                "portfolio_context": portfolio_summary,
                "user_preferences": self.user_config.risk.__dict__
            }
            
            # Create specific prompt for position analysis
            analysis_prompt = f"""
            Analyze this specific position in detail:
            
            Position: {json.dumps(position, indent=2)}
            Portfolio Context: {json.dumps(portfolio_summary, indent=2)}
            
            Provide detailed position analysis in JSON format with:
            - Current position assessment
            - Risk evaluation specific to this holding
            - Recommendation (buy more, hold, reduce, sell)
            - Target allocation percentage
            - Key factors affecting this position
            - Monitoring criteria
            - Action timeline
            """
            
            # This would call the AI advisor with a specific position prompt
            # For now, return basic analysis
            return {
                "ticker": ticker,
                "position": position,
                "analysis": "Detailed AI analysis would go here",
                "recommendation": "hold",  # placeholder
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing position {ticker}: {e}")
            return {"error": f"Position analysis failed: {e}"}
    
    def get_portfolio_evolution(self, days: int = 30) -> Dict[str, Any]:
        """
        Get portfolio evolution over time
        """
        try:
            portfolio_summary = self.holdings_provider.get_portfolio_summary()
            owner = portfolio_summary.get('owner', 'unknown')
            
            # Get historical data
            history = historical_store.get_portfolio_history(owner, days)
            metrics = historical_store.calculate_portfolio_metrics(owner)
            
            return {
                "portfolio_owner": owner,
                "period_days": days,
                "historical_snapshots": len(history),
                "performance_metrics": metrics,
                "evolution_summary": self._summarize_portfolio_evolution(history),
                "current_portfolio": portfolio_summary,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio evolution: {e}")
            return {"error": f"Portfolio evolution analysis failed: {e}"}
    
    def update_advisory_mode(self, new_mode: str) -> bool:
        """
        Update the advisory mode and reinitialize AI advisor
        """
        try:
            # Update user configuration
            self.user_config.advisory.primary_mode = new_mode
            
            # Reinitialize AI advisor
            self._initialize_ai_advisor()
            
            logger.info(f"Advisory mode updated to: {new_mode}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating advisory mode: {e}")
            return False
    
    def explain_recommendation(self, recommendation: str, ticker: str = None) -> str:
        """
        Get detailed explanation for a recommendation
        """
        try:
            portfolio_summary = self.holdings_provider.get_portfolio_summary()
            
            context = {
                "recommendation": recommendation,
                "ticker": ticker,
                "portfolio": portfolio_summary,
                "user_config": {
                    "risk_tolerance": self.user_config.risk.risk_tolerance,
                    "advisory_mode": self.user_config.advisory.primary_mode
                }
            }
            
            explanation = self.ai_advisor.explain_recommendation(recommendation, context)
            return explanation
            
        except Exception as e:
            logger.error(f"Error explaining recommendation: {e}")
            return f"Unable to explain recommendation: {e}"
    
    def _generate_common_scenarios(self, portfolio_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate common scenarios for analysis
        """
        scenarios = []
        positions = portfolio_summary.get('positions', [])
        
        if len(positions) >= 2:
            # Largest position scenarios
            largest_pos = max(positions, key=lambda x: x.get('shares', 0) * x.get('avg_price', 0))
            scenarios.append({
                "description": f"What if I sell 50% of {largest_pos['ticker']}?",
                "type": "position_reduction"
            })
            
            # Diversification scenario
            if len(positions) >= 3:
                scenarios.append({
                    "description": "What if I rebalance to equal weights across all positions?",
                    "type": "rebalancing"
                })
            
            # Sector concentration scenario
            scenarios.append({
                "description": "What if banking sector underperforms by 20%?",
                "type": "sector_stress"
            })
        
        return scenarios
    
    def _save_to_history(self, portfolio_data: Dict[str, Any], analysis: Dict[str, Any]):
        """
        Save analysis to historical database
        """
        try:
            # Save portfolio snapshot
            historical_store.save_portfolio_snapshot(
                portfolio_data=portfolio_data,
                ai_analysis=analysis,
                advisory_mode=self.ai_advisor.mode.value
            )
            
            # Extract and save AI insights
            insights = []
            main_advisory = analysis.get('main_advisory', {})
            
            # Extract action items as insights
            for action in main_advisory.get('action_items', []):
                insights.append({
                    'type': 'action_item',
                    'ticker': action.get('ticker', ''),
                    'recommendation': action.get('action', ''),
                    'rationale': action.get('rationale', ''),
                    'confidence_score': 0.8,  # Default confidence
                    'priority': action.get('priority', 'medium')
                })
            
            # Extract risk warnings as insights
            risk_analysis = analysis.get('additional_analyses', {}).get('risk_analysis', {})
            for warning in risk_analysis.get('risk_management_recommendations', {}).get('immediate_actions', []):
                insights.append({
                    'type': 'risk_warning',
                    'ticker': '',
                    'recommendation': warning,
                    'rationale': 'Risk management recommendation',
                    'confidence_score': 0.9,
                    'priority': 'high'
                })
            
            if insights:
                historical_store.save_ai_insights(insights, portfolio_data.get('owner', 'unknown'))
            
            logger.info("Analysis saved to historical database")
            
        except Exception as e:
            logger.error(f"Error saving to history: {e}")
    
    def _summarize_portfolio_evolution(self, history: List) -> Dict[str, Any]:
        """
        Summarize portfolio evolution from historical data
        """
        if len(history) < 2:
            return {"message": "Insufficient historical data"}
        
        # Sort by date
        history_sorted = sorted(history, key=lambda x: x.date)
        
        first = history_sorted[0]
        last = history_sorted[-1]
        
        return {
            "period_start": first.date,
            "period_end": last.date,
            "initial_value": first.total_invested_value,
            "current_value": last.total_invested_value,
            "value_change": last.total_invested_value - first.total_invested_value,
            "value_change_pct": ((last.total_invested_value - first.total_invested_value) / first.total_invested_value * 100) if first.total_invested_value > 0 else 0,
            "position_changes": {
                "initial_positions": first.total_positions,
                "current_positions": last.total_positions,
                "net_change": last.total_positions - first.total_positions
            }
        }
    
    def _send_advisory_email(self, analysis: Dict[str, Any]) -> bool:
        """
        Send advisory email with analysis results
        """
        try:
            if not self.email_sender:
                logger.warning("No email sender configured")
                return False
            
            if not self.user_config.email.recipients:
                logger.warning("No email recipients configured")
                return False
            
            # Prepare email data
            portfolio_data = analysis.get('portfolio_summary', {})
            main_advisory = analysis.get('main_advisory', {})
            additional_analyses = analysis.get('additional_analyses', {})
            
            # Create consolidated advisory email data for all stocks
            stock_advisories = []
            for position in portfolio_data.get('positions', []):
                # Calculate performance metrics
                current_value = position.get('shares', 0) * position.get('avg_price', 0)
                target_value = position.get('shares', 0) * position.get('target_price', position.get('avg_price', 0))
                pl_pct = 0.0  # No current price, so no P/L calculation
                
                stock_advisory = {
                    'position': {
                        'ticker': position.get('ticker', ''),
                        'exchange': position.get('exchange', ''),
                        'shares': position.get('shares', 0),
                        'avg_price': position.get('avg_price', 0),
                        'target_price': position.get('target_price', position.get('avg_price', 0))
                    },
                    'market_data': {
                        'price': position.get('avg_price', 0),  # Use avg_price as current price
                        'change': 0,
                        'change_pct': 0,
                        'volume': 0
                    },
                    'advisory': {
                        'action': 'hold',  # Default action
                        'reasoning': 'Part of portfolio advisory analysis',
                        'priority': 'medium'
                    },
                    'performance': {
                        'total_value': current_value,
                        'pl_pct': pl_pct,
                        'pl_amount': 0
                    },
                    'generated_at': analysis.get('generated_at')
                }
                stock_advisories.append(stock_advisory)
            
            # Extract portfolio metrics from main advisory and ensure all required fields exist
            portfolio_health = main_advisory.get('portfolio_health', {})
            portfolio_metrics = {
                'total_value': portfolio_data.get('total_invested_value', 0),
                'total_pl_pct': 0.0,  # No current prices, so no P/L
                'total_pl_amount': 0,
                'overall_score': portfolio_health.get('overall_score', 7),
                'health_status': portfolio_health.get('health_status', 'good'),
                'key_strengths': portfolio_health.get('key_strengths', []),
                'key_weaknesses': portfolio_health.get('key_weaknesses', [])
            }
            
            # Send consolidated email using simple AI advisory template
            for recipient in self.user_config.email.recipients:
                logger.info(f"Sending AI advisory email to {recipient}")
                logger.info(f"Main advisory keys: {list(main_advisory.keys())}")
                logger.info(f"Additional analyses keys: {list(additional_analyses.keys())}")
                
                success = self._send_simple_ai_advisory_email(
                    main_advisory=main_advisory,
                    additional_analyses=additional_analyses,
                    portfolio_data=portfolio_data,
                    analysis=analysis,
                    recipient=recipient
                )
                
                if success:
                    logger.info(f"AI advisory email sent successfully to {recipient}")
                else:
                    logger.error(f"Failed to send AI advisory email to {recipient}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending advisory email: {e}")
            return False

    def _send_simple_ai_advisory_email(self, main_advisory: Dict[str, Any], 
                                     additional_analyses: Dict[str, Any], 
                                     portfolio_data: Dict[str, Any], 
                                     analysis: Dict[str, Any],
                                     recipient: str) -> bool:
        """
        Send simple AI advisory email using the new template
        """
        try:
            from jinja2 import Environment, FileSystemLoader
            from pathlib import Path
            from datetime import datetime
            
            # Setup Jinja2 environment
            template_dir = Path(__file__).parent.parent / "email_service" / "templates"
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=True
            )
            
            # Add strftime filter
            def strftime_filter(date_str, format_str='%B %d, %Y at %I:%M %p'):
                try:
                    if isinstance(date_str, str):
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        return dt.strftime(format_str)
                    return str(date_str)
                except:
                    return str(date_str)
            
            env.filters['strftime'] = strftime_filter
            
            # Get template - use specific template for Entry & Exit Strategy mode
            if hasattr(self, 'ai_advisor') and self.ai_advisor and self.ai_advisor.mode == AdvisoryMode.ENTRY_EXIT_STRATEGY:
                template = env.get_template("entry_exit_strategy.html")
                subject = f"🎯 Entry & Exit Strategy Advisory - {len(portfolio_data.get('positions', []))} Holdings - {datetime.now().strftime('%B %d, %Y')}"
            else:
                template = env.get_template("ai_advisory_simple.html")
                subject = f"🤖 AI Portfolio Advisory - {len(portfolio_data.get('positions', []))} Holdings - {datetime.now().strftime('%B %d, %Y')}"
            
            # Prepare template data with safe defaults
            safe_main_advisory = {
                'portfolio_health': {
                    'overall_score': 7,
                    'health_status': 'good',
                    'key_strengths': ['Diversified portfolio'],
                    'key_weaknesses': ['Monitor risk levels']
                },
                'diversification': {
                    'score': 7,
                    'concentration_risk': 'medium',
                    'sector_allocation': {'Other': 100},
                    'recommendations': ['Monitor sector allocation']
                },
                'risk_assessment': {
                    'overall_risk': 'medium',
                    'sector_risk': {'Other': 'medium'},
                    'position_sizing_issues': [],
                    'suggested_risk_controls': ['Regular monitoring']
                },
                'action_items': [],
                'performance_vs_benchmark': {
                    'benchmark': 'VN-Index',
                    'estimated_outperformance': 'market-level',
                    'risk_adjusted_performance': 'similar'
                }
            }
            
            # Update with actual data if available
            if main_advisory:
                safe_main_advisory.update(main_advisory)
            
            template_data = {
                "date": datetime.now().strftime('%B %d, %Y'),
                "portfolio": portfolio_data if portfolio_data else {'total_positions': 0},
                "main_advisory": safe_main_advisory,
                "additional_analyses": additional_analyses,
                "generated_at": analysis.get('generated_at', datetime.now().isoformat())
            }
            
            # Render HTML
            html_content = template.render(**template_data)
            
            # Create subject (already set above)
            
            # Send email using the email sender's base method
            return self.email_sender.send_email(recipient, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending simple AI advisory email: {e}")
            return False

    def generate_dual_advisory_with_emails(self, save_to_history: bool = True, 
                                         email_recipient: str = None) -> Dict[str, Any]:
        """
        Generate both regular advisory and Entry & Exit Strategy analysis, then send both emails
        """
        try:
            logger.info("Starting dual advisory generation (Regular + Entry & Exit Strategy)")
            
            results = {
                "success": False,
                "regular_advisory": {},
                "entry_exit_advisory": {},
                "emails_sent": {
                    "regular": False,
                    "entry_exit": False
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Store original mode
            original_mode = self.ai_advisor.mode if hasattr(self, 'ai_advisor') else None
            
            # 1. Generate Regular Advisory (Long-term by default)
            logger.info("Generating regular advisory analysis...")
            self._initialize_ai_advisor(AdvisoryMode.LONG_TERM)
            regular_advisory = self.generate_daily_advisory(save_to_history=save_to_history)
            results["regular_advisory"] = regular_advisory
            
            # Send regular advisory email
            if email_recipient and regular_advisory.get("success"):
                logger.info(f"📧 STEP 1: Sending regular advisory email to {email_recipient}")
                # Extract the needed data from regular_advisory
                portfolio_data = regular_advisory.get("portfolio_data", {})
                main_advisory = regular_advisory.get("main_advisory", {})
                additional_analyses = regular_advisory.get("additional_analyses", {})
                
                email_sent = self._send_simple_ai_advisory_email(
                    main_advisory=main_advisory,
                    additional_analyses=additional_analyses,
                    portfolio_data=portfolio_data,
                    analysis=regular_advisory,
                    recipient=email_recipient
                )
                results["emails_sent"]["regular"] = email_sent
                logger.info(f"✅ Regular advisory email sent: {email_sent}")
                
                # Wait 3 seconds between emails (tuần tự - sequential)
                if email_sent:
                    logger.info("⏳ Waiting 3 seconds before sending next email...")
                    time.sleep(3)
            
            # 2. Generate Entry & Exit Strategy Advisory
            logger.info("📊 STEP 2: Generating Entry & Exit Strategy analysis...")
            self._initialize_ai_advisor(AdvisoryMode.ENTRY_EXIT_STRATEGY)
            entry_exit_advisory = self.generate_daily_advisory(save_to_history=save_to_history)
            results["entry_exit_advisory"] = entry_exit_advisory
            
            # Send Entry & Exit Strategy email
            if email_recipient and entry_exit_advisory.get("success"):
                logger.info(f"📧 STEP 2: Sending Entry & Exit Strategy email to {email_recipient}")
                # Extract the needed data from entry_exit_advisory
                portfolio_data = entry_exit_advisory.get("portfolio_data", {})
                main_advisory = entry_exit_advisory.get("main_advisory", {})
                additional_analyses = entry_exit_advisory.get("additional_analyses", {})
                
                email_sent = self._send_simple_ai_advisory_email(
                    main_advisory=main_advisory,
                    additional_analyses=additional_analyses,
                    portfolio_data=portfolio_data,
                    analysis=entry_exit_advisory,
                    recipient=email_recipient
                )
                results["emails_sent"]["entry_exit"] = email_sent
                logger.info(f"✅ Entry & Exit Strategy email sent: {email_sent}")
            
            # Restore original mode if it existed
            if original_mode:
                self._initialize_ai_advisor(original_mode)
            
            # Update success status
            results["success"] = (
                regular_advisory.get("success", False) and 
                entry_exit_advisory.get("success", False)
            )
            
            # Summary
            total_holdings = regular_advisory.get("holdings_count", 0)
            emails_sent_count = sum(results["emails_sent"].values())
            
            logger.info(f"Dual advisory completed - Holdings: {total_holdings}, Emails sent: {emails_sent_count}/2")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in dual advisory generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_entry_exit_and_risk_analysis(self, save_to_history: bool = True, 
                                             email_recipient: str = None) -> Dict[str, Any]:
        """
        Generate Entry & Exit Strategy and Risk & Volatility analysis, then send both emails
        """
        try:
            logger.info("Starting Entry & Exit Strategy + Risk & Volatility analysis")
            
            results = {
                "success": False,
                "entry_exit_advisory": {},
                "risk_volatility_advisory": {},
                "emails_sent": {
                    "entry_exit": False,
                    "risk_volatility": False
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Store original mode
            original_mode = self.ai_advisor.mode if hasattr(self, 'ai_advisor') else None
            
            # 1. Generate Entry & Exit Strategy Advisory
            logger.info("📊 STEP 1: Generating Entry & Exit Strategy analysis...")
            self._initialize_ai_advisor(AdvisoryMode.ENTRY_EXIT_STRATEGY)
            entry_exit_advisory = self.generate_daily_advisory(save_to_history=save_to_history, send_email=False)
            results["entry_exit_advisory"] = entry_exit_advisory
            
            # Send Entry & Exit Strategy email
            if email_recipient and entry_exit_advisory.get("success"):
                logger.info(f"📧 STEP 1: Sending Entry & Exit Strategy email to {email_recipient}")
                # Extract the needed data from entry_exit_advisory
                portfolio_data = entry_exit_advisory.get("portfolio_data", {})
                main_advisory = entry_exit_advisory.get("main_advisory", {})
                additional_analyses = entry_exit_advisory.get("additional_analyses", {})
                
                email_sent = self._send_simple_ai_advisory_email(
                    main_advisory=main_advisory,
                    additional_analyses=additional_analyses,
                    portfolio_data=portfolio_data,
                    analysis=entry_exit_advisory,
                    recipient=email_recipient
                )
                results["emails_sent"]["entry_exit"] = email_sent
                logger.info(f"✅ Entry & Exit Strategy email sent: {email_sent}")
                
                # Wait 3 seconds between emails (tuần tự - sequential)
                if email_sent:
                    logger.info("⏳ Waiting 3 seconds before sending next email...")
                    time.sleep(3)
            
            # 2. Generate Risk & Volatility Advisory  
            logger.info("📊 STEP 2: Generating Risk & Volatility analysis...")
            self._initialize_ai_advisor(AdvisoryMode.RISK_VOLATILITY)
            risk_volatility_advisory = self.generate_daily_advisory(save_to_history=save_to_history, send_email=False)
            results["risk_volatility_advisory"] = risk_volatility_advisory
            
            # Send Risk & Volatility email
            if email_recipient and risk_volatility_advisory.get("success"):
                logger.info(f"📧 STEP 2: Sending Risk & Volatility email to {email_recipient}")
                # Extract the needed data from risk_volatility_advisory
                portfolio_data = risk_volatility_advisory.get("portfolio_data", {})
                main_advisory = risk_volatility_advisory.get("main_advisory", {})
                additional_analyses = risk_volatility_advisory.get("additional_analyses", {})
                
                email_sent = self._send_simple_ai_advisory_email(
                    main_advisory=main_advisory,
                    additional_analyses=additional_analyses,
                    portfolio_data=portfolio_data,
                    analysis=risk_volatility_advisory,
                    recipient=email_recipient
                )
                results["emails_sent"]["risk_volatility"] = email_sent
                logger.info(f"✅ Risk & Volatility email sent: {email_sent}")
            
            # Restore original mode if it existed
            if original_mode:
                self._initialize_ai_advisor(original_mode)
            
            # Update success status
            results["success"] = (
                entry_exit_advisory.get("success", False) and 
                risk_volatility_advisory.get("success", False)
            )
            
            # Summary
            total_holdings = entry_exit_advisory.get("holdings_count", 0)
            emails_sent_count = sum(results["emails_sent"].values())
            
            logger.info(f"Entry & Exit + Risk & Volatility analysis completed - Holdings: {total_holdings}, Emails sent: {emails_sent_count}/2")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in Entry & Exit + Risk & Volatility analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
