import pytest
from src.advisory.engine import AdvisoryEngine
from src.models.holdings import Holdings

# Sample holdings for testing
sample_holdings = {
    "owner": "Quat",
    "currency": "VND",
    "timezone": "Asia/Ho_Chi_Minh",
    "positions": [
        {"ticker": "FPT", "exchange": "HOSE", "shares": 500, "avg_price": 121000, "target_price": 145000, "max_drawdown_pct": -12},
        {"ticker": "VNM", "exchange": "HOSE", "shares": 300, "avg_price": 68000, "target_price": 80000, "max_drawdown_pct": -10}
    ]
}

@pytest.fixture
def advisory_engine():
    holdings = Holdings(**sample_holdings)
    return AdvisoryEngine(holdings)

def test_profit_loss(advisory_engine):
    advisory_engine.update_market_data({
        "FPT": {"current_price": 123000},
        "VNM": {"current_price": 70000}
    })
    advisory_engine.calculate_advisories()
    
    fpt_advisory = advisory_engine.advisories["FPT"]
    vnm_advisory = advisory_engine.advisories["VNM"]
    
    assert fpt_advisory["pl_pct_vs_avg"] == pytest.approx(1.65, rel=1e-2)
    assert vnm_advisory["pl_pct_vs_avg"] == pytest.approx(2.94, rel=1e-2)

def test_advisory_actions(advisory_engine):
    advisory_engine.update_market_data({
        "FPT": {"current_price": 123000},
        "VNM": {"current_price": 70000}
    })
    advisory_engine.calculate_advisories()
    
    fpt_advisory = advisory_engine.advisories["FPT"]
    vnm_advisory = advisory_engine.advisories["VNM"]
    
    assert fpt_advisory["action"] in ["hold", "add_small", "add", "trim", "take_profit", "reduce", "exit"]
    assert vnm_advisory["action"] in ["hold", "add_small", "add", "trim", "take_profit", "reduce", "exit"]

def test_risk_checks(advisory_engine):
    advisory_engine.update_market_data({
        "FPT": {"current_price": 110000},
        "VNM": {"current_price": 65000}
    })
    advisory_engine.calculate_advisories()
    
    fpt_advisory = advisory_engine.advisories["FPT"]
    vnm_advisory = advisory_engine.advisories["VNM"]
    
    assert fpt_advisory["risk"]["max_drawdown_pct"] == -12
    assert vnm_advisory["risk"]["max_drawdown_pct"] == -10

def test_advisory_output_structure(advisory_engine):
    advisory_engine.update_market_data({
        "FPT": {"current_price": 123000},
        "VNM": {"current_price": 70000}
    })
    advisory_engine.calculate_advisories()
    
    fpt_advisory = advisory_engine.advisories["FPT"]
    
    assert "action" in fpt_advisory
    assert "rationale" in fpt_advisory
    assert "key_signals" in fpt_advisory
    assert "risk_notes" in fpt_advisory
    assert "levels" in fpt_advisory
    assert "next_checks" in fpt_advisory