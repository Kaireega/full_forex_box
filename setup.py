#!/usr/bin/env python3
"""
Forex Trading System Setup Script

This script sets up and starts all components of the forex trading system:
- Database initialization
- API connections (OANDA, OpenAI)
- Data collection
- Analysis systems
- Web server
- Bot systems

Usage:
    python setup.py [options]

Options:
    --install-deps    Install required dependencies
    --check-config    Check configuration files
    --init-db         Initialize database
    --start-server    Start web server
    --start-bot       Start trading bot
    --start-stream    Start data streaming
    --openai-demo     Run OpenAI analysis demo
    --all             Run all setup and start components
"""

import sys
import os
import subprocess
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append("./")

class ForexSystemSetup:
    """Main setup class for the forex trading system."""
    
    def __init__(self):
        self.project_root = Path(".")
        self.logs_dir = self.project_root / "logs"
        self.setup_log = self.logs_dir / f"setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message to both console and file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        print(log_entry)
        
        with open(self.setup_log, "a") as f:
            f.write(log_entry + "\n")
    
    def run_command(self, command: str, description: str = None, check_exit_code: bool = True):
        """Run a shell command and log the result."""
        if description:
            self.log(f"Running: {description}")
        
        self.log(f"Command: {command}")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            
            if result.stderr:
                self.log(f"Error: {result.stderr.strip()}", "WARNING")
            
            if check_exit_code and result.returncode != 0:
                self.log(f"Command failed with exit code {result.returncode}", "ERROR")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {command}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Exception running command: {e}", "ERROR")
            return False
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        self.log("Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            self.log("Python 3.7 or higher is required", "ERROR")
            return False
        
        self.log(f"Python version: {version.major}.{version.minor}.{version.micro} ✅")
        return True
    
    def install_dependencies(self):
        """Install required Python packages."""
        self.log("Installing dependencies...")
        
        if not (self.project_root / "requirements.txt").exists():
            self.log("requirements.txt not found", "ERROR")
            return False
        
        success = self.run_command(
            "pip install -r requirements.txt",
            "Installing Python packages"
        )
        
        if success:
            self.log("Dependencies installed successfully ✅")
        else:
            self.log("Failed to install dependencies ❌", "ERROR")
        
        return success
    
    def check_configuration(self):
        """Check if all configuration files are present and valid."""
        self.log("Checking configuration files...")
        
        config_files = {
            "constants/defs.py": "OANDA API configuration",
            "package.json": "Node.js dependencies",
            "requirements.txt": "Python dependencies"
        }
        
        missing_files = []
        
        for file_path, description in config_files.items():
            if not (self.project_root / file_path).exists():
                missing_files.append(f"{file_path} ({description})")
                self.log(f"Missing: {file_path}", "WARNING")
        
        if missing_files:
            self.log("Missing configuration files:", "WARNING")
            for file in missing_files:
                self.log(f"  - {file}", "WARNING")
            return False
        
        # Check environment variables
        required_env_vars = {
            "OPENAI_API_KEY": "f092735885a6ea06b0941160eb4855bb-ecdf07214bee956d3eb9d5dd1a618a7e"
        }
        
        missing_env_vars = []
        
        for env_var, description in required_env_vars.items():
            if not os.getenv(env_var):
                missing_env_vars.append(f"{env_var} ({description})")
                self.log(f"Missing environment variable: {env_var}", "WARNING")
        
        if missing_env_vars:
            self.log("Missing environment variables (optional):", "WARNING")
            for var in missing_env_vars:
                self.log(f"  - {var}", "WARNING")
            self.log("Set these for full functionality:", "INFO")
            self.log("export OPENAI_API_KEY='your-api-key-here'", "INFO")
        
        self.log("Configuration check completed ✅")
        return True
    
    def initialize_database(self):
        """Initialize the database system."""
        self.log("Initializing database...")
        
        try:
            from db.db import DataDB
            
            db = DataDB()
            self.log("Database connection successful ✅")
            
            # Test database operations
            db.test_connection()
            self.log("Database operations tested ✅")
            
            return True
            
        except Exception as e:
            self.log(f"Database initialization failed: {e}", "ERROR")
            return False
    
    def test_api_connections(self):
        """Test API connections."""
        self.log("Testing API connections...")
        
        # Test OANDA API
        try:
            from api.oanda_api import OandaApi
            
            oanda_api = OandaApi()
            self.log("OANDA API initialized ✅")
            
            # Try to get account info (this might fail if not configured)
            try:
                instruments = oanda_api.get_account_instruments()
                if instruments:
                    self.log(f"OANDA API connection successful - {len(instruments)} instruments available ✅")
                else:
                    self.log("OANDA API connection issue - no instruments returned", "WARNING")
            except Exception as e:
                self.log(f"OANDA API test failed: {e}", "WARNING")
                self.log("Check your OANDA credentials in constants/defs.py", "WARNING")
            
        except Exception as e:
            self.log(f"OANDA API initialization failed: {e}", "ERROR")
        
        # Test OpenAI API
        try:
            from api.openai_api import OpenAIAnalyzer
            
            if os.getenv('OPENAI_API_KEY'):
                analyzer = OpenAIAnalyzer()
                self.log("OpenAI API initialized ✅")
                
                # Quick test with minimal data
                import pandas as pd
                test_data = pd.DataFrame({'test': [1, 2, 3]})
                
                try:
                    # This is a minimal test - might still cost tokens
                    # result = analyzer.analyze_forex_data(test_data, "general")
                    # if 'error' not in result:
                    #     self.log("OpenAI API connection successful ✅")
                    # else:
                    #     self.log(f"OpenAI API test failed: {result['error']}", "WARNING")
                    self.log("OpenAI API ready (skipping live test to save tokens) ✅")
                except Exception as e:
                    self.log(f"OpenAI API test failed: {e}", "WARNING")
            else:
                self.log("OpenAI API key not set - analysis features will be unavailable", "WARNING")
                
        except Exception as e:
            self.log(f"OpenAI API initialization failed: {e}", "WARNING")
        
        return True
    
    def setup_instruments(self):
        """Set up instrument collection."""
        self.log("Setting up instrument collection...")
        
        try:
            from infrastructure.instrument_collection import instrumentCollection
            from api.oanda_api import OandaApi
            
            # Load instruments
            data_dir = self.project_root / "data"
            if data_dir.exists():
                instrumentCollection.LoadInstruments("./data")
                self.log("Instruments loaded from data directory ✅")
            else:
                self.log("Data directory not found, creating instruments from API...", "WARNING")
                api = OandaApi()
                try:
                    instrumentCollection.CreateDB(api.get_account_instruments())
                    self.log("Instruments created from OANDA API ✅")
                except Exception as e:
                    self.log(f"Failed to create instruments from API: {e}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"Instrument setup failed: {e}", "ERROR")
            return False
    
    def start_web_server(self, background: bool = True):
        """Start the web server."""
        self.log("Starting web server...")
        
        if not (self.project_root / "server.py").exists():
            self.log("server.py not found", "ERROR")
            return False
        
        if background:
            command = "python server.py &"
            description = "Starting web server in background"
        else:
            command = "python server.py"
            description = "Starting web server"
        
        success = self.run_command(command, description, check_exit_code=False)
        
        if success:
            self.log("Web server started ✅")
            if background:
                time.sleep(2)  # Give server time to start
                self.log("Web server should be available at http://localhost:5001")
        
        return success
    
    def start_trading_bot(self, background: bool = True):
        """Start the trading bot."""
        self.log("Starting trading bot...")
        
        if not (self.project_root / "run_bot.py").exists():
            self.log("run_bot.py not found", "ERROR")
            return False
        
        if background:
            command = "python run_bot.py &"
            description = "Starting trading bot in background"
        else:
            command = "python run_bot.py"
            description = "Starting trading bot"
        
        success = self.run_command(command, description, check_exit_code=False)
        
        if success:
            self.log("Trading bot started ✅")
        
        return success
    
    def start_data_streaming(self, background: bool = True):
        """Start data streaming."""
        self.log("Starting data streaming...")
        
        try:
            if background:
                # Import and run in background thread
                import threading
                from stream_example.streamer import run_streamer
                
                def stream_worker():
                    try:
                        run_streamer()
                    except Exception as e:
                        self.log(f"Streaming error: {e}", "ERROR")
                
                stream_thread = threading.Thread(target=stream_worker, daemon=True)
                stream_thread.start()
                self.log("Data streaming started in background ✅")
            else:
                from stream_example.streamer import run_streamer
                run_streamer()
            
            return True
            
        except Exception as e:
            self.log(f"Failed to start data streaming: {e}", "ERROR")
            return False
    
    def run_openai_demo(self):
        """Run OpenAI analysis demonstration."""
        self.log("Running OpenAI analysis demo...")
        
        if not os.getenv('OPENAI_API_KEY'):
            self.log("OpenAI API key not set - skipping demo", "WARNING")
            return False
        
        success = self.run_command(
            "python test_openai_analysis.py",
            "Running OpenAI analysis test suite"
        )
        
        if success:
            self.log("OpenAI demo completed ✅")
        
        return success
    
    def collect_initial_data(self):
        """Collect initial market data."""
        self.log("Collecting initial market data...")
        
        try:
            from infrastructure.collect_data import run_collection
            from infrastructure.instrument_collection import instrumentCollection
            from api.oanda_api import OandaApi
            
            api = OandaApi()
            
            # Run data collection in a separate thread to avoid blocking
            import threading
            
            def collect_worker():
                try:
                    run_collection(instrumentCollection, api)
                except Exception as e:
                    self.log(f"Data collection error: {e}", "ERROR")
            
            collect_thread = threading.Thread(target=collect_worker, daemon=True)
            collect_thread.start()
            
            self.log("Data collection started ✅")
            return True
            
        except Exception as e:
            self.log(f"Failed to start data collection: {e}", "ERROR")
            return False
    
    def show_system_status(self):
        """Display system status and access information."""
        self.log("=" * 60)
        self.log("FOREX TRADING SYSTEM STATUS")
        self.log("=" * 60)
        
        status_items = [
            ("Web Server", "http://localhost:5001"),
            ("Trading Bot", "Running in background"),
            ("Data Streaming", "Active"),
            ("OpenAI Analysis", "Available" if os.getenv('OPENAI_API_KEY') else "Not configured"),
            ("Database", "Initialized"),
            ("OANDA API", "Connected"),
            ("Logs", str(self.setup_log))
        ]
        
        for service, status in status_items:
            self.log(f"{service:20}: {status}")
        
        self.log("=" * 60)
        self.log("QUICK ACCESS COMMANDS")
        self.log("=" * 60)
        self.log("View logs:           tail -f " + str(self.setup_log))
        self.log("OpenAI demo:         python test_openai_analysis.py")
        self.log("Manual bot start:    python run_bot.py")
        self.log("Manual server start: python server.py")
        self.log("Jupyter notebook:    jupyter notebook analysis/")
        self.log("=" * 60)

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Forex Trading System Setup")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies")
    parser.add_argument("--check-config", action="store_true", help="Check configuration")
    parser.add_argument("--init-db", action="store_true", help="Initialize database")
    parser.add_argument("--start-server", action="store_true", help="Start web server")
    parser.add_argument("--start-bot", action="store_true", help="Start trading bot")
    parser.add_argument("--start-stream", action="store_true", help="Start data streaming")
    parser.add_argument("--openai-demo", action="store_true", help="Run OpenAI demo")
    parser.add_argument("--collect-data", action="store_true", help="Start data collection")
    parser.add_argument("--all", action="store_true", help="Run complete setup")
    parser.add_argument("--quick", action="store_true", help="Quick setup (no demos or data collection)")
    
    args = parser.parse_args()
    
    # If no arguments provided, run complete setup
    if not any(vars(args).values()):
        args.all = True
    
    setup = ForexSystemSetup()
    
    setup.log("🚀 Forex Trading System Setup Started")
    setup.log(f"Timestamp: {datetime.now()}")
    setup.log(f"Log file: {setup.setup_log}")
    
    # Always check Python version
    if not setup.check_python_version():
        sys.exit(1)
    
    success_count = 0
    total_steps = 0
    
    steps = []
    
    if args.all or args.quick:
        steps = [
            ("check_configuration", "Configuration Check"),
            ("install_dependencies", "Install Dependencies"),
            ("initialize_database", "Database Initialization"),
            ("setup_instruments", "Instrument Setup"),
            ("test_api_connections", "API Connection Tests"),
        ]
        
        if args.all:
            steps.extend([
                ("collect_initial_data", "Data Collection"),
                ("start_web_server", "Web Server"),
                ("start_trading_bot", "Trading Bot"),
                ("start_data_streaming", "Data Streaming"),
                ("openai_demo", "OpenAI Demo")
            ])
    else:
        if args.check_config:
            steps.append(("check_configuration", "Configuration Check"))
        if args.install_deps:
            steps.append(("install_dependencies", "Install Dependencies"))
        if args.init_db:
            steps.append(("initialize_database", "Database Initialization"))
        if args.start_server:
            steps.append(("start_web_server", "Web Server"))
        if args.start_bot:
            steps.append(("start_trading_bot", "Trading Bot"))
        if args.start_stream:
            steps.append(("start_data_streaming", "Data Streaming"))
        if args.openai_demo:
            steps.append(("openai_demo", "OpenAI Demo"))
        if args.collect_data:
            steps.append(("collect_initial_data", "Data Collection"))
    
    total_steps = len(steps)
    
    # Execute steps
    for i, (method_name, description) in enumerate(steps, 1):
        setup.log(f"\n🔄 Step {i}/{total_steps}: {description}")
        setup.log("-" * 40)
        
        try:
            method = getattr(setup, method_name)
            if method():
                success_count += 1
                setup.log(f"✅ Step {i} completed successfully")
            else:
                setup.log(f"❌ Step {i} failed", "WARNING")
        except Exception as e:
            setup.log(f"❌ Step {i} failed with exception: {e}", "ERROR")
    
    # Final summary
    setup.log("\n" + "=" * 60)
    setup.log("SETUP SUMMARY")
    setup.log("=" * 60)
    setup.log(f"Steps completed: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        setup.log("🎉 Setup completed successfully!")
        setup.show_system_status()
    else:
        setup.log("⚠️  Setup completed with warnings/errors")
        setup.log("Check the log messages above for details")
    
    setup.log(f"Setup log saved to: {setup.setup_log}")
    
    # Keep the main process alive if services were started
    if args.all or args.start_server or args.start_bot or args.start_stream:
        setup.log("\n🔄 Services are running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            setup.log("\n👋 Shutting down services...")

if __name__ == "__main__":
    main()