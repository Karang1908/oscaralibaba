import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from src/config.env
src_dir = Path(__file__).parent.parent / 'src'
load_dotenv(src_dir / 'config.env')

# API Keys
# Qwen AI Configuration (uses OPENAI_API_KEY environment variable)
QWEN_API_KEY = os.getenv('OPENAI_API_KEY')
BLAND_AI_API_KEY = os.getenv('BLAND_AI_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# Google Search API Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

# Portfolio Configuration
BROKERAGE_ACCOUNT_ID = os.getenv('BROKERAGE_ACCOUNT_ID')
PORTFOLIO_VALUE = float(os.getenv('PORTFOLIO_VALUE', '10000'))  # Default $10,000

# Investment Parameters
UNUSED_BALANCE_THRESHOLD = 0.5  # 50% above average monthly spending
MIN_INVESTMENT_AMOUNT = 100  # Minimum amount to consider for investment
MAX_INVESTMENT_AMOUNT = 10000  # Maximum amount for a single investment

# Stock Market Configuration
STOCK_MARKET_HOURS = {
    'open': '09:30',
    'close': '16:00',
    'timezone': 'US/Eastern'
}

# Voice Call Configuration
CALLBACK_URL = os.getenv('CALLBACK_URL')
USER_PHONE_NUMBER = os.getenv('USER_PHONE_NUMBER')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/wallet_monitor.db')