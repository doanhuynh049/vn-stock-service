"""
Enhanced AI Advisor with Multiple Strategies and Modes
- Supports different advisory modes (long-term, swing trading, dividend-focused)
- Portfolio scenario analysis
- Benchmark comparison
- Risk metrics and explanations
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from enum import Enum
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.api_logger import APILogger

logger = logging.getLogger(__name__)

class AdvisoryMode(Enum):
    LONG_TERM = "long_term"
    SWING_TRADER = "swing_trader"
    DIVIDEND_FOCUSED = "dividend_focused"
    GROWTH_ORIENTED = "growth_oriented"
    VALUE_INVESTOR = "value_investor"
    CONSERVATIVE = "conservative"
    ENTRY_EXIT_STRATEGY = "entry_exit_strategy"
    RISK_VOLATILITY = "risk_volatility"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EnhancedAIAdvisor:
    """
    Enhanced AI Advisor with customizable strategies and comprehensive analysis
    """
    
    def __init__(self, api_key: str, api_url: str, mode: AdvisoryMode = AdvisoryMode.LONG_TERM):
        self.api_key = api_key
        self.api_url = api_url
        self.mode = mode
        self.api_logger = APILogger()
        
        # Strategy-specific configurations
        self.strategy_configs = {
            AdvisoryMode.LONG_TERM: {
                "time_horizon": "3-5 years",
                "focus": "fundamental analysis, company growth, market position",
                "risk_tolerance": "medium to high",
                "rebalancing_frequency": "quarterly",
                "key_metrics": ["P/E ratio", "ROE", "debt-to-equity", "revenue growth"]
            },
            AdvisoryMode.SWING_TRADER: {
                "time_horizon": "1-6 months",
                "focus": "technical analysis, momentum, market cycles",
                "risk_tolerance": "medium to high",
                "rebalancing_frequency": "monthly",
                "key_metrics": ["RSI", "moving averages", "volume patterns", "support/resistance"]
            },
            AdvisoryMode.DIVIDEND_FOCUSED: {
                "time_horizon": "5+ years",
                "focus": "dividend yield, payout stability, dividend growth",
                "risk_tolerance": "low to medium",
                "rebalancing_frequency": "semi-annually",
                "key_metrics": ["dividend yield", "payout ratio", "dividend growth rate", "free cash flow"]
            },
            AdvisoryMode.GROWTH_ORIENTED: {
                "time_horizon": "2-5 years",
                "focus": "revenue growth, market expansion, innovation",
                "risk_tolerance": "high",
                "rebalancing_frequency": "quarterly",
                "key_metrics": ["revenue growth", "market share", "R&D spending", "profit margins"]
            },
            AdvisoryMode.VALUE_INVESTOR: {
                "time_horizon": "3-7 years",
                "focus": "undervalued stocks, book value, intrinsic value",
                "risk_tolerance": "medium",
                "rebalancing_frequency": "semi-annually",
                "key_metrics": ["P/B ratio", "P/E ratio", "debt levels", "asset quality"]
            },
            AdvisoryMode.CONSERVATIVE: {
                "time_horizon": "5+ years",
                "focus": "capital preservation, stable returns, low volatility",
                "risk_tolerance": "low",
                "rebalancing_frequency": "annually",
                "key_metrics": ["beta", "volatility", "debt-to-equity", "dividend coverage"]
            },
            AdvisoryMode.ENTRY_EXIT_STRATEGY: {
                "time_horizon": "3 months to 2 years",
                "focus": "optimal entry points, exit strategies, support/resistance levels",
                "risk_tolerance": "medium to high",
                "rebalancing_frequency": "monthly",
                "key_metrics": ["entry price range", "target prices", "support levels", "resistance levels"]
            },
            AdvisoryMode.RISK_VOLATILITY: {
                "time_horizon": "ongoing",
                "focus": "risk assessment, volatility analysis, position sizing, hedging strategies",
                "risk_tolerance": "variable",
                "rebalancing_frequency": "as needed",
                "key_metrics": ["risk levels", "volatility measures", "correlation analysis", "position sizing"]
            }
        }
    
    def set_advisory_mode(self, mode: AdvisoryMode):
        """Change the advisory mode"""
        self.mode = mode
        logger.info(f"Advisory mode changed to: {mode.value}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_portfolio_advisory(self, portfolio_data: Dict[str, Any], 
                                  benchmark: str = "VN-Index",
                                  custom_instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive portfolio advisory with selected strategy
        """
        try:
            strategy_config = self.strategy_configs[self.mode]
            
            prompt = self._create_portfolio_prompt(
                portfolio_data, benchmark, strategy_config, custom_instructions
            )
            
            response = self._call_ai_model(prompt, timeout=60)
            return self._process_portfolio_response(response, portfolio_data)
            
        except Exception as e:
            logger.error(f"Error generating portfolio advisory: {e}")
            return self._fallback_portfolio_advisory(portfolio_data)
    
    def generate_scenario_analysis(self, portfolio_data: Dict[str, Any], 
                                 scenario: str) -> Dict[str, Any]:
        """
        Generate what-if scenario analysis
        Example: "What if I sell 50% of FPT and buy VHM?"
        """
        try:
            prompt = self._create_scenario_prompt(portfolio_data, scenario)
            response = self._call_ai_model(prompt, timeout=45)
            return self._process_scenario_response(response)
            
        except Exception as e:
            logger.error(f"Error generating scenario analysis: {e}")
            return {"error": f"Scenario analysis failed: {e}"}
    
    def generate_benchmark_comparison(self, portfolio_data: Dict[str, Any],
                                    benchmarks: List[str] = ["VN-Index", "VN30"]) -> Dict[str, Any]:
        """
        Compare portfolio performance against benchmarks
        """
        try:
            prompt = self._create_benchmark_prompt(portfolio_data, benchmarks)
            response = self._call_ai_model(prompt, timeout=40)
            return self._process_benchmark_response(response)
            
        except Exception as e:
            logger.error(f"Error generating benchmark comparison: {e}")
            return {"error": f"Benchmark comparison failed: {e}"}
    
    def generate_risk_analysis(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed risk analysis with professional metrics
        """
        try:
            prompt = self._create_risk_analysis_prompt(portfolio_data)
            response = self._call_ai_model(prompt, timeout=50)
            return self._process_risk_response(response)
            
        except Exception as e:
            logger.error(f"Error generating risk analysis: {e}")
            return {"error": f"Risk analysis failed: {e}"}
    
    def explain_recommendation(self, recommendation: str, context: Dict[str, Any]) -> str:
        """
        Get detailed explanation for a specific recommendation
        """
        try:
            prompt = f"""
            You are a Vietnamese investment advisor. Explain in detail why you made this recommendation:
            
            Recommendation: {recommendation}
            Context: {json.dumps(context, indent=2)}
            
            Please provide a clear, educational explanation that:
            1. Explains the reasoning behind the recommendation
            2. Identifies the key factors that led to this decision
            3. Discusses potential risks and benefits
            4. Suggests monitoring criteria
            5. Provides educational insights for the investor
            
            Make the explanation accessible but professional.
            """
            
            response = self._call_ai_model(prompt, timeout=30)
            
            if response and 'candidates' in response and response['candidates']:
                return response['candidates'][0]['content']['parts'][0]['text']
            
            return "Unable to generate explanation at this time."
            
        except Exception as e:
            logger.error(f"Error explaining recommendation: {e}")
            return f"Error generating explanation: {e}"
    
    def _create_portfolio_prompt(self, portfolio_data: Dict[str, Any], 
                               benchmark: str, strategy_config: Dict[str, Any],
                               custom_instructions: Optional[str]) -> str:
        """Create comprehensive portfolio analysis prompt"""
        
        # Special handling for Entry & Exit Strategy mode
        if self.mode == AdvisoryMode.ENTRY_EXIT_STRATEGY:
            return self._create_entry_exit_prompt(portfolio_data, strategy_config, custom_instructions)
        
        # Special handling for Risk & Volatility mode
        if self.mode == AdvisoryMode.RISK_VOLATILITY:
            return self._create_risk_volatility_prompt(portfolio_data, strategy_config, custom_instructions)
        
        mode_description = f"""
        Advisory Mode: {self.mode.value.replace('_', ' ').title()}
        Time Horizon: {strategy_config['time_horizon']}
        Focus Areas: {strategy_config['focus']}
        Risk Tolerance: {strategy_config['risk_tolerance']}
        Key Metrics: {', '.join(strategy_config['key_metrics'])}
        """
        
        custom_section = f"\nAdditional Instructions: {custom_instructions}" if custom_instructions else ""
        
        prompt = f"""
        You are an expert Vietnamese stock market advisor specializing in {self.mode.value.replace('_', ' ')} investing.
        
        {mode_description}
        
        Portfolio Data:
        {json.dumps(portfolio_data, indent=2)}
        
        Please provide comprehensive analysis in the following JSON format:
        {{
            "portfolio_health": {{
                "overall_score": <1-10>,
                "health_status": "<excellent/good/fair/poor>",
                "key_strengths": ["strength1", "strength2"],
                "key_weaknesses": ["weakness1", "weakness2"]
            }},
            "diversification": {{
                "score": <1-10>,
                "sector_allocation": {{"Banking": 40, "Technology": 30, "Other": 30}},
                "concentration_risk": "<low/medium/high>",
                "recommendations": ["diversification_rec1", "diversification_rec2"]
            }},
            "risk_assessment": {{
                "overall_risk": "<low/medium/high>",
                "sector_risk": {{"Banking": "medium", "Technology": "high"}},
                "position_sizing_issues": ["issue1", "issue2"],
                "suggested_risk_controls": ["control1", "control2"]
            }},
            "performance_vs_benchmark": {{
                "benchmark": "{benchmark}",
                "estimated_outperformance": "<percentage>",
                "risk_adjusted_performance": "<assessment>",
                "correlation_analysis": "<analysis>"
            }},
            "action_items": [
                {{
                    "action": "<buy/sell/hold/rebalance>",
                    "ticker": "<ticker_or_sector>",
                    "priority": "<high/medium/low>",
                    "rationale": "<detailed_explanation>",
                    "target_allocation": "<percentage>",
                    "timeline": "<timeframe>"
                }}
            ],
            "market_outlook": {{
                "vietnam_market_view": "<bullish/neutral/bearish>",
                "sector_outlook": {{"Banking": "positive", "Technology": "neutral"}},
                "macroeconomic_factors": ["factor1", "factor2"],
                "opportunities": ["opportunity1", "opportunity2"],
                "threats": ["threat1", "threat2"]
            }},
            "monitoring_schedule": {{
                "daily_checks": ["metric1", "metric2"],
                "weekly_reviews": ["review1", "review2"],
                "monthly_assessments": ["assessment1", "assessment2"],
                "rebalancing_triggers": ["trigger1", "trigger2"]
            }},
            "educational_insights": {{
                "key_lessons": ["lesson1", "lesson2"],
                "market_concepts": ["concept1", "concept2"],
                "improvement_suggestions": ["suggestion1", "suggestion2"]
            }}
        }}
        
        Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
        Market: Vietnamese Stock Market (HOSE, HNX, UPCoM)
        Currency: VND
        {custom_section}
        
        Please provide realistic, actionable advice based on current Vietnamese market conditions and the specified investment strategy.
        """
        
        return prompt
    
    def _create_entry_exit_prompt(self, portfolio_data: Dict[str, Any], 
                                 strategy_config: Dict[str, Any],
                                 custom_instructions: Optional[str]) -> str:
        """Create Entry & Exit Strategy specific prompt"""
        
        mode_description = f"""
        Advisory Mode: Entry & Exit Strategy Analysis
        Time Horizon: {strategy_config['time_horizon']}
        Focus Areas: {strategy_config['focus']}
        Key Metrics: {', '.join(strategy_config['key_metrics'])}
        """
        
        custom_section = f"\nAdditional Instructions: {custom_instructions}" if custom_instructions else ""
        
        prompt = f"""
        You are an expert Vietnamese stock market advisor specializing in Entry & Exit Strategy analysis.
        
        {mode_description}
        
        Portfolio Holdings:
        {json.dumps(portfolio_data, indent=2)}
        
        SPECIFIC TASK: For each of my holdings, provide:
        1. An optimal entry price range (if I were to buy more)
        2. A clear exit strategy, including short-term (3-month) and long-term (1–2 years) target prices
        3. Key support and resistance levels to watch
        4. A brief explanation of the reasoning behind these recommendations, considering both technical and fundamental factors
        
        IMPORTANT OUTPUT REQUIREMENTS:
        - Provide COMPLETE and VALID JSON format only
        - All prices must be in VND (Vietnamese Dong)
        - Ensure all JSON brackets and commas are properly closed
        - Do not include any text outside the JSON structure
        - Each stock MUST have entry_exit_analysis with all required fields
        
        Please provide analysis in the following EXACT JSON format:
        {{
            "portfolio_health": {{
                "overall_score": <1-10>,
                "health_status": "<excellent/good/fair/poor>",
                "key_strengths": ["strength1", "strength2"],
                "key_weaknesses": ["weakness1", "weakness2"]
            }},
            "diversification": {{
                "score": <1-10>,
                "sector_allocation": {{"Banking": 40, "Technology": 30, "Other": 30}},
                "concentration_risk": "<low/medium/high>",
                "recommendations": ["diversification_rec1", "diversification_rec2"]
            }},
            "risk_assessment": {{
                "overall_risk": "<low/medium/high>",
                "sector_risk": {{"Banking": "medium", "Technology": "high"}},
                "position_sizing_issues": ["issue1", "issue2"],
                "suggested_risk_controls": ["control1", "control2"]
            }},
            "performance_vs_benchmark": {{
                "benchmark": "VN-Index",
                "estimated_performance": "<assessment>",
                "strategy_effectiveness": "<evaluation>"
            }},
            "entry_exit_analysis": [
                {{
                    "ticker": "<stock_symbol>",
                    "current_position": "<number_of_shares>",
                    "optimal_entry_range": {{
                        "min_price": <price_in_vnd>,
                        "max_price": <price_in_vnd>,
                        "rationale": "<explanation>"
                    }},
                    "exit_strategy": {{
                        "short_term_target": {{
                            "price": <price_in_vnd>,
                            "timeframe": "3 months",
                            "probability": "<high/medium/low>",
                            "rationale": "<explanation>"
                        }},
                        "long_term_target": {{
                            "price": <price_in_vnd>,
                            "timeframe": "1-2 years",
                            "probability": "<high/medium/low>",
                            "rationale": "<explanation>"
                        }}
                    }},
                    "technical_levels": {{
                        "support_levels": [<price1>, <price2>, <price3>],
                        "resistance_levels": [<price1>, <price2>, <price3>],
                        "key_moving_averages": {{
                            "ma_20": <price>,
                            "ma_50": <price>,
                            "ma_200": <price>
                        }}
                    }},
                    "fundamental_analysis": {{
                        "pe_ratio": <ratio>,
                        "pb_ratio": <ratio>,
                        "growth_prospects": "<assessment>",
                        "financial_health": "<strong/moderate/weak>"
                    }},
                    "risk_factors": ["risk1", "risk2", "risk3"],
                    "catalysts": ["catalyst1", "catalyst2"],
                    "recommendation": {{
                        "action": "<buy_more/hold/partial_sell/full_sell>",
                        "reasoning": "<detailed_explanation>",
                        "stop_loss": <price_in_vnd>,
                        "take_profit": <price_in_vnd>
                    }}
                }}
            ],
            "action_items": [
                {{
                    "action": "<specific_action>",
                    "ticker": "<ticker>",
                    "priority": "<high/medium/low>",
                    "rationale": "<detailed_explanation>",
                    "timeline": "<timeframe>"
                }}
            ],
            "market_outlook": {{
                "vietnam_market_view": "<bullish/neutral/bearish>",
                "sector_outlook": {{"Banking": "positive", "Technology": "neutral"}},
                "trading_environment": "<favorable/challenging>",
                "key_market_drivers": ["driver1", "driver2"]
            }},
            "monitoring_schedule": {{
                "daily_checks": ["price_levels", "volume_patterns"],
                "weekly_reviews": ["technical_indicators", "news_flow"],
                "trigger_events": ["earnings", "market_events"],
                "rebalancing_signals": ["signal1", "signal2"]
            }},
            "educational_insights": {{
                "trading_concepts": ["concept1", "concept2"],
                "risk_management_tips": ["tip1", "tip2"],
                "market_timing_guidance": ["guidance1", "guidance2"]
            }}
        }}
        
        Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
        Market: Vietnamese Stock Market (HOSE, HNX, UPCoM)
        Currency: VND
        {custom_section}
        
        Focus on providing specific, actionable entry and exit points with clear reasoning based on both technical analysis and fundamental factors. Consider current Vietnamese market conditions, economic outlook, and sector-specific trends.
        """
        
        return prompt

    def _create_risk_volatility_prompt(self, portfolio_data: Dict[str, Any], 
                                     strategy_config: Dict[str, Any],
                                     custom_instructions: Optional[str]) -> str:
        """Create Risk & Volatility specific prompt"""
        
        mode_description = f"""
        Advisory Mode: Risk & Volatility Analysis
        Time Horizon: {strategy_config['time_horizon']}
        Focus Areas: {strategy_config['focus']}
        Key Metrics: {', '.join(strategy_config['key_metrics'])}
        """
        
        custom_section = f"\nAdditional Instructions: {custom_instructions}" if custom_instructions else ""
        
        prompt = f"""
        You are an expert Vietnamese risk management and volatility specialist.
        
        {mode_description}
        
        Portfolio Holdings:
        {json.dumps(portfolio_data, indent=2)}
        
        SPECIFIC TASK: Evaluate the risk and volatility profile of my portfolio holdings. For each asset, identify whether it is high-risk, medium-risk, or relatively stable. Suggest how I should adjust position sizes to balance risk and manage potential downside. Include recommendations on diversification, correlation between assets, and possible hedging strategies.
        
        IMPORTANT OUTPUT REQUIREMENTS:
        - Provide COMPLETE and VALID JSON format only
        - Classify each holding's risk level (high/medium/low)
        - Include specific position sizing recommendations
        - Provide correlation analysis between holdings
        - Suggest concrete hedging strategies for Vietnamese market
        - Do not include any text outside the JSON structure
        
        Please provide analysis in the following JSON format:
        {{
            "portfolio_health": {{
                "overall_score": <1-10>,
                "health_status": "<excellent/good/fair/poor>",
                "key_strengths": ["strength1", "strength2"],
                "key_weaknesses": ["weakness1", "weakness2"]
            }},
            "diversification": {{
                "score": <1-10>,
                "sector_allocation": {{"Banking": 40, "Technology": 30, "Other": 30}},
                "concentration_risk": "<low/medium/high>",
                "recommendations": ["diversification_rec1", "diversification_rec2"]
            }},
            "risk_assessment": {{
                "overall_risk": "<low/medium/high>",
                "portfolio_volatility": "<low/medium/high>",
                "beta_estimate": <number>,
                "var_estimate": "<percentage>",
                "max_drawdown_potential": "<percentage>"
            }},
            "individual_risk_analysis": [
                {{
                    "ticker": "<stock_symbol>",
                    "current_position": "<number_of_shares>",
                    "current_weight": "<percentage_of_portfolio>",
                    "risk_classification": "<high/medium/low>",
                    "volatility_level": "<high/medium/low>",
                    "beta_estimate": <number>,
                    "risk_factors": ["factor1", "factor2"],
                    "position_sizing": {{
                        "current_allocation": "<percentage>",
                        "recommended_allocation": "<percentage>",
                        "adjustment_needed": "<increase/decrease/maintain>",
                        "rationale": "<explanation>"
                    }},
                    "correlation_notes": "<how_it_correlates_with_other_holdings>"
                }}
            ],
            "correlation_analysis": {{
                "high_correlation_pairs": [
                    {{"assets": ["ticker1", "ticker2"], "correlation": <0.0-1.0>, "risk_impact": "<explanation>"}}
                ],
                "diversification_effectiveness": "<poor/fair/good/excellent>",
                "concentration_risks": ["risk1", "risk2"]
            }},
            "hedging_strategies": [
                {{
                    "strategy": "<strategy_name>",
                    "purpose": "<what_risk_it_addresses>",
                    "implementation": "<how_to_implement>",
                    "cost_estimate": "<relative_cost>",
                    "effectiveness": "<low/medium/high>",
                    "vietnamese_market_applicability": "<explanation>"
                }}
            ],
            "position_sizing_recommendations": {{
                "rebalancing_needed": <true/false>,
                "suggested_changes": [
                    {{"ticker": "<symbol>", "action": "<increase/decrease/maintain>", "target_weight": "<percentage>", "rationale": "<explanation>"}}
                ],
                "risk_budget_allocation": {{"conservative": "<percentage>", "moderate": "<percentage>", "aggressive": "<percentage>"}},
                "cash_reserve_recommendation": "<percentage>"
            }},
            "action_items": [
                {{
                    "action": "<specific_action>",
                    "ticker": "<ticker_or_ALL>",
                    "priority": "<high/medium/low>",
                    "rationale": "<detailed_explanation>",
                    "timeline": "<timeframe>",
                    "risk_impact": "<how_it_affects_portfolio_risk>"
                }}
            ],
            "market_outlook": {{
                "vietnam_market_risk": "<low/medium/high>",
                "sector_risk_outlook": {{"Banking": "medium", "Technology": "high"}},
                "macro_risk_factors": ["factor1", "factor2"],
                "risk_monitoring_priorities": ["priority1", "priority2"]
            }},
            "monitoring_schedule": {{
                "daily_risk_checks": ["metric1", "metric2"],
                "weekly_volatility_review": ["review1", "review2"],
                "monthly_correlation_analysis": ["analysis1", "analysis2"],
                "stress_test_frequency": "<monthly/quarterly>"
            }},
            "educational_insights": {{
                "risk_management_concepts": ["concept1", "concept2"],
                "volatility_insights": ["insight1", "insight2"],
                "hedging_education": ["education1", "education2"]
            }}
        }}
        
        Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
        Market: Vietnamese Stock Market (HOSE, HNX, UPCoM)
        Currency: VND
        {custom_section}
        
        Focus on providing specific, actionable risk management recommendations based on Vietnamese market conditions, available hedging instruments, and realistic position sizing strategies for retail investors.
        """
        
        return prompt

    def _create_scenario_prompt(self, portfolio_data: Dict[str, Any], scenario: str) -> str:
        """Create scenario analysis prompt"""
        
        prompt = f"""
        You are a Vietnamese portfolio analyst. Analyze this what-if scenario:
        
        Current Portfolio:
        {json.dumps(portfolio_data, indent=2)}
        
        Scenario: {scenario}
        
        Please provide scenario analysis in JSON format:
        {{
            "scenario_description": "{scenario}",
            "impact_analysis": {{
                "portfolio_value_change": "<percentage>",
                "risk_profile_change": "<description>",
                "diversification_impact": "<improvement/neutral/deterioration>",
                "sector_allocation_change": {{"Banking": "+5%", "Technology": "-10%"}}
            }},
            "projected_outcomes": {{
                "best_case": {{
                    "return_potential": "<percentage>",
                    "timeline": "<timeframe>",
                    "key_drivers": ["driver1", "driver2"]
                }},
                "base_case": {{
                    "return_potential": "<percentage>",
                    "timeline": "<timeframe>",
                    "probability": "<percentage>"
                }},
                "worst_case": {{
                    "potential_loss": "<percentage>",
                    "risk_factors": ["risk1", "risk2"]
                }}
            }},
            "recommendation": {{
                "should_execute": <true/false>,
                "confidence_level": "<high/medium/low>",
                "rationale": "<detailed_explanation>",
                "alternative_approaches": ["alternative1", "alternative2"],
                "implementation_steps": ["step1", "step2"],
                "monitoring_criteria": ["criterion1", "criterion2"]
            }},
            "risk_considerations": ["risk1", "risk2", "risk3"],
            "market_timing": {{
                "current_timing": "<excellent/good/fair/poor>",
                "optimal_timing": "<description>",
                "market_conditions_needed": ["condition1", "condition2"]
            }}
        }}
        
        Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
        """
        
        return prompt
    
    def _create_benchmark_prompt(self, portfolio_data: Dict[str, Any], benchmarks: List[str]) -> str:
        """Create benchmark comparison prompt"""
        
        prompt = f"""
        You are a Vietnamese market analyst. Compare this portfolio against major benchmarks.
        
        Portfolio:
        {json.dumps(portfolio_data, indent=2)}
        
        Benchmarks to compare: {', '.join(benchmarks)}
        
        Provide comparison in JSON format:
        {{
            "benchmark_comparison": {{
                "VN-Index": {{
                    "correlation": "<high/medium/low>",
                    "beta": <estimated_beta>,
                    "expected_outperformance": "<percentage>",
                    "risk_vs_return": "<better/similar/worse>"
                }},
                "VN30": {{
                    "correlation": "<high/medium/low>",
                    "beta": <estimated_beta>,
                    "expected_outperformance": "<percentage>",
                    "risk_vs_return": "<better/similar/worse>"
                }}
            }},
            "sector_vs_market": {{
                "Banking": {{
                    "portfolio_weight": "<percentage>",
                    "market_weight": "<percentage>",
                    "over_under_weight": "<overweight/underweight>",
                    "justification": "<explanation>"
                }},
                "Technology": {{
                    "portfolio_weight": "<percentage>",
                    "market_weight": "<percentage>",
                    "over_under_weight": "<overweight/underweight>",
                    "justification": "<explanation>"
                }}
            }},
            "performance_attribution": {{
                "sector_allocation_effect": "<positive/negative/neutral>",
                "stock_selection_effect": "<positive/negative/neutral>",
                "interaction_effect": "<description>",
                "total_active_return": "<estimated_percentage>"
            }},
            "recommendations": {{
                "maintain_overweights": ["sector1", "sector2"],
                "reduce_overweights": ["sector1", "sector2"],
                "add_exposure": ["sector1", "sector2"],
                "rationale": "<detailed_explanation>"
            }}
        }}
        
        Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
        """
        
        return prompt
    
    def _create_risk_analysis_prompt(self, portfolio_data: Dict[str, Any]) -> str:
        """Create comprehensive risk analysis prompt"""
        
        prompt = f"""
        You are a Vietnamese risk management specialist. Provide detailed risk analysis.
        
        Portfolio:
        {json.dumps(portfolio_data, indent=2)}
        
        Provide comprehensive risk analysis in JSON format:
        {{
            "risk_metrics": {{
                "estimated_portfolio_beta": <value>,
                "concentration_risk_score": <1-10>,
                "sector_concentration": {{"Banking": 40, "Technology": 30}},
                "single_stock_risk": {{
                    "largest_position": "<ticker>",
                    "percentage": "<percentage>",
                    "risk_level": "<high/medium/low>"
                }}
            }},
            "risk_factors": {{
                "systematic_risks": [
                    {{
                        "factor": "Vietnam Market Risk",
                        "impact": "<high/medium/low>",
                        "description": "<explanation>",
                        "mitigation": "<strategy>"
                    }}
                ],
                "unsystematic_risks": [
                    {{
                        "factor": "Sector Concentration",
                        "impact": "<high/medium/low>",
                        "description": "<explanation>",
                        "mitigation": "<strategy>"
                    }}
                ]
            }},
            "scenario_stress_tests": {{
                "market_crash_20pct": {{
                    "estimated_portfolio_loss": "<percentage>",
                    "recovery_timeline": "<timeframe>",
                    "worst_performers": ["ticker1", "ticker2"]
                }},
                "sector_rotation": {{
                    "impact_if_banking_underperforms": "<percentage>",
                    "impact_if_tech_underperforms": "<percentage>"
                }},
                "currency_devaluation": {{
                    "vnd_weakness_impact": "<percentage>",
                    "hedging_recommendations": ["strategy1", "strategy2"]
                }}
            }},
            "risk_management_recommendations": {{
                "immediate_actions": ["action1", "action2"],
                "medium_term_adjustments": ["adjustment1", "adjustment2"],
                "hedging_strategies": ["strategy1", "strategy2"],
                "stop_loss_suggestions": {{
                    "ticker1": "<percentage>",
                    "ticker2": "<percentage>"
                }}
            }},
            "risk_monitoring": {{
                "daily_metrics": ["metric1", "metric2"],
                "weekly_reviews": ["review1", "review2"],
                "alert_triggers": [
                    {{
                        "condition": "<description>",
                        "action": "<recommended_action>"
                    }}
                ]
            }}
        }}
        
        Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
        """
        
        return prompt
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_ai_model(self, prompt: str, timeout: int = 30) -> Dict[str, Any]:
        """Call the AI model with retry logic"""
        start_time = time.time()
        request_id = self.api_logger.log_ai_request(
            provider="Gemini",
            model="gemini-2.0-flash",
            prompt=prompt
        )
        
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 4096
                }
            }
            
            url = f"{self.api_url}?key={self.api_key}"
            logger.debug(f"Making API request to: {url[:100]}...")
            logger.debug(f"Payload keys: {list(payload.keys())}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            duration_ms = (time.time() - start_time) * 1000
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            data = response.json()
            
            logger.debug(f"Response data keys: {list(data.keys()) if data else 'None'}")
            
            # Log successful response
            self.api_logger.log_ai_response(
                request_id=request_id,
                provider="Gemini",
                response_text=data['candidates'][0]['content']['parts'][0]['text'] if data.get('candidates') else "No response",
                duration_ms=duration_ms
            )
            
            return data
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"API call failed with {type(e).__name__}: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text[:500]}")
            
            self.api_logger.log_ai_response(
                request_id=request_id,
                provider="Gemini",
                response_text="",
                duration_ms=duration_ms,
                error=str(e)
            )
            raise
    
    def _process_portfolio_response(self, response: Dict[str, Any], portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI response for portfolio analysis"""
        try:
            if 'candidates' in response and response['candidates']:
                ai_response = response['candidates'][0]['content']['parts'][0]['text']
                
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    json_text = json_match.group()
                    
                    # Clean up common JSON issues more aggressively
                    # Remove trailing commas before closing brackets
                    json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
                    
                    # Fix incomplete strings at the end (like `"beta_estimate"` without value)
                    json_text = re.sub(r'"[^"]*"\s*$', '""', json_text)
                    
                    # Fix incomplete key-value pairs (like `"key":` without value)
                    json_text = re.sub(r':\s*$', ': ""', json_text)
                    
                    # Remove incomplete objects at the end
                    json_text = re.sub(r',\s*"[^"]*"\s*:\s*"[^"]*$', '', json_text)
                    
                    # Ensure proper closing brackets if missing
                    open_braces = json_text.count('{')
                    close_braces = json_text.count('}')
                    if open_braces > close_braces:
                        json_text += '}' * (open_braces - close_braces)
                    
                    open_brackets = json_text.count('[')
                    close_brackets = json_text.count(']')
                    if open_brackets > close_brackets:
                        json_text += ']' * (open_brackets - close_brackets)
                    
                    # Store complete AI response for email template
                    complete_ai_response = ai_response
                    
                    # Try to parse JSON
                    try:
                        analysis = json.loads(json_text)
                        logger.info("Successfully parsed AI response JSON")
                        
                        # Add the complete AI response for email template usage
                        analysis['_complete_ai_response'] = complete_ai_response
                        analysis['_json_text'] = json_text
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse AI response JSON: {e}")
                        logger.error(f"Problematic JSON text (first 2000 chars): {json_text[:2000]}")
                        logger.debug(f"Full JSON text length: {len(json_text)} characters")
                        
                        # Try to extract usable data with regex as fallback
                        analysis = self._extract_data_with_regex(ai_response, portfolio_data)
                        if analysis:
                            analysis['_complete_ai_response'] = complete_ai_response
                            analysis['_extraction_method'] = 'regex_fallback'
                        else:
                            analysis = self._fallback_portfolio_advisory(portfolio_data)
                            analysis['_complete_ai_response'] = complete_ai_response
                            analysis['_extraction_method'] = 'complete_fallback'
                    
                    # Add metadata
                    analysis['metadata'] = {
                        'analysis_mode': self.mode.value,
                        'generated_at': datetime.now().isoformat(),
                        'portfolio_positions': len(portfolio_data.get('positions', [])),
                        'ai_model': 'gemini-2.0-flash'
                    }
                    
                    return analysis
            
            return self._fallback_portfolio_advisory(portfolio_data)
            
        except Exception as e:
            logger.error(f"Error processing portfolio response: {e}")
            return self._fallback_portfolio_advisory(portfolio_data)
    
    def _extract_data_with_regex(self, ai_response: str, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from AI response using regex when JSON parsing fails"""
        try:
            import re
            
            # Initialize result structure
            result = {}
            
            # Extract portfolio health score
            score_match = re.search(r'"overall_score":\s*(\d+)', ai_response)
            if score_match:
                score = int(score_match.group(1))
                result['portfolio_health'] = {
                    'overall_score': score,
                    'health_status': 'good' if score >= 7 else 'fair' if score >= 5 else 'poor',
                    'key_strengths': ["Extracted from partial response"],
                    'key_weaknesses': ["Partial data due to parsing error"]
                }
            
            # Extract diversification info
            result['diversification'] = {
                'score': 6,
                'sector_allocation': {"Banking": 40, "Technology": 20, "Other": 40},
                'concentration_risk': 'medium',
                'recommendations': ["Data extracted from incomplete response"]
            }
            
            # Extract risk assessment
            risk_match = re.search(r'"overall_risk":\s*"([^"]+)"', ai_response)
            overall_risk = risk_match.group(1) if risk_match else 'medium'
            
            result['risk_assessment'] = {
                'overall_risk': overall_risk,
                'sector_risk': {"Banking": "medium", "Technology": "high"},
                'position_sizing_issues': ["Partial analysis due to parsing error"],
                'suggested_risk_controls': ["Review complete analysis in logs"]
            }
            
            # Add entry/exit analysis for entry_exit_strategy mode
            if self.mode == AdvisoryMode.ENTRY_EXIT_STRATEGY:
                result['entry_exit_analysis'] = [{
                    'ticker': pos.get('ticker', 'Unknown'),
                    'current_position': pos.get('shares', 0),
                    'optimal_entry_range': {
                        'min_price': pos.get('avg_price', 0) * 0.9,
                        'max_price': pos.get('avg_price', 0) * 1.1,
                        'rationale': 'Estimated based on current price (partial data)'
                    },
                    'exit_strategy': {
                        'short_term_target': {
                            'price': pos.get('target_price', pos.get('avg_price', 0) * 1.2),
                            'timeframe': '3 months',
                            'probability': 'medium',
                            'rationale': 'Estimated target (partial data)'
                        },
                        'long_term_target': {
                            'price': pos.get('target_price', pos.get('avg_price', 0) * 1.5),
                            'timeframe': '1-2 years',
                            'probability': 'medium',
                            'rationale': 'Long-term growth estimate (partial data)'
                        }
                    },
                    'technical_levels': {
                        'support_levels': [pos.get('avg_price', 0) * 0.9, pos.get('avg_price', 0) * 0.85],
                        'resistance_levels': [pos.get('avg_price', 0) * 1.1, pos.get('avg_price', 0) * 1.2],
                        'key_moving_averages': {'ma_20': 0, 'ma_50': 0, 'ma_200': 0}
                    },
                    'recommendation': {
                        'action': 'hold',
                        'reasoning': 'Partial analysis - review complete response in logs',
                        'stop_loss': pos.get('avg_price', 0) * 0.85,
                        'take_profit': pos.get('target_price', pos.get('avg_price', 0) * 1.2)
                    }
                } for pos in portfolio_data.get('positions', [])[:5]]  # Limit to 5 positions
            
            # Default action items
            result['action_items'] = [{
                'action': 'review',
                'ticker': 'ALL',
                'priority': 'high',
                'rationale': 'Complete analysis failed to parse - review logs for full AI response',
                'timeline': 'immediate'
            }]
            
            result['market_outlook'] = {
                'vietnam_market_view': 'neutral',
                'sector_outlook': {"Banking": "neutral", "Technology": "neutral"},
                'trading_environment': 'challenging',
                'key_market_drivers': ["Partial analysis available"]
            }
            
            logger.info("Successfully extracted partial data using regex fallback")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract data with regex: {e}")
            return None
    
    def _process_scenario_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI response for scenario analysis"""
        try:
            if 'candidates' in response and response['candidates']:
                ai_response = response['candidates'][0]['content']['parts'][0]['text']
                
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {"error": "Could not parse scenario analysis response"}
            
        except Exception as e:
            logger.error(f"Error processing scenario response: {e}")
            return {"error": f"Scenario processing failed: {e}"}
    
    def _process_benchmark_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI response for benchmark comparison"""
        try:
            if 'candidates' in response and response['candidates']:
                ai_response = response['candidates'][0]['content']['parts'][0]['text']
                
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {"error": "Could not parse benchmark comparison response"}
            
        except Exception as e:
            logger.error(f"Error processing benchmark response: {e}")
            return {"error": f"Benchmark processing failed: {e}"}
    
    def _process_risk_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI response for risk analysis"""
        try:
            if 'candidates' in response and response['candidates']:
                ai_response = response['candidates'][0]['content']['parts'][0]['text']
                
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {"error": "Could not parse risk analysis response"}
            
        except Exception as e:
            logger.error(f"Error processing risk response: {e}")
            return {"error": f"Risk processing failed: {e}"}
    
    def _fallback_portfolio_advisory(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback advisory when AI fails"""
        return {
            "portfolio_health": {
                "overall_score": 6,
                "health_status": "fair",
                "key_strengths": ["Diversified holdings", "Long-term focus"],
                "key_weaknesses": ["Analysis temporarily unavailable"]
            },
            "diversification": {
                "score": 6,
                "concentration_risk": "medium",
                "recommendations": ["Monitor sector allocation", "Consider rebalancing"]
            },
            "action_items": [{
                "action": "monitor",
                "ticker": "all",
                "priority": "medium",
                "rationale": "AI analysis temporarily unavailable, maintain current positions",
                "timeline": "daily"
            }],
            "metadata": {
                "analysis_mode": self.mode.value,
                "generated_at": datetime.now().isoformat(),
                "fallback": True
            },
            "error": "AI analysis temporarily unavailable"
        }
