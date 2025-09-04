import os
import logging
import requests
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from config.config import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class NewsAnalyzer:
    def __init__(self):
        self.search_engine_id = GOOGLE_SEARCH_ENGINE_ID
        self.service = None
        
        # Initialize Google Search API if credentials are available
        if GOOGLE_API_KEY and GOOGLE_API_KEY != 'your_google_api_key_here':
            try:
                self.service = build('customsearch', 'v1', developerKey=GOOGLE_API_KEY)
                logger.info("Google Search API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google Search API: {e}")
                self.service = None
                logger.info("Using fallback sentiment analysis")
        else:
            logger.info("Google Search API not configured - using fallback sentiment analysis")
    
    def search_stock_news(self, symbol, company_name=None, days_back=7):
        """Search for recent news about a specific stock"""
        if not self.service:
            logger.info(f"Using fallback mode for {symbol} news (Google Search API disabled)")
            return []
        
        try:
            # Create search query
            company_term = company_name if company_name else symbol
            query = f"{symbol} {company_term} stock news"
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            date_restrict = f"d{days_back}"
            
            # Perform search
            result = self.service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=10,
                dateRestrict=date_restrict,
                sort='date'
            ).execute()
            
            news_items = []
            if 'items' in result:
                for item in result['items']:
                    news_items.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'link': item.get('link', ''),
                        'source': item.get('displayLink', ''),
                        'date': item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time', '')
                    })
            
            logger.info(f"Found {len(news_items)} news articles for {symbol}")
            return news_items
            
        except Exception as e:
            logger.error(f"Error searching news for {symbol}: {e}")
            return []
    
    def search_market_news(self, market_type="global", days_back=3):
        """Search for general market news"""
        if not self.service:
            logger.info(f"Using fallback mode for {market_type} market news (Google Search API disabled)")
            return []
        
        try:
            # Create market-specific search queries
            market_queries = {
                'global': 'global stock market news financial markets',
                'us': 'US stock market NYSE NASDAQ S&P 500 Dow Jones',
                'eu': 'European stock market FTSE DAX CAC 40 Euro Stoxx',
                'asia': 'Asian stock market Nikkei Hang Seng Shanghai Composite'
            }
            
            query = market_queries.get(market_type, market_queries['global'])
            date_restrict = f"d{days_back}"
            
            # Perform search
            result = self.service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=8,
                dateRestrict=date_restrict,
                sort='date'
            ).execute()
            
            news_items = []
            if 'items' in result:
                for item in result['items']:
                    news_items.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'link': item.get('link', ''),
                        'source': item.get('displayLink', ''),
                        'date': item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time', '')
                    })
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error searching {market_type} market news: {e}")
            return []
    
    def analyze_sentiment(self, news_items):
        """Analyze sentiment of news items (basic keyword-based analysis)"""
        positive_keywords = [
            'growth', 'profit', 'gain', 'rise', 'increase', 'bullish', 'optimistic',
            'strong', 'beat', 'exceed', 'outperform', 'upgrade', 'buy', 'positive',
            'rally', 'surge', 'boom', 'recovery', 'expansion'
        ]
        
        negative_keywords = [
            'loss', 'decline', 'fall', 'drop', 'bearish', 'pessimistic', 'weak',
            'miss', 'underperform', 'downgrade', 'sell', 'negative', 'crash',
            'plunge', 'recession', 'crisis', 'concern', 'risk', 'volatility'
        ]
        
        sentiment_scores = []
        
        for item in news_items:
            text = (item.get('title', '') + ' ' + item.get('snippet', '')).lower()
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in text)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text)
            
            if positive_count > negative_count:
                sentiment = 'positive'
                score = min(positive_count - negative_count, 5) / 5.0
            elif negative_count > positive_count:
                sentiment = 'negative'
                score = -min(negative_count - positive_count, 5) / 5.0
            else:
                sentiment = 'neutral'
                score = 0.0
            
            sentiment_scores.append({
                'title': item.get('title', ''),
                'sentiment': sentiment,
                'score': score,
                'source': item.get('source', '')
            })
        
        # Calculate overall sentiment
        if sentiment_scores:
            avg_score = sum(item['score'] for item in sentiment_scores) / len(sentiment_scores)
            if avg_score > 0.2:
                overall_sentiment = 'positive'
            elif avg_score < -0.2:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
        else:
            overall_sentiment = 'neutral'
            avg_score = 0.0
        
        return {
            'overall_sentiment': overall_sentiment,
            'average_score': avg_score,
            'individual_scores': sentiment_scores,
            'total_articles': len(sentiment_scores)
        }
    
    def get_stock_news_summary(self, symbol, company_name=None):
        """Get comprehensive news summary for a stock"""
        news_items = self.search_stock_news(symbol, company_name)
        
        if not news_items:
            return {
                'symbol': symbol,
                'news_available': False,
                'sentiment': 'neutral',
                'sentiment_score': 0.0,
                'total_articles': 0,
                'recent_headlines': [],
                'summary': 'No recent news found'
            }
        
        sentiment_analysis = self.analyze_sentiment(news_items)
        
        # Create summary
        recent_headlines = [item['title'] for item in news_items[:3]]
        
        return {
            'symbol': symbol,
            'news_available': True,
            'sentiment': sentiment_analysis['overall_sentiment'],
            'sentiment_score': sentiment_analysis['average_score'],
            'total_articles': sentiment_analysis['total_articles'],
            'recent_headlines': recent_headlines,
            'summary': f"Found {len(news_items)} recent articles with {sentiment_analysis['overall_sentiment']} sentiment"
        }
    
    def get_market_sentiment(self):
        """Get overall market sentiment from recent news"""
        market_types = ['global', 'us', 'eu', 'asia']
        market_sentiments = {}
        
        for market in market_types:
            news_items = self.search_market_news(market)
            if news_items:
                sentiment_analysis = self.analyze_sentiment(news_items)
                market_sentiments[market] = {
                    'sentiment': sentiment_analysis['overall_sentiment'],
                    'score': sentiment_analysis['average_score'],
                    'articles_count': len(news_items)
                }
            else:
                market_sentiments[market] = {
                    'sentiment': 'neutral',
                    'score': 0.0,
                    'articles_count': 0
                }
        
        # Calculate overall market sentiment
        all_scores = [data['score'] for data in market_sentiments.values() if data['articles_count'] > 0]
        if all_scores:
            overall_score = sum(all_scores) / len(all_scores)
            if overall_score > 0.1:
                overall_sentiment = 'positive'
            elif overall_score < -0.1:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
        else:
            overall_sentiment = 'neutral'
            overall_score = 0.0
        
        return {
            'overall_sentiment': overall_sentiment,
            'overall_score': overall_score,
            'regional_sentiments': market_sentiments,
            'timestamp': datetime.now().isoformat()
        }