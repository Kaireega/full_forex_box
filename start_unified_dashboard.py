#!/usr/bin/env python3
"""
Startup Script for Unified Forex Trading Dashboard

This script starts the comprehensive unified dashboard that combines:
- Real-time trading system control
- Price charts and technical analysis
- Economic calendars
- Comprehensive trading analysis
- All functionality from both web_dashboard and forex-dash
"""

import sys
import os
import time
import threading
from datetime import datetime

# Add project root to path
sys.path.append("./")

def print_banner():
    """Print startup banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🚀 UNIFIED FOREX TRADING DASHBOARD                       ║
    ║                                                              ║
    ║    Comprehensive Real-time Trading System                   ║
    ║    with AI Analysis, Charts & Economic Data                 ║
    ║                                                              ║
    ║    Features:                                                 ║
    ║    • Real-time Trading System Control                       ║
    ║    • Interactive Price Charts                               ║
    ║    • Technical Analysis Indicators                          ║
    ║    • Economic Calendars (TE & FF)                          ║
    ║    • Comprehensive AI Analysis                              ║
    ║    • Risk Management & Position Sizing                      ║
    ║    • Multi-timeframe Analysis                               ║
    ║    • Pattern Recognition                                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'flask',
        'flask_cors',
        'numpy',
        'pandas',
        'requests',
        'threading',
        'datetime'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"  ❌ {module} - MISSING")
    
    if missing_modules:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_modules)}")
        print("Please install missing dependencies:")
        print("pip install " + " ".join(missing_modules))
        return False
    
    print("✅ All dependencies available")
    return True

def check_api_credentials():
    """Check if API credentials are configured."""
    print("\n🔑 Checking API credentials...")
    
    # Check OANDA credentials
    try:
        from api.oanda_api import OandaApi
        api = OandaApi()
        account = api.get_account_summary()
        
        if account and 'id' in account:
            print("  ✅ OANDA API credentials configured")
            print(f"     Account: {account['id']}")
            print(f"     Currency: {account['currency']}")
            print(f"     Balance: {account['balance']}")
        else:
            print("  ❌ OANDA API credentials not configured or invalid")
            return False
            
    except Exception as e:
        print(f"  ❌ OANDA API error: {e}")
        return False
    
    # Check OpenAI credentials (optional)
    try:
        from analysis.openai_analysis import OpenAIAnalyzer
        print("  ✅ OpenAI API available for AI analysis")
    except ImportError:
        print("  ⚠️  OpenAI API not configured (AI analysis will be limited)")
    
    return True

def start_dashboard():
    """Start the unified dashboard."""
    print("\n🌐 Starting Unified Dashboard...")
    
    try:
        # Import and start the dashboard
        from unified_dashboard.app import app
        
        print("✅ Dashboard server initialized")
        print("📊 Access the dashboard at: http://localhost:5001")
        print("🔧 API endpoints available at: http://localhost:5001/api/")
        print("💚 Health check at: http://localhost:5001/health")
        print("\n" + "="*60)
        
        # Start the Flask app
        app.run(host='0.0.0.0', port=5001, debug=False)
        
    except ImportError as e:
        print(f"❌ Error importing dashboard: {e}")
        print("Make sure you're running this script from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return False

def main():
    """Main startup function."""
    print_banner()
    
    # Check if running from correct directory
    if not os.path.exists('unified_dashboard'):
        print("❌ Error: unified_dashboard directory not found")
        print("Please run this script from the project root directory")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        return
    
    # Check API credentials
    if not check_api_credentials():
        print("\n❌ API credentials check failed. Please configure your API credentials.")
        print("See SETUP_README.md for configuration instructions.")
        return
    
    print("\n🚀 Starting Unified Forex Trading Dashboard...")
    print("Press Ctrl+C to stop the dashboard")
    
    try:
        start_dashboard()
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
        print("Thank you for using the Unified Forex Trading Dashboard!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the logs for more details")

if __name__ == "__main__":
    main() 