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
                    analysis = json.loads(json_match.group())
                    
                    # Add metadata
                    analysis['metadata'] = {
                        'analysis_mode': self.mode.value,
                        'generated_at': datetime.now().isoformat(),
                        'portfolio_positions': len(portfolio_data.get('positions', [])),
                        'ai_model': 'gemini-2.0-flash'
                    }
                    
                    return analysis
            
            return self._fallback_portfolio_advisory(portfolio_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response JSON: {e}")
            return self._fallback_portfolio_advisory(portfolio_data)
        except Exception as e:
            logger.error(f"Error processing portfolio response: {e}")
            return self._fallback_portfolio_advisory(portfolio_data)
    
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
