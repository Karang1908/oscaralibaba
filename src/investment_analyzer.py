import pandas as pd
import numpy as np
from datetime import datetime
import logging
import yfinance as yf
import requests
from config.config import *
from .portfolio_monitor import PortfolioMonitor
from .news_analyzer import NewsAnalyzer

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class InvestmentAnalyzer:
    def __init__(self):
        self.portfolio_monitor = PortfolioMonitor()
        self.news_analyzer = NewsAnalyzer()
        # Initialize with global market indices for analysis
        self.market_indices = {
            'US': ['^GSPC', '^DJI', '^IXIC'],  # S&P 500, Dow Jones, NASDAQ
            'EU': ['^STOXX50E', '^GDAXI', '^FCHI'],  # Euro Stoxx 50, DAX, CAC 40
            'Asia': ['^N225', '^HSI', '000001.SS'],  # Nikkei 225, Hang Seng, Shanghai Composite
            'UK': ['^FTSE'],  # FTSE 100
            'Canada': ['^GSPTSE'],  # TSX Composite
            'Australia': ['^AXJO']  # ASX 200
        }
        self.market_data = self.get_market_overview()
        
    def get_market_overview(self):
        """Get global market overview data"""
        try:
            market_data = {}
            for region, indices in self.market_indices.items():
                market_data[region] = {}
                for index in indices:
                    try:
                        ticker = yf.Ticker(index)
                        info = ticker.history(period="1d")
                        if not info.empty:
                            market_data[region][index] = {
                                'price': info['Close'].iloc[-1],
                                'change': info['Close'].iloc[-1] - info['Open'].iloc[-1],
                                'change_percent': ((info['Close'].iloc[-1] - info['Open'].iloc[-1]) / info['Open'].iloc[-1]) * 100
                            }
                    except Exception as e:
                        logger.warning(f"Error fetching data for {index}: {e}")
                        continue
            return market_data
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return {}

    def update_market_data(self):
        """Update market overview data"""
        self.market_data = self.get_market_overview()
        return self.market_data

    def identify_unused_funds(self):
        """Identify unused cash based on spending patterns and thresholds"""
        try:
            # Get current cash balance
            current_balance = self.portfolio_monitor.get_cash_balance()
            
            # Calculate spending patterns
            spending_patterns = self.portfolio_monitor.calculate_spending_patterns()
            if not spending_patterns:
                # If no spending patterns, use default threshold
                monthly_average = 1500.0  # Default $1500 monthly spending
            else:
                monthly_average = spending_patterns['monthly_average']
            
            # Calculate threshold (50% above monthly spending)
            threshold = monthly_average * (1 + UNUSED_BALANCE_THRESHOLD)
            
            # Calculate unused funds (anything above 1 month of spending)
            safety_net = monthly_average * 1  # Keep 1 month of expenses as safety net
            unused_funds = current_balance - safety_net
            
            # Unused funds calculated: ${unused_funds:.2f}
            
            if unused_funds >= MIN_INVESTMENT_AMOUNT:  # Minimum investment amount in USD
                return {
                    'total_balance': current_balance,
                    'monthly_average': monthly_average,
                    'unused_funds': unused_funds,
                    'threshold': threshold,
                    'available_for_investment': unused_funds
                }
            return None
            
        except Exception as e:
            logger.error(f"Error identifying unused funds: {e}")
            return None

    def get_investment_suggestions(self, amount_usd, include_growth_stocks=False):
        """Get real-time global stock investment suggestions"""
        try:
            # Update market data before calculations
            self.update_market_data()
            
            # Define global stock symbols by region and category
            global_stocks = {
                'US_BlueChip': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'JNJ', 'PG'],
                'US_Growth': ['PLTR', 'ROKU', 'SQ', 'SHOP', 'ZM', 'NFLX', 'AMD', 'CRM', 'SNOW', 'COIN'],
                'EU_BlueChip': ['ASML', 'SAP', 'LVMH.PA', 'NVO', 'MC.PA', 'OR.PA', 'SAN.PA', 'TTE.PA'],
                'UK_BlueChip': ['SHEL.L', 'AZN.L', 'ULVR.L', 'BP.L', 'VOD.L', 'HSBA.L'],
                'Asia_BlueChip': ['TSM', 'BABA', '7203.T', '005930.KS', 'TM', '6758.T'],
                'Canada_BlueChip': ['SHOP.TO', 'RY.TO', 'TD.TO', 'CNR.TO', 'SU.TO'],
                'Australia_BlueChip': ['CBA.AX', 'BHP.AX', 'CSL.AX', 'WBC.AX']
            }
            
            # Select stocks based on preferences
            stock_symbols = []
            stock_symbols.extend(global_stocks['US_BlueChip'])
            stock_symbols.extend(global_stocks['EU_BlueChip'][:4])  # Top 4 EU stocks
            stock_symbols.extend(global_stocks['UK_BlueChip'][:3])  # Top 3 UK stocks
            stock_symbols.extend(global_stocks['Asia_BlueChip'][:4])  # Top 4 Asian stocks
            
            if include_growth_stocks:
                stock_symbols.extend(global_stocks['US_Growth'])
                stock_symbols.extend(global_stocks['Canada_BlueChip'][:3])
                stock_symbols.extend(global_stocks['Australia_BlueChip'][:2])
            
            suggestions = []
            
            for symbol in stock_symbols:
                try:
                    # Get stock data
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="30d")
                    info = ticker.info
                    
                    if hist.empty:
                        continue
                    
                    current_price = hist['Close'].iloc[-1]
                    
                    # Calculate daily return
                    daily_return = (current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]
                    
                    # Calculate volatility (30-day)
                    volatility = hist['Close'].pct_change().std() * np.sqrt(252)  # Annualized volatility
                    
                    # Determine stock category and region
                    stock_category = 'Blue Chip'
                    region = 'US'
                    currency = 'USD'
                    
                    for category, stocks in global_stocks.items():
                        if symbol in stocks:
                            if 'Growth' in category:
                                stock_category = 'Growth'
                            if 'EU' in category:
                                region = 'Europe'
                                currency = 'EUR'
                            elif 'UK' in category:
                                region = 'UK'
                                currency = 'GBP'
                            elif 'Asia' in category:
                                region = 'Asia'
                                currency = 'Local'
                            elif 'Canada' in category:
                                region = 'Canada'
                                currency = 'CAD'
                            elif 'Australia' in category:
                                region = 'Australia'
                                currency = 'AUD'
                            break
                    
                    is_growth_stock = stock_category == 'Growth'
                    
                    # Determine risk level based on volatility, stock type, and region
                    base_risk = 0
                    if is_growth_stock:
                        base_risk += 1
                    if region not in ['US', 'UK']:  # Add risk for emerging/foreign markets
                        base_risk += 0.5
                    
                    if volatility < 0.2:
                        risk_level = 'low' if base_risk < 1 else 'medium'
                    elif volatility < 0.3:
                        risk_level = 'medium' if base_risk < 1.5 else 'high'
                    elif volatility < 0.5:
                        risk_level = 'high'
                    else:
                        risk_level = 'extreme'
                    
                    risk_warning = None
                    if is_growth_stock:
                        risk_warning = "Growth stocks can be volatile and may experience significant price swings."
                    if region not in ['US', 'UK']:
                        risk_warning = (risk_warning or "") + f" International investments may involve currency and political risks."
                    
                    # Calculate how many shares can be bought
                    shares_affordable = int(amount_usd / current_price)
                    
                    suggestion = {
                        'symbol': symbol,
                        'company_name': info.get('longName', symbol),
                        'price': current_price,
                        'currency': currency,
                        'region': region,
                        'category': stock_category,
                        'sector': info.get('sector', 'N/A'),
                        'industry': info.get('industry', 'N/A'),
                        'risk_level': risk_level,
                        'daily_return': daily_return,
                        'volatility': volatility,
                        'volume': hist['Volume'].iloc[-1],
                        'market_cap': info.get('marketCap', 0),
                        'pe_ratio': info.get('trailingPE', 'N/A'),
                        'dividend_yield': info.get('dividendYield', 0),
                        'is_growth_stock': is_growth_stock,
                        'risk_warning': risk_warning,
                        'shares_affordable': shares_affordable,
                        'investment_amount': shares_affordable * current_price
                    }
                    
                    suggestions.append(suggestion)
                    
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
                    continue
            
            # Sort suggestions: Prioritize by performance, then diversify by region
            suggestions.sort(key=lambda x: (-x['daily_return'], x['region'], x['risk_level']))
            
            # Enhance with news sentiment analysis
            try:
                suggestions = self.enhance_suggestions_with_news(suggestions)
                logger.info("Enhanced investment suggestions with news sentiment analysis")
            except Exception as e:
                logger.warning(f"Could not enhance suggestions with news: {e}")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting investment suggestions: {e}")
            return []
    
    def get_regional_market_performance(self):
        """Get performance summary by region"""
        try:
            regional_performance = {}
            for region, indices in self.market_indices.items():
                if region in self.market_data:
                    total_change = 0
                    count = 0
                    for index, data in self.market_data[region].items():
                        total_change += data.get('change_percent', 0)
                        count += 1
                    
                    if count > 0:
                        regional_performance[region] = {
                            'avg_change_percent': total_change / count,
                            'trend': 'positive' if total_change > 0 else 'negative',
                            'indices_count': count
                        }
            
            return regional_performance
        except Exception as e:
            logger.error(f"Error getting regional performance: {e}")
            return {}

    def enhance_suggestions_with_news(self, suggestions):
        """Enhance investment suggestions with news sentiment analysis"""
        enhanced_suggestions = []
        
        for suggestion in suggestions:
            try:
                # Get news summary for the stock
                news_summary = self.news_analyzer.get_stock_news_summary(
                    suggestion['symbol'], 
                    suggestion.get('company_name', '')
                )
                
                # Add news data to suggestion
                suggestion['news_sentiment'] = news_summary['sentiment']
                suggestion['news_score'] = news_summary.get('sentiment_score', 0.0)
                suggestion['news_available'] = news_summary['news_available']
                suggestion['recent_headlines'] = news_summary.get('recent_headlines', [])
                
                # Adjust recommendation based on news sentiment
                if news_summary['sentiment'] == 'positive':
                    suggestion['recommendation_strength'] = min(suggestion.get('recommendation_strength', 0.5) + 0.1, 1.0)
                elif news_summary['sentiment'] == 'negative':
                    suggestion['recommendation_strength'] = max(suggestion.get('recommendation_strength', 0.5) - 0.1, 0.0)
                
                enhanced_suggestions.append(suggestion)
                
            except Exception as e:
                logger.warning(f"Could not get news for {suggestion['symbol']}: {e}")
                # Add default news data
                suggestion['news_sentiment'] = 'neutral'
                suggestion['news_score'] = 0.0
                suggestion['news_available'] = False
                suggestion['recent_headlines'] = []
                enhanced_suggestions.append(suggestion)
        
        return enhanced_suggestions

    def get_market_sentiment_analysis(self):
        """Get comprehensive market sentiment analysis"""
        try:
            market_sentiment = self.news_analyzer.get_market_sentiment()
            logger.info(f"Market sentiment analysis: {market_sentiment['overall_sentiment']}")
            return market_sentiment
        except Exception as e:
            logger.warning(f"Could not get market sentiment: {e}")
            return {
                'overall_sentiment': 'neutral',
                'overall_score': 0.0,
                'regional_sentiments': {},
                'timestamp': datetime.now().isoformat()
            }

    def get_stock_price(self, symbol):
        """Get current stock price in USD"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                return hist['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"Error fetching {symbol} price: {e}")
            return None

    def _get_risk_level(self, risk_score):
        """Convert risk score to risk level"""
        if risk_score < 0.1:
            return 'low'
        elif risk_score < 0.3:
            return 'medium'
        else:
            return 'high'

    def analyze_investment_opportunity(self, symbol, amount):
        """Analyze a specific stock investment opportunity"""
        try:
            # Get historical data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="90d")  # 3 months of data
            info = ticker.info
            
            if hist.empty:
                return None
            
            # Calculate technical indicators
            hist['sma_7'] = hist['Close'].rolling(window=7).mean()
            hist['sma_30'] = hist['Close'].rolling(window=30).mean()
            hist['rsi'] = self._calculate_rsi(hist['Close'])
            
            # Get current price
            current_price = hist['Close'].iloc[-1]
            
            # Calculate shares affordable
            shares_affordable = int(amount / current_price)
            
            # Generate analysis
            analysis = {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'current_price': current_price,
                'shares_affordable': shares_affordable,
                'investment_amount': shares_affordable * current_price,
                'trend': 'bullish' if hist['sma_7'].iloc[-1] > hist['sma_30'].iloc[-1] else 'bearish',
                'rsi': hist['rsi'].iloc[-1],
                'volatility': hist['Close'].pct_change().std() * np.sqrt(252),  # Annualized volatility
                'volume_trend': 'increasing' if hist['Volume'].iloc[-1] > hist['Volume'].mean() else 'decreasing',
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A')
            }
            
            # Add risk assessment
            analysis['risk_level'] = self._assess_risk(analysis)
            
            # Add recommendation
            analysis['recommendation'] = self._generate_recommendation(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing investment opportunity: {e}")
            return None

    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _assess_risk(self, analysis):
        """Assess risk level based on technical analysis"""
        risk_score = 0
        
        # Trend analysis
        risk_score += 1 if analysis['trend'] == 'bullish' else 2
        
        # RSI analysis
        if analysis['rsi'] > 70:
            risk_score += 2  # Overbought
        elif analysis['rsi'] < 30:
            risk_score += 0  # Oversold (potential opportunity)
        else:
            risk_score += 1
            
        # Volatility analysis (annualized)
        if analysis['volatility'] > 0.4:  # High volatility
            risk_score += 3
        elif analysis['volatility'] > 0.25:  # Medium volatility
            risk_score += 2
        else:
            risk_score += 1  # Low volatility
            
        # Volume analysis
        risk_score += 1 if analysis['volume_trend'] == 'increasing' else 2
        
        # Beta analysis (if available)
        if isinstance(analysis.get('beta'), (int, float)):
            if analysis['beta'] > 1.5:
                risk_score += 2
            elif analysis['beta'] > 1.0:
                risk_score += 1
        
        # Convert to risk level
        if risk_score <= 4:
            return 'low'
        elif risk_score <= 7:
            return 'medium'
        elif risk_score <= 10:
            return 'high'
        else:
            return 'extreme'
    
    def _generate_recommendation(self, analysis):
        """Generate investment recommendation based on analysis"""
        score = 0
        
        # Positive factors
        if analysis['trend'] == 'bullish':
            score += 2
        if analysis['rsi'] < 30:  # Oversold
            score += 2
        elif 30 <= analysis['rsi'] <= 70:  # Neutral RSI
            score += 1
        if analysis['volume_trend'] == 'increasing':
            score += 1
        if analysis['volatility'] < 0.25:  # Low volatility
            score += 1
        
        # Generate recommendation
        if score >= 6:
            return 'Strong Buy'
        elif score >= 4:
            return 'Buy'
        elif score >= 2:
            return 'Hold'
        else:
            return 'Sell'
    
    def get_portfolio_recommendations(self):
        """Get recommendations for the current portfolio"""
        try:
            holdings = self.portfolio_monitor.get_stock_holdings()
            recommendations = []
            
            for symbol, holding in holdings.items():
                analysis = self.analyze_investment_opportunity(symbol, holding['value'])
                if analysis:
                    recommendations.append({
                        'symbol': symbol,
                        'current_shares': holding['shares'],
                        'current_value': holding['value'],
                        'recommendation': analysis['recommendation'],
                        'risk_level': analysis['risk_level'],
                        'trend': analysis['trend']
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting portfolio recommendations: {e}")
            return []