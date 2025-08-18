# Changelog

All notable changes to the VN Stock Advisory Notifier will be documented in this file.

## [1.2.0] - 2025-08-18

### Added
- **Enhanced AI Portfolio Advisory**: Comprehensive portfolio insights including risk analysis, performance insights, strategic recommendations, and Vietnam market context
- **AI Fallback for Price Data**: Intelligent fallback system using Google Gemini AI when SSI and CafeF APIs fail
- **Improved Email Templates**: Beautiful new sections in portfolio overview emails with AI insights
- **Risk Scoring**: Portfolio risk analysis with 1-10 scoring system
- **Market Context Analysis**: Vietnam-specific market outlook and sector trend analysis
- **Strategic Recommendations**: Immediate actions, rebalancing advice, and market timing suggestions

### Enhanced
- **Portfolio Advisory Prompt**: More sophisticated AI prompts for better portfolio analysis
- **Error Handling**: Robust fallback chain for data retrieval (SSI → CafeF → AI → Basic estimates)
- **Email Styling**: Enhanced CSS for better visual presentation of AI insights
- **Documentation**: Comprehensive README and development guides

### Technical Improvements
- **AI Response Processing**: Better parsing and validation of Gemini AI responses
- **Data Provider Architecture**: Improved provider factory with multiple fallback options
- **Template Engine**: Enhanced Jinja2 templates with conditional rendering for AI insights
- **Configuration Management**: Better environment variable handling and validation

## [1.1.0] - 2025-01-21

### Added
- **Google Gemini AI Integration**: Complete migration from OpenAI to Google Gemini AI
- **SSI API Integration**: Primary data source using SSI FastConnect API
- **CafeF Fallback**: Web scraping fallback when SSI API fails
- **Portfolio Management**: JSON-based portfolio configuration
- **Email Notifications**: HTML email templates for stocks and portfolio overview
- **Scheduling System**: APScheduler with cron-style scheduling
- **Docker Support**: Complete containerization with Docker Compose

### Features
- **Technical Analysis**: RSI, MACD, SMA indicators
- **Risk Management**: Stop-loss suggestions and position sizing
- **Multiple Data Providers**: Pluggable architecture for different data sources
- **Timezone Support**: Asia/Ho_Chi_Minh timezone handling
- **Dry Run Mode**: Safe testing without sending real emails

### Infrastructure
- **Production Ready**: Systemd service files for Linux deployment
- **Logging**: Structured logging with configurable levels
- **Configuration**: Environment-based configuration management
- **Testing**: Comprehensive test suite with mock data

## [1.0.0] - 2024-12-01

### Initial Release
- **Basic Stock Analysis**: Simple stock advisory system
- **Mock Data Provider**: Testing infrastructure
- **Basic Email Templates**: Simple HTML email notifications
- **Core Architecture**: Modular design with adapters, advisory engine, and email service

---

## Planned Features

### [1.3.0] - Future
- **Real-time Alerts**: WebSocket integration for real-time price alerts
- **Mobile App**: Companion mobile application
- **Advanced Charts**: Technical analysis charts in emails
- **Multi-currency Support**: Support for USD and other currencies
- **Machine Learning**: Predictive models for stock movements

### [1.4.0] - Future
- **Portfolio Optimization**: Modern Portfolio Theory implementation
- **Backtesting**: Historical performance analysis
- **Social Sentiment**: Integration with social media sentiment analysis
- **API Endpoints**: RESTful API for third-party integrations
