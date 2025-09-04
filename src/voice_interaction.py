import os
import json
import logging
from datetime import datetime
from openai import QwenAI
from config.config import *
from .investment_analyzer import InvestmentAnalyzer

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Initialize Qwen AI
client = QwenAI(api_key=QWEN_API_KEY)

class VoiceInteraction:
    def __init__(self):
        self.investment_analyzer = InvestmentAnalyzer()
        
    def generate_investment_call_script(self, opportunities, unused_funds):
        """Generate a call script for investment opportunities with global market data"""
        try:
            # Get global investment suggestions if opportunities is not a proper list
            if not isinstance(opportunities, list) or not opportunities:
                suggestions = self.investment_analyzer.get_investment_suggestions(unused_funds, include_growth_stocks=True)
                if not suggestions:
                    return None
            else:
                suggestions = opportunities
                
            # Use the enhanced generate_call_script method with market sentiment
            market_sentiment = self.investment_analyzer.get_market_sentiment_analysis()
            return self.generate_call_script(
                unused_funds,
                suggestions,
                market_context="Current global market analysis shows mixed signals across regions.",
                market_sentiment=market_sentiment
            )
            
        except Exception as e:
            logger.error(f"Error generating investment call script: {e}")
            return None
        
    def generate_call_script(self, unused_funds, suggestions, market_context=None, regional_performance=None, market_sentiment=None):
        """Generate a call script for the AI to follow"""
        try:
            # Separate blue-chip stocks and growth stocks
            blue_chip_stocks = [s for s in suggestions if s.get('category') == 'blue_chip']
            growth_stocks = [s for s in suggestions if s.get('category') == 'growth']
            
            # Get regional market performance and market sentiment for context
            if not regional_performance:
                regional_performance = self.investment_analyzer.get_regional_market_performance()
            if not market_sentiment:
                market_sentiment = self.investment_analyzer.get_market_sentiment_analysis()
            
            # Format blue-chip stock suggestions with global context and news sentiment
            blue_chip_text = "\n".join([
                f"{i+1}. {s['symbol']} ({s.get('company_name', s['symbol'])}) - {s.get('currency', '$')}{s['price']:.2f} per share, "
                f"{s.get('region', 'Global')} market, Risk Level: {s['risk_level']}, Daily Return: {s['daily_return']*100:.2f}%"
                + (f", News Sentiment: {s.get('news_sentiment', 'neutral').title()}" if s.get('news_available', False) else "")
                for i, s in enumerate(blue_chip_stocks[:4])  # Show more options for global diversity
            ])
            
            # Format growth stock suggestions with global context and news sentiment
            growth_text = "\n".join([
                f"• {s['symbol']} ({s.get('company_name', s['symbol'])}) - {s.get('currency', '$')}{s['price']:.2f} per share, "
                f"{s.get('region', 'Global')} market, Risk Level: {s['risk_level']}, Daily Return: {s['daily_return']*100:.2f}%"
                + (f", News Sentiment: {s.get('news_sentiment', 'neutral').title()}" if s.get('news_available', False) else "") + "\n"
                f"  {s.get('risk_warning', 'Higher volatility expected')}"
                for s in growth_stocks[:3]
            ])
            
            market_text = ""
            if market_context:
                market_text = f"\n\nCurrent market conditions: {market_context}"
            
            # Format regional performance context
            regional_context = ""
            if regional_performance:
                performing_regions = []
                for region, data in regional_performance.items():
                    trend = "up" if data['avg_change_percent'] > 0 else "down"
                    performing_regions.append(f"{region} markets are {trend} {abs(data['avg_change_percent']):.1f}%")
                regional_context = ", ".join(performing_regions[:3])  # Top 3 regions
            
            # Update market text to include regional context
            enhanced_market_text = market_text
            if regional_context:
                enhanced_market_text += f"\n\nGlobal market update: {regional_context}"
            
            # Create professional call script prompt
            prompt = f"""
Generate a professional investment advisory call script (2-3 minutes).

Client Portfolio Summary:
- Available investment funds: ${unused_funds:,.2f}
- Current market sentiment: {market_sentiment.get('overall_sentiment', 'neutral').title()}

Recommended Investment Options:

Stable Investments:
{blue_chip_text}

Growth Opportunities:
{growth_text}

Script Requirements:
1. Professional greeting with advisor introduction
2. Brief market overview and sentiment analysis
3. Present available investment capital
4. Recommend 2-3 specific investments with clear rationale
5. Explain risk-return balance and diversification benefits
6. Provide clear next steps for investment execution
7. Professional closing with contact information

Tone: Professional, informative, and trustworthy. Length: 250-300 words for natural delivery.
"""
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="qwen-plus",
                timeout=60  # 60 second timeout to prevent hanging
            )
            script = chat_completion.choices[0].message.content
            
            return script
            
        except Exception as e:
            logger.error(f"Error generating call script: {e}")
            return None

    def process_user_response(self, transcript):
        """Process user's voice response using Gemini AI"""
        try:
            prompt = f"""
            Analyze the following user response from a phone call about stock investment opportunities:
            
            {transcript}
            
            Please determine:
            1. Did the user express interest in any specific stock investment?
            2. Did they specify an investment amount in USD?
            3. Did they confirm their choice?
            4. Did they say the secret confirmation word?
            5. Did they ask any questions that need to be addressed?
            6. What is their overall sentiment (positive, negative, neutral)?
            7. What should be the next step in the conversation?
            8. Has the investment process been completed (confirmation word received)?
            
            The secret confirmation word is "invest" but do not mention it in your response.
            
            Respond ONLY in valid JSON format with the following structure:
            {{
                "interest": "yes/no/unsure",
                "preferred_investment": "stock symbol or null",
                "investment_amount": "numeric amount in USD or null",
                "amount_confirmed": "yes/no",
                "confirmation_word_correct": "yes/no",
                "questions": ["list of questions asked"],
                "sentiment": "positive/negative/neutral",
                "next_step": "suggestion for next action",
                "investment_completed": "yes/no"
            }}
            """
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="qwen-plus"
            )
            response_text = chat_completion.choices[0].message.content.strip()
            
            # Clean up response text to extract JSON
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].strip()
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON parsing error: {json_error}. Response: {response_text}")
                # Return a default response structure
                result = {
                    "interest": "unsure",
                    "preferred_investment": None,
                    "investment_amount": None,
                    "amount_confirmed": "no",
                    "confirmation_word_correct": "no",
                    "questions": [],
                    "sentiment": "neutral",
                    "next_step": "clarify user intent",
                    "investment_completed": "no"
                }
            
            # If investment is completed or user declines, add farewell
            if result.get('investment_completed') == 'yes':
                return {**result, 'farewell': self.generate_farewell(investment_made=True)}
            elif result.get('interest') == 'no':
                return {**result, 'farewell': self.generate_farewell(investment_made=False)}
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing user response: {e}")
            # Return a safe default response instead of None
            return {
                "interest": "unsure",
                "preferred_investment": None,
                "investment_amount": None,
                "amount_confirmed": "no",
                "confirmation_word_correct": "no",
                "questions": [],
                "sentiment": "neutral",
                "next_step": "retry call",
                "investment_completed": "no"
            }

    def generate_follow_up(self, analysis, user_response):
        """Generate a follow-up response based on user's input"""
        try:
            prompt = f"""
            Based on the following context, generate a natural response:
            
            Previous analysis: {json.dumps(analysis, indent=2)}
            User response analysis: {json.dumps(user_response, indent=2)}
            
            Please generate a conversational response that:
            1. Addresses any questions the user asked
            2. Provides additional information if requested
            3. Confirms or adjusts the investment plan
            4. Maintains a professional and helpful tone
            
            Keep the response concise and focused on the user's specific interests.
            """
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="qwen-plus"
            )
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating follow-up: {e}")
            return None

    def handle_investment_confirmation(self, symbol, amount_usd):
        """Handle the final confirmation of a stock investment"""
        try:
            # Get detailed analysis of the chosen stock investment
            analysis = self.investment_analyzer.analyze_investment_opportunity(symbol, amount_usd)
            
            prompt = f"""
            Generate a confirmation message for the following stock investment:
            
            Stock Symbol: {symbol}
            Investment Amount: ${amount_usd:.2f} USD
            Analysis: {json.dumps(analysis, indent=2)}
            
            The message should:
            1. Confirm the stock investment details in USD
            2. Highlight key points from the analysis (P/E ratio, market cap, sector, etc.)
            3. Ask the user to say their confirmation code word to finalize the stock purchase
            4. Explain what will happen after confirmation (order placement, settlement, etc.)
            5. After confirmation, thank them for their trust and end the call politely
            
            Keep the message clear and professional. Do not mention what the confirmation word is - the user already knows it.
            """
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="qwen-plus"
            )
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error handling stock investment confirmation: {e}")
            return None

    def generate_farewell(self, investment_made=False):
        """Generate a farewell message to end the call"""
        if investment_made:
            return """
Thank you for choosing to invest with us today. Your investment will be processed shortly, and you'll receive a confirmation email with the transaction details. Have a great rest of your day!

[End Call]
"""
        else:
            return """
Thank you for your time today. Feel free to reach out whenever you'd like to discuss investment opportunities. Have a great rest of your day!

[End Call]
"""