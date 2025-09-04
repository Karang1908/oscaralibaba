import time
from src.portfolio_monitor import PortfolioMonitor
from src.investment_analyzer import InvestmentAnalyzer
from src.voice_interaction import VoiceInteraction
from src.conversation_logger import ConversationLogger
import requests
import logging
from config.config import *
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_bland_ai_call(script):
    """Make a call using Bland AI"""
    try:
        url = "https://api.bland.ai/v1/calls"
        
        headers = {
            "Authorization": f"Bearer {BLAND_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Get phone number and webhook URL from environment variables
        phone_number = os.getenv('USER_PHONE_NUMBER')
        webhook_url = os.getenv('CALLBACK_URL')
        
        data = {
            "phone_number": phone_number,
            "task": script,
            "webhook_url": webhook_url,
            "model": "enhanced"  # Use enhanced model for better voice quality
        }
        
        logger.info(f"Making call to {phone_number}")
        logger.info(f"Using webhook URL: {webhook_url}")
        logger.info(f"Using API key: {BLAND_AI_API_KEY[:10]}...")
        
        response = requests.post(url, headers=headers, json=data)
        
        logger.info(f"API Response Status: {response.status_code}")
        logger.info(f"API Response Headers: {response.headers}")
        logger.info(f"API Response Body: {response.text}")
        
        response.raise_for_status()
        
        call_data = response.json()
        logger.info(f"Call initiated successfully. Response: {call_data}")
        return call_data.get('call_id')
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error making Bland AI call: {e}")
        logger.error(f"Response text: {e.response.text if hasattr(e, 'response') else 'No response text'}")
        return None
    except Exception as e:
        logger.error(f"Error making Bland AI call: {e}")
        return None

def run_demo():
    print("🚀 Starting AI Stock Portfolio Monitor Demo")
    print("------------------------------------------")
    
    # Initialize components
    portfolio_monitor = PortfolioMonitor()  # Start with default portfolio
    investment_analyzer = InvestmentAnalyzer()
    voice_interaction = VoiceInteraction()
    conversation_logger = ConversationLogger()
    
    # Get current market overview
    market_data = investment_analyzer.get_market_overview()
    
    # Set up high cash balance scenario
    print("\n📊 Scenario: High Cash Balance with Investment Opportunities")
    print("Description: Showing unused cash detection and stock investment opportunities")
    print("------------------------------------------------------------------")
    
    # Set initial cash balance
    initial_cash = 10000  # $10,000 starting cash
    print(f"Initial Cash Balance: ${initial_cash:.2f}")
    
    # Log initial state
    conversation_logger.log_initial_state(initial_cash, 1.0, 500)  # $500 monthly spending
    
    # Add some stock transactions to show normal usage
    print("\n💸 Recent Portfolio Activity:")
    
    # Add some stock purchases
    portfolio_monitor.add_transaction("AAPL", 10, 150.00)  # Bought 10 shares of Apple at $150
    transaction_msg = f"Bought 10 shares of AAPL at $150.00 (Total: $1,500.00)"
    print(f"- {transaction_msg}")
    conversation_logger.log_interaction("system", transaction_msg, {"type": "stock_purchase", "symbol": "AAPL", "shares": 10, "price": 150.00})
    
    portfolio_monitor.add_transaction("MSFT", 5, 300.00)  # Bought 5 shares of Microsoft at $300
    transaction_msg = f"Bought 5 shares of MSFT at $300.00 (Total: $1,500.00)"
    print(f"- {transaction_msg}")
    conversation_logger.log_interaction("system", transaction_msg, {"type": "stock_purchase", "symbol": "MSFT", "shares": 5, "price": 300.00})
    
    # Update cash balance after purchases
    portfolio_monitor.update_cash_balance(-3000)  # Spent $3,000 on stocks
    transaction_msg = f"Cash used for stock purchases: $3,000.00"
    print(f"- {transaction_msg}")
    conversation_logger.log_interaction("system", transaction_msg, {"type": "cash_transaction", "amount": -3000})
    
    # Show current portfolio status
    current_cash = portfolio_monitor.get_cash_balance()
    portfolio_value = portfolio_monitor.get_portfolio_value()
    holdings = portfolio_monitor.get_stock_holdings()
    
    balance_msg = f"Current Cash Balance: ${current_cash:.2f}"
    print(f"\n💰 {balance_msg}")
    print(f"📈 Total Portfolio Value: ${portfolio_value:.2f}")
    print(f"📊 Stock Holdings: {len(holdings)} different stocks")
    
    for symbol, shares in holdings.items():
        print(f"   - {symbol}: {shares} shares")
    
    conversation_logger.log_interaction("system", balance_msg, {"type": "balance_update", "cash_balance": current_cash, "portfolio_value": portfolio_value})
    
    # Calculate monthly spending and unused cash
    monthly_spending = 500  # $500 monthly expenses
    safety_net = monthly_spending * 3  # Keep 3 months of expenses as safety net
    unused_funds = current_cash - safety_net
    
    if unused_funds >= 500:  # Minimum investment amount in USD
        unused_funds_msg = (
            f"Unused Cash Detected!\n"
            f"Monthly Spending: ${monthly_spending:.2f}\n"
            f"Safety Net (3 months): ${safety_net:.2f}\n"
            f"Unused Cash Available: ${unused_funds:.2f}"
        )
        print(f"\n💡 {unused_funds_msg}")
        conversation_logger.log_interaction("system", unused_funds_msg, {
            "type": "unused_funds_detection",
            "monthly_spending": monthly_spending,
            "safety_net": safety_net,
            "unused_funds": unused_funds
        })
        
        # Get stock investment suggestions
        print("\n🔍 Analyzing Stock Investment Opportunities...")
        suggestions = investment_analyzer.get_investment_suggestions(unused_funds, include_growth_stocks=True)
        
        if suggestions:
            print("\n📈 Real-Time Stock Investment Opportunities:")
            conversation_logger.log_investment_suggestions(suggestions)
            
            # Print blue-chip stocks
            blue_chip_stocks = [s for s in suggestions if s.get('category') == 'blue_chip']
            print("\n📊 Blue-Chip Stock Options:")
            for i, suggestion in enumerate(blue_chip_stocks, 1):
                print(f"\n{i}. {suggestion['symbol']} ({suggestion.get('company_name', suggestion['symbol'])})")
                print(f"   Current Price: ${suggestion['price']:.2f}")
                print(f"   Risk Level: {suggestion['risk_level']}")
                print(f"   Daily Return: {suggestion['daily_return']*100:.2f}%")
                print(f"   Market Cap: ${suggestion.get('market_cap', 0):,.0f}")
                print(f"   P/E Ratio: {suggestion.get('pe_ratio', 'N/A')}")
            
            # Print growth stock investments if any
            growth_stocks = [s for s in suggestions if s.get('category') == 'growth']
            if growth_stocks:
                print("\n🚀 Growth Stock Options (Higher Volatility):")
                for i, suggestion in enumerate(growth_stocks, len(blue_chip_stocks) + 1):
                    print(f"\n{i}. {suggestion['symbol']} ({suggestion.get('company_name', suggestion['symbol'])})")
                    print(f"   Current Price: ${suggestion['price']:.2f}")
                    print(f"   Risk Level: {suggestion['risk_level']}")
                    print(f"   Daily Return: {suggestion['daily_return']*100:.2f}%")
                    print(f"   Market Cap: ${suggestion.get('market_cap', 0):,.0f}")
                    print(f"   Sector: {suggestion.get('sector', 'N/A')}")
                    if suggestion.get('risk_warning'):
                        print(f"   {suggestion['risk_warning']}")
            
            # Generate call script
            script = voice_interaction.generate_call_script(unused_funds, suggestions)
            
            if script:
                print("\n🗣️ AI Call Script:")
                print("----------------------")
                print(script)
                conversation_logger.log_interaction("ai", script, {"type": "call_script"})
                
                # Make the actual call using Bland AI
                print("\n📞 Initiating Phone Call...")
                call_id = make_bland_ai_call(script)
                if call_id:
                    call_msg = (
                        f"Call initiated successfully! Call ID: {call_id}\n"
                        f"You should receive a call at {os.getenv('USER_PHONE_NUMBER')}\n"
                        f"Webhook URL for responses: {os.getenv('CALLBACK_URL')}"
                    )
                    print(f"✅ {call_msg}")
                    conversation_logger.log_interaction("system", call_msg, {
                        "type": "call_initiated",
                        "call_id": call_id
                    })
                else:
                    error_msg = "Failed to initiate call. Check the logs for details."
                    print(f"❌ {error_msg}")
                    conversation_logger.log_interaction("system", error_msg, {"type": "call_error"})
                
                print("\n⏳ Waiting for your response on the phone...")
                print("The system will process your voice response and make investment decisions accordingly.")
                
                # Simulate a successful investment response
                print("\n🔄 Simulating user response and investment process...")
                time.sleep(2)
                
                # Simulate a successful investment response
                response = {
                    'interest': 'yes',
                    'preferred_investment': 'AAPL',
                    'investment_amount': 2000,  # $2000 investment
                    'amount_confirmed': 'yes',
                    'confirmation_word_correct': 'yes',
                    'questions': [],
                    'sentiment': 'positive',
                    'next_step': 'finalize investment',
                    'investment_completed': 'yes',
                    'farewell': voice_interaction.generate_farewell(investment_made=True)
                }
                
                # Log user's decision
                conversation_logger.log_interaction("user", "Confirmed investment decision", response)
                
                print("\n📱 Call Summary:")
                summary_msg = f"User chose to invest ${response['investment_amount']:.2f} in {response['preferred_investment']}"
                print(f"- {summary_msg}")
                print("- Investment confirmed with security code word")
                
                # Execute the investment
                stock_price = 150.00  # Current AAPL price
                shares_to_buy = response['investment_amount'] // stock_price
                if shares_to_buy > 0:
                    portfolio_monitor.add_transaction(response['preferred_investment'], shares_to_buy, stock_price)
                    portfolio_monitor.update_cash_balance(-response['investment_amount'])
                    execution_msg = f"Investment executed: {shares_to_buy} shares of {response['preferred_investment']} at ${stock_price:.2f} per share"
                    print(f"- {execution_msg}")
                
                # Log final investment decision
                conversation_logger.log_investment_decision(response)
                
                print("\n🗣️ Ending Call:")
                print(response['farewell'])
                conversation_logger.log_interaction("ai", response['farewell'], {"type": "farewell"})
                
                # Save conversation summary
                summary_file = conversation_logger.save_summary()
                print(f"\n📝 Conversation summary saved to: {summary_file}")
                
    else:
        msg = "No unused cash detected at this time"
        print(f"\nℹ️ {msg}")
        conversation_logger.log_interaction("system", msg, {"type": "no_unused_funds"})
    
    # Show final portfolio status
    final_cash = portfolio_monitor.get_cash_balance()
    final_portfolio_value = portfolio_monitor.get_portfolio_value()
    final_holdings = portfolio_monitor.get_stock_holdings()
    
    print(f"\n💰 Final Cash Balance: ${final_cash:.2f}")
    print(f"📈 Final Portfolio Value: ${final_portfolio_value:.2f}")
    print(f"📊 Final Holdings: {len(final_holdings)} different stocks")
    
    for symbol, shares in final_holdings.items():
        print(f"   - {symbol}: {shares} shares")
    
    # Generate conversation summary
    print("\n📋 Generating Conversation Summary...")
    summary = conversation_logger.get_conversation_summary()
    print(f"\n📄 Session Summary:\n{summary}")
    
    print("\n🎯 Demo completed successfully!")
    print("This demo showcased:")
    print("- Unused cash detection in stock portfolio")
    print("- Real-time stock market analysis")
    print("- AI-powered voice interaction for stock investments")
    print("- Stock investment opportunity recommendations")
    print("- Portfolio tracking and conversation logging")

if __name__ == "__main__":
    run_demo()