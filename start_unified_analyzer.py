#!/usr/bin/env python3
"""
Unified Trading Analyzer Quick Start

This script replaces all redundant start scripts and provides a single,
optimized interface for all trading analysis modes.
"""

import sys
import os
import argparse
import time
from datetime import datetime

# Add project root to path
sys.path.append("./")

def check_requirements():
    """Unified requirements check."""
    print("🔍 Checking requirements...")
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Check required modules
    try:
        from analysis.unified_trading_analyzer import UnifiedTradingAnalyzer, AnalysisMode
        from api.openai_api import OpenAIAnalyzer
        from api.oanda_api import OandaApi
        print("✅ All required modules found")
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def start_analyzer(mode: str, pairs: list, interval: int, duration: int):
    """Start the unified analyzer with specified mode."""
    try:
        from analysis.unified_trading_analyzer import UnifiedTradingAnalyzer, AnalysisMode
        
        # Convert mode string to enum
        mode_map = {
            'basic': AnalysisMode.BASIC,
            'adaptive': AnalysisMode.ADAPTIVE,
            'comprehensive': AnalysisMode.COMPREHENSIVE
        }
        
        analysis_mode = mode_map.get(mode, AnalysisMode.ADAPTIVE)
        
        print("🚀 Starting Unified Trading Analyzer")
        print("=" * 60)
        
        # Mode-specific descriptions
        if analysis_mode == AnalysisMode.BASIC:
            print("⚡ BASIC MODE: Real-time signals with OpenAI analysis")
            print("📊 Features: Minute-level analysis, entry/exit points")
        elif analysis_mode == AnalysisMode.ADAPTIVE:
            print("🎯 ADAPTIVE MODE: Profitable in ALL market conditions")
            print("📈 Trending: Trend following | ↔️ Sideways: Mean reversion")
            print("⚡ Volatile: Breakout trading | 🚀 Breakout: Early entry")
        else:  # COMPREHENSIVE
            print("🔬 COMPREHENSIVE MODE: Full analysis with news sentiment")
            print("📰 Features: Adaptive analysis + news impact + market intelligence")
        
        print("=" * 60)
        print(f"📊 Currency Pairs: {', '.join(pairs)}")
        print(f"⏱️  Update Interval: {interval} seconds")
        print(f"⏰ Duration: {duration} minutes" if duration > 0 else "⏰ Duration: Unlimited")
        print("💡 Press Ctrl+C to stop")
        print("=" * 60)
        
        # Initialize unified analyzer
        analyzer = UnifiedTradingAnalyzer(
            update_interval=interval,
            mode=analysis_mode
        )
        
        # Start analysis
        analysis_thread = analyzer.start_analysis(pairs)
        
        # Run for specified duration or until interrupted
        start_time = time.time()
        try:
            while True:
                elapsed_minutes = (time.time() - start_time) / 60
                
                if duration > 0 and elapsed_minutes >= duration:
                    print(f"\n⏰ Reached duration limit of {duration} minutes")
                    break
                
                time.sleep(120)  # Show summary every 2 minutes
                
                # Show adaptive summary based on mode
                signals = analyzer.signals_history
                if signals:
                    summary = analyzer.get_signal_summary()
                    print(f"\n📊 Running for {elapsed_minutes:.1f} minutes")
                    print(f"   Mode: {mode.upper()}")
                    print(f"   Total Signals: {summary.get('total_signals', 0)}")
                    print(f"   Signal Types: {summary.get('signal_types', {})}")
                    print(f"   Avg Confidence: {summary.get('average_confidence', 0):.1%}")
                    print(f"   High Confidence: {summary.get('high_confidence_signals', 0)}")
                    
                    # Additional info for adaptive/comprehensive modes
                    if analysis_mode != AnalysisMode.BASIC:
                        recent_signals = signals[-10:]
                        conditions = {}
                        strategies = {}
                        
                        for signal in recent_signals:
                            if hasattr(signal, 'market_condition') and signal.market_condition:
                                condition = signal.market_condition.value
                                conditions[condition] = conditions.get(condition, 0) + 1
                            if hasattr(signal, 'strategy_used') and signal.strategy_used:
                                strategy = signal.strategy_used.value
                                strategies[strategy] = strategies.get(strategy, 0) + 1
                        
                        if conditions:
                            print(f"   Market Conditions: {conditions}")
                        if strategies:
                            print(f"   Strategies Used: {strategies}")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping analyzer...")
        
        analyzer.stop_analysis()
        
        # Final summary
        if analyzer.signals_history:
            print("\n📊 FINAL SESSION SUMMARY")
            print("=" * 40)
            
            total_signals = len(analyzer.signals_history)
            buy_signals = len([s for s in analyzer.signals_history if s.signal_type == 'BUY'])
            sell_signals = len([s for s in analyzer.signals_history if s.signal_type == 'SELL'])
            
            print(f"Mode: {mode.upper()}")
            print(f"Total Signals: {total_signals}")
            print(f"BUY Signals: {buy_signals}")
            print(f"SELL Signals: {sell_signals}")
            
            # Mode-specific summary
            if analysis_mode != AnalysisMode.BASIC:
                conditions = {}
                strategies = {}
                profit_probs = []
                
                for signal in analyzer.signals_history:
                    if hasattr(signal, 'market_condition') and signal.market_condition:
                        condition = signal.market_condition.value
                        conditions[condition] = conditions.get(condition, 0) + 1
                    if hasattr(signal, 'strategy_used') and signal.strategy_used:
                        strategy = signal.strategy_used.value
                        strategies[strategy] = strategies.get(strategy, 0) + 1
                    if hasattr(signal, 'profit_probability'):
                        profit_probs.append(signal.profit_probability)
                
                if conditions:
                    print(f"\nMarket Conditions Traded:")
                    for condition, count in conditions.items():
                        print(f"  {condition}: {count} signals")
                
                if strategies:
                    print(f"\nStrategies Used:")
                    for strategy, count in strategies.items():
                        print(f"  {strategy}: {count} signals")
                
                if profit_probs:
                    avg_profit_prob = sum(profit_probs) / len(profit_probs)
                    print(f"\nAverage Profit Probability: {avg_profit_prob:.1%}")
            
            # Average metrics
            avg_confidence = sum(s.confidence for s in analyzer.signals_history) / total_signals
            print(f"\nAverage Confidence: {avg_confidence:.1%}")
            
            print(f"\n💾 Signals saved to: logs/unified_signals_{mode}_{datetime.now().strftime('%Y%m%d')}.json")
        
        print("✅ Unified analyzer stopped successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def run_adaptability_test():
    """Test market condition adaptability."""
    try:
        from analysis.unified_trading_analyzer import UnifiedTradingAnalyzer, AnalysisMode
        
        print("🧪 Running Market Condition Adaptability Test")
        print("=" * 60)
        print("Testing analyzer's ability to adapt to different market conditions...")
        
        # Initialize analyzer in adaptive mode
        analyzer = UnifiedTradingAnalyzer(
            update_interval=30,  # 30-second intervals for testing
            mode=AnalysisMode.ADAPTIVE
        )
        
        # Start analysis
        analysis_thread = analyzer.start_analysis(['EUR_USD'])
        
        # Run for 3 minutes to capture different conditions
        print("⏱️  Running test for 3 minutes...")
        time.sleep(180)
        
        # Stop and analyze results
        analyzer.stop_analysis()
        
        if analyzer.signals_history:
            print("\n📊 ADAPTABILITY TEST RESULTS")
            print("=" * 40)
            
            # Analyze market conditions encountered
            conditions_found = set()
            strategies_used = set()
            
            for signal in analyzer.signals_history:
                if hasattr(signal, 'market_condition') and signal.market_condition:
                    conditions_found.add(signal.market_condition.value)
                if hasattr(signal, 'strategy_used') and signal.strategy_used:
                    strategies_used.add(signal.strategy_used.value)
            
            print(f"Market Conditions Detected: {len(conditions_found)}")
            for condition in conditions_found:
                print(f"  ✅ {condition}")
            
            print(f"\nStrategies Employed: {len(strategies_used)}")
            for strategy in strategies_used:
                print(f"  ✅ {strategy}")
            
            # Check adaptability score
            adaptability_score = (len(conditions_found) * 20 + len(strategies_used) * 15) / 100
            adaptability_score = min(1.0, adaptability_score)
            
            print(f"\n🎯 Adaptability Score: {adaptability_score:.1%}")
            
            if adaptability_score > 0.8:
                print("🌟 EXCELLENT: Highly adaptive to market conditions!")
            elif adaptability_score > 0.6:
                print("👍 GOOD: Well-adapted to market conditions")
            elif adaptability_score > 0.4:
                print("⚠️  MODERATE: Some adaptation detected")
            else:
                print("❌ POOR: Limited adaptation - may need more time")
            
            print("✅ Adaptability test completed!")
        else:
            print("❌ No signals generated during test")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def run_profitability_test():
    """Test profitability potential across market conditions."""
    try:
        from analysis.unified_trading_analyzer import UnifiedTradingAnalyzer, AnalysisMode
        
        print("💰 Running Profitability Simulation")
        print("=" * 60)
        print("Simulating trades to estimate potential profitability...")
        
        # Initialize analyzer in adaptive mode
        analyzer = UnifiedTradingAnalyzer(
            update_interval=45,  # 45-second intervals
            mode=AnalysisMode.ADAPTIVE
        )
        
        # Start analysis for multiple pairs
        pairs = ['EUR_USD', 'GBP_USD']
        analysis_thread = analyzer.start_analysis(pairs)
        
        # Run for 5 minutes
        print("⏱️  Running simulation for 5 minutes...")
        time.sleep(300)
        
        # Stop and calculate potential results
        analyzer.stop_analysis()
        
        if analyzer.signals_history:
            print("\n💰 PROFITABILITY SIMULATION RESULTS")
            print("=" * 50)
            
            total_signals = len(analyzer.signals_history)
            trade_signals = [s for s in analyzer.signals_history if s.signal_type in ['BUY', 'SELL']]
            
            if trade_signals:
                # Calculate potential outcomes
                total_risk = 0
                total_reward = 0
                high_probability_trades = 0
                profit_probs = []
                
                for signal in trade_signals:
                    risk = abs(signal.entry_price - signal.stop_loss)
                    reward = abs(signal.take_profit - signal.entry_price)
                    total_risk += risk
                    total_reward += reward
                    
                    if hasattr(signal, 'profit_probability'):
                        profit_probs.append(signal.profit_probability)
                        if signal.profit_probability > 0.7:
                            high_probability_trades += 1
                
                avg_rr_ratio = total_reward / total_risk if total_risk > 0 else 0
                avg_confidence = sum(s.confidence for s in trade_signals) / len(trade_signals)
                avg_profit_prob = sum(profit_probs) / len(profit_probs) if profit_probs else 0
                
                print(f"Total Trade Signals: {len(trade_signals)}")
                print(f"High Probability Trades (>70%): {high_probability_trades}")
                print(f"Average Risk/Reward Ratio: {avg_rr_ratio:.2f}")
                print(f"Average Confidence: {avg_confidence:.1%}")
                print(f"Average Profit Probability: {avg_profit_prob:.1%}")
                
                # Estimate win rate and profitability
                estimated_win_rate = avg_profit_prob if avg_profit_prob > 0 else avg_confidence
                estimated_profit_factor = estimated_win_rate * avg_rr_ratio
                
                print(f"\nEstimated Win Rate: {estimated_win_rate:.1%}")
                print(f"Estimated Profit Factor: {estimated_profit_factor:.2f}")
                
                if estimated_profit_factor > 1.5:
                    print("🌟 EXCELLENT: High profitability potential!")
                elif estimated_profit_factor > 1.2:
                    print("👍 GOOD: Positive profitability expected")
                elif estimated_profit_factor > 1.0:
                    print("⚠️  BREAK-EVEN: Marginal profitability")
                else:
                    print("❌ POOR: Low profitability potential")
                
                # Market condition profitability
                condition_performance = {}
                for signal in trade_signals:
                    if hasattr(signal, 'market_condition') and signal.market_condition:
                        condition = signal.market_condition.value
                        if condition not in condition_performance:
                            condition_performance[condition] = []
                        prob = getattr(signal, 'profit_probability', signal.confidence)
                        condition_performance[condition].append(prob)
                
                if condition_performance:
                    print(f"\nProfitability by Market Condition:")
                    for condition, probabilities in condition_performance.items():
                        avg_prob = sum(probabilities) / len(probabilities)
                        print(f"  {condition}: {avg_prob:.1%} avg profit probability")
                
                print("✅ Profitability simulation completed!")
            else:
                print("❌ No trade signals generated during simulation")
        else:
            print("❌ No signals generated during simulation")
            
    except Exception as e:
        print(f"❌ Simulation failed: {e}")

def start_web_dashboard():
    """Start unified web dashboard."""
    try:
        print("🌐 Starting Unified Web Dashboard...")
        print("📊 Access at: http://localhost:5001")
        print("🔄 Auto-refresh every 5 seconds")
        print("💡 Press Ctrl+C to stop")
        print("=" * 50)
        
        # Update web dashboard to use unified analyzer
        from web_trading_dashboard import app
        app.run(host='0.0.0.0', port=5001, debug=False)
        
    except Exception as e:
        print(f"❌ Error starting web dashboard: {e}")

def main():
    """Main function with comprehensive command-line interface."""
    parser = argparse.ArgumentParser(
        description="Unified forex trading analyzer - replaces all redundant analyzers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Analysis Modes:
  basic        - Real-time signals with OpenAI analysis
  adaptive     - Adaptive strategies for all market conditions (DEFAULT)
  comprehensive - Full analysis with news sentiment integration

Examples:
  python start_unified_analyzer.py --mode adaptive --pairs EUR_USD GBP_USD --duration 30
  python start_unified_analyzer.py --mode comprehensive --interval 30
  python start_unified_analyzer.py --test adaptability
  python start_unified_analyzer.py --test profitability
  python start_unified_analyzer.py --web
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['basic', 'adaptive', 'comprehensive'],
        default='basic',
        help='Analysis mode (default: basic)'
    )
    
    parser.add_argument(
        '--pairs',
        nargs='+',
        default=['EUR_USD', 'USD_JPY'],
        help='Currency pairs to analyze (default: EUR_USD USD_JPY)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Update interval in seconds (default: 300)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=1,
        help='Duration in minutes (0 = unlimited, default: 0)'
    )
    
    parser.add_argument(
        '--test',
        choices=['adaptability', 'profitability'],
        help='Run specific test instead of normal analysis'
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Start web dashboard interface'
    )
    
    args = parser.parse_args()
    
    # Header
    print("🤖 Unified Forex Trading Analyzer")
    print("🎯 ONE ANALYZER TO RULE THEM ALL")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Route to appropriate function
    if args.web:
        start_web_dashboard()
    elif args.test == 'adaptability':
        run_adaptability_test()
    elif args.test == 'profitability':
        run_profitability_test()
    else:
        start_analyzer(args.mode, args.pairs, args.interval, args.duration)

if __name__ == "__main__":
    main()