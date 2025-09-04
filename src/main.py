from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from datetime import datetime
import os
import requests
import time
from config.config import *
from src.portfolio_monitor import PortfolioMonitor
from src.investment_analyzer import InvestmentAnalyzer
from src.voice_interaction import VoiceInteraction

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()

# Initialize components
portfolio_monitor = PortfolioMonitor()
investment_analyzer = InvestmentAnalyzer()
voice_interaction = VoiceInteraction()

def make_bland_ai_call(script):
    """Make a call using Bland AI"""
    try:
        url = "https://api.bland.ai/v1/calls"
        
        headers = {
            "Authorization": f"Bearer {BLAND_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "phone_number": USER_PHONE_NUMBER,
            "task": script,
            "webhook_url": CALLBACK_URL,
            "model": "enhanced"  # Use enhanced model for better voice quality
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        call_id = response.json().get('call_id')
        logger.info(f"Call initiated successfully. Call ID: {call_id}")
        return call_id
        
    except Exception as e:
        logger.error(f"Error making Bland AI call: {e}")
        return None

def check_unused_funds():
    """Check for unused funds and initiate calls immediately if needed"""
    try:
        logger.info("Checking for unused funds...")
        
        # Get unused funds analysis
        unused_funds_data = investment_analyzer.identify_unused_funds()
        
        if unused_funds_data and unused_funds_data['unused_funds'] > 0:
            unused_funds = unused_funds_data['unused_funds']
            logger.info(f"Found ${unused_funds:.2f} in unused funds - TRIGGERING IMMEDIATE CALL")
            
            # Get investment opportunities
            opportunities = investment_analyzer.get_investment_opportunities(unused_funds)
            
            if opportunities:
                # Generate call script using the new method
                script = voice_interaction.generate_investment_call_script(opportunities, unused_funds)
                
                if script:
                    # Make the call immediately
                    logger.info("Making immediate call due to unused funds detection...")
                    call_id = make_bland_ai_call(script)
                    if call_id:
                        logger.info(f"CALL INITIATED SUCCESSFULLY! Call ID: {call_id}")
                        logger.info(f"You should receive a call shortly at {PHONE_NUMBER}")
                        return True
                    else:
                        logger.error("Failed to initiate investment call")
                        return False
                else:
                    logger.error("Failed to generate call script")
                    return False
            else:
                logger.info("No suitable investment opportunities found")
                return False
        else:
            logger.info("No unused funds available for investment")
            return False
            
    except Exception as e:
        logger.error(f"Error in check_unused_funds: {e}")
        return False

def handle_call_completion(call_id, transcript):
    """Handle completed calls and process user responses"""
    try:
        logger.info(f"Processing completed call {call_id} with transcript: {transcript}")
        
        # Process user's response
        user_response = voice_interaction.process_user_response(transcript)
        if not user_response:
            logger.error("Failed to process user response")
            return
            
        # Handle stock investment confirmation if user expressed interest
        if user_response['interest'] == 'yes' and user_response['preferred_investment']:
            symbol = user_response['preferred_investment']
            # Get unused funds for investment calculation
            unused_funds_data = investment_analyzer.identify_unused_funds()
            if unused_funds_data:
                unused_funds = unused_funds_data['unused_funds']
                amount = min(unused_funds, MAX_INVESTMENT_AMOUNT)
                
                confirmation = voice_interaction.handle_investment_confirmation(symbol, amount)
                if confirmation:
                    # Make follow-up call with confirmation
                    make_bland_ai_call(confirmation)
                    logger.info(f"Stock investment confirmation call made for {symbol}")
                    
        # Generate follow-up if needed
        elif user_response['questions'] or user_response['next_step'] != 'end':
            # Get unused funds for analysis
            unused_funds_data = investment_analyzer.identify_unused_funds()
            if unused_funds_data and user_response.get('preferred_investment'):
                symbol = user_response['preferred_investment']
                amount = min(unused_funds_data['unused_funds'], MAX_INVESTMENT_AMOUNT)
                
                follow_up = voice_interaction.generate_follow_up(
                    investment_analyzer.analyze_investment_opportunity(symbol, amount),
                    user_response
                )
                if follow_up:
                    # Make follow-up call
                    make_bland_ai_call(follow_up)
                    logger.info(f"Follow-up call made for {symbol}")
                    
    except Exception as e:
        logger.error(f"Error handling call completion: {e}")

def start_direct_calling_system():
    """Start the direct calling system without Flask"""
    logger.info("Starting direct calling system...")
    
    # Add scheduled job to check for unused funds
    scheduler.add_job(
        check_unused_funds,
        'interval',
        hours=24,  # Check daily
        next_run_time=datetime.now()
    )
    
    # Also check immediately on startup
    logger.info("Performing initial unused funds check...")
    check_unused_funds()
    
    logger.info("Direct calling system started. Scheduler running...")
    scheduler.start()

if __name__ == '__main__':
    try:
        start_direct_calling_system()
    except KeyboardInterrupt:
        logger.info("Shutting down direct calling system...")
        scheduler.shutdown()