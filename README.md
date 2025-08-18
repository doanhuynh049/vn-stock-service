# VN Stock Advisory Notifier

A production-ready Python application that analyzes Vietnam stock portfolios daily using Google Gemini AI and sends actionable advisory emails with AI fallback for price data when APIs fail.

## Features

- **Daily Stock Analysis**: Automated analysis of Vietnam stock holdings (HOSE/HNX/UPCoM)
- **AI-Powered Insights**: Uses Google Gemini AI for comprehensive portfolio and stock analysis
- **Enhanced Portfolio Overview**: Detailed AI insights including risk analysis, performance insights, strategic recommendations, and market context
- **Multiple Data Sources**: Primary SSI API with CafeF fallback, plus AI-powered price estimation when APIs fail
- **Email Notifications**: Beautiful HTML emails for individual stocks and portfolio overview
- **Configurable Scheduling**: Daily analysis at your preferred time with cron-style scheduling
- **Risk Management**: Stop-loss suggestions, concentration risk alerts, position sizing recommendations
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Quick Start

### 1. Prerequisites

- Python 3.6+
- Google Gemini API key
- SMTP email credentials (Gmail recommended)

### 2. Installation

```bash
git clone <repository>
cd vn-stock-service
pip install -r requirements.txt
```

### 3. Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required: Gemini AI API
LLM_PROVIDER=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
LLM_API_KEY=your_gemini_api_key_here

# Required: Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
MAIL_TO=your_email@gmail.com

# Schedule (7:30 AM daily by default)
SCHEDULE_CRON=30 7 * * *
TIMEZONE=Asia/Ho_Chi_Minh

# Set to false to send real emails
DRY_RUN=true
```

### 4. Portfolio Setup

Edit `data/holdings.json` with your positions:

```json
{
  "owner": "Your Name",
  "currency": "VND",
  "timezone": "Asia/Ho_Chi_Minh",
  "positions": [
    {
      "ticker": "FPT",
      "exchange": "HOSE",
      "shares": 100,
      "avg_price": 125000,
      "target_price": 145000,
      "max_drawdown_pct": -12,
      "notes": "Technology leader"
    }
  ]
}
```

### 5. Usage

```bash
# Test the system
python3 main.py

# Run manual analysis
python3 run_manual.py

# Start scheduler
python3 run_scheduler.py

# Docker deployment
docker-compose up --build
```

## Data Sources & AI Fallback

The system uses a robust fallback chain for price data:

1. **Primary**: SSI (Sài Gòn Securities) FastConnect API
2. **Fallback**: CafeF.vn web scraping
3. **AI Fallback**: Google Gemini AI for price estimation when APIs fail
4. **Basic Fallback**: Hardcoded estimates for common Vietnamese stocks

## Enhanced AI Portfolio Insights

The system now provides comprehensive AI-powered portfolio analysis including:

- **Overall Assessment**: Professional portfolio health summary
- **Performance Insights**: P/L analysis, best/worst performers, momentum stocks
- **Risk Analysis**: Concentration risks, sector exposure, correlation analysis with risk scoring
- **Strategic Recommendations**: Immediate actions, rebalancing advice, sector allocation, market timing
- **Market Context**: Vietnam market outlook, sector trends, macro factors

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Gemini API endpoint | Required |
| `LLM_API_KEY` | Google Gemini API key | Required |
| `SMTP_HOST` | Email server hostname | Required |
| `SMTP_USER` | Email username | Required |
| `SMTP_PASS` | Email password/app password | Required |
| `MAIL_TO` | Recipient email | Required |
| `SCHEDULE_CRON` | Cron schedule | `30 7 * * *` |
| `TIMEZONE` | Timezone | `Asia/Ho_Chi_Minh` |
| `DRY_RUN` | Safe testing mode | `true` |
| `VN_DATA_PROVIDER` | Data source | `mock` |

## Project Structure

```
vn-stock-service/
├── src/
│   ├── adapters/          # Data providers (SSI, CafeF, AI fallback)
│   ├── advisory/          # AI analysis engine
│   ├── config/            # Configuration management
│   ├── email_service/     # Email templates and sending
│   ├── models/            # Data models
│   ├── scheduler/         # Task scheduling
│   └── utils/             # Utilities
├── data/                  # Portfolio data
├── deployment/            # Docker and systemd configs
├── tests/                 # Unit tests
└── requirements.txt       # Dependencies
```

## Deployment Options

### Docker
```bash
docker-compose up -d
```

### Systemd (Linux)
```bash
sudo cp deployment/systemd/vn-stock-advisory.service /etc/systemd/system/
sudo systemctl enable vn-stock-advisory
sudo systemctl start vn-stock-advisory
```

## AI Advisory Actions

- `hold`: Maintain current position
- `add_small`: Add small position
- `add`: Increase position
- `trim`: Reduce position slightly
- `take_profit`: Take profits at target
- `reduce`: Significantly reduce position
- `exit`: Close position entirely

## Troubleshooting

### Gemini API Issues
- Verify API key is correct and active
- Check API quotas and limits
- Test connectivity with `python3 test_gemini.py`

### Email Issues
- Use App Passwords for Gmail (not regular password)
- Enable 2FA and generate app-specific password
- Check SMTP settings and firewall

### Data Provider Issues
- SSI API may have rate limits
- CafeF scraping requires stable internet
- AI fallback provides estimates when both fail

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for educational and informational purposes only. Not financial advice. Always conduct your own research and consult with financial advisors before making investment decisions.