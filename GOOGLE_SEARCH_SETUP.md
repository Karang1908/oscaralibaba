# Google Search API Setup Guide

This guide explains how to set up Google Search API integration for enhanced news sentiment analysis in the AI Investment System.

## Overview

The Google Search API integration provides:
- Real-time stock news sentiment analysis
- Market sentiment tracking across global regions
- Enhanced investment recommendations with news context
- Recent headlines for individual stocks

## Prerequisites

1. Google Cloud Platform account
2. Google Custom Search Engine
3. Google Search API credentials

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Custom Search API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Custom Search API"
   - Click "Enable"

### 2. Create API Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API Key"
3. Copy the generated API key
4. (Optional) Restrict the API key to Custom Search API for security

### 3. Set Up Custom Search Engine

1. Go to [Google Custom Search Engine](https://cse.google.com/cse/)
2. Click "Add" to create a new search engine
3. Configure your search engine:
   - **Sites to search**: Enter `*` to search the entire web
   - **Name**: Choose a descriptive name (e.g., "Investment News Search")
   - **Language**: Select your preferred language
4. Click "Create"
5. Copy the **Search Engine ID** from the setup page

### 4. Configure the Application

1. Open `src/config.env` file
2. Replace the placeholder values:
   ```env
   # Google Search API Configuration
   GOOGLE_API_KEY=your_actual_google_api_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_actual_search_engine_id_here
   ```

### 5. Test the Integration

Run the test script to verify everything is working:

```bash
source new_venv/bin/activate
python test_google_search.py
```

## Features Enabled

Once configured, the following features will be available:

### Stock News Sentiment
- Automatic news sentiment analysis for individual stocks
- Recent headlines for each investment suggestion
- Sentiment scores affecting recommendation strength

### Market Sentiment Analysis
- Global market sentiment tracking
- Regional sentiment analysis (US, EU, Asia)
- Market sentiment integration in investment calls

### Enhanced Investment Calls
- News sentiment included in call scripts
- Market context with recent news analysis
- More informed investment recommendations

## API Usage Limits

- Google Custom Search API has a free tier with 100 searches per day
- Additional searches require billing setup
- Monitor usage in Google Cloud Console

## Fallback Behavior

If Google Search API is not configured or fails:
- System continues to work with neutral sentiment
- Investment recommendations still function
- No news headlines will be available
- Market sentiment defaults to neutral

## Troubleshooting

### Common Issues

1. **"API key not valid" error**
   - Verify the API key is correct in `config.env`
   - Ensure Custom Search API is enabled in Google Cloud
   - Check API key restrictions

2. **"Search engine not found" error**
   - Verify the Search Engine ID is correct
   - Ensure the custom search engine is properly configured

3. **No search results**
   - Check if the search engine is set to search the entire web (`*`)
   - Verify the search engine is active

### Testing Individual Components

```python
# Test news analyzer directly
from src.news_analyzer import NewsAnalyzer
analyzer = NewsAnalyzer()
result = analyzer.get_stock_news_summary('AAPL', 'Apple Inc')
print(result)
```

## Security Considerations

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables for production
   - Restrict API key usage to specific APIs

2. **Rate Limiting**
   - Monitor API usage to avoid exceeding quotas
   - Implement caching for frequently requested data
   - Consider upgrading to paid tier for higher limits

## Cost Optimization

1. **Efficient Queries**
   - Cache news results for short periods
   - Limit the number of articles fetched
   - Use specific search terms to improve relevance

2. **Monitoring**
   - Set up billing alerts in Google Cloud
   - Monitor daily API usage
   - Review search query effectiveness

## Support

For issues with:
- **Google APIs**: Check [Google Cloud Support](https://cloud.google.com/support)
- **Custom Search**: See [Custom Search documentation](https://developers.google.com/custom-search)
- **Application Integration**: Review the test script and logs for debugging