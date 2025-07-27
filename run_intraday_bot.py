#!/usr/bin/env python3
"""
Intraday Trading Bot Runner
===========================

This script runs the enhanced intraday trading bot with:
- Faster response times (M1 timeframes)
- Session-aware trading
- Intraday pattern recognition
- Dynamic position sizing
- Real-time risk management

Usage:
    python run_intraday_bot.py

Requirements:
    - OANDA API credentials configured
    - Required Python packages installed
    - Proper risk management settings
"""

import sys
import os
import signal
import time
from datetime import datetime
import pytz

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.intraday_bot import IntradayBot
from infrastructure.log_wrapper import LogWrapper

class IntradayBotRunner:
    """Runner class for the intraday trading bot"""
    
    def __init__(self):
        self.bot = None
        self.logger = LogWrapper("intraday_runner")
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        if self.bot:
            self.bot.log_to_main("Bot shutdown requested")
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        self.logger.logger.info("Checking prerequisites...")
        
        # Check if settings file exists
        if not os.path.exists("./bot/intraday_settings.json"):
            self.logger.logger.error("intraday_settings.json not found!")
            return False
        
        # Check if we're in trading hours
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        
        self.logger.logger.info(f"Current time (ET): {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if it's a weekday
        if now.weekday() >= 5:
            self.logger.logger.warning("Weekend detected - bot will run but may not trade")
        
        # Check if we're in active hours
        hour = now.hour
        if 8 <= hour <= 16:
            self.logger.logger.info("✅ Active trading hours detected")
        else:
            self.logger.logger.warning("⚠️ Outside active trading hours - bot will wait for session")
        
        return True
    
    def start_bot(self):
        """Start the intraday trading bot"""
        try:
            self.logger.logger.info("Starting Intraday Trading Bot...")
            
            # Initialize the bot
            self.bot = IntradayBot()
            
            # Start the main loop
            self.running = True
            self.bot.run()
            
        except KeyboardInterrupt:
            self.logger.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.logger.error(f"Error starting bot: {e}")
            raise
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        self.logger.logger.info("Cleaning up...")
        
        if self.bot:
            try:
                # Close any open positions
                self.bot.close_all_positions()
            except Exception as e:
                self.logger.logger.error(f"Error during cleanup: {e}")
        
        self.logger.logger.info("Cleanup complete")
    
    def run(self):
        """Main runner method"""
        self.logger.logger.info("=" * 50)
        self.logger.logger.info("INTRADAY TRADING BOT STARTUP")
        self.logger.logger.info("=" * 50)
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.logger.logger.error("Prerequisites check failed. Exiting.")
            return 1
        
        # Start the bot
        try:
            self.start_bot()
        except Exception as e:
            self.logger.logger.error(f"Fatal error: {e}")
            return 1
        
        return 0

def main():
    """Main entry point"""
    runner = IntradayBotRunner()
    return runner.run()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)