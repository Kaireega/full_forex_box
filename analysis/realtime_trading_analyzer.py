#!/usr/bin/env python3
"""
Real-time Minute-Based Trading Analyzer with OpenAI

This module provides minute-by-minute analysis for forex trading decisions,
focusing on entry and exit point predictions using OpenAI.
"""

import sys
import os
import time
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass

# Add project root to path
sys.path.append("../")

from api.openai_api import OpenAIAnalyzer
from api.oanda_api import OandaApi

@dataclass
class TradingSignal:
    """Data class for trading signals."""
    timestamp: str
    currency_pair: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD', 'EXIT'
    confidence: float  # 0.0 to 1.0
    entry_price: float
    stop_loss: float
    take_profit: float
    reasoning: str
    market_conditions: str
    risk_level: str  # 'LOW', 'MEDIUM', 'HIGH'

class RealtimeTradingAnalyzer:
    """Real-time minute-based trading analyzer using OpenAI."""
    
    def __init__(self, openai_api_key: Optional[str] = None, update_interval: int = 60):
        """
        Initialize the real-time analyzer.
        
        Args:
            openai_api_key: OpenAI API key
            update_interval: Update interval in seconds (default: 60 for 1-minute updates)
        """
        self.openai_analyzer = OpenAIAnalyzer(openai_api_key)
        self.oanda_api = OandaApi()
        self.update_interval = update_interval
        
        # Trading parameters
        self.currency_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD']
        self.analysis_history = {}
        self.signals_history = []
        self.is_running = False
        
        # Risk management settings
        self.max_risk_per_trade = 0.02  # 2% risk per trade
        self.max_concurrent_trades = 3
        self.min_confidence_threshold = 0.7
        
    def start_realtime_analysis(self, currency_pairs: List[str] = None):
        """Start real-time minute-based analysis."""
        if currency_pairs:
            self.currency_pairs = currency_pairs
            
        self.is_running = True
        
        print(f"🚀 Starting real-time trading analysis for: {', '.join(self.currency_pairs)}")
        print(f"📊 Update interval: {self.update_interval} seconds")
        print(f"🤖 Using OpenAI for trade predictions")
        print("=" * 60)
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        analysis_thread.start()
        
        return analysis_thread
    
    def stop_realtime_analysis(self):
        """Stop real-time analysis."""
        self.is_running = False
        print("🛑 Stopping real-time analysis...")
    
    def _analysis_loop(self):
        """Main analysis loop running every minute."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Analyze each currency pair
                for pair in self.currency_pairs:
                    self._analyze_currency_pair(pair)
                
                # Calculate sleep time to maintain exact intervals
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"❌ Error in analysis loop: {e}")
                time.sleep(5)  # Brief pause before retrying
    
    def _analyze_currency_pair(self, pair: str):
        """Analyze a specific currency pair for trading opportunities."""
        try:
            # Get recent market data
            market_data = self._get_market_data(pair)
            if not market_data:
                return
            
            # Perform OpenAI analysis
            signal = self._generate_trading_signal(pair, market_data)
            
            if signal:
                # Store signal
                self.signals_history.append(signal)
                
                # Keep only last 100 signals to manage memory
                if len(self.signals_history) > 100:
                    self.signals_history = self.signals_history[-100:]
                
                # Print signal if significant
                if signal.signal_type != 'HOLD' or signal.confidence > 0.8:
                    self._print_signal(signal)
                
                # Save to file for external monitoring
                self._save_signal_to_file(signal)
                
        except Exception as e:
            print(f"❌ Error analyzing {pair}: {e}")
    
    def _get_market_data(self, pair: str, lookback_minutes: int = 60) -> Optional[Dict]:
        """Get recent market data for analysis."""
        try:
            # Get minute-level candle data
            candles_df = self.oanda_api.get_candles_df(
                pair, 
                count=lookback_minutes, 
                granularity="M1"  # 1-minute candles
            )
            
            if candles_df is None or candles_df.empty:
                return None
            
            # Calculate technical indicators
            data = self._calculate_indicators(candles_df)
            
            # Add current market context
            current_price = float(candles_df.iloc[-1]['mid_c'])
            price_change = current_price - float(candles_df.iloc[-20]['mid_c'])  # 20-minute change
            volatility = float(candles_df['mid_c'].pct_change().rolling(20).std().iloc[-1])
            
            market_data = {
                'pair': pair,
                'current_price': current_price,
                'price_change_20m': price_change,
                'volatility': volatility,
                'candles': candles_df.tail(20).to_dict('records'),  # Last 20 minutes
                'indicators': data
            }
            
            return market_data
            
        except Exception as e:
            print(f"❌ Error getting market data for {pair}: {e}")
            return None
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators for analysis."""
        try:
            close_prices = df['mid_c'].astype(float)
            high_prices = df['mid_h'].astype(float)
            low_prices = df['mid_l'].astype(float)
            
            # Moving averages
            ma_5 = close_prices.rolling(5).mean().iloc[-1]
            ma_10 = close_prices.rolling(10).mean().iloc[-1]
            ma_20 = close_prices.rolling(20).mean().iloc[-1]
            
            # RSI (simplified)
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # MACD (simplified)
            ema_12 = close_prices.ewm(span=12).mean()
            ema_26 = close_prices.ewm(span=26).mean()
            macd_line = (ema_12 - ema_26).iloc[-1]
            
            # Bollinger Bands
            bb_middle = close_prices.rolling(20).mean().iloc[-1]
            bb_std = close_prices.rolling(20).std().iloc[-1]
            bb_upper = bb_middle + (2 * bb_std)
            bb_lower = bb_middle - (2 * bb_std)
            
            # Support and Resistance levels
            recent_highs = high_prices.tail(20)
            recent_lows = low_prices.tail(20)
            resistance = recent_highs.max()
            support = recent_lows.min()
            
            return {
                'ma_5': ma_5,
                'ma_10': ma_10,
                'ma_20': ma_20,
                'rsi': rsi,
                'macd': macd_line,
                'bb_upper': bb_upper,
                'bb_middle': bb_middle,
                'bb_lower': bb_lower,
                'resistance': resistance,
                'support': support,
                'current_price': close_prices.iloc[-1]
            }
            
        except Exception as e:
            print(f"❌ Error calculating indicators: {e}")
            return {}
    
    def _generate_trading_signal(self, pair: str, market_data: Dict) -> Optional[TradingSignal]:
        """Generate trading signal using OpenAI analysis."""
        try:
            # Prepare data for OpenAI
            analysis_prompt = self._create_trading_prompt(pair, market_data)
            
            # Get OpenAI analysis
            response = self.openai_analyzer.client.chat.completions.create(
                model=self.openai_analyzer.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert forex trading analyst. Analyze the provided market data and give specific trading recommendations with entry/exit points. 
                        
                        Respond in JSON format with:
                        {
                            "signal": "BUY|SELL|HOLD|EXIT",
                            "confidence": 0.0-1.0,
                            "entry_price": number,
                            "stop_loss": number,
                            "take_profit": number,
                            "reasoning": "detailed explanation",
                            "market_conditions": "current market state",
                            "risk_level": "LOW|MEDIUM|HIGH"
                        }"""
                    },
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            # Parse response
            ai_response = response.choices[0].message.content
            signal_data = json.loads(ai_response)
            
            # Create trading signal
            signal = TradingSignal(
                timestamp=datetime.now().isoformat(),
                currency_pair=pair,
                signal_type=signal_data['signal'],
                confidence=float(signal_data['confidence']),
                entry_price=float(signal_data['entry_price']),
                stop_loss=float(signal_data['stop_loss']),
                take_profit=float(signal_data['take_profit']),
                reasoning=signal_data['reasoning'],
                market_conditions=signal_data['market_conditions'],
                risk_level=signal_data['risk_level']
            )
            
            return signal
            
        except Exception as e:
            print(f"❌ Error generating signal for {pair}: {e}")
            return None
    
    def _create_trading_prompt(self, pair: str, market_data: Dict) -> str:
        """Create detailed prompt for OpenAI analysis."""
        indicators = market_data['indicators']
        current_price = market_data['current_price']
        
        prompt = f"""
        FOREX TRADING ANALYSIS REQUEST
        
        Currency Pair: {pair}
        Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Current Price: {current_price:.5f}
        
        TECHNICAL INDICATORS:
        - Moving Averages: MA5={indicators.get('ma_5', 0):.5f}, MA10={indicators.get('ma_10', 0):.5f}, MA20={indicators.get('ma_20', 0):.5f}
        - RSI: {indicators.get('rsi', 50):.2f}
        - MACD: {indicators.get('macd', 0):.5f}
        - Bollinger Bands: Upper={indicators.get('bb_upper', 0):.5f}, Middle={indicators.get('bb_middle', 0):.5f}, Lower={indicators.get('bb_lower', 0):.5f}
        - Support Level: {indicators.get('support', 0):.5f}
        - Resistance Level: {indicators.get('resistance', 0):.5f}
        
        MARKET CONTEXT:
        - 20-minute price change: {market_data['price_change_20m']:.5f}
        - Volatility: {market_data['volatility']:.5f}
        
        RECENT PRICE ACTION:
        {self._format_price_action(market_data['candles'])}
        
        TRADING REQUIREMENTS:
        1. Provide specific entry price (within 0.0005 pips of current price)
        2. Set stop loss (risk management - max 20 pips for majors)
        3. Set take profit (risk/reward ratio should be at least 1:1.5)
        4. Confidence level (only recommend trades with >70% confidence)
        5. Consider current market volatility for position sizing
        
        ANALYSIS FOCUS:
        - Identify immediate (1-5 minute) trading opportunities
        - Look for trend continuation or reversal signals
        - Consider support/resistance levels for entry/exit
        - Evaluate momentum indicators
        - Assess overall market sentiment
        
        Provide actionable trading recommendation with specific price levels.
        """
        
        return prompt
    
    def _format_price_action(self, candles: List[Dict]) -> str:
        """Format recent price action for analysis."""
        if not candles:
            return "No recent price data available"
        
        action_summary = []
        recent_candles = candles[-10:]  # Last 10 minutes
        
        for i, candle in enumerate(recent_candles):
            time_ago = len(recent_candles) - i
            direction = "🟢" if float(candle['mid_c']) > float(candle['mid_o']) else "🔴"
            action_summary.append(
                f"{time_ago}min ago: {direction} O:{candle['mid_o']} H:{candle['mid_h']} L:{candle['mid_l']} C:{candle['mid_c']}"
            )
        
        return "\n".join(action_summary)
    
    def _print_signal(self, signal: TradingSignal):
        """Print trading signal to console."""
        timestamp = datetime.fromisoformat(signal.timestamp).strftime('%H:%M:%S')
        
        # Choose emoji based on signal type
        signal_emoji = {
            'BUY': '🟢',
            'SELL': '🔴', 
            'HOLD': '🟡',
            'EXIT': '🚪'
        }
        
        print(f"\n{signal_emoji.get(signal.signal_type, '❓')} [{timestamp}] {signal.currency_pair} - {signal.signal_type}")
        print(f"   💡 Confidence: {signal.confidence:.1%}")
        print(f"   📍 Entry: {signal.entry_price:.5f}")
        print(f"   🛑 Stop Loss: {signal.stop_loss:.5f}")
        print(f"   🎯 Take Profit: {signal.take_profit:.5f}")
        print(f"   ⚠️  Risk Level: {signal.risk_level}")
        print(f"   📊 Market: {signal.market_conditions}")
        print(f"   🧠 Reasoning: {signal.reasoning[:100]}...")
    
    def _save_signal_to_file(self, signal: TradingSignal):
        """Save signal to JSON file for external monitoring."""
        try:
            signals_file = f"logs/trading_signals_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Ensure logs directory exists
            os.makedirs("logs", exist_ok=True)
            
            # Load existing signals
            signals = []
            if os.path.exists(signals_file):
                with open(signals_file, 'r') as f:
                    signals = json.load(f)
            
            # Add new signal
            signals.append({
                'timestamp': signal.timestamp,
                'currency_pair': signal.currency_pair,
                'signal_type': signal.signal_type,
                'confidence': signal.confidence,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'reasoning': signal.reasoning,
                'market_conditions': signal.market_conditions,
                'risk_level': signal.risk_level
            })
            
            # Save updated signals
            with open(signals_file, 'w') as f:
                json.dump(signals, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error saving signal to file: {e}")
    
    def get_current_signals(self) -> List[TradingSignal]:
        """Get current trading signals."""
        return self.signals_history[-10:] if self.signals_history else []
    
    def get_signal_summary(self) -> Dict:
        """Get summary of recent signals."""
        if not self.signals_history:
            return {"message": "No signals generated yet"}
        
        recent_signals = self.signals_history[-20:]  # Last 20 signals
        
        summary = {
            "total_signals": len(recent_signals),
            "signal_types": {},
            "average_confidence": 0,
            "high_confidence_signals": 0,
            "currency_pairs": {}
        }
        
        confidences = []
        
        for signal in recent_signals:
            # Count signal types
            summary["signal_types"][signal.signal_type] = summary["signal_types"].get(signal.signal_type, 0) + 1
            
            # Count currency pairs
            summary["currency_pairs"][signal.currency_pair] = summary["currency_pairs"].get(signal.currency_pair, 0) + 1
            
            # Collect confidences
            confidences.append(signal.confidence)
            
            # Count high confidence signals
            if signal.confidence >= 0.8:
                summary["high_confidence_signals"] += 1
        
        if confidences:
            summary["average_confidence"] = sum(confidences) / len(confidences)
        
        return summary

def main():
    """Example usage of the realtime trading analyzer."""
    try:
        print("🚀 Starting Real-time Forex Trading Analyzer with OpenAI")
        print("=" * 60)
        
        # Initialize analyzer
        analyzer = RealtimeTradingAnalyzer(update_interval=60)  # 1-minute updates
        
        # Start real-time analysis for major pairs
        major_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY']
        analysis_thread = analyzer.start_realtime_analysis(major_pairs)
        
        # Keep running and show periodic summaries
        try:
            while True:
                time.sleep(300)  # Show summary every 5 minutes
                
                summary = analyzer.get_signal_summary()
                print(f"\n📊 5-Minute Summary:")
                print(f"   Signals generated: {summary.get('total_signals', 0)}")
                print(f"   Average confidence: {summary.get('average_confidence', 0):.1%}")
                print(f"   High confidence signals: {summary.get('high_confidence_signals', 0)}")
                print(f"   Signal types: {summary.get('signal_types', {})}")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping analyzer...")
            analyzer.stop_realtime_analysis()
            
    except Exception as e:
        print(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()