# VN Stock Advisory Notifier

## Overview
The VN Stock Advisory Notifier is a background application designed to analyze your Vietnam stock holdings daily. It fetches market data, generates actionable advice using AI, and sends detailed email notifications for each stock as well as an overall portfolio summary.

## Features
- Daily analysis of stock holdings from HOSE, HNX, and UPCoM.
- AI-driven advisory for each stock based on current market data and user-defined parameters.
- Email notifications with detailed stock insights and portfolio overview.
- Configurable scheduling to run at a specified local time.
- Support for multiple data providers, including mock and real data sources.

## Project Structure
```
vn-stock-advisory
├── src
│   ├── app.py
│   ├── config
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── adapters
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── mock_provider.py
│   │   └── vn_data_provider.py
│   ├── advisory
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── indicators.py
│   │   └── ai_advisor.py
│   ├── email
│   │   ├── __init__.py
│   │   ├── sender.py
│   │   └── templates
│   │       ├── stock_detail.html
│   │       └── portfolio_overview.html
│   ├── scheduler
│   │   ├── __init__.py
│   │   └── jobs.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── holdings.py
│   │   └── market_data.py
│   └── utils
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── tests
│   ├── __init__.py
│   ├── test_adapters.py
│   ├── test_advisory.py
│   ├── test_email.py
│   └── fixtures
│       └── sample_holdings.json
├── data
│   └── holdings.json
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── deployment
│   ├── systemd
│   │   └── vn-stock-advisory.service
│   └── docker-deploy.sh
└── README.md
```

## Setup Instructions
1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd vn-stock-advisory
   ```

2. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Copy `.env.example` to `.env` and fill in the required values:
   ```
   VN_DATA_PROVIDER=mock|provider1
   SCHEDULE_CRON=30 7 * * *
   SMTP_HOST=<your_smtp_host>
   SMTP_PORT=<your_smtp_port>
   SMTP_USER=<your_smtp_user>
   SMTP_PASS=<your_smtp_password>
   MAIL_TO=<your_email>
   LLM_PROVIDER=<your_llm_provider>
   LLM_API_KEY=<your_llm_api_key>
   ```

4. **Run the Application**
   You can run the application locally using:
   ```
   python src/app.py
   ```

5. **Docker Deployment**
   To build and run the application using Docker:
   ```
   docker-compose up --build
   ```

## Environment Variables
- `VN_DATA_PROVIDER`: Specifies the data provider to use (mock or real).
- `SCHEDULE_CRON`: Cron expression for scheduling the daily analysis.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`: SMTP configuration for sending emails.
- `MAIL_TO`: Email address for receiving notifications.
- `LLM_PROVIDER`, `LLM_API_KEY`: Configuration for the AI model provider.

## Troubleshooting Tips
- Ensure all environment variables are set correctly.
- Check the logs for any errors during execution.
- If using a real data provider, verify API access and permissions.

## Contribution
Feel free to contribute to the project by submitting issues or pull requests. Your feedback and suggestions are welcome!

## License
This project is licensed under the MIT License. See the LICENSE file for more details.