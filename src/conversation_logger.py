import json
import logging
from datetime import datetime
import os
from pathlib import Path

class ConversationLogger:
    def __init__(self, log_dir="logs"):
        """Initialize the conversation logger"""
        self.log_dir = log_dir
        self.current_conversation = {
            "timestamp": datetime.now().isoformat(),
            "conversation_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "initial_state": {},
            "interactions": [],
            "investment_suggestions": [],
            "final_decision": None,
            "pol_price_usd": None
        }
        
        # Create logs directory if it doesn't exist
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Set up file logging
        self.log_file = os.path.join(
            log_dir, 
            f"conversation_{self.current_conversation['conversation_id']}.log"
        )
        self.json_file = os.path.join(
            log_dir, 
            f"conversation_{self.current_conversation['conversation_id']}.json"
        )
        
        # Configure file logger
        self.logger = logging.getLogger(f"conversation_{self.current_conversation['conversation_id']}")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(fh)

    def log_initial_state(self, balance_pol, pol_price_usd, monthly_spending_pol):
        """Log the initial state of the wallet"""
        initial_state = {
            "balance_pol": balance_pol,
            "balance_usd": balance_pol * pol_price_usd,
            "pol_price_usd": pol_price_usd,
            "monthly_spending_pol": monthly_spending_pol,
            "monthly_spending_usd": monthly_spending_pol * pol_price_usd
        }
        
        self.current_conversation["initial_state"] = initial_state
        self.current_conversation["pol_price_usd"] = pol_price_usd
        
        self.logger.info(f"Initial State:")
        self.logger.info(f"Balance: {balance_pol:.2f} POL (≈ ${balance_pol * pol_price_usd:.2f})")
        self.logger.info(f"POL Price: ${pol_price_usd:.6f}")
        self.logger.info(f"Monthly Spending: {monthly_spending_pol:.2f} POL (≈ ${monthly_spending_pol * pol_price_usd:.2f})")
        
        self._save_json()

    def log_investment_suggestions(self, suggestions):
        """Log investment suggestions"""
        self.current_conversation["investment_suggestions"] = suggestions
        
        self.logger.info("\nInvestment Suggestions:")
        for suggestion in suggestions:
            self.logger.info(
                f"{suggestion['symbol']}: {suggestion['price_in_pol']:.2f} POL "
                f"(${suggestion['price']:.2f}) - Risk: {suggestion['risk_level']}"
            )
        
        self._save_json()

    def log_interaction(self, role, message, metadata=None):
        """Log an interaction (AI or user)"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "message": message,
            "metadata": metadata or {}
        }
        
        self.current_conversation["interactions"].append(interaction)
        
        self.logger.info(f"\n{role.upper()}: {message}")
        if metadata:
            self.logger.info(f"Metadata: {json.dumps(metadata, indent=2)}")
        
        self._save_json()

    def log_investment_decision(self, decision):
        """Log the final investment decision"""
        self.current_conversation["final_decision"] = decision
        
        pol_price = self.current_conversation["pol_price_usd"]
        amount_pol = decision.get("investment_amount", 0)
        
        self.logger.info("\nFinal Investment Decision:")
        self.logger.info(
            f"Amount: {amount_pol:.2f} POL (≈ ${amount_pol * pol_price:.2f})"
        )
        self.logger.info(f"Asset: {decision.get('preferred_investment')}")
        self.logger.info(f"Status: {decision.get('status', 'completed')}")
        
        self._save_json()

    def _save_json(self):
        """Save the current conversation to JSON file"""
        with open(self.json_file, 'w') as f:
            json.dump(self.current_conversation, f, indent=2)

    def get_conversation_summary(self):
        """Get a human-readable summary of the conversation"""
        pol_price = self.current_conversation["pol_price_usd"]
        initial_state = self.current_conversation["initial_state"]
        final_decision = self.current_conversation["final_decision"]
        
        summary = [
            "\n=== Conversation Summary ===",
            f"Date: {self.current_conversation['timestamp']}",
            f"\nInitial State:",
            f"- Balance: {initial_state['balance_pol']:.2f} POL (≈ ${initial_state['balance_usd']:.2f})",
            f"- POL Price: ${pol_price:.6f}",
            f"- Monthly Spending: {initial_state['monthly_spending_pol']:.2f} POL "
            f"(≈ ${initial_state['monthly_spending_usd']:.2f})",
            "\nInteractions:"
        ]
        
        for interaction in self.current_conversation["interactions"]:
            summary.append(
                f"\n{interaction['role'].upper()} ({interaction['timestamp']}):"
                f"\n{interaction['message']}"
            )
        
        if final_decision:
            summary.extend([
                "\nFinal Decision:",
                f"- Amount: {final_decision['investment_amount']:.2f} POL "
                f"(≈ ${final_decision['investment_amount'] * pol_price:.2f})",
                f"- Asset: {final_decision['preferred_investment']}",
                f"- Status: {final_decision.get('status', 'completed')}"
            ])
        
        return "\n".join(summary)

    def save_summary(self, filename=None):
        """Save the conversation summary to a file"""
        if filename is None:
            filename = os.path.join(
                self.log_dir,
                f"summary_{self.current_conversation['conversation_id']}.txt"
            )
        
        with open(filename, 'w') as f:
            f.write(self.get_conversation_summary())
        
        return filename 