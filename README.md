# AI Stock Portfolio Monitor

An intelligent system that monitors stock portfolio balances, identifies unused cash, and suggests stock investment opportunities through voice calls.

## Features

- Real-time monitoring of stock portfolio and cash balances
- Analysis of spending patterns to identify unused cash
- Stock investment suggestions based on market data and technical analysis
- Voice interaction using Bland AI and Gemini AI
- Automated stock investment execution based on user commands

## Prerequisites

- Python 3.8+
- API keys for:
  - Gemini AI
  - Bland AI
  - Alpha Vantage (Stock Market Data)
  - Yahoo Finance (Free stock data)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-stock-portfolio-monitor.git
cd ai-stock-portfolio-monitor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
BLAND_AI_API_KEY=your_bland_ai_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
BROKERAGE_ACCOUNT_ID=your_brokerage_account_id
PORTFOLIO_VALUE=your_initial_portfolio_value
CALLBACK_URL=your_webhook_url
USER_PHONE_NUMBER=your_phone_number
```

## Usage

1. Start the application:
```bash
python src/main.py
```

2. The system will:
   - Monitor your stock portfolio and cash balances daily
   - Identify unused cash based on spending patterns
   - Generate stock investment suggestions when unused cash is detected
   - Initiate voice calls to discuss stock investment opportunities
   - Execute stock investments based on your voice commands

## Project Structure

```
ai_stock_portfolio_monitor/
├── config/
│   └── config.py           # Configuration and environment variables
├── src/
│   ├── main.py            # Main application and Flask server
│   ├── portfolio_monitor.py  # Stock portfolio balance monitoring
│   ├── investment_analyzer.py  # Stock investment analysis
│   ├── voice_interaction.py    # Voice call handling
│   └── mock_portfolio.py      # Portfolio simulation for testing
├── tests/                 # Test files
├── data/                  # Data storage
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Configuration

You can adjust various parameters in `config/config.py`:

- `UNUSED_BALANCE_THRESHOLD`: Percentage above average spending to consider cash as unused
- `MIN_INVESTMENT_AMOUNT`: Minimum amount to consider for stock investment
- `MAX_INVESTMENT_AMOUNT`: Maximum amount for a single stock investment
- `ALPHA_VANTAGE_API_KEY`: Alpha Vantage API key for stock market data
- `STOCK_MARKET_HOURS`: Trading hours configuration

## Security

- Brokerage account credentials are stored securely and never exposed
- API keys are managed through environment variables
- All stock transactions require voice confirmation
- Investment amounts are capped to prevent large unauthorized transactions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided for educational purposes only. Use at your own risk. The developers are not responsible for any financial losses incurred through the use of this software.