#!/usr/bin/env python3
"""
Standalone Phone Calling Script
This script checks for unused funds and immediately makes a call if any are found.
Run this script anytime you want to trigger a call manually.
"""

import logging
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import *
from src.portfolio_monitor import PortfolioMonitor
from src.investment_analyzer import InvestmentAnalyzer
from src.voice_interaction import VoiceInteraction
import requests

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def make_bland_ai_call(script):
    """Make a call using Bland AI"""
    try:
        url = "https://api.bland.ai/v1/calls"
        headers = {
            "Authorization": f"Bearer {BLAND_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "phone_number": USER_PHONE_NUMBER,
            "task": script,
            "voice": "maya",
            "reduce_latency": True,
            "max_duration": 300  # 5 minutes max
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            call_data = response.json()
            call_id = call_data.get('call_id')
            print(f"✓ Call initiated successfully! Call ID: {call_id}")
            return call_id
        else:
            logger.error(f"Failed to make call: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error making Bland AI call: {e}")
        return None

def check_and_call():
    """Check for unused funds and make a call if any are found"""
    try:
        print("Analyzing portfolio for investment opportunities...")
        
        # Initialize components
        portfolio_monitor = PortfolioMonitor()
        investment_analyzer = InvestmentAnalyzer()
        voice_interaction = VoiceInteraction()
        
        # Check for unused funds
        unused_funds_data = investment_analyzer.identify_unused_funds()
        
        if unused_funds_data and unused_funds_data['unused_funds'] > 0:
            unused_funds = unused_funds_data['unused_funds']
            print(f"✓ Available for investment: ${unused_funds:.2f}")
            
            # Get investment opportunities
            opportunities = investment_analyzer.get_investment_suggestions(unused_funds)
            
            if opportunities:
                # Generate call script
                script = voice_interaction.generate_investment_call_script(opportunities, unused_funds)
                
                if script:
                    print("✓ Investment script generated. Initiating call...")
                    call_id = make_bland_ai_call(script)
                    
                    if call_id:
                        print("✓ Call in progress. Please answer your phone.")
                        return True
                    else:
                        logger.error("Failed to initiate call")
                        return False
                else:
                    logger.error("Failed to generate call script")
                    return False
            else:
                print("No suitable investment opportunities found.")
                return False
        else:
            print("No excess funds available for investment.")
            return False
            
    except Exception as e:
        logger.error(f"Error in check_and_call: {e}")
        return False

if __name__ == '__main__':
    print("=== Investment Advisory Call System ===")
    
    success = check_and_call()
    
    if not success:
        print("No call initiated - insufficient funds or system error.")
    
    print("Analysis complete.")