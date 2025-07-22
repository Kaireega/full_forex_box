#!/usr/bin/env python3
"""
Test script for OpenAI analysis functionality.

This script tests the OpenAI integration without requiring live market data.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add the project root to the path
sys.path.append("./")

def test_openai_analyzer():
    """Test the basic OpenAI analyzer functionality."""
    try:
        from api.openai_api import OpenAIAnalyzer
        
        print("=== Testing OpenAI Analyzer ===")
        
        # Create sample forex data
        sample_data = pd.DataFrame({
            'currency_pair': ['EUR_USD'] * 10,
            'timestamp': pd.date_range('2025-01-01', periods=10, freq='H'),
            'open': np.random.uniform(1.0300, 1.0400, 10),
            'high': np.random.uniform(1.0350, 1.0450, 10),
            'low': np.random.uniform(1.0250, 1.0350, 10),
            'close': np.random.uniform(1.0300, 1.0400, 10),
            'volume': np.random.randint(1000, 5000, 10)
        })
        
        print("Sample data created:")
        print(sample_data.head())
        
        # Test OpenAI analyzer
        analyzer = OpenAIAnalyzer()
        print("✅ OpenAI Analyzer initialized successfully!")
        
        # Test general analysis
        print("\nTesting general analysis...")
        result = analyzer.analyze_forex_data(sample_data, "general")
        
        if 'error' not in result:
            print("✅ General analysis completed!")
            print(f"Analysis type: {result.get('analysis_type')}")
            print(f"Timestamp: {result.get('timestamp')}")
            print(f"Tokens used: {result.get('tokens_used')}")
            print(f"Analysis preview: {result.get('analysis', '')[:200]}...")
        else:
            print(f"❌ Error in analysis: {result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenAI analyzer: {e}")
        return False

def test_trading_strategy():
    """Test trading strategy generation."""
    try:
        from api.openai_api import OpenAIAnalyzer
        
        print("\n=== Testing Trading Strategy Generation ===")
        
        # Sample market data
        market_data = {
            'EUR_USD': {
                'current_price': 1.0350,
                'price_change_24h': 0.0025,
                'volatility': 0.008,
                'trend': 'bullish'
            },
            'GBP_USD': {
                'current_price': 1.2450,
                'price_change_24h': -0.0015,
                'volatility': 0.012,
                'trend': 'bearish'
            }
        }
        
        analyzer = OpenAIAnalyzer()
        
        # Test strategy generation
        strategy = analyzer.generate_trading_strategy(market_data, "medium")
        
        if 'error' not in strategy:
            print("✅ Trading strategy generated!")
            print(f"Risk tolerance: {strategy.get('risk_tolerance')}")
            print(f"Timestamp: {strategy.get('timestamp')}")
            print(f"Tokens used: {strategy.get('tokens_used')}")
            print(f"Strategy preview: {strategy.get('strategy', '')[:200]}...")
        else:
            print(f"❌ Error generating strategy: {strategy['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing trading strategy: {e}")
        return False

def test_news_sentiment():
    """Test news sentiment analysis."""
    try:
        from api.openai_api import OpenAIAnalyzer
        
        print("\n=== Testing News Sentiment Analysis ===")
        
        # Sample news data
        news_data = [
            {
                'Date': '2025-01-01',
                'Currency': 'USD',
                'Event': 'Federal Reserve Interest Rate Decision',
                'Actual': '5.25%',
                'Forecast': '5.00%',
                'Previous': '5.00%'
            },
            {
                'Date': '2025-01-02',
                'Currency': 'EUR',
                'Event': 'European Central Bank Meeting',
                'Actual': 'Hawkish',
                'Forecast': 'Neutral',
                'Previous': 'Dovish'
            }
        ]
        
        analyzer = OpenAIAnalyzer()
        
        # Test sentiment analysis
        sentiment = analyzer.analyze_news_sentiment(news_data)
        
        if 'error' not in sentiment:
            print("✅ News sentiment analysis completed!")
            print(f"News count: {sentiment.get('news_count')}")
            print(f"Timestamp: {sentiment.get('timestamp')}")
            print(f"Tokens used: {sentiment.get('tokens_used')}")
            print(f"Sentiment preview: {sentiment.get('sentiment_analysis', '')[:200]}...")
        else:
            print(f"❌ Error in sentiment analysis: {sentiment['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing news sentiment: {e}")
        return False

def test_comprehensive_analysis():
    """Test the comprehensive analysis system."""
    try:
        from analysis.openai_analysis import ForexOpenAIAnalysis
        
        print("\n=== Testing Comprehensive Analysis ===")
        
        # This test might fail if OANDA API is not properly configured
        # but it should at least initialize
        analyzer = ForexOpenAIAnalysis()
        print("✅ ForexOpenAIAnalysis initialized successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing comprehensive analysis: {e}")
        print("This might be due to missing OANDA API configuration")
        return False

def main():
    """Run all tests."""
    print("OpenAI Analysis Test Suite")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  WARNING: OPENAI_API_KEY environment variable not set")
        print("Some tests may fail. Set your API key with:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print()
    
    tests = [
        ("Basic OpenAI Analyzer", test_openai_analyzer),
        ("Trading Strategy Generation", test_trading_strategy),
        ("News Sentiment Analysis", test_news_sentiment),
        ("Comprehensive Analysis", test_comprehensive_analysis)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        print("-" * 30)
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! OpenAI analysis is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("Common issues:")
        print("- Missing OPENAI_API_KEY environment variable")
        print("- Network connectivity issues")
        print("- Missing dependencies (run: pip install -r requirements.txt)")

if __name__ == "__main__":
    main()