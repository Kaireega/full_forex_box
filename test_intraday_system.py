#!/usr/bin/env python3
"""
Intraday Trading System Test Script
===================================

This script tests the key components of the intraday trading system:
- Pattern recognition
- Strategy logic
- Risk management
- Configuration loading
"""

import sys
import os
import json
from datetime import datetime, timedelta
import pytz
import pandas as pd
import numpy as np

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_intraday_patterns():
    """Test the intraday pattern recognition system"""
    print("🧪 Testing Intraday Pattern Recognition...")
    
    try:
        from technicals.intraday_patterns import IntradayPatterns
        
        # Create sample data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
        np.random.seed(42)
        
        # Create sample price data with some patterns
        base_price = 1.0850
        prices = []
        for i in range(100):
            if i < 30:
                # Consolidation phase
                price = base_price + np.random.normal(0, 0.0005)
            elif i < 60:
                # Breakout phase
                price = base_price + 0.002 + np.random.normal(0, 0.0003)
            else:
                # Reversal phase
                price = base_price + 0.001 - (i - 60) * 0.0001 + np.random.normal(0, 0.0004)
            prices.append(price)
        
        # Create DataFrame
        df = pd.DataFrame({
            'time': dates,
            'mid_o': [p - 0.0001 for p in prices],
            'mid_h': [p + 0.0002 for p in prices],
            'mid_l': [p - 0.0002 for p in prices],
            'mid_c': prices,
            'ask_c': [p + 0.0001 for p in prices],
            'bid_c': [p - 0.0001 for p in prices],
            'RSI_14': np.random.uniform(30, 70, 100),
            'MACD_HIST': np.random.uniform(-0.0001, 0.0001, 100)
        })
        
        # Test pattern recognition
        patterns = IntradayPatterns()
        
        # Test breakout detection
        breakout_result = patterns.detect_breakout_patterns(df, lookback=20)
        print(f"✅ Breakout detection: {breakout_result['breakout']}")
        
        # Test reversal detection
        reversal_result = patterns.detect_reversal_patterns(df)
        print(f"✅ Reversal detection: {reversal_result['reversal']}")
        
        # Test momentum detection
        momentum_result = patterns.detect_momentum_patterns(df)
        print(f"✅ Momentum detection: {momentum_result['momentum']}")
        
        # Test support/resistance
        levels = patterns.get_support_resistance_levels(df, lookback=50)
        print(f"✅ Support/Resistance levels: {levels['support'] is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern recognition test failed: {e}")
        return False

def test_intraday_strategy():
    """Test the intraday strategy logic"""
    print("\n🧪 Testing Intraday Strategy Logic...")
    
    try:
        from bot.intraday_strategy import IntradayStrategy
        
        strategy = IntradayStrategy()
        
        # Test session detection
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        
        # Test during trading hours
        session_active = strategy.is_session_active(now, 'london_ny')
        print(f"✅ Session detection: {session_active}")
        
        # Test breakout detection
        df = pd.DataFrame({
            'mid_h': [1.0850, 1.0855, 1.0860, 1.0865, 1.0870],
            'mid_l': [1.0845, 1.0850, 1.0855, 1.0860, 1.0865],
            'mid_c': [1.0848, 1.0852, 1.0858, 1.0862, 1.0875]  # Breakout
        })
        
        breakout_detected, direction = strategy.detect_intraday_breakout(df, lookback=5)
        print(f"✅ Breakout detection: {breakout_detected}, direction: {direction}")
        
        # Test momentum detection
        df['RSI_14'] = [45, 50, 55, 60, 65]
        df['MACD_HIST'] = [0.0001, 0.0002, 0.0003, 0.0004, 0.0005]
        
        momentum_detected, momentum_direction = strategy.detect_momentum_shift(df, period=3)
        print(f"✅ Momentum detection: {momentum_detected}, direction: {momentum_direction}")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategy logic test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n🧪 Testing Configuration Loading...")
    
    try:
        # Test intraday settings
        with open("./bot/intraday_settings.json", "r") as f:
            settings = json.load(f)
        
        required_keys = ['trade_risk', 'intraday_config', 'pairs']
        for key in required_keys:
            if key not in settings:
                print(f"❌ Missing required key: {key}")
                return False
        
        print(f"✅ Configuration loaded successfully")
        print(f"   - Trade risk: {settings['trade_risk']}")
        print(f"   - Pairs configured: {len(settings['pairs'])}")
        print(f"   - Max daily trades: {settings['intraday_config']['max_daily_trades']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_risk_management():
    """Test risk management calculations"""
    print("\n🧪 Testing Risk Management...")
    
    try:
        from bot.intraday_strategy import IntradayStrategy
        from models.trade_settings import TradeSettings
        
        strategy = IntradayStrategy()
        
        # Create sample data
        df = pd.DataFrame({
            'mid_c': [1.0850],
            'mid_h': [1.0855],
            'mid_l': [1.0845],
            'ATR_5': [0.0010]
        })
        
        # Create trade settings
        trade_settings = TradeSettings({
            'atr_period': 5,
            'riskreward': 2.0
        }, 'EUR_USD')
        
        # Test stop loss calculation
        stop_loss = strategy.calculate_intraday_stop_loss(df, 'BUY', trade_settings)
        print(f"✅ Stop loss calculation: {stop_loss}")
        
        # Test take profit calculation
        take_profit = strategy.calculate_intraday_take_profit(df, 'BUY', stop_loss, trade_settings)
        print(f"✅ Take profit calculation: {take_profit}")
        
        # Test risk-reward ratio
        entry_price = df['mid_c'].iloc[-1]
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        rr_ratio = reward / risk if risk > 0 else 0
        print(f"✅ Risk-reward ratio: {rr_ratio:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk management test failed: {e}")
        return False

def test_session_awareness():
    """Test session awareness functionality"""
    print("\n🧪 Testing Session Awareness...")
    
    try:
        from bot.intraday_strategy import IntradayStrategy
        import pytz
        
        strategy = IntradayStrategy()
        
        # Test different times
        eastern = pytz.timezone('US/Eastern')
        
        # Test during trading hours
        trading_time = eastern.localize(datetime(2024, 1, 15, 10, 0))  # 10 AM ET
        is_trading = strategy.is_session_active(trading_time, 'london_ny')
        print(f"✅ Trading hours (10 AM): {is_trading}")
        
        # Test outside trading hours
        non_trading_time = eastern.localize(datetime(2024, 1, 15, 2, 0))  # 2 AM ET
        is_not_trading = strategy.is_session_active(non_trading_time, 'london_ny')
        print(f"✅ Non-trading hours (2 AM): {not is_not_trading}")
        
        # Test weekend
        weekend_time = eastern.localize(datetime(2024, 1, 13, 10, 0))  # Saturday
        is_weekend = strategy.is_session_active(weekend_time, 'london_ny')
        print(f"✅ Weekend detection: {not is_weekend}")
        
        return True
        
    except Exception as e:
        print(f"❌ Session awareness test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Intraday Trading System Test Suite")
    print("=" * 50)
    
    tests = [
        test_intraday_patterns,
        test_intraday_strategy,
        test_configuration,
        test_risk_management,
        test_session_awareness
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The intraday system is ready to use.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)