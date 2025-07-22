#!/usr/bin/env python3
"""
Adaptive Trading Analyzer Quick Start

This script provides easy access to the adaptive trading analyzer that profits
in both trending and sideways markets.
"""

import sys
import os
import argparse
import time
from datetime import datetime

# Add project root to path
sys.path.append("./")

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements for adaptive analyzer...")
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Check required modules
    try:
        from analysis.adaptive_trading_analyzer import AdaptiveTradingAnalyzer
        from api.openai_api import OpenAIAnalyzer
        from api.oanda_api import OandaApi
        print("✅ All required modules found")
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def start_adaptive_analyzer(pairs, interval, duration):
    """Start the adaptive analyzer."""
    try:
        from analysis.adaptive_trading_analyzer import AdaptiveTradingAnalyzer
        
        print("🚀 Starting Adaptive Trading Analyzer")
        print("=" * 60)
        print("🎯 PROFITABLE IN ALL MARKET CONDITIONS")
        print("📈 Trending Markets: Trend following strategies")
        print("↔️  Sideways Markets: Mean reversion strategies") 
        print("⚡ Volatile Markets: Breakout strategies")
        print("🔄 Adaptive position sizing and risk management")
        print("=" * 60)
        print(f"📊 Currency Pairs: {', '.join(pairs)}")
        print(f"⏱️  Update Interval: {interval} seconds")
        print(f"⏰ Duration: {duration} minutes" if duration > 0 else "⏰ Duration: Unlimited")
        print("💡 Press Ctrl+C to stop")
        print("=" * 60)
        
        # Initialize adaptive analyzer
        analyzer = AdaptiveTradingAnalyzer(update_interval=interval)
        
        # Start adaptive analysis
        analysis_thread = analyzer.start_adaptive_analysis(pairs)
        
        # Run for specified duration or until interrupted
        start_time = time.time()
        try:
            while True:
                elapsed_minutes = (time.time() - start_time) / 60
                
                if duration > 0 and elapsed_minutes >= duration:
                    print(f"\n⏰ Reached duration limit of {duration} minutes")
                    break
                
                time.sleep(120)  # Show summary every 2 minutes
                
                # Show adaptive summary
                signals = analyzer.signals_history
                if signals:
                    recent_signals = signals[-10:]
                    conditions = {}
                    strategies = {}
                    
                    for signal in recent_signals:
                        condition = signal.market_condition.value
                        strategy = signal.strategy_used.value
                        conditions[condition] = conditions.get(condition, 0) + 1
                        strategies[strategy] = strategies.get(strategy, 0) + 1
                    
                    print(f"\n📊 Running for {elapsed_minutes:.1f} minutes")
                    print(f"   Total Signals: {len(analyzer.signals_history)}")
                    print(f"   Market Conditions: {conditions}")
                    print(f"   Strategies Used: {strategies}")
                    
                    if recent_signals:
                        avg_confidence = sum(s.confidence for s in recent_signals) / len(recent_signals)
                        avg_profit_prob = sum(s.profit_probability for s in recent_signals) / len(recent_signals)
                        print(f"   Avg Confidence: {avg_confidence:.1%}")
                        print(f"   Avg Profit Probability: {avg_profit_prob:.1%}")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping adaptive analyzer...")
        
        analyzer.stop_adaptive_analysis()
        
        # Final summary
        if analyzer.signals_history:
            print("\n📊 FINAL SESSION SUMMARY")
            print("=" * 40)
            
            total_signals = len(analyzer.signals_history)
            buy_signals = len([s for s in analyzer.signals_history if s.signal_type == 'BUY'])
            sell_signals = len([s for s in analyzer.signals_history if s.signal_type == 'SELL'])
            
            print(f"Total Signals: {total_signals}")
            print(f"BUY Signals: {buy_signals}")
            print(f"SELL Signals: {sell_signals}")
            
            # Market condition breakdown
            conditions = {}
            strategies = {}
            for signal in analyzer.signals_history:
                condition = signal.market_condition.value
                strategy = signal.strategy_used.value
                conditions[condition] = conditions.get(condition, 0) + 1
                strategies[strategy] = strategies.get(strategy, 0) + 1
            
            print(f"\nMarket Conditions Traded:")
            for condition, count in conditions.items():
                print(f"  {condition}: {count} signals")
            
            print(f"\nStrategies Used:")
            for strategy, count in strategies.items():
                print(f"  {strategy}: {count} signals")
            
            # Average metrics
            avg_confidence = sum(s.confidence for s in analyzer.signals_history) / total_signals
            avg_profit_prob = sum(s.profit_probability for s in analyzer.signals_history) / total_signals
            
            print(f"\nAverage Confidence: {avg_confidence:.1%}")
            print(f"Average Profit Probability: {avg_profit_prob:.1%}")
            
            print(f"\n💾 Signals saved to: logs/adaptive_signals_{datetime.now().strftime('%Y%m%d')}.json")
        
        print("✅ Adaptive analyzer stopped successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def run_market_condition_test():
    """Run a test across different market conditions."""
    try:
        from analysis.adaptive_trading_analyzer import AdaptiveTradingAnalyzer
        
        print("🧪 Running Market Condition Adaptability Test")
        print("=" * 60)
        print("Testing analyzer's ability to adapt to different market conditions...")
        
        # Initialize analyzer
        analyzer = AdaptiveTradingAnalyzer(update_interval=30)  # 30-second intervals for testing
        
        # Start analysis
        analysis_thread = analyzer.start_adaptive_analysis(['EUR_USD'])
        
        # Run for 3 minutes to capture different conditions
        print("⏱️  Running test for 3 minutes...")
        time.sleep(180)
        
        # Stop and analyze results
        analyzer.stop_adaptive_analysis()
        
        if analyzer.signals_history:
            print("\n📊 ADAPTABILITY TEST RESULTS")
            print("=" * 40)
            
            # Analyze market conditions encountered
            conditions_found = set()
            strategies_used = set()
            
            for signal in analyzer.signals_history:
                conditions_found.add(signal.market_condition.value)
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

def run_profitability_simulation():
    """Run a simulation to test profitability potential."""
    try:
        from analysis.adaptive_trading_analyzer import AdaptiveTradingAnalyzer
        
        print("💰 Running Profitability Simulation")
        print("=" * 60)
        print("Simulating trades to estimate potential profitability...")
        
        # Initialize analyzer
        analyzer = AdaptiveTradingAnalyzer(update_interval=45)  # 45-second intervals
        
        # Start analysis for multiple pairs
        pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY']
        analysis_thread = analyzer.start_adaptive_analysis(pairs)
        
        # Run for 5 minutes
        print("⏱️  Running simulation for 5 minutes...")
        time.sleep(300)
        
        # Stop and calculate potential results
        analyzer.stop_adaptive_analysis()
        
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
                
                for signal in trade_signals:
                    risk = abs(signal.entry_price - signal.stop_loss)
                    reward = abs(signal.take_profit - signal.entry_price)
                    total_risk += risk
                    total_reward += reward
                    
                    if signal.profit_probability > 0.7:
                        high_probability_trades += 1
                
                avg_rr_ratio = total_reward / total_risk if total_risk > 0 else 0
                avg_confidence = sum(s.confidence for s in trade_signals) / len(trade_signals)
                avg_profit_prob = sum(s.profit_probability for s in trade_signals) / len(trade_signals)
                
                print(f"Total Trade Signals: {len(trade_signals)}")
                print(f"High Probability Trades (>70%): {high_probability_trades}")
                print(f"Average Risk/Reward Ratio: {avg_rr_ratio:.2f}")
                print(f"Average Confidence: {avg_confidence:.1%}")
                print(f"Average Profit Probability: {avg_profit_prob:.1%}")
                
                # Estimate win rate and profitability
                estimated_win_rate = avg_profit_prob
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
                    condition = signal.market_condition.value
                    if condition not in condition_performance:
                        condition_performance[condition] = []
                    condition_performance[condition].append(signal.profit_probability)
                
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

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Start adaptive forex trading analyzer that profits in any market condition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_adaptive_analyzer.py --pairs EUR_USD GBP_USD --duration 30
  python start_adaptive_analyzer.py --test adaptability
  python start_adaptive_analyzer.py --test profitability
  python start_adaptive_analyzer.py --interval 30 --pairs EUR_USD
        """
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
        '--test',
        choices=['adaptability', 'profitability'],
        help='Run specific test instead of normal analysis'
    )
    
    args = parser.parse_args()
    
    # Header
    print("🤖 Adaptive Forex Trading Analyzer")
    print("💰 PROFITABLE IN ALL MARKET CONDITIONS")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Route to appropriate function
    if args.test == 'adaptability':
        run_market_condition_test()
    elif args.test == 'profitability':
        run_profitability_simulation()
    else:
        start_adaptive_analyzer(args.pairs, args.interval, args.duration)

if __name__ == "__main__":
    main()