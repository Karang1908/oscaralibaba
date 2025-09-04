import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from config.config import *

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockPortfolio:
    def __init__(self, initial_cash=50000.0):
        self.initial_cash = initial_cash  # Store initial cash balance
        self.cash_balance = initial_cash  # Current cash balance in USD
        self.holdings = {}  # Stock holdings {symbol: shares}
        self.transactions = []
        self._last_reset_time = datetime.now()  # Initialize last reset time
        self._generate_initial_transactions()
        self._generate_initial_holdings()

    def _generate_initial_holdings(self):
        """Generate initial stock holdings for the mock portfolio"""
        # Start with some diversified holdings
        initial_stocks = {
            'AAPL': 5,   # 5 shares of Apple
            'MSFT': 3,   # 3 shares of Microsoft
            'GOOGL': 2,  # 2 shares of Google
            'TSLA': 1,   # 1 share of Tesla
            'SPY': 10    # 10 shares of S&P 500 ETF
        }
        self.holdings = initial_stocks
        
        # Log initial holdings
        for symbol, shares in initial_stocks.items():
            self.transactions.append({
                'id': f'initial_{symbol}',
                'symbol': symbol,
                'action': 'buy',
                'shares': shares,
                'price': self._get_mock_price(symbol),
                'timestamp': datetime.now() - timedelta(days=30),
                'total_value': shares * self._get_mock_price(symbol)
            })

    def _get_mock_price(self, symbol):
        """Get mock stock prices for simulation"""
        mock_prices = {
            'AAPL': 175.50,
            'MSFT': 380.25,
            'GOOGL': 140.75,
            'TSLA': 245.30,
            'SPY': 450.80,
            'NVDA': 875.20,
            'AMZN': 155.40,
            'META': 485.60,
            'NFLX': 425.90,
            'AMD': 142.35
        }
        return mock_prices.get(symbol, 100.0)  # Default to $100 if symbol not found

    def _generate_initial_transactions(self):
        """Generate initial transaction history for the mock portfolio"""
        start_date = datetime.now() - timedelta(days=30)
        
        # Generate some dividend payments and small trades
        for i in range(10):
            date = start_date + timedelta(days=i * 3)
            
            # Simulate dividend payments
            if np.random.random() > 0.7:
                dividend_amount = np.random.uniform(25.0, 150.0)
                self.transactions.append({
                    'id': f'dividend_{i}',
                    'symbol': 'DIVIDEND',
                    'action': 'dividend',
                    'shares': 0,
                    'price': 0,
                    'timestamp': date,
                    'total_value': dividend_amount
                })
            
            # Simulate small stock purchases/sales
            if np.random.random() > 0.6:
                symbols = ['AAPL', 'MSFT', 'GOOGL', 'SPY']
                symbol = np.random.choice(symbols)
                shares = np.random.randint(1, 3)
                action = np.random.choice(['buy', 'sell'])
                price = self._get_mock_price(symbol) * np.random.uniform(0.95, 1.05)
                
                self.transactions.append({
                    'id': f'trade_{i}',
                    'symbol': symbol,
                    'action': action,
                    'shares': shares,
                    'price': price,
                    'timestamp': date,
                    'total_value': shares * price
                })

    def get_portfolio_value(self):
        """Get total portfolio value (cash + holdings)"""
        holdings_value = sum(
            shares * self._get_mock_price(symbol) 
            for symbol, shares in self.holdings.items()
        )
        total_value = self.cash_balance + holdings_value
        logger.info(f"Portfolio value: ${total_value:.2f} (Cash: ${self.cash_balance:.2f}, Holdings: ${holdings_value:.2f})")
        return total_value

    def get_cash_balance(self):
        """Get current cash balance"""
        return self.cash_balance

    def get_holdings(self):
        """Get current stock holdings with values"""
        holdings_with_values = {}
        for symbol, shares in self.holdings.items():
            price = self._get_mock_price(symbol)
            holdings_with_values[symbol] = {
                'shares': shares,
                'price': price,
                'value': shares * price
            }
        return holdings_with_values

    def get_transaction_history(self, days=30):
        """Get transaction history"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        filtered_transactions = [
            tx for tx in self.transactions
            if start_date <= tx['timestamp'] <= end_date
        ]
        
        return pd.DataFrame(filtered_transactions)

    def calculate_spending_patterns(self, days=30):
        """Calculate spending patterns from stock transactions"""
        transactions = self.get_transaction_history(days)
        if transactions.empty:
            return None
        
        # Only consider buy transactions and dividend reinvestments for spending patterns
        spending_transactions = transactions[
            (transactions['action'] == 'buy') | 
            (transactions['action'] == 'dividend_reinvest')
        ]
        
        if spending_transactions.empty:
            return {
                'daily_average': 50.0,
                'weekly_average': 350.0,
                'monthly_average': 1500.0
            }
        
        daily_spending = spending_transactions.groupby(
            spending_transactions['timestamp'].dt.date
        )['total_value'].sum()
        
        weekly_spending = spending_transactions.groupby(
            spending_transactions['timestamp'].dt.isocalendar().week
        )['total_value'].sum()
        
        return {
            'daily_average': daily_spending.mean() if not daily_spending.empty else 150.0,
            'weekly_average': weekly_spending.mean() if not weekly_spending.empty else 1050.0,
            'monthly_average': (daily_spending.mean() * 30) if not daily_spending.empty else 4500.0
        }

    def update_cash_balance(self, new_balance):
        """Update the cash balance"""
        self.cash_balance = new_balance
        logger.info(f"Updated cash balance to: ${self.cash_balance:.2f}")

    def add_transaction(self, symbol, action, shares, price=None):
        """Add a new transaction (buy/sell/dividend)"""
        if price is None:
            price = self._get_mock_price(symbol)
        
        total_value = shares * price if action in ['buy', 'sell'] else shares  # For dividends, shares is the amount
        
        transaction = {
            'id': f'manual_{len(self.transactions)}',
            'symbol': symbol,
            'action': action,
            'shares': shares,
            'price': price,
            'timestamp': datetime.now(),
            'total_value': total_value
        }
        self.transactions.append(transaction)
        
        # Update holdings and cash based on action
        if action == 'buy':
            self.cash_balance -= total_value
            self.holdings[symbol] = self.holdings.get(symbol, 0) + shares
        elif action == 'sell':
            self.cash_balance += total_value
            self.holdings[symbol] = max(0, self.holdings.get(symbol, 0) - shares)
        elif action == 'dividend':
            self.cash_balance += total_value
        
        logger.info(f"Added transaction: {action} {shares} shares of {symbol} at ${price:.2f}")
        logger.info(f"New cash balance: ${self.cash_balance:.2f}")

    def get_idle_cash(self):
        """Calculate idle cash that could be invested"""
        # Consider cash above 1 month of average spending as idle
        spending_patterns = self.calculate_spending_patterns()
        if not spending_patterns:
            return max(0, self.cash_balance - 1000)  # Keep $1000 as emergency fund
        
        monthly_spending = spending_patterns['monthly_average']
        emergency_fund = monthly_spending * 1  # 1 month of expenses only
        idle_cash = max(0, self.cash_balance - emergency_fund)
        
        logger.info(f"Cash balance: ${self.cash_balance:.2f}, Monthly spending: ${monthly_spending:.2f}, Emergency fund: ${emergency_fund:.2f}, Idle cash: ${idle_cash:.2f}")
        return idle_cash