from typing import Dict, Any, List, Optional
import requests
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class AIAdvisor:
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        
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
            "You are a Vietnam portfolio manager. Analyze the overall portfolio and provide summary insights. "
            "Focus on total P/L, concentration risks, sector balance, and priority actions. "
            "Return valid JSON with: "
            '{"total_pl_pct": number, "risk_alerts": ["alert1"], "top_movers": ["ticker1"], '
            '"concentration_risks": ["risk1"], "priority_todos": ["todo1", "todo2", "todo3"]}'
        )
        
        user_prompt = f"Analyze this portfolio: {json.dumps(portfolio_data, indent=2)}"
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
        
        response = requests.post(
            url, 
            headers=headers, 
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            
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
        """Process portfolio AI response"""
        return {
            "total_pl_pct": response.get("total_pl_pct", 0),
            "risk_alerts": response.get("risk_alerts", []),
            "top_movers": response.get("top_movers", []),
            "concentration_risks": response.get("concentration_risks", []),
            "priority_todos": response.get("priority_todos", [])
        }
    
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