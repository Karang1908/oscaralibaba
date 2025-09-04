import pandas as pd
from datetime import datetime, timedelta
import logging
import yfinance as yf
from config.config import *
from .mock_portfolio import MockPortfolio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioMonitor:
    def __init__(self):
        # Initialize mock portfolio instead of real connections
        self.mock_portfolio = MockPortfolio(initial_cash=50000.0)  # Start with $50,000
        
    def get_cash_balance(self):
        """Get cash balance from mock portfolio"""
        return self.mock_portfolio.get_cash_balance()

    def get_stock_holdings(self):
        """Get stock holdings from mock portfolio"""
        return self.mock_portfolio.get_holdings()

    def get_portfolio_value(self):
        """Get total portfolio value (cash + holdings)"""
        return self.mock_portfolio.get_portfolio_value()

    def get_transaction_history(self, days=30):
        """Get transaction history from mock portfolio"""
        return self.mock_portfolio.get_transaction_history(days)

    def calculate_spending_patterns(self, days=30):
        """Calculate spending patterns from mock portfolio"""
        return self.mock_portfolio.calculate_spending_patterns(days)

    def update_cash_balance(self, new_balance):
        """Update the mock portfolio cash balance"""
        self.mock_portfolio.update_cash_balance(new_balance)

    def add_transaction(self, symbol, action, shares, price=None):
        """Add a new transaction to the mock portfolio"""
        self.mock_portfolio.add_transaction(symbol, action, shares, price)

    def get_stock_price(self, symbol):
        """Get real-time stock price using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
            else:
                logger.warning(f"No data found for symbol: {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_market_data(self, symbols, period="1mo"):
        """Get market data for multiple stocks"""
        try:
            data = yf.download(symbols, period=period, group_by='ticker')
            return data
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None

    def calculate_portfolio_performance(self, days=30):
        """Calculate portfolio performance metrics"""
        try:
            # Get current portfolio value
            current_value = self.get_portfolio_value()
            
            # Calculate performance based on transaction history
            transactions = self.get_transaction_history(days)
            if transactions.empty:
                return {
                    'total_return': 0.0,
                    'daily_return': 0.0,
                    'volatility': 0.0
                }
            
            # Simple performance calculation
            initial_value = self.mock_portfolio.initial_cash
            total_return = ((current_value - initial_value) / initial_value) * 100
            daily_return = total_return / days
            
            return {
                'total_return': total_return,
                'daily_return': daily_return,
                'current_value': current_value,
                'initial_value': initial_value
            }
        except Exception as e:
            logger.error(f"Error calculating portfolio performance: {e}")
            return None

    def get_idle_cash(self):
        """Get idle cash that could be invested"""
        return self.mock_portfolio.get_idle_cash()

    def analyze_diversification(self):
        """Analyze portfolio diversification"""
        holdings = self.get_stock_holdings()
        if not holdings:
            return None
        
        total_value = sum(holding['value'] for holding in holdings.values())
        diversification = {}
        
        for symbol, holding in holdings.items():
            percentage = (holding['value'] / total_value) * 100
            diversification[symbol] = {
                'percentage': percentage,
                'value': holding['value'],
                'shares': holding['shares']
            }
        
        return diversification