#!/usr/bin/env python3
"""
Comprehensive Trading Strategy - Unified Intraday Trading System

This module combines all analysis logic into one comprehensive strategy:
- Technical analysis (indicators, patterns)
- Fundamental analysis (economic calendars, news)
- AI/ML analysis (OpenAI, pattern recognition)
- Risk management
- Position sizing
- Entry/exit logic

Designed for intraday trading patterns with real-time decision making.
"""

import sys
import os
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import threading
from queue import Queue

# Add project root to path
sys.path.append("../")

from technicals.indicators import TechnicalIndicators
from technicals.patterns import PatternRecognition
from api.oanda_api import OandaApi
from models.trade_decision import TradeDecision
from models.trade_settings import TradeSettings
import constants.defs as defs
from infrastructure.log_wrapper import LogWrapper

# Import analysis components
try:
    from analysis.unified_trading_analyzer import UnifiedTradingAnalyzer
    from analysis.realtime_trading_analyzer import RealtimeTradingAnalyzer
    from analysis.openai_analysis import OpenAIAnalyzer
    ANALYSIS_AVAILABLE = True
except ImportError as e:
    ANALYSIS_AVAILABLE = False
    print(f"⚠️  Some analysis components not available: {e}")

class StrategyMode(Enum):
    """Trading strategy modes."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"

class TimeFrame(Enum):
    """Trading timeframes."""
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"

class MarketCondition(Enum):
    """Market condition types."""
    TRENDING = "trending"
    VOLATILE = "volatile"
    SIDEWAYS = "sideways"
    RANGING = "ranging"

@dataclass
class SignalStrength:
    """Signal strength analysis."""
    technical_score: float  # 0-1
    fundamental_score: float  # 0-1
    ai_score: float  # 0-1
    pattern_score: float  # 0-1
    overall_score: float  # 0-1
    confidence: float  # 0-1
    risk_level: str  # "low", "medium", "high"

@dataclass
class ComprehensiveSignal:
    """Comprehensive trading signal."""
    timestamp: datetime
    pair: str
    signal_type: str  # "BUY", "SELL", "HOLD", "EXIT"
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    signal_strength: SignalStrength
    market_condition: MarketCondition
    reasoning: str
    risk_reward_ratio: float
    expected_duration: timedelta
    source_analysis: Dict[str, Any]

class ComprehensiveTradingStrategy:
    """
    Comprehensive trading strategy that combines all analysis methods.
    
    Features:
    - Multi-timeframe analysis
    - Technical indicator confluence
    - Pattern recognition
    - Fundamental analysis
    - AI/ML insights
    - Risk management
    - Position sizing
    - Real-time adaptation
    """
    
    def __init__(self, 
                 mode: StrategyMode = StrategyMode.MODERATE,
                 pairs: List[str] = None,
                 timeframes: List[TimeFrame] = None,
                 risk_per_trade: float = 0.02,
                 max_positions: int = 5):
        
        self.mode = mode
        self.pairs = pairs or ["EUR_USD", "GBP_USD", "USD_JPY", "USD_CAD", "AUD_USD"]
        self.timeframes = timeframes or [TimeFrame.M15, TimeFrame.H1, TimeFrame.H4]
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        
        # Initialize components
        self.logger = LogWrapper("ComprehensiveStrategy")
        self.api = OandaApi()
        self.indicators = TechnicalIndicators()
        self.patterns = PatternRecognition()
        
        # Analysis components
        self.unified_analyzer = None
        self.realtime_analyzer = None
        self.openai_analyzer = None
        
        if ANALYSIS_AVAILABLE:
            try:
                self.unified_analyzer = UnifiedTradingAnalyzer()
                self.realtime_analyzer = RealtimeTradingAnalyzer()
                self.openai_analyzer = OpenAIAnalyzer()
            except Exception as e:
                self.logger.warning(f"Some analysis components failed to initialize: {e}")
        
        # Strategy state
        self.is_running = False
        self.signals_history = []
        self.market_conditions = {}
        self.active_positions = {}
        self.performance_metrics = {}
        
        # Threading
        self.analysis_queue = Queue()
        self.signal_queue = Queue()
        self.stop_event = threading.Event()
        
        # Initialize strategy parameters based on mode
        self._initialize_strategy_parameters()
        
        self.logger.logger.info(f"Comprehensive Trading Strategy initialized in {mode.value} mode")
    
    def _initialize_strategy_parameters(self):
        """Initialize strategy parameters based on mode."""
        if self.mode == StrategyMode.CONSERVATIVE:
            self.min_signal_strength = 0.8
            self.min_risk_reward = 2.0
            self.max_daily_trades = 3
            self.position_sizing_multiplier = 0.5
            self.stop_loss_multiplier = 1.5
            
        elif self.mode == StrategyMode.MODERATE:
            self.min_signal_strength = 0.7
            self.min_risk_reward = 1.5
            self.max_daily_trades = 5
            self.position_sizing_multiplier = 1.0
            self.stop_loss_multiplier = 1.0
            
        elif self.mode == StrategyMode.AGGRESSIVE:
            self.min_signal_strength = 0.6
            self.min_risk_reward = 1.2
            self.max_daily_trades = 8
            self.position_sizing_multiplier = 1.5
            self.stop_loss_multiplier = 0.8
            
        else:  # ADAPTIVE
            self.min_signal_strength = 0.7
            self.min_risk_reward = 1.5
            self.max_daily_trades = 5
            self.position_sizing_multiplier = 1.0
            self.stop_loss_multiplier = 1.0
        
        # OpenAI calling parameters
        self.min_confidence_threshold = 0.7
        self.openai_call_cooldown = 300  # 5 minutes between OpenAI calls per pair
        self.last_openai_calls = {}  # Track last OpenAI call time per pair
        
        # Trade alerts
        self.trade_alerts = []
        self.max_trade_alerts = 10
    
    def start_strategy(self):
        """Start the comprehensive trading strategy."""
        if self.is_running:
            self.logger.warning("Strategy is already running")
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        # Start analysis threads
        self.analysis_thread = threading.Thread(target=self._analysis_worker, daemon=True)
        self.signal_thread = threading.Thread(target=self._signal_worker, daemon=True)
        
        self.analysis_thread.start()
        self.signal_thread.start()
        
        self.logger.logger.info("Comprehensive trading strategy started")
    
    def stop_strategy(self):
        """Stop the comprehensive trading strategy."""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        # Wait for threads to finish
        if hasattr(self, 'analysis_thread'):
            self.analysis_thread.join(timeout=5)
        if hasattr(self, 'signal_thread'):
            self.signal_thread.join(timeout=5)
        
        self.logger.logger.info("Comprehensive trading strategy stopped")
    
    def _analysis_worker(self):
        """Worker thread for continuous market analysis."""
        while not self.stop_event.is_set():
            try:
                for pair in self.pairs:
                    if self.stop_event.is_set():
                        break
                    
                    # Analyze market conditions
                    market_condition = self._analyze_market_condition(pair)
                    self.market_conditions[pair] = market_condition
                    
                    # Generate comprehensive signal
                    signal = self._generate_comprehensive_signal(pair, market_condition)
                    
                    if signal and signal.signal_strength.overall_score >= self.min_signal_strength:
                        self.signal_queue.put(signal)
                
                # Adaptive mode adjustments
                if self.mode == StrategyMode.ADAPTIVE:
                    self._adapt_strategy_parameters()
                
                time.sleep(30)  # Analysis interval
                
            except Exception as e:
                self.logger.logger.error(f"Error in analysis worker: {e}")
                time.sleep(60)
    
    def _signal_worker(self):
        """Worker thread for signal processing and trade execution."""
        while not self.stop_event.is_set():
            try:
                if not self.signal_queue.empty():
                    signal = self.signal_queue.get(timeout=1)
                    
                    # Validate signal
                    if self._validate_signal(signal):
                        # Execute trade
                        self._execute_signal(signal)
                    
                    # Add to history
                    self.signals_history.append(signal)
                    
                    # Limit history size
                    if len(self.signals_history) > 1000:
                        self.signals_history = self.signals_history[-500:]
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.logger.error(f"Error in signal worker: {e}")
                time.sleep(5)
    
    def _analyze_market_condition(self, pair: str) -> MarketCondition:
        """Analyze current market condition for a pair."""
        try:
            # Get recent candles for analysis
            candles = self.api.get_candles_df(pair, granularity='H1', count=100)
            if candles is None or candles.empty:
                return MarketCondition.SIDEWAYS
            
            # Calculate volatility
            returns = candles['mid_c'].pct_change().dropna()
            volatility = returns.std()
            
            # Calculate trend strength
            sma_20 = candles['mid_c'].rolling(20).mean()
            sma_50 = candles['mid_c'].rolling(50).mean()
            trend_strength = abs(sma_20.iloc[-1] - sma_50.iloc[-1]) / sma_50.iloc[-1]
            
            # Determine market condition
            if volatility > 0.02:  # High volatility
                if trend_strength > 0.01:  # Strong trend
                    return MarketCondition.TRENDING
                else:
                    return MarketCondition.VOLATILE
            else:  # Low volatility
                if trend_strength > 0.005:  # Weak trend
                    return MarketCondition.SIDEWAYS
                else:
                    return MarketCondition.RANGING
                    
        except Exception as e:
            self.logger.logger.error(f"Error analyzing market condition for {pair}: {e}")
            return MarketCondition.SIDEWAYS
    
    def _process_candles(self, candles: List[Dict]) -> pd.DataFrame:
        """Process candle data into DataFrame with indicators."""
        df = pd.DataFrame(candles)
        df['time'] = pd.to_datetime(df['time'])
        df['open'] = df['mid'].apply(lambda x: float(x['o']))
        df['high'] = df['mid'].apply(lambda x: float(x['h']))
        df['low'] = df['mid'].apply(lambda x: float(x['l']))
        df['close'] = df['mid'].apply(lambda x: float(x['c']))
        df['volume'] = df['volume'].astype(float)
        
        # Add technical indicators
        df = self.indicators.add_all_indicators(df)
        
        return df
    
    def _analyze_trend(self, price_data: Dict[TimeFrame, pd.DataFrame]) -> Dict[str, float]:
        """Analyze trend across timeframes."""
        trend_scores = {}
        
        for tf, df in price_data.items():
            if len(df) < 20:
                continue
            
            # EMA trend analysis
            ema_20 = df['ema_20'].iloc[-1]
            ema_50 = df['ema_50'].iloc[-1]
            ema_200 = df['ema_200'].iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Trend scoring
            trend_score = 0.0
            
            # Price vs EMAs
            if current_price > ema_20 > ema_50 > ema_200:
                trend_score += 0.4  # Strong bullish
            elif current_price > ema_20 > ema_50:
                trend_score += 0.2  # Moderate bullish
            elif current_price < ema_20 < ema_50 < ema_200:
                trend_score -= 0.4  # Strong bearish
            elif current_price < ema_20 < ema_50:
                trend_score -= 0.2  # Moderate bearish
            
            # MACD trend
            if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
                trend_score += 0.2
            else:
                trend_score -= 0.2
            
            # RSI trend
            rsi = df['rsi'].iloc[-1]
            if 40 < rsi < 60:
                trend_score += 0.1  # Neutral
            elif rsi > 60:
                trend_score += 0.1  # Bullish
            else:
                trend_score -= 0.1  # Bearish
            
            trend_scores[tf.value] = np.clip(trend_score, -1, 1)
        
        return trend_scores
    
    def _analyze_volatility(self, price_data: Dict[TimeFrame, pd.DataFrame]) -> Dict[str, float]:
        """Analyze volatility across timeframes."""
        volatility_scores = {}
        
        for tf, df in price_data.items():
            if len(df) < 20:
                continue
            
            # ATR-based volatility
            atr = df['atr'].iloc[-1]
            avg_atr = df['atr'].rolling(20).mean().iloc[-1]
            
            if avg_atr > 0:
                volatility_ratio = atr / avg_atr
                volatility_scores[tf.value] = np.clip(volatility_ratio, 0, 2)
            else:
                volatility_scores[tf.value] = 0.5
        
        return volatility_scores
    
    def _analyze_momentum(self, price_data: Dict[TimeFrame, pd.DataFrame]) -> Dict[str, float]:
        """Analyze momentum across timeframes."""
        momentum_scores = {}
        
        for tf, df in price_data.items():
            if len(df) < 20:
                continue
            
            # RSI momentum
            rsi = df['rsi'].iloc[-1]
            rsi_momentum = (rsi - 50) / 50  # -1 to 1 scale
            
            # MACD momentum
            macd = df['macd'].iloc[-1]
            macd_signal = df['macd_signal'].iloc[-1]
            macd_momentum = (macd - macd_signal) / abs(macd_signal) if abs(macd_signal) > 0 else 0
            macd_momentum = np.clip(macd_momentum, -1, 1)
            
            # Stochastic momentum
            stoch_k = df['stoch_k'].iloc[-1]
            stoch_momentum = (stoch_k - 50) / 50  # -1 to 1 scale
            
            # Combined momentum
            momentum = (rsi_momentum + macd_momentum + stoch_momentum) / 3
            momentum_scores[tf.value] = np.clip(momentum, -1, 1)
        
        return momentum_scores
    
    def _analyze_strength(self, price_data: Dict[TimeFrame, pd.DataFrame]) -> Dict[str, float]:
        """Analyze market strength across timeframes."""
        strength_scores = {}
        
        for tf, df in price_data.items():
            if len(df) < 20:
                continue
            
            # Volume analysis
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(20).mean().iloc[-1]
            volume_strength = current_volume / avg_volume if avg_volume > 0 else 1.0
            volume_strength = np.clip(volume_strength, 0, 3)
            
            # Price strength (distance from moving averages)
            current_price = df['close'].iloc[-1]
            ema_20 = df['ema_20'].iloc[-1]
            ema_50 = df['ema_50'].iloc[-1]
            
            price_strength_20 = abs(current_price - ema_20) / ema_20 if ema_20 > 0 else 0
            price_strength_50 = abs(current_price - ema_50) / ema_50 if ema_50 > 0 else 0
            
            # Combined strength
            strength = (volume_strength + price_strength_20 + price_strength_50) / 3
            strength_scores[tf.value] = np.clip(strength, 0, 1)
        
        return strength_scores
    
    def _find_support_resistance(self, price_data: Dict[TimeFrame, pd.DataFrame]) -> Dict[str, List[float]]:
        """Find support and resistance levels."""
        all_highs = []
        all_lows = []
        
        for tf, df in price_data.items():
            if len(df) < 20:
                continue
            
            # Find recent highs and lows
            highs = df['high'].rolling(5, center=True).max()
            lows = df['low'].rolling(5, center=True).min()
            
            # Find pivot points
            for i in range(2, len(df) - 2):
                if df['high'].iloc[i] == highs.iloc[i]:
                    all_highs.append(df['high'].iloc[i])
                if df['low'].iloc[i] == lows.iloc[i]:
                    all_lows.append(df['low'].iloc[i])
        
        # Cluster levels
        support_levels = self._cluster_levels(all_lows, tolerance=0.001)
        resistance_levels = self._cluster_levels(all_highs, tolerance=0.001)
        
        # Key levels (round numbers, psychological levels)
        current_price = price_data[list(price_data.keys())[0]]['close'].iloc[-1]
        key_levels = self._find_key_levels(current_price)
        
        return {
            'support': support_levels,
            'resistance': resistance_levels,
            'key_levels': key_levels
        }
    
    def _cluster_levels(self, levels: List[float], tolerance: float) -> List[float]:
        """Cluster nearby levels together."""
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) <= tolerance:
                current_cluster.append(level)
            else:
                # Average the cluster
                clustered.append(np.mean(current_cluster))
                current_cluster = [level]
        
        # Add last cluster
        if current_cluster:
            clustered.append(np.mean(current_cluster))
        
        return clustered
    
    def _find_key_levels(self, current_price: float) -> List[float]:
        """Find key psychological levels near current price."""
        key_levels = []
        
        # Round numbers
        for i in range(-10, 11):
            level = round(current_price + i * 0.01, 2)
            if abs(level - current_price) <= 0.05:
                key_levels.append(level)
        
        # Major levels (0.5, 1.0, etc.)
        major_levels = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        for level in major_levels:
            if abs(level - current_price) <= 0.1:
                key_levels.append(level)
        
        return sorted(list(set(key_levels)))
    
    def _determine_trend(self, trend_analysis: Dict[str, float]) -> str:
        """Determine overall trend from timeframe analysis."""
        if not trend_analysis:
            return "sideways"
        
        avg_trend = np.mean(list(trend_analysis.values()))
        
        if avg_trend > 0.3:
            return "bullish"
        elif avg_trend < -0.3:
            return "bearish"
        else:
            return "sideways"
    
    def _generate_comprehensive_signal(self, pair: str, market_condition: MarketCondition) -> Optional[ComprehensiveSignal]:
        """Generate comprehensive trading signal for a pair."""
        try:
            # Get current price
            candles = self.api.get_candles_df(pair, granularity='M1', count=1)
            if candles is None or candles.empty:
                return None
            current_price = candles['mid_c'].iloc[-1]
            
            # Step 1: Get technical signals
            technical_signals = self._get_technical_signals(pair)
            
            # Step 2: Get pattern signals
            pattern_signals = self._get_pattern_signals(pair)
            
            # Step 3: Get fundamental signals
            fundamental_signals = self._get_fundamental_signals(pair)
            
            # Step 4: Check if conditions warrant OpenAI analysis
            should_call_openai = self._should_call_openai(
                technical_signals, pattern_signals, fundamental_signals, market_condition
            )
            
            # Step 5: Only call OpenAI if conditions are favorable
            if should_call_openai:
                ai_signals = self._get_ai_signals(pair, market_condition)
                self.logger.logger.info(f"🤖 OpenAI analysis called for {pair} - conditions favorable")
            else:
                ai_signals = {'openai': 'HOLD', 'ai_confidence': 0.5}
                self.logger.logger.info(f"⏸️  OpenAI analysis skipped for {pair} - conditions not favorable")
            
            # Step 6: Combine all signals
            combined_signal = self._combine_signals(
                technical_signals, pattern_signals, fundamental_signals, ai_signals
            )
            
            if not combined_signal or combined_signal == 'HOLD':
                return None
            
            # Step 7: Calculate signal strength
            signal_strength = self._calculate_signal_strength(
                technical_signals, pattern_signals, fundamental_signals, ai_signals
            )
            
            # Step 8: Check if signal is strong enough to alert
            if signal_strength.confidence >= self.min_confidence_threshold:
                # Determine entry, stop loss, and take profit
                entry_price = current_price
                stop_loss, take_profit = self._calculate_exit_levels(
                    pair, combined_signal, market_condition, current_price
                )
                
                # Calculate position size
                position_size = self._calculate_position_size(
                    pair, entry_price, stop_loss, signal_strength
                )
                
                # Calculate risk-reward ratio
                risk_reward_ratio = abs(take_profit - entry_price) / abs(stop_loss - entry_price)
                
                # Generate reasoning
                reasoning = self._generate_reasoning(
                    technical_signals, pattern_signals, fundamental_signals, ai_signals, market_condition
                )
                
                # Create signal
                signal = ComprehensiveSignal(
                    timestamp=datetime.now(),
                    pair=pair,
                    signal_type=combined_signal,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=position_size,
                    signal_strength=signal_strength,
                    market_condition=market_condition,
                    reasoning=reasoning,
                    risk_reward_ratio=risk_reward_ratio,
                    expected_duration=timedelta(hours=4),
                    source_analysis={
                        'technical': technical_signals,
                        'pattern': pattern_signals,
                        'fundamental': fundamental_signals,
                        'ai': ai_signals
                    }
                )
                
                # Add to trade alerts
                self._add_trade_alert(signal)
                
                return signal
            
            return None
            
        except Exception as e:
            self.logger.logger.error(f"Error generating comprehensive signal for {pair}: {e}")
            return None
    
    def _get_technical_signals(self, pair: str) -> Dict[str, Any]:
        """Get technical analysis signals."""
        signals = {}
        
        try:
            # Get price data for primary timeframe
            primary_tf = self.timeframes[0]
            candles = self.api.get_candles_df(pair, granularity=primary_tf.value, count=100)
            
            if candles is None or candles.empty:
                return signals
            
            # Calculate technical indicators
            from technicals.indicators import TechnicalIndicators
            technical_indicators = TechnicalIndicators()
            df = technical_indicators.calculate_all_indicators(candles)
            
            # RSI signals
            rsi = df['RSI'].iloc[-1] if 'RSI' in df.columns else 50
            if rsi < 30:
                signals['rsi'] = 'BUY'
            elif rsi > 70:
                signals['rsi'] = 'SELL'
            else:
                signals['rsi'] = 'HOLD'
            
            # MACD signals
            if 'MACD' in df.columns and 'MACD_SIGNAL' in df.columns:
                macd = df['MACD'].iloc[-1]
                macd_signal = df['MACD_SIGNAL'].iloc[-1]
                if macd > macd_signal:
                    signals['macd'] = 'BUY'
                elif macd < macd_signal:
                    signals['macd'] = 'SELL'
                else:
                    signals['macd'] = 'HOLD'
            
            # Moving average signals
            if 'SMA_20' in df.columns and 'SMA_50' in df.columns:
                sma_20 = df['SMA_20'].iloc[-1]
                sma_50 = df['SMA_50'].iloc[-1]
                current_price = df['mid_c'].iloc[-1]
                
                if current_price > sma_20 > sma_50:
                    signals['ma'] = 'BUY'
                elif current_price < sma_20 < sma_50:
                    signals['ma'] = 'SELL'
                else:
                    signals['ma'] = 'HOLD'
            
            # Bollinger Bands signals
            if 'BB_upper' in df.columns and 'BB_lower' in df.columns:
                bb_upper = df['BB_upper'].iloc[-1]
                bb_lower = df['BB_lower'].iloc[-1]
                current_price = df['mid_c'].iloc[-1]
                
                if current_price <= bb_lower:
                    signals['bb'] = 'BUY'
                elif current_price >= bb_upper:
                    signals['bb'] = 'SELL'
                else:
                    signals['bb'] = 'HOLD'
                    
        except Exception as e:
            self.logger.logger.error(f"Error getting technical signals for {pair}: {e}")
        
        return signals
    
    def _get_pattern_signals(self, pair: str) -> Dict[str, Any]:
        """Get candlestick pattern signals."""
        signals = {}
        
        try:
            # Get price data for pattern analysis
            candles = self.api.get_candles_df(pair, granularity=self.timeframes[0].value, count=100)
            
            if candles is None or candles.empty:
                return signals
            
            # Calculate basic candle properties
            candles['body_size'] = abs(candles['mid_c'] - candles['mid_o'])
            candles['total_range'] = candles['mid_h'] - candles['mid_l']
            candles['body_perc'] = (candles['body_size'] / candles['total_range']) * 100
            candles['direction'] = [1 if c >= o else -1 for c, o in zip(candles['mid_c'], candles['mid_o'])]
            
            # Get latest candle
            latest = candles.iloc[-1]
            
            # Simple pattern detection
            if latest['body_perc'] < 10:
                signals['doji'] = 'NEUTRAL'
            if latest['body_perc'] < 30 and latest['direction'] == 1:
                signals['hammer'] = 'BUY'
            if latest['body_perc'] < 30 and latest['direction'] == -1:
                signals['shooting_star'] = 'SELL'
            if 10 < latest['body_perc'] < 40:
                signals['spinning_top'] = 'NEUTRAL'
                
        except Exception as e:
            self.logger.logger.error(f"Error getting pattern signals for {pair}: {e}")
        
        return signals
    
    def _get_fundamental_signals(self, pair: str) -> Dict[str, Any]:
        """Get fundamental analysis signals."""
        signals = {}
        
        try:
            # This would integrate with economic calendar data
            # For now, return neutral signals
            signals['economic_calendar'] = 'NEUTRAL'
            signals['news_sentiment'] = 'NEUTRAL'
            signals['correlation'] = 'NEUTRAL'
            
        except Exception as e:
            self.logger.logger.error(f"Error getting fundamental signals for {pair}: {e}")
        
        return signals
    
    def _get_ai_signals(self, pair: str, market_condition: MarketCondition) -> Dict[str, Any]:
        """Get AI analysis signals."""
        signals = {}
        
        try:
            if self.openai_analyzer:
                ai_analysis = self.openai_analyzer.analyze_pair(pair, market_condition)
                signals['openai'] = ai_analysis.get('signal', 'HOLD')
                signals['ai_confidence'] = ai_analysis.get('confidence', 0.5)
            else:
                signals['openai'] = 'HOLD'
                signals['ai_confidence'] = 0.5
            
        except Exception as e:
            self.logger.logger.error(f"Error getting AI signals for {pair}: {e}")
            signals['openai'] = 'HOLD'
            signals['ai_confidence'] = 0.5
        
        return signals
    
    def _combine_signals(self, technical: Dict, pattern: Dict, fundamental: Dict, ai: Dict) -> Optional[str]:
        """Combine all signals into a final decision."""
        buy_count = 0
        sell_count = 0
        hold_count = 0
        
        # Count signals
        for signals in [technical, pattern, fundamental, ai]:
            for signal_type in signals.values():
                if isinstance(signal_type, str):
                    if signal_type == 'BUY':
                        buy_count += 1
                    elif signal_type == 'SELL':
                        sell_count += 1
                    else:
                        hold_count += 1
        
        # Decision logic
        total_signals = buy_count + sell_count + hold_count
        if total_signals == 0:
            return None
        
        buy_ratio = buy_count / total_signals
        sell_ratio = sell_count / total_signals
        
        if buy_ratio > 0.6:
            return 'BUY'
        elif sell_ratio > 0.6:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _calculate_signal_strength(self, technical: Dict, pattern: Dict, fundamental: Dict, ai: Dict) -> SignalStrength:
        """Calculate overall signal strength."""
        # Technical score
        technical_score = 0.5  # Base score
        if technical:
            buy_signals = sum(1 for s in technical.values() if s == 'BUY')
            sell_signals = sum(1 for s in technical.values() if s == 'SELL')
            total_signals = len(technical)
            if total_signals > 0:
                technical_score = max(buy_signals, sell_signals) / total_signals
        
        # Pattern score
        pattern_score = 0.5
        if pattern:
            detected_patterns = sum(1 for p in pattern.values() if p != 'HOLD')
            total_patterns = len(pattern)
            if total_patterns > 0:
                pattern_score = detected_patterns / total_patterns
        
        # Fundamental score
        fundamental_score = 0.5  # Neutral for now
        
        # AI score
        ai_score = ai.get('ai_confidence', 0.5)
        
        # Overall score
        overall_score = (technical_score + pattern_score + fundamental_score + ai_score) / 4
        
        # Confidence based on agreement
        agreement = 0
        if technical_score > 0.7: agreement += 1
        if pattern_score > 0.7: agreement += 1
        if fundamental_score > 0.7: agreement += 1
        if ai_score > 0.7: agreement += 1
        
        confidence = agreement / 4
        
        # Risk level
        if confidence > 0.8:
            risk_level = "low"
        elif confidence > 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return SignalStrength(
            technical_score=technical_score,
            fundamental_score=fundamental_score,
            ai_score=ai_score,
            pattern_score=pattern_score,
            overall_score=overall_score,
            confidence=confidence,
            risk_level=risk_level
        )
    
    def _calculate_exit_levels(self, pair: str, signal: str, market_condition: MarketCondition, current_price: float) -> Tuple[float, float]:
        """Calculate stop loss and take profit levels."""
        # Get ATR for volatility-based stops
        candles = self.api.get_candles_df(pair, granularity=self.timeframes[0].value, count=20)
        if candles is not None and not candles.empty:
            # Calculate ATR manually
            candles['tr'] = candles[['mid_h', 'mid_l', 'mid_c']].max(axis=1) - candles[['mid_h', 'mid_l', 'mid_c']].min(axis=1)
            atr = candles['tr'].rolling(14).mean().iloc[-1]
        else:
            atr = current_price * 0.001  # Default 0.1%
        
        # Calculate stop loss
        if signal == 'BUY':
            stop_loss = current_price - (atr * self.stop_loss_multiplier)
            take_profit = current_price + (atr * self.stop_loss_multiplier * self.min_risk_reward)
        else:  # SELL
            stop_loss = current_price + (atr * self.stop_loss_multiplier)
            take_profit = current_price - (atr * self.stop_loss_multiplier * self.min_risk_reward)
        
        # Adjust to key levels (simplified since we don't have key_levels in enum)
        return stop_loss, take_profit
    
    def _adjust_to_key_level(self, price: float, key_levels: List[float]) -> float:
        """Adjust price to nearest key level."""
        if not key_levels:
            return price
        
        closest_level = min(key_levels, key=lambda x: abs(x - price))
        if abs(closest_level - price) / price < 0.001:  # Within 0.1%
            return closest_level
        
        return price
    
    def _calculate_position_size(self, pair: str, entry_price: float, stop_loss: float, signal_strength: SignalStrength) -> float:
        """Calculate position size based on risk management."""
        # Get account balance
        account = self.api.get_account_summary()
        if not account or 'account' not in account:
            return 0.0
        
        balance = float(account['account']['balance'])
        
        # Calculate risk amount
        risk_amount = balance * self.risk_per_trade
        
        # Calculate position size
        price_risk = abs(entry_price - stop_loss)
        if price_risk == 0:
            return 0.0
        
        base_position_size = risk_amount / price_risk
        
        # Adjust for signal strength
        adjusted_position_size = base_position_size * signal_strength.confidence * self.position_sizing_multiplier
        
        # Check maximum positions
        if len(self.active_positions) >= self.max_positions:
            adjusted_position_size *= 0.5
        
        return adjusted_position_size
    
    def _generate_reasoning(self, technical: Dict, pattern: Dict, fundamental: Dict, ai: Dict, market_condition: MarketCondition) -> str:
        """Generate reasoning for the signal."""
        reasons = []
        
        # Technical reasoning
        if technical:
            tech_signals = [f"{k}: {v}" for k, v in technical.items() if v != 'HOLD']
            if tech_signals:
                reasons.append(f"Technical: {', '.join(tech_signals)}")
        
        # Pattern reasoning
        if pattern:
            pattern_signals = [f"{k}: {v}" for k, v in pattern.items() if v != 'HOLD']
            if pattern_signals:
                reasons.append(f"Patterns: {', '.join(pattern_signals)}")
        
        # Market condition reasoning
        reasons.append(f"Market: {market_condition.value} condition")
        
        # AI reasoning
        if ai.get('ai_confidence', 0) > 0.7:
            reasons.append(f"AI: High confidence ({ai['ai_confidence']:.2f})")
        
        return ' | '.join(reasons) if reasons else "No specific reasoning available"
    
    def _validate_signal(self, signal: ComprehensiveSignal) -> bool:
        """Validate signal before execution."""
        # Check minimum requirements
        if signal.signal_strength.overall_score < self.min_signal_strength:
            return False
        
        if signal.risk_reward_ratio < self.min_risk_reward:
            return False
        
        # Check daily trade limit
        today = datetime.now().date()
        today_trades = sum(1 for s in self.signals_history 
                          if s.timestamp.date() == today and s.signal_type in ['BUY', 'SELL'])
        
        if today_trades >= self.max_daily_trades:
            return False
        
        # Check existing positions
        if signal.pair in self.active_positions:
            return False
        
        return True
    
    def _execute_signal(self, signal: ComprehensiveSignal):
        """Execute the trading signal."""
        try:
            # Place the trade
            trade_result = self.api.place_trade(
                signal.pair,
                signal.signal_type.lower(),
                signal.position_size,
                signal.stop_loss,
                signal.take_profit
            )
            
            if trade_result and 'orderFillTransaction' in trade_result:
                # Record active position
                self.active_positions[signal.pair] = {
                    'signal': signal,
                    'trade_id': trade_result['orderFillTransaction']['id'],
                    'timestamp': datetime.now()
                }
                
                self.logger.logger.info(f"Executed {signal.signal_type} signal for {signal.pair} at {signal.entry_price}")
                
                # Update performance metrics
                self._update_performance_metrics(signal)
            else:
                self.logger.warning(f"Failed to execute signal for {signal.pair}")
                
        except Exception as e:
            self.logger.logger.error(f"Error executing signal for {signal.pair}: {e}")
    
    def _update_performance_metrics(self, signal: ComprehensiveSignal):
        """Update performance metrics."""
        # This would track performance over time
        # For now, just log the signal
        pass
    
    def _adapt_strategy_parameters(self):
        """Adapt strategy parameters based on recent performance."""
        # This would analyze recent performance and adjust parameters
        # For now, keep default parameters
        pass
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """Get current strategy status."""
        return {
            'is_running': self.is_running,
            'mode': self.mode.value,
            'pairs': self.pairs,
            'active_positions': len(self.active_positions),
            'total_signals': len(self.signals_history),
            'performance_metrics': self.performance_metrics,
            'market_conditions': {pair: {
                'trend': mc.trend,
                'volatility': mc.volatility,
                'momentum': mc.momentum,
                'strength': mc.strength
            } for pair, mc in self.market_conditions.items()}
        }
    
    def get_recent_signals(self, limit: int = 10) -> List[ComprehensiveSignal]:
        """Get recent trading signals."""
        return self.signals_history[-limit:] if self.signals_history else []
    
    def get_comprehensive_analysis(self, pair: str) -> Dict[str, Any]:
        """Get comprehensive analysis for a pair."""
        try:
            market_condition = self.market_conditions.get(pair)
            if not market_condition:
                market_condition = self._analyze_market_condition(pair)
            
            signal = self._generate_comprehensive_signal(pair, market_condition)
            
            return {
                'market_condition': {
                    'type': market_condition.value,
                    'description': f"Market is {market_condition.value}"
                },
                'signal': {
                    'type': signal.signal_type if signal else 'HOLD',
                    'strength': signal.signal_strength.overall_score if signal else 0.0,
                    'confidence': signal.signal_strength.confidence if signal else 0.0,
                    'risk_level': signal.signal_strength.risk_level if signal else 'medium'
                } if signal else None,
                'analysis_components': {
                    'technical': self._get_technical_signals(pair),
                    'pattern': self._get_pattern_signals(pair),
                    'fundamental': self._get_fundamental_signals(pair),
                    'ai': self._get_ai_signals(pair, market_condition)
                }
            }
            
        except Exception as e:
            self.logger.logger.error(f"Error getting comprehensive analysis for {pair}: {e}")
            return {'error': str(e)}
    
    def _should_call_openai(self, technical_signals: Dict, pattern_signals: Dict, 
                           fundamental_signals: Dict, market_condition: MarketCondition) -> bool:
        """Determine if OpenAI should be called based on price action and conditions."""
        try:
            # Check cooldown period
            current_time = time.time()
            pair = list(technical_signals.keys())[0] if technical_signals else "unknown"
            
            if pair in self.last_openai_calls:
                time_since_last_call = current_time - self.last_openai_calls[pair]
                if time_since_last_call < self.openai_call_cooldown:
                    return False
            
            # Check if technical conditions are favorable
            technical_score = 0
            buy_signals = sum(1 for s in technical_signals.values() if s == 'BUY')
            sell_signals = sum(1 for s in technical_signals.values() if s == 'SELL')
            total_technical = len(technical_signals)
            
            if total_technical > 0:
                technical_score = max(buy_signals, sell_signals) / total_technical
            
            # Check if pattern conditions are favorable
            pattern_score = 0
            if pattern_signals:
                detected_patterns = sum(1 for p in pattern_signals.values() if p != 'HOLD')
                total_patterns = len(pattern_signals)
                if total_patterns > 0:
                    pattern_score = detected_patterns / total_patterns
            
            # Check market conditions (simplified for enum)
            market_score = 0
            if market_condition in [MarketCondition.TRENDING, MarketCondition.VOLATILE]:
                market_score += 0.5  # Favorable conditions
            
            # Calculate overall score
            overall_score = (technical_score + pattern_score + market_score) / 3
            
            # Only call OpenAI if conditions are favorable
            should_call = overall_score >= 0.6
            
            if should_call:
                self.last_openai_calls[pair] = current_time
            
            return should_call
            
        except Exception as e:
            self.logger.logger.error(f"Error checking if OpenAI should be called: {e}")
            return False
    
    def _add_trade_alert(self, signal: ComprehensiveSignal):
        """Add a trade alert to the dashboard and shared data store."""
        try:
            alert = {
                'id': f"alert_{int(time.time())}",
                'timestamp': signal.timestamp.isoformat(),
                'pair': signal.pair,
                'signal_type': signal.signal_type,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'position_size': signal.position_size,
                'confidence': signal.signal_strength.confidence,
                'risk_reward_ratio': signal.risk_reward_ratio,
                'reasoning': signal.reasoning,
                'status': 'pending'  # pending, executed, expired
            }
            
            # Add to local alerts list
            self.trade_alerts.insert(0, alert)
            
            # Keep only the most recent alerts
            if len(self.trade_alerts) > self.max_trade_alerts:
                self.trade_alerts = self.trade_alerts[:self.max_trade_alerts]
            
            # Add to shared data store if available
            try:
                from shared_data_store import get_shared_store, TradeAlert
                store = get_shared_store()
                
                shared_alert = TradeAlert(
                    id=alert['id'],
                    timestamp=alert['timestamp'],
                    pair=alert['pair'],
                    signal_type=alert['signal_type'],
                    entry_price=alert['entry_price'],
                    stop_loss=alert['stop_loss'],
                    take_profit=alert['take_profit'],
                    position_size=alert['position_size'],
                    confidence=alert['confidence'],
                    risk_reward_ratio=alert['risk_reward_ratio'],
                    reasoning=alert['reasoning'],
                    status=alert['status'],
                    source_system='comprehensive_strategy'
                )
                
                store.add_trade_alert(shared_alert)
                
                # Send message to other systems
                store.send_message({
                    'type': 'trade_alert',
                    'alert': shared_alert,
                    'source': 'comprehensive_strategy'
                })
                
            except ImportError:
                self.logger.logger.debug("Shared data store not available")
            except Exception as e:
                self.logger.logger.error(f"Error adding to shared data store: {e}")
            
            self.logger.logger.info(f"🚨 Trade Alert Added: {signal.signal_type} {signal.pair} @ {signal.entry_price}")
            
        except Exception as e:
            self.logger.logger.error(f"Error adding trade alert: {e}")
    
    def get_trade_alerts(self) -> List[Dict]:
        """Get current trade alerts for the dashboard."""
        # Remove expired alerts (older than 1 hour)
        current_time = datetime.now()
        valid_alerts = []
        
        for alert in self.trade_alerts:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if (current_time - alert_time).total_seconds() < 3600:  # 1 hour
                valid_alerts.append(alert)
        
        self.trade_alerts = valid_alerts
        return self.trade_alerts
    
    def execute_trade_alert(self, alert_id: str) -> bool:
        """Execute a trade alert."""
        try:
            for alert in self.trade_alerts:
                if alert['id'] == alert_id and alert['status'] == 'pending':
                    # Create signal from alert
                    signal = ComprehensiveSignal(
                        timestamp=datetime.fromisoformat(alert['timestamp']),
                        pair=alert['pair'],
                        signal_type=alert['signal_type'],
                        entry_price=alert['entry_price'],
                        stop_loss=alert['stop_loss'],
                        take_profit=alert['take_profit'],
                        position_size=alert['position_size'],
                        signal_strength=SignalStrength(
                            technical_score=0.7,
                            fundamental_score=0.7,
                            ai_score=0.7,
                            pattern_score=0.7,
                            overall_score=alert['confidence'],
                            confidence=alert['confidence'],
                            risk_level='medium'
                        ),
                        market_condition=MarketCondition(
                            trend='bullish',
                            volatility=0.5,
                            momentum=0.5,
                            strength=0.7,
                            support_levels=[],
                            resistance_levels=[],
                            key_levels=[]
                        ),
                        reasoning=alert['reasoning'],
                        risk_reward_ratio=alert['risk_reward_ratio'],
                        expected_duration=timedelta(hours=4),
                        source_analysis={}
                    )
                    
                    # Execute the signal
                    success = self._execute_signal(signal)
                    
                    if success:
                        alert['status'] = 'executed'
                        self.logger.logger.info(f"✅ Trade Alert Executed: {alert_id}")
                        return True
                    else:
                        alert['status'] = 'failed'
                        self.logger.logger.error(f"❌ Trade Alert Failed: {alert_id}")
                        return False
            
            return False
            
        except Exception as e:
            self.logger.logger.error(f"Error executing trade alert: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize strategy
    strategy = ComprehensiveTradingStrategy(
        mode=StrategyMode.MODERATE,
        pairs=["EUR_USD", "GBP_USD", "USD_JPY"],
        timeframes=[TimeFrame.M15, TimeFrame.H1],
        risk_per_trade=0.02,
        max_positions=3
    )
    
    # Start strategy
    strategy.start_strategy()
    
    try:
        # Keep running
        while True:
            time.sleep(60)
            
            # Print status
            status = strategy.get_strategy_status()
            print(f"Active positions: {status['active_positions']}")
            print(f"Total signals: {status['total_signals']}")
            
    except KeyboardInterrupt:
        print("\nStopping strategy...")
        strategy.stop_strategy()
        print("Strategy stopped.") 