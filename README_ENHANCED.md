# VN Stock Advisory - Enhanced AI-First System

🚀 **Revolutionary AI-powered portfolio advisory system for Vietnamese stock market** - No price fetching required!

## 🌟 Key Features

### 🧠 **AI-First Architecture**
- **Pure AI Analysis**: No price fetching, API dependencies, or data scraping
- **Holdings-Only Approach**: Simply maintain your portfolio in JSON format
- **Google Gemini 2.0**: Advanced AI model with comprehensive market understanding

### 📈 **Multiple Advisory Modes**
- **Long-Term Investor**: Focus on fundamentals and long-term growth
- **Swing Trader**: Technical analysis and momentum strategies  
- **Dividend Focused**: Income-oriented stock selection
- **Growth Oriented**: High-growth potential companies
- **Value Investor**: Undervalued opportunities
- **Conservative**: Risk-averse stable investments

### 🎯 **Advanced Analytics**
- **Scenario Analysis**: "What-if" portfolio simulations
- **Risk Management**: Concentration, sector allocation, drawdown analysis
- **Benchmark Comparison**: VN-Index, VN30, HNX performance comparison
- **Historical Tracking**: Portfolio evolution and performance metrics
- **Action Items**: Specific, prioritized recommendations

### 📧 **Smart Notifications**
- **Daily Reports**: Automated email with portfolio insights
- **Weekly Summaries**: Portfolio performance and trend analysis
- **Custom Scheduling**: Configurable timing and frequency
- **Bilingual Support**: English and Vietnamese reports

### ⚙️ **Professional Configuration**
- **YAML/TOML Config**: User-friendly configuration management
- **Risk Profiles**: Customizable risk tolerance and position sizing
- **Email Templates**: Professional HTML email layouts
- **Historical Database**: SQLite for performance tracking

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/your-repo/vn-stock-service
cd vn-stock-service

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file:

```bash
# Gemini AI Configuration
LLM_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# System Configuration
TIMEZONE=Asia/Ho_Chi_Minh
SCHEDULE_CRON=30 7 * * 1-5
DRY_RUN=true
LOG_LEVEL=INFO
```

### 3. Portfolio Setup

Create your portfolio in `data/holdings.json`:

```json
{
  "owner": "Your Name",
  "currency": "VND",
  "timezone": "Asia/Ho_Chi_Minh",
  "last_updated": "2025-01-21T10:00:00+07:00",
  "positions": [
    {
      "ticker": "FPT",
      "exchange": "HOSE",
      "shares": 500,
      "avg_price": 121000,
      "target_price": 145000,
      "max_drawdown_pct": -12,
      "notes": "Technology leader"
    },
    {
      "ticker": "VCB",
      "exchange": "HOSE", 
      "shares": 200,
      "avg_price": 95000,
      "target_price": 110000,
      "max_drawdown_pct": -15,
      "notes": "Top banking stock"
    }
  ]
}
```

### 4. User Configuration

Customize `config/user_config.yaml`:

```yaml
advisory:
  primary_mode: "long_term"
  enable_scenario_analysis: true
  benchmark_comparisons: ["VN-Index", "VN30-Index"]

risk:
  risk_tolerance: "moderate"
  max_position_size: 25.0
  default_stop_loss: -15.0

email:
  enabled: true
  recipients: ["your-email@example.com"]
  schedule:
    time: "08:00"
    days: [0, 1, 2, 3, 4]  # Monday-Friday
```

### 5. Test the System

```bash
# Test all components
python main.py

# Generate manual advisory
python src/app.py --mode advisory

# Test scenario analysis
python src/app.py --mode scenario --scenario "What if banking sector drops 20%?"

# Start the API server
python src/app.py --mode api --port 8000

# Start automated scheduler
python run_scheduler.py
```

## � Email System Architecture

The VN Stock Advisory system includes a sophisticated email notification system that automatically sends daily portfolio insights and analysis reports. Here's how it works:

### 🔧 **Email System Components**

#### **1. Email Service (`src/email_service/sender.py`)**
The core email engine with two modes:

**Production Mode (`EmailSender`)**
- Real SMTP email delivery
- HTML email templates with Jinja2
- Professional portfolio reports
- Error handling and logging

**Testing Mode (`DryRunEmailSender`)**
- Saves emails as HTML files (no actual sending)
- Perfect for development and testing
- Outputs to `output/emails/` directory

#### **2. HTML Email Templates (`src/email_service/templates/`)**
Professional email templates include:

- **`all_stocks_advisory.html`** - Complete portfolio overview
- **`portfolio_overview.html`** - Summary dashboard  
- **`stock_detail.html`** - Individual stock analysis
- **`stock_detail_clean.html`** - Simplified stock report

### ⚙️ **Email Configuration**

#### **Environment Variables (`.env`)**
```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Recipients
EMAIL_TO=recipient@example.com

# Control email sending
DRY_RUN=true  # Set to false for real emails
```

#### **User Configuration (`config/user_config.yaml`)**
```yaml
email:
  enabled: true
  recipients: 
    - "your-email@example.com"
    - "family@example.com"
  schedule:
    time: "08:00"
    days: [0, 1, 2, 3, 4]  # Monday-Friday
  include_detailed_analysis: true
  include_scenarios: false
```

### 🚀 **Email Sending Flow**

#### **1. Scheduled Daily Email (Automatic)**
```bash
# Triggered by run_scheduler.py daily
Daily Schedule: 7:30 AM Vietnam Time (Monday-Friday)
Weekly Summary: Fridays 6:00 PM
```

**Process Flow:**
1. **Advisory Generation**: Enhanced AI engine generates portfolio analysis
2. **Template Processing**: Jinja2 renders HTML email with portfolio data
3. **Email Composition**: SMTP message with HTML content and styling
4. **Delivery**: Send via configured SMTP server (Gmail, Outlook, etc.)
5. **Logging**: Track delivery status and errors

#### **2. Manual Email Sending**
```bash
# Send single email via API
curl -X POST http://localhost:8000/advisory/daily

# Send email via CLI
python src/app.py --mode advisory
```

### 📧 **Email Content Structure**

#### **Daily Advisory Email Contains:**

**📊 Portfolio Overview**
- Total portfolio value and performance
- Position count and diversification metrics
- Top performers and underperformers
- Risk concentration alerts

**🎯 AI Analysis per Stock**
- Current holding details (shares, avg price, target)
- AI-generated recommendation (buy/hold/sell)
- Risk assessment and key signals
- Sector analysis and market context

**📈 Advanced Insights**
- Portfolio rebalancing suggestions
- Market timing recommendations
- Risk management alerts
- Action items with priorities

**🔍 Visual Elements**
- Color-coded performance indicators
- Professional styling and charts
- Mobile-responsive design
- Vietnamese market branding

### 🛠 **Email System Usage Examples**

#### **Test Email System**
```python
from src.email_service.sender import EmailSender, DryRunEmailSender

# Test mode (saves to files)
dry_sender = DryRunEmailSender()
dry_sender.test_connection()  # Always returns True

# Production mode  
sender = EmailSender(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your-email@gmail.com", 
    smtp_pass="your-app-password"
)

# Test SMTP connection
if sender.test_connection():
    print("✓ Email system ready")
```

#### **Send Custom Advisory Email**
```python
from src.advisory.enhanced_engine import EnhancedAdvisoryEngine

# Generate advisory data
engine = EnhancedAdvisoryEngine()
advisory = engine.generate_daily_advisory()

# Prepare email data
email_data = {
    "advisory_date": advisory['advisory_date'],
    "portfolio": advisory['portfolio_summary'],
    "advisory": advisory['main_advisory'],
    "additional_analyses": advisory['additional_analyses']
}

# Send email
success = sender.send_daily_advisory(email_data)
```

### 📱 **Email Template Features**

#### **Professional Design**
- **Responsive Layout**: Works on desktop and mobile
- **Modern Styling**: Clean, professional appearance
- **Color Coding**: Green (profits), Red (losses), Blue (neutral)
- **Vietnamese Branding**: Localized for VN market

#### **Rich Content**
- **Performance Tables**: Sortable position data
- **AI Insights**: Natural language analysis
- **Action Items**: Prioritized recommendations
- **Market Context**: Vietnam-specific market commentary

#### **Technical Features**
- **HTML/CSS**: Professional email-safe styling
- **Jinja2 Templates**: Dynamic content generation
- **UTF-8 Support**: Vietnamese characters and symbols
- **Attachment Support**: Can include reports or charts

### 🔒 **Email Security & Privacy**

#### **SMTP Security**
- **TLS Encryption**: Secure email transmission
- **App Passwords**: Gmail app-specific passwords
- **OAuth2 Support**: Modern authentication (configurable)

#### **Data Privacy**
- **Local Processing**: All analysis done locally
- **No Cloud Dependencies**: Portfolio data stays private
- **Configurable Recipients**: Control who receives emails

#### **Error Handling**
- **Retry Logic**: Automatic retry on failures
- **Fallback Options**: Graceful degradation
- **Comprehensive Logging**: Track all email operations

### 🎯 **Email Automation Schedule**

#### **Daily Reports (Monday-Friday 7:30 AM)**
- Complete portfolio analysis
- Individual stock recommendations
- Risk management alerts
- Market context and timing

#### **Weekly Summaries (Fridays 6:00 PM)** 
- Weekly performance review
- Portfolio evolution analysis
- Historical trend insights
- Strategy recommendations

#### **Custom Triggers**
- Manual API calls
- Scenario analysis results
- Risk threshold breaches
- Portfolio rebalancing alerts

### 🛡 **Troubleshooting Email Issues**

#### **Common Problems & Solutions**

**Email Not Sending**
```bash
# Check SMTP settings
python -c "from src.email_service.sender import EmailSender; \
           EmailSender('smtp.gmail.com', 587, 'user', 'pass').test_connection()"

# Verify .env configuration
grep -E "(SMTP_|EMAIL_)" .env

# Check DRY_RUN mode
echo $DRY_RUN  # Should be 'false' for real emails
```

**Gmail Authentication Issues**
```bash
# Use App Password, not regular password
# Enable 2FA on Google Account
# Generate App Password in Google Security Settings
# Use app password in SMTP_PASSWORD
```

**Template Rendering Errors**
```bash
# Check template files exist
ls src/email_service/templates/

# Verify Jinja2 syntax
python -c "from jinja2 import Template; Template('{{ test }}').render(test='OK')"
```

**Email Formatting Issues**
```bash
# Test email saved to file in DRY_RUN mode
ls output/emails/

# Open in browser to verify appearance
open output/emails/latest_email.html
```

The email system is designed to be robust, secure, and user-friendly, providing professional-quality portfolio reports directly to your inbox every trading day! 📧📈

## �📊 Usage Examples

### Manual Advisory Generation

```python
from src.advisory.enhanced_engine import EnhancedAdvisoryEngine

# Initialize engine
engine = EnhancedAdvisoryEngine()

# Generate comprehensive advisory
advisory = engine.generate_daily_advisory()

print(f"Portfolio: {advisory['portfolio_summary']['total_positions']} positions")
print(f"Total Value: {advisory['portfolio_summary']['total_invested_value']:,.0f} VND")
print(f"Advisory Mode: {advisory['advisory_mode']}")
```

### Scenario Analysis

```python
# Analyze what-if scenarios
scenario_result = engine.analyze_scenario(
    "What if I reduce my FPT position by 50%?"
)

print(f"Scenario Impact: {scenario_result['analysis']}")
```

### Position Analysis

```python
# Get detailed position analysis
position_analysis = engine.get_position_analysis("FPT")

print(f"Recommendation: {position_analysis['recommendation']}")
print(f"Analysis: {position_analysis['analysis']}")
```

## 🔧 API Endpoints

### Portfolio Management
- `GET /portfolio` - Get portfolio summary
- `GET /position/{ticker}` - Get position analysis

### Advisory Generation
- `GET /advisory/daily` - Get daily advisory
- `POST /advisory/daily` - Generate new advisory
- `POST /scenario/analyze` - Analyze scenario

### Configuration
- `GET /config/user` - Get user configuration
- `POST /config/advisory_mode` - Update advisory mode

### Historical Data
- `GET /history/evolution?days=30` - Portfolio evolution

## 📋 System Architecture

```
📁 VN Stock Service/
├── 📄 main.py                    # Main entry point
├── 📄 run_scheduler.py           # Automated scheduler
├── 📁 src/
│   ├── 📄 app.py                 # FastAPI application
│   ├── 📁 adapters/
│   │   └── 📄 holdings_provider.py    # Holdings-only data provider
│   ├── 📁 advisory/
│   │   ├── 📄 enhanced_engine.py      # Main advisory engine
│   │   └── 📄 enhanced_ai_advisor.py  # Multi-mode AI advisor
│   ├── 📁 config/
│   │   └── 📄 user_config.py          # Configuration management
│   ├── 📁 data/
│   │   └── 📄 historical_store.py     # SQLite historical storage
│   └── 📁 email_service/
│       └── 📄 sender.py               # Email notifications
├── 📁 data/
│   └── 📄 holdings.json               # Your portfolio
└── 📁 config/
    └── 📄 user_config.yaml            # User preferences
```

## 🎯 Advisory Modes Explained

### Long-Term Investor
- Focus on company fundamentals and growth prospects
- Dividend sustainability and yield analysis
- Sector rotation and economic cycle considerations
- 1-3 year investment horizon

### Swing Trader  
- Technical analysis and momentum indicators
- Entry/exit timing recommendations
- Short to medium-term opportunities (days to months)
- Risk management for active trading

### Dividend Focused
- Dividend yield and payout ratio analysis
- Income stability and growth assessment
- REIT and utility stock preferences
- Tax-efficient income strategies

### Growth Oriented
- High-growth potential companies
- Technology and innovation focus
- Market expansion opportunities
- Higher risk tolerance for growth

### Value Investor
- Undervalued stock identification
- P/E, P/B ratio analysis
- Asset-based valuation methods
- Long-term value realization

### Conservative
- Capital preservation focus
- Blue-chip and established companies
- Lower volatility preferences
- Defensive sector allocation

## ⚡ Performance Features

### Local Caching
- AI response caching to reduce API calls
- Configurable cache duration and size
- Improved response times

### Historical Analytics
- Portfolio evolution tracking
- Performance benchmarking
- Trend analysis and insights
- SQLite database storage

### Batch Processing
- Efficient bulk portfolio analysis
- Optimized AI prompt engineering
- Minimal API usage

## 🔒 Security & Privacy

- **No External Dependencies**: No price APIs or web scraping
- **Local Data**: All portfolio data stored locally
- **Configurable Logging**: Control sensitive data logging
- **Environment Variables**: Secure credential management

## 🌍 Vietnamese Market Support

- **Local Exchanges**: HOSE, HNX, UPCoM support
- **Currency**: VND formatting and calculations
- **Market Hours**: Vietnamese timezone support
- **Sector Classification**: Vietnamese company sectors
- **Regulatory Awareness**: Local market regulations

## 📧 Email Templates

Professional HTML email templates included:

- **Daily Advisory**: Comprehensive portfolio analysis
- **Weekly Summary**: Performance overview and trends
- **Risk Alerts**: Important portfolio warnings
- **Scenario Reports**: What-if analysis results

## 🐳 Docker Deployment

```dockerfile
# Build and run with Docker
docker build -t vn-stock-advisory .
docker run -d \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/.env:/app/.env \
  --name vn-advisory \
  vn-stock-advisory
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: Support via configured email system

---

**Transform your Vietnamese stock portfolio with AI-powered insights - no data feeds required!** 🚀📈
