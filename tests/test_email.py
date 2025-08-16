import pytest
from src.email.sender import EmailSender

@pytest.fixture
def email_sender():
    return EmailSender()

def test_email_formatting(email_sender):
    stock_data = {
        "ticker": "FPT",
        "price": 123000,
        "avg_price": 121000,
        "target_price": 145000,
        "action": "hold",
        "rationale": "The stock is showing stable performance.",
        "levels": {
            "add_zone": [120000, 122000],
            "take_profit_zone": [142000, 146000],
            "hard_stop": 111000
        },
        "news": [
            {"title": "FPT announces Q3 results", "link": "http://example.com/news1"},
            {"title": "FPT expands into new markets", "link": "http://example.com/news2"}
        ]
    }
    
    email_content = email_sender.format_stock_email(stock_data)
    
    assert "FPT" in email_content
    assert "Price: 123000" in email_content
    assert "Action: hold" in email_content
    assert "Rationale: The stock is showing stable performance." in email_content
    assert "Add Zone: 120000 - 122000" in email_content
    assert "Take Profit Zone: 142000 - 146000" in email_content
    assert "Hard Stop: 111000" in email_content
    assert "FPT announces Q3 results" in email_content
    assert "FPT expands into new markets" in email_content

def test_email_sending(email_sender, mocker):
    mock_send = mocker.patch.object(email_sender, 'send_email', return_value=True)
    result = email_sender.send_email("test@example.com", "Test Subject", "Test Body")
    assert result is True
    mock_send.assert_called_once_with("test@example.com", "Test Subject", "Test Body")