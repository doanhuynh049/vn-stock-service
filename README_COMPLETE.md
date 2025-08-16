# VN Stock Advisory Notifier

A production-ready background application that analyzes Vietnam stock holdings daily using Google Gemini AI and sends actionable advisory emails.

## Features

- **Daily Stock Analysis**: Automated analysis of your Vietnam stock portfolio (HOSE/HNX/UPCoM)
- **AI-Powered Insights**: Uses Google Gemini AI to generate actionable trading advice
- **Email Notifications**: Sends detailed HTML emails for each stock and portfolio overview
- **Configurable Scheduling**: Run daily at your preferred time with cron-style scheduling
- **Multiple Data Providers**: Pluggable architecture supports mock and real data sources
- **Technical Analysis**: RSI, MACD, SMA crossovers, volume analysis
- **Risk Management**: Stop-loss suggestions, position sizing recommendations
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Quick Start

### 1. Prerequisites

- Python 3.6+ 
- Google Gemini API key
- SMTP email credentials (Gmail recommended)

### 2. Installation

```bash
# Clone and setup
git clone <repository>
cd vn-stock-advisory

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and email settings
```

### 3. Configuration

Edit `.env` file with your settings:

```bash
# Required: Gemini AI API
LLM_PROVIDER=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
LLM_API_KEY=your_gemini_api_key_here

# Required: Email Settings (for Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_TO=your_email@gmail.com

# Schedule (7:30 AM daily by default)
SCHEDULE_CRON=30 7 * * *
TIMEZONE=Asia/Ho_Chi_Minh

# Set to false to send real emails
DRY_RUN=true
```

### 4. Portfolio Setup

Create or edit `data/holdings.json` with your positions:

```json
{
  "owner": "Your Name",
  "currency": "VND", 
  "timezone": "Asia/Ho_Chi_Minh",
  "positions": [
    {
      "ticker": "FPT",
      "exchange": "HOSE",
      "shares": 500,
      "avg_price": 121000,
      "target_price": 145000,
      "max_drawdown_pct": -12
    },
    {
      "ticker": "VNM",
      "exchange": "HOSE",
      "shares": 300,
      "avg_price": 68000,
      "target_price": 80000,
      "max_drawdown_pct": -10
    }
  ]
}
```

### 5. Test the System

```bash
# Test basic functionality
python3 main.py

# Run a single advisory manually
python3 run_manual.py

# Start the scheduler
python3 run_scheduler.py
```

## Running Options

### Local Development

```bash
# Test the system
python3 main.py

# Run scheduler (Ctrl+C to stop)  
python3 run_scheduler.py

# Manual single run
python3 run_manual.py
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.simple.yml up -d

# View logs
docker-compose logs -f vn-stock-advisory

# Stop
docker-compose down
```

### Production Deployment

```bash
# Using systemd (Linux)
sudo cp deployment/systemd/vn-stock-advisory.service /etc/systemd/system/
sudo systemctl enable vn-stock-advisory
sudo systemctl start vn-stock-advisory

# Check status
sudo systemctl status vn-stock-advisory
```

## Environment Variables

### Required Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PROVIDER` | Gemini API endpoint | `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent` |
| `LLM_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `SMTP_HOST` | Email server hostname | `smtp.gmail.com` |
| `SMTP_USER` | Email username | `your_email@gmail.com` |
| `SMTP_PASS` | Email password/app password | `your_password` |
| `MAIL_TO` | Recipient email | `your_email@gmail.com` |

### Optional Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SCHEDULE_CRON` | `30 7 * * *` | Cron schedule (7:30 AM daily) |
| `TIMEZONE` | `Asia/Ho_Chi_Minh` | Timezone for scheduling |
| `DRY_RUN` | `true` | Set to `false` to send real emails |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `VN_DATA_PROVIDER` | `mock` | Data provider (mock, vietcap, cafef) |

## Data Providers

### Mock Provider (Default)
- Generates realistic but fake market data
- Perfect for testing and development
- No external API dependencies

### Real Data Providers
The system supports pluggable data providers. To add a real Vietnam stock data source:

1. Implement the `DataProviderInterface` in `src/adapters/`
2. Add provider configuration in `.env`
3. Update `VN_DATA_PROVIDER` setting

Example providers that can be implemented:
- VietCap API
- CafeF scraping (with ToS compliance)
- SSI/VPS broker APIs
- Yahoo Finance VN

## AI Advisory System

The system uses Google Gemini AI to analyze:

- **Technical Indicators**: RSI, MACD, SMA crossovers
- **Price Action**: Support/resistance levels, breakouts
- **Volume Analysis**: Unusual volume spikes
- **Risk Assessment**: Stop-loss levels, position sizing
- **Market Context**: Sector trends, news sentiment

### Advisory Actions
- `hold`: Maintain current position
- `add_small`: Add small position
- `add`: Increase position
- `trim`: Reduce position slightly
- `take_profit`: Take profits at target
- `reduce`: Significantly reduce position
- `exit`: Close position entirely

## Email Templates

The system generates HTML emails with:

### Per-Stock Emails
- Current price and change
- Position P&L
- AI advisory recommendation
- Key technical levels
- Risk notes and next actions

### Portfolio Overview
- Total portfolio performance
- Top movers
- Risk alerts
- Priority action items
- Sector allocation

## Troubleshooting

### Common Issues

**Gemini API Errors**
```bash
# Test API connectivity
python3 -c "
import requests, os
from dotenv import load_dotenv
load_dotenv()
print('Testing Gemini API...')
# Your test code here
"
```

**Email Sending Issues**
- For Gmail, use App Passwords instead of regular password
- Enable 2FA and generate app-specific password
- Check SMTP settings and firewall

**Scheduler Not Running**
- Check cron expression format: `minute hour day month dayofweek`
- Verify timezone settings
- Check logs in `logs/vn-stock-advisory.log`

### Logs

```bash
# View application logs
tail -f logs/vn-stock-advisory.log

# View scheduler logs (if using systemd)
journalctl -u vn-stock-advisory -f
```

## Development

### Project Structure

```
vn-stock-advisory/
├── src/
│   ├── adapters/          # Data provider interfaces
│   ├── advisory/          # AI and analysis engine
│   ├── config/            # Configuration management
│   ├── email_service/     # Email templates and sending
│   ├── models/           # Data models
│   ├── scheduler/        # Task scheduling
│   └── utils/            # Utilities and helpers
├── data/                 # Portfolio data
├── logs/                 # Application logs
├── output/              # Generated emails (dry run)
├── tests/               # Unit tests
└── deployment/          # Deployment scripts
```

### Adding Features

1. **New Data Provider**: Implement `DataProviderInterface`
2. **New Indicators**: Add to `advisory/indicators.py`
3. **Email Templates**: Modify HTML templates in `email_service/templates/`
4. **Custom Analysis**: Extend `advisory/engine.py`

### Testing

```bash
# Run tests
python3 -m pytest tests/

# Test specific component
python3 -m pytest tests/test_advisory.py -v
```

## Security Notes

- Store API keys securely (use environment variables)
- Use app passwords for email authentication
- Consider using secrets management in production
- Regular security updates for dependencies

## License

[Your License Here]

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Test individual components
4. Open an issue with detailed error information

---

**Disclaimer**: This software is for educational and informational purposes only. Not financial advice. Trade at your own risk.
