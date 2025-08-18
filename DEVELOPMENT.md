# VN Stock Advisory Notifier - Development Setup

## Development Environment Setup

### Prerequisites
- Python 3.6+ 
- pip package manager
- Git
- Google Gemini API access
- Email account with SMTP access

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd vn-stock-service
   ```

2. **Set up Python virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and email settings
   ```

5. **Test the setup**
   ```bash
   python3 main.py
   python3 test_gemini.py
   ```

## Development Workflow

### Running Tests
```bash
# Run all tests
python3 -m pytest tests/

# Run specific test
python3 -m pytest tests/test_advisory.py -v

# Test Gemini integration
python3 test_gemini.py
```

### Manual Testing
```bash
# Test system components
python3 main.py

# Run single advisory analysis
python3 run_manual.py

# Start scheduler (Ctrl+C to stop)
python3 run_scheduler.py
```

### Code Structure

- `src/adapters/` - Data provider interfaces and implementations
- `src/advisory/` - AI analysis engine and technical indicators
- `src/email_service/` - Email templates and sending logic
- `src/scheduler/` - Background task scheduling
- `src/config/` - Configuration management
- `data/` - Portfolio data files
- `tests/` - Unit tests and fixtures

### Adding New Features

1. **New Data Provider**: Implement `DataProviderInterface` in `src/adapters/`
2. **New Technical Indicators**: Add to `src/advisory/indicators.py`
3. **Email Template Changes**: Modify files in `src/email_service/templates/`
4. **New Analysis Logic**: Extend `src/advisory/engine.py`

### Environment Variables for Development

Create `.env` file with these settings:

```bash
# Development settings
DRY_RUN=true
LOG_LEVEL=DEBUG
VN_DATA_PROVIDER=mock

# AI Configuration (required)
LLM_PROVIDER=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
LLM_API_KEY=your_gemini_api_key

# Email Configuration (for testing)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
MAIL_TO=your_email@gmail.com

# Scheduling
SCHEDULE_CRON=30 7 * * *
TIMEZONE=Asia/Ho_Chi_Minh
```

### Debugging Tips

1. **Enable debug logging**: Set `LOG_LEVEL=DEBUG` in `.env`
2. **Use dry run mode**: Keep `DRY_RUN=true` during development
3. **Test with mock data**: Use `VN_DATA_PROVIDER=mock` for reliable testing
4. **Check logs**: Application logs provide detailed error information

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure all tests pass: `python3 -m pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Production Deployment

See main README.md for production deployment instructions using Docker or systemd.

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure you're in the project directory and virtual environment is activated
cd vn-stock-service
source venv/bin/activate
```

**API Errors**
```bash
# Test Gemini API connection
python3 test_gemini.py
```

**Email Issues**
```bash
# For Gmail, use App Passwords, not regular password
# Enable 2FA and generate app-specific password
```

**Dependencies Issues**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```
