from typing import Dict, Any, List, Optional
import requests
import json
import logging
import time
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.api_logger import APILogger

logger = logging.getLogger(__name__)

class AIAdvisor:
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self.api_logger = APILogger()
        
    def generate_advisory(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI advisory for a single stock"""
        try:
            prompt = self._create_prompt(stock_data)
            response = self._call_ai_model(prompt)
            return self._process_response(response)
        except Exception as e:
            logger.error(f"Error generating advisory for {stock_data.get('ticker')}: {e}")
            return self._fallback_advisory(stock_data)
    
    def generate_portfolio_advisory(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate portfolio overview advisory"""
        try:
            prompt = self._create_portfolio_prompt(portfolio_data)
            response = self._call_ai_model(prompt)
            return self._process_portfolio_response(response)
        except Exception as e:
            logger.error(f"Error generating portfolio advisory: {e}")
            return self._fallback_portfolio_advisory(portfolio_data)

    def _create_prompt(self, stock_data: Dict[str, Any]) -> str:
        system_prompt = (
            "You are a disciplined Vietnam-equities strategist. "
            "Give concise, actionable guidance with risk controls. No hype. Cite signals you used. "
            "Return your response in valid JSON format with the following structure: "
            '{"action": "hold|add_small|add|trim|take_profit|reduce|exit", '
            '"rationale": "brief explanation", '
            '"key_signals": ["signal1", "signal2"], '
            '"risk_notes": "risk assessment", '
            '"levels": {"add_zone": [low, high], "take_profit_zone": [low, high], "hard_stop": value}, '
            '"next_checks": ["condition1", "condition2"]}'
        )
        
        user_data = {
            "ticker": stock_data["ticker"],
            "exchange": stock_data["exchange"],
            "date": stock_data["date"],
            "price": stock_data["price"],
            "avg_price": stock_data["avg_price"],
            "target_price": stock_data["target_price"],
            "pct_to_target": stock_data["pct_to_target"],
            "pl_pct_vs_avg": stock_data["pl_pct_vs_avg"],
            "tech": stock_data["tech"],
            "fundamentals": stock_data.get("fundamentals", {}),
            "news_sentiment": stock_data.get("news_sentiment", {}),
            "risk": stock_data["risk"]
        }
        
        user_prompt = f"Analyze this Vietnam stock data and provide advisory: {json.dumps(user_data, indent=2)}"
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _create_portfolio_prompt(self, portfolio_data: Dict[str, Any]) -> str:
        system_prompt = (
            "You are an experienced Vietnam portfolio manager with deep knowledge of Vietnamese stocks and market dynamics. "
            "Analyze this portfolio comprehensively and provide professional insights.\n\n"
            
            "ANALYSIS FOCUS:\n"
            "1. Risk Assessment: Concentration, sector exposure, correlation risks\n"
            "2. Performance Analysis: P/L trends, underperformers, top movers\n"
            "3. Strategic Recommendations: Rebalancing, sector allocation, timing\n"
            "4. Market Context: Vietnam market conditions, sector rotation, upcoming events\n"
            "5. Action Items: Immediate, short-term, and long-term priorities\n\n"
            
            "Return your analysis in valid JSON format with this structure:\n"
            '{\n'
            '  "overall_assessment": "Brief 2-3 sentence summary of portfolio health",\n'
            '  "performance_insights": {\n'
            '    "total_pl_analysis": "Analysis of overall P/L performance",\n'
            '    "best_performers": ["ticker1: reason", "ticker2: reason"],\n'
            '    "underperformers": ["ticker1: reason", "ticker2: reason"],\n'
            '    "momentum_stocks": ["ticker1", "ticker2"]\n'
            '  },\n'
            '  "risk_analysis": {\n'
            '    "concentration_risks": ["specific risk descriptions"],\n'
            '    "sector_risks": ["sector exposure concerns"],\n'
            '    "correlation_risks": ["stocks that move together"],\n'
            '    "risk_score": "number 1-10 where 10 is highest risk"\n'
            '  },\n'
            '  "strategic_recommendations": {\n'
            '    "immediate_actions": ["urgent actions for today/this week"],\n'
            '    "rebalancing_advice": ["specific position adjustments"],\n'
            '    "sector_allocation": ["sector-specific recommendations"],\n'
            '    "market_timing": ["timing considerations for Vietnam market"]\n'
            '  },\n'
            '  "market_context": {\n'
            '    "vietnam_market_outlook": "Current VN market conditions assessment",\n'
            '    "sector_trends": ["which sectors are favored/avoided and why"],\n'
            '    "macro_factors": ["key economic factors affecting portfolio"]\n'
            '  },\n'
            '  "priority_todos": [\n'
            '    "High Priority: specific actionable item",\n'
            '    "Medium Priority: specific actionable item",\n'
            '    "Low Priority: specific actionable item"\n'
            '  ]\n'
            '}'
        )
        
        # Enhanced portfolio data context
        portfolio_context = {
            "portfolio_summary": portfolio_data,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "market_session": "Vietnam trading hours",
            "currency": "VND"
        }
        
        user_prompt = (
            f"Please analyze this Vietnamese stock portfolio and provide comprehensive insights:\n\n"
            f"{json.dumps(portfolio_context, indent=2)}\n\n"
            f"Consider the following in your analysis:\n"
            f"- Vietnamese market dynamics and typical sector rotations\n"
            f"- Banking sector concentration (VCB, TCB, ACB, BID)\n"
            f"- Technology exposure (FPT)\n"
            f"- Consumer and industrial diversification\n"
            f"- Position sizing and risk management\n"
            f"- Current Vietnam economic environment"
        )
        
        return f"{system_prompt}\n\n{user_prompt}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_ai_model(self, prompt: str) -> Dict[str, Any]:
        """Call Gemini AI model with retry logic"""
        return self._call_gemini(prompt)
    
    def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        """Call Google Gemini API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 500
            }
        }
        
        url = f"{self.api_url}?key={self.api_key}"
        
        # Log the AI API request
        start_time = time.time()
        request_id = self.api_logger.log_ai_request(
            api_name="Gemini_Advisory",
            method="POST",
            url=url,
            prompt=prompt,
            model_config=data.get("generationConfig", {})
        )
        
        response = requests.post(
            url, 
            headers=headers, 
            json=data,
            timeout=30
        )
        duration_ms = (time.time() - start_time) * 1000
        response.raise_for_status()
        
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Log successful AI response
            self.api_logger.log_ai_response(
                request_id=request_id,
                api_name="Gemini_Advisory",
                status_code=response.status_code,
                ai_response=content,
                response_headers=dict(response.headers),
                duration_ms=duration_ms,
                usage_stats=result.get('usageMetadata', {})
            )
            
            # Try to parse as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback: extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                raise ValueError("Could not parse Gemini response as JSON")
        else:
            # Log error response
            self.api_logger.log_ai_response(
                request_id=request_id,
                api_name="Gemini_Advisory",
                status_code=response.status_code,
                duration_ms=duration_ms,
                error="No valid candidates in Gemini response"
            )
            raise ValueError("No valid response from Gemini API")

    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate AI response"""
        return {
            "action": response.get("action", "hold"),
            "rationale": response.get("rationale", "No rationale provided"),
            "key_signals": response.get("key_signals", []),
            "risk_notes": response.get("risk_notes", ""),
            "levels": response.get("levels", {}),
            "next_checks": response.get("next_checks", [])
        }
    
    def _process_portfolio_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process enhanced portfolio AI response"""
        # Extract the enhanced portfolio analysis
        overall_assessment = response.get("overall_assessment", "Portfolio analysis completed.")
        performance_insights = response.get("performance_insights", {})
        risk_analysis = response.get("risk_analysis", {})
        strategic_recommendations = response.get("strategic_recommendations", {})
        market_context = response.get("market_context", {})
        priority_todos = response.get("priority_todos", [])
        
        # Backwards compatibility for basic fields
        basic_response = {
            "total_pl_pct": response.get("total_pl_pct", 0),
            "risk_alerts": risk_analysis.get("concentration_risks", []) + risk_analysis.get("sector_risks", []),
            "top_movers": performance_insights.get("momentum_stocks", []),
            "concentration_risks": risk_analysis.get("concentration_risks", []),
            "priority_todos": priority_todos
        }
        
        # Enhanced fields for improved display
        enhanced_response = {
            "overall_assessment": overall_assessment,
            "performance_insights": {
                "total_pl_analysis": performance_insights.get("total_pl_analysis", ""),
                "best_performers": performance_insights.get("best_performers", []),
                "underperformers": performance_insights.get("underperformers", []),
                "momentum_stocks": performance_insights.get("momentum_stocks", [])
            },
            "risk_analysis": {
                "concentration_risks": risk_analysis.get("concentration_risks", []),
                "sector_risks": risk_analysis.get("sector_risks", []),
                "correlation_risks": risk_analysis.get("correlation_risks", []),
                "risk_score": risk_analysis.get("risk_score", 5)
            },
            "strategic_recommendations": {
                "immediate_actions": strategic_recommendations.get("immediate_actions", []),
                "rebalancing_advice": strategic_recommendations.get("rebalancing_advice", []),
                "sector_allocation": strategic_recommendations.get("sector_allocation", []),
                "market_timing": strategic_recommendations.get("market_timing", [])
            },
            "market_context": {
                "vietnam_market_outlook": market_context.get("vietnam_market_outlook", ""),
                "sector_trends": market_context.get("sector_trends", []),
                "macro_factors": market_context.get("macro_factors", [])
            },
            "priority_todos": priority_todos
        }
        
        # Merge basic and enhanced for compatibility
        return {**basic_response, **enhanced_response}
    
    def _fallback_advisory(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback advisory when AI fails"""
        pl_pct = stock_data.get("pl_pct_vs_avg", 0)
        pct_to_target = stock_data.get("pct_to_target", 0)
        
        if pl_pct < -10:
            action = "reduce"
        elif pct_to_target > 15:
            action = "take_profit"
        elif pl_pct > 0 and pct_to_target > 5:
            action = "hold"
        else:
            action = "add_small"
            
        return {
            "action": action,
            "rationale": "Fallback analysis based on P/L and target distance",
            "key_signals": ["AI_UNAVAILABLE"],
            "risk_notes": "AI analysis unavailable - using basic rules",
            "levels": {},
            "next_checks": ["Monitor AI service availability"]
        }
    
    def _fallback_portfolio_advisory(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback portfolio advisory"""
        return {
            "total_pl_pct": 0,
            "risk_alerts": ["AI service unavailable"],
            "top_movers": [],
            "concentration_risks": [],
            "priority_todos": ["Check AI service", "Review positions manually"]
        }