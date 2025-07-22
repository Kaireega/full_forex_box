#!/usr/bin/env python3
"""
Quick Start Script for Real-time Forex Trading Analyzer

This script provides easy access to start the OpenAI-powered real-time trading analyzer
with different configurations and interfaces.
"""

import sys
import os
import argparse
import threading
import time
from datetime import datetime

# Add project root to path
sys.path.append("./")

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Check required modules
    try:
        from analysis.realtime_trading_analyzer import RealtimeTradingAnalyzer
        from api.openai_api import OpenAIAnalyzer
        from api.oanda_api import OandaApi
        print("✅ All required modules found")
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def start_console_analyzer(pairs, interval, duration):
    """Start console-based analyzer."""
    try:
        from analysis.realtime_trading_analyzer import RealtimeTradingAnalyzer
        
        print("🚀 Starting Console-Based Real-time Analyzer")
        print("=" * 60)
        print(f"📊 Currency Pairs: {', '.join(pairs)}")
        print(f"⏱️  Update Interval: {interval} seconds")
        print(f"⏰ Duration: {duration} minutes")
        print("💡 Press Ctrl+C to stop")
        print("=" * 60)
        
        # Initialize analyzer
        analyzer = RealtimeTradingAnalyzer(update_interval=interval)
        
        # Start analysis
        analysis_thread = analyzer.start_realtime_analysis(pairs)
        
        # Run for specified duration or until interrupted
        start_time = time.time()
        try:
            while True:
                elapsed_minutes = (time.time() - start_time) / 60
                
                if duration > 0 and elapsed_minutes >= duration:
                    print(f"\n⏰ Reached duration limit of {duration} minutes")
                    break
                
                time.sleep(60)  # Show summary every minute
                
                summary = analyzer.get_signal_summary()
                if summary and 'total_signals' in summary:
                    print(f"\n📊 Running for {elapsed_minutes:.1f} minutes | "
                          f"Signals: {summary.get('total_signals', 0)} | "
                          f"Avg Confidence: {summary.get('average_confidence', 0):.1%}")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping analyzer...")
        
        analyzer.stop_realtime_analysis()
        print("✅ Analyzer stopped successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def start_web_dashboard():
    """Start web dashboard interface."""
    try:
        print("🌐 Starting Web Dashboard...")
        print("📊 Access at: http://localhost:5001")
        print("🔄 Auto-refresh every 5 seconds")
        print("💡 Press Ctrl+C to stop")
        print("=" * 50)
        
        # Import and start web server
        from web_trading_dashboard import app
        app.run(host='0.0.0.0', port=5001, debug=False)
        
    except Exception as e:
        print(f"❌ Error starting web dashboard: {e}")

def start_background_analyzer(pairs, interval, log_file):
    """Start analyzer in background with file logging."""
    try:
        from analysis.realtime_trading_analyzer import RealtimeTradingAnalyzer
        
        print("🔄 Starting Background Analyzer...")
        print(f"📁 Signals logged to: {log_file}")
        print(f"📊 Currency Pairs: {', '.join(pairs)}")
        print(f"⏱️  Update Interval: {interval} seconds")
        print("💡 Check logs directory for signal files")
        
        # Initialize analyzer
        analyzer = RealtimeTradingAnalyzer(update_interval=interval)
        
        # Start analysis in background
        analysis_thread = analyzer.start_realtime_analysis(pairs)
        
        print("✅ Background analyzer started successfully")
        print("   Signals will be saved to logs/trading_signals_YYYYMMDD.json")
        print("   Use './start.sh check' to monitor status")
        
        return analyzer, analysis_thread
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def run_quick_test():
    """Run a quick test of the analyzer."""
    try:
        from analysis.realtime_trading_analyzer import RealtimeTradingAnalyzer
        
        print("🧪 Running Quick Test...")
        print("⏱️  Test Duration: 2 minutes")
        print("📊 Testing EUR_USD analysis")
        
        # Initialize analyzer
        analyzer = RealtimeTradingAnalyzer(update_interval=30)  # 30-second intervals for testing
        
        # Start analysis
        analysis_thread = analyzer.start_realtime_analysis(['EUR_USD'])
        
        # Run for 2 minutes
        time.sleep(120)
        
        # Stop and show results
        analyzer.stop_realtime_analysis()
        
        summary = analyzer.get_signal_summary()
        signals = analyzer.get_current_signals()
        
        print("📊 Test Results:")
        print(f"   Total signals: {summary.get('total_signals', 0)}")
        print(f"   Average confidence: {summary.get('average_confidence', 0):.1%}")
        print(f"   Recent signals: {len(signals)}")
        
        if signals:
            latest = signals[-1]
            print(f"   Latest signal: {latest.currency_pair} {latest.signal_type} "
                  f"(Confidence: {latest.confidence:.1%})")
        
        print("✅ Quick test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Start OpenAI-powered real-time forex trading analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_trading_analyzer.py --mode console --pairs EUR_USD GBP_USD --duration 30
  python start_trading_analyzer.py --mode web
  python start_trading_analyzer.py --mode background --pairs EUR_USD USD_JPY
  python start_trading_analyzer.py --mode test
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['console', 'web', 'background', 'test'],
        default='console',
        help='Analysis mode (default: console)'
    )
    
    parser.add_argument(
        '--pairs',
        nargs='+',
        default=['EUR_USD', 'GBP_USD', 'USD_JPY'],
        help='Currency pairs to analyze (default: EUR_USD GBP_USD USD_JPY)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Update interval in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=0,
        help='Duration in minutes (0 = unlimited, default: 0)'
    )
    
    parser.add_argument(
        '--log-file',
        default='trading_signals.log',
        help='Log file for background mode (default: trading_signals.log)'
    )
    
    args = parser.parse_args()
    
    # Header
    print("🤖 OpenAI-Powered Forex Trading Analyzer")
    print("=" * 50)
    print(f"Mode: {args.mode.upper()}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Route to appropriate mode
    if args.mode == 'console':
        start_console_analyzer(args.pairs, args.interval, args.duration)
    
    elif args.mode == 'web':
        start_web_dashboard()
    
    elif args.mode == 'background':
        analyzer, thread = start_background_analyzer(args.pairs, args.interval, args.log_file)
        if analyzer:
            try:
                # Keep script running
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n🛑 Stopping background analyzer...")
                analyzer.stop_realtime_analysis()
    
    elif args.mode == 'test':
        run_quick_test()

if __name__ == "__main__":
    main()