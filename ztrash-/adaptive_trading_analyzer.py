#!/usr/bin/env python3
"""
Adaptive Forex Trading Analyzer with OpenAI

This module provides adaptive trading strategies that work profitably in both
trending and sideways markets using advanced market condition detection.
"""

import sys
import os
import time
import threading
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add project root to path
sys.path.append("../")

from api.openai_api import OpenAIAnalyzer
from api.oanda_api import OandaApi

class MarketCondition(Enum):
    """Market condition types."""
    STRONG_TREND_UP = "strong_trend_up"
    WEAK_TREND_UP = "weak_trend_up"
    SIDEWAYS = "sideways"
    WEAK_TREND_DOWN = "weak_trend_down"
    STRONG_TREND_DOWN = "strong_trend_down"
    VOLATILE = "volatile"
    BREAKOUT = "breakout"

class TradingStrategy(Enum):
    """Trading strategy types."""
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    CONSERVATIVE = "conservative"

@dataclass
class MarketAnalysis:
    """Comprehensive market analysis data."""
    condition: MarketCondition
    trend_strength: float  # -1 to 1
    volatility: float  # 0 to 1
    momentum: float  # -1 to 1
    mean_reversion_signal: float  # -1 to 1
    breakout_probability: float  # 0 to 1
    support_strength: float  # 0 to 1
    resistance_strength: float  # 0 to 1
    recommended_strategy: TradingStrategy
    confidence: float  # 0 to 1

@dataclass
class AdaptiveSignal:
    """Enhanced trading signal with adaptive features."""
    timestamp: str
    currency_pair: str
    signal_type: str
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    reasoning: str
    market_condition: MarketCondition
    strategy_used: TradingStrategy
    risk_level: str
    position_size_recommendation: float
    time_horizon: str  # "scalp", "short", "medium", "long"
    profit_probability: float
    alternative_entry: Optional[float] = None
    trailing_stop: Optional[float] = None

class AdaptiveTradingAnalyzer:
    """Adaptive trading analyzer that works in all market conditions."""
    
    def __init__(self, openai_api_key: Optional[str] = None, update_interval: int = 60):
        """Initialize the adaptive analyzer."""
        self.openai_analyzer = OpenAIAnalyzer(openai_api_key)
        self.oanda_api = OandaApi()
        self.update_interval = update_interval
        
        # Trading parameters
        self.currency_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD']
        self.signals_history = []
        self.market_analysis_history = {}
        self.is_running = False
        
        # Adaptive parameters
        self.min_confidence_threshold = 0.65  # Lower for more opportunities
        self.max_daily_trades = 10
        self.daily_trade_count = {}
        
        # Risk management
        self.max_risk_per_trade = 0.015  # 1.5% per trade
        self.max_portfolio_risk = 0.06  # 6% total portfolio risk
        self.win_rate_target = 0.65  # Target 65% win rate
        
        # Market condition thresholds
        self.trend_strength_threshold = 0.3
        self.volatility_threshold = 0.015
        self.sideways_threshold = 0.2
        
    def start_adaptive_analysis(self, currency_pairs: List[str] = None):
        """Start adaptive real-time analysis."""
        if currency_pairs:
            self.currency_pairs = currency_pairs
            
        self.is_running = True
        
        print(f"🚀 Starting Adaptive Trading Analysis")
        print(f"📊 Currency Pairs: {', '.join(self.currency_pairs)}")
        print(f"⏱️  Update Interval: {self.update_interval} seconds")
        print(f"🎯 Target Win Rate: {self.win_rate_target:.1%}")
        print(f"🛡️  Max Risk Per Trade: {self.max_risk_per_trade:.1%}")
        print("🤖 Adaptive strategies for all market conditions")
        print("=" * 60)
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=self._adaptive_analysis_loop, daemon=True)
        analysis_thread.start()
        
        return analysis_thread
    
    def _adaptive_analysis_loop(self):
        """Main adaptive analysis loop."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Reset daily counters if new day
                self._reset_daily_counters_if_needed()
                
                # Analyze each currency pair
                for pair in self.currency_pairs:
                    if self._should_analyze_pair(pair):
                        self._analyze_pair_adaptively(pair)
                
                # Calculate sleep time
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"❌ Error in adaptive analysis loop: {e}")
                time.sleep(5)
    
    def _analyze_pair_adaptively(self, pair: str):
        """Perform adaptive analysis for a currency pair."""
        try:
            # Get comprehensive market data
            market_data = self._get_comprehensive_market_data(pair)
            if not market_data:
                return
            
            # Analyze market conditions
            market_analysis = self._analyze_market_conditions(market_data)
            
            # Store market analysis
            self.market_analysis_history[pair] = market_analysis
            
            # Generate adaptive signal based on market conditions
            signal = self._generate_adaptive_signal(pair, market_data, market_analysis)
            
            if signal and self._validate_signal(signal):
                self.signals_history.append(signal)
                
                # Keep history manageable
                if len(self.signals_history) > 100:
                    self.signals_history = self.signals_history[-100:]
                
                # Print significant signals
                if signal.signal_type != 'HOLD' or signal.confidence > 0.8:
                    self._print_adaptive_signal(signal)
                
                # Save signal
                self._save_adaptive_signal(signal)
                
                # Update daily trade count
                if signal.signal_type in ['BUY', 'SELL']:
                    today = datetime.now().strftime('%Y-%m-%d')
                    self.daily_trade_count[today] = self.daily_trade_count.get(today, 0) + 1
                
        except Exception as e:
            print(f"❌ Error analyzing {pair}: {e}")
    
    def _get_comprehensive_market_data(self, pair: str, lookback_minutes: int = 120) -> Optional[Dict]:
        """Get comprehensive market data for adaptive analysis."""
        try:
            # Get multiple timeframes
            m1_data = self.oanda_api.get_candles_df(pair, count=60, granularity="M1")  # 1-minute
            m5_data = self.oanda_api.get_candles_df(pair, count=60, granularity="M5")  # 5-minute
            h1_data = self.oanda_api.get_candles_df(pair, count=24, granularity="H1")  # 1-hour
            
            if any(df is None or df.empty for df in [m1_data, m5_data, h1_data]):
                return None
            
            # Calculate comprehensive indicators
            indicators = self._calculate_comprehensive_indicators(m1_data, m5_data, h1_data)
            
            # Market structure analysis
            structure = self._analyze_market_structure(m1_data, m5_data, h1_data)
            
            # Price action patterns
            patterns = self._identify_price_patterns(m1_data)
            
            current_price = float(m1_data.iloc[-1]['mid_c'])
            
            return {
                'pair': pair,
                'current_price': current_price,
                'm1_data': m1_data,
                'm5_data': m5_data,
                'h1_data': h1_data,
                'indicators': indicators,
                'structure': structure,
                'patterns': patterns,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting comprehensive data for {pair}: {e}")
            return None
    
    def _analyze_market_conditions(self, market_data: Dict) -> MarketAnalysis:
        """Analyze current market conditions comprehensively."""
        try:
            indicators = market_data['indicators']
            structure = market_data['structure']
            patterns = market_data['patterns']
            
            # Calculate trend strength
            trend_strength = self._calculate_trend_strength(indicators, structure)
            
            # Calculate volatility
            volatility = indicators.get('volatility', 0)
            
            # Calculate momentum
            momentum = self._calculate_momentum(indicators)
            
            # Mean reversion signal
            mean_reversion_signal = self._calculate_mean_reversion_signal(indicators)
            
            # Breakout probability
            breakout_probability = self._calculate_breakout_probability(structure, patterns)
            
            # Support/Resistance strength
            support_strength = structure.get('support_strength', 0)
            resistance_strength = structure.get('resistance_strength', 0)
            
            # Determine market condition
            market_condition = self._determine_market_condition(
                trend_strength, volatility, momentum, breakout_probability
            )
            
            # Recommend strategy
            recommended_strategy = self._recommend_strategy(market_condition, volatility, momentum)
            
            # Calculate overall confidence
            confidence = self._calculate_market_confidence(
                trend_strength, volatility, support_strength, resistance_strength
            )
            
            return MarketAnalysis(
                condition=market_condition,
                trend_strength=trend_strength,
                volatility=volatility,
                momentum=momentum,
                mean_reversion_signal=mean_reversion_signal,
                breakout_probability=breakout_probability,
                support_strength=support_strength,
                resistance_strength=resistance_strength,
                recommended_strategy=recommended_strategy,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"❌ Error analyzing market conditions: {e}")
            return MarketAnalysis(
                condition=MarketCondition.SIDEWAYS,
                trend_strength=0, volatility=0, momentum=0,
                mean_reversion_signal=0, breakout_probability=0,
                support_strength=0, resistance_strength=0,
                recommended_strategy=TradingStrategy.CONSERVATIVE,
                confidence=0
            )
    
    def _calculate_comprehensive_indicators(self, m1_data: pd.DataFrame, 
                                          m5_data: pd.DataFrame, 
                                          h1_data: pd.DataFrame) -> Dict:
        """Calculate comprehensive technical indicators across timeframes."""
        try:
            indicators = {}
            
            # M1 indicators (short-term)
            m1_close = m1_data['mid_c'].astype(float)
            indicators['m1_rsi'] = self._calculate_rsi(m1_close, 14)
            indicators['m1_macd'] = self._calculate_macd(m1_close)
            indicators['m1_bb'] = self._calculate_bollinger_bands(m1_close, 20)
            indicators['m1_sma_5'] = m1_close.rolling(5).mean().iloc[-1]
            indicators['m1_sma_20'] = m1_close.rolling(20).mean().iloc[-1]
            
            # M5 indicators (medium-term)
            m5_close = m5_data['mid_c'].astype(float)
            indicators['m5_rsi'] = self._calculate_rsi(m5_close, 14)
            indicators['m5_macd'] = self._calculate_macd(m5_close)
            indicators['m5_bb'] = self._calculate_bollinger_bands(m5_close, 20)
            indicators['m5_sma_10'] = m5_close.rolling(10).mean().iloc[-1]
            indicators['m5_sma_50'] = m5_close.rolling(50).mean().iloc[-1]
            
            # H1 indicators (long-term)
            h1_close = h1_data['mid_c'].astype(float)
            indicators['h1_rsi'] = self._calculate_rsi(h1_close, 14)
            indicators['h1_macd'] = self._calculate_macd(h1_close)
            indicators['h1_sma_20'] = h1_close.rolling(20).mean().iloc[-1]
            
            # Volatility measures
            indicators['volatility'] = m1_close.pct_change().rolling(20).std().iloc[-1]
            indicators['atr'] = self._calculate_atr(m1_data, 14)
            
            # Multi-timeframe alignment
            indicators['timeframe_alignment'] = self._calculate_timeframe_alignment(
                indicators['m1_sma_5'], indicators['m5_sma_10'], indicators['h1_sma_20']
            )
            
            return indicators
            
        except Exception as e:
            print(f"❌ Error calculating indicators: {e}")
            return {}
    
    def _analyze_market_structure(self, m1_data: pd.DataFrame, 
                                 m5_data: pd.DataFrame, 
                                 h1_data: pd.DataFrame) -> Dict:
        """Analyze market structure for support/resistance and trends."""
        try:
            structure = {}
            
            # Support and resistance levels
            m1_highs = m1_data['mid_h'].astype(float)
            m1_lows = m1_data['mid_l'].astype(float)
            
            # Recent swing highs and lows
            structure['resistance_levels'] = self._find_resistance_levels(m1_highs)
            structure['support_levels'] = self._find_support_levels(m1_lows)
            
            # Calculate support/resistance strength
            current_price = float(m1_data.iloc[-1]['mid_c'])
            structure['support_strength'] = self._calculate_level_strength(
                structure['support_levels'], current_price, 'support'
            )
            structure['resistance_strength'] = self._calculate_level_strength(
                structure['resistance_levels'], current_price, 'resistance'
            )
            
            # Market structure trend
            structure['higher_highs'] = self._count_higher_highs(m1_highs)
            structure['higher_lows'] = self._count_higher_lows(m1_lows)
            structure['lower_highs'] = self._count_lower_highs(m1_highs)
            structure['lower_lows'] = self._count_lower_lows(m1_lows)
            
            # Range detection
            structure['range_bound'] = self._detect_range_bound_market(m5_data)
            structure['range_top'] = self._find_range_top(m5_data)
            structure['range_bottom'] = self._find_range_bottom(m5_data)
            
            return structure
            
        except Exception as e:
            print(f"❌ Error analyzing market structure: {e}")
            return {}
    
    def _generate_adaptive_signal(self, pair: str, market_data: Dict, 
                                 market_analysis: MarketAnalysis) -> Optional[AdaptiveSignal]:
        """Generate adaptive trading signal based on market conditions."""
        try:
            # Create adaptive prompt based on market condition
            prompt = self._create_adaptive_prompt(pair, market_data, market_analysis)
            
            # Get OpenAI analysis
            response = self.openai_analyzer.client.chat.completions.create(
                model=self.openai_analyzer.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_adaptive_system_prompt(market_analysis.condition)
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent results
                max_tokens=1000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            signal_data = json.loads(ai_response)
            
            # Calculate adaptive parameters
            position_size = self._calculate_adaptive_position_size(market_analysis)
            time_horizon = self._determine_time_horizon(market_analysis)
            profit_probability = self._calculate_profit_probability(market_analysis, signal_data)
            
            # Create adaptive signal
            signal = AdaptiveSignal(
                timestamp=datetime.now().isoformat(),
                currency_pair=pair,
                signal_type=signal_data['signal'],
                confidence=float(signal_data['confidence']),
                entry_price=float(signal_data['entry_price']),
                stop_loss=float(signal_data['stop_loss']),
                take_profit=float(signal_data['take_profit']),
                reasoning=signal_data['reasoning'],
                market_condition=market_analysis.condition,
                strategy_used=market_analysis.recommended_strategy,
                risk_level=signal_data['risk_level'],
                position_size_recommendation=position_size,
                time_horizon=time_horizon,
                profit_probability=profit_probability,
                alternative_entry=signal_data.get('alternative_entry'),
                trailing_stop=signal_data.get('trailing_stop')
            )
            
            return signal
            
        except Exception as e:
            print(f"❌ Error generating adaptive signal for {pair}: {e}")
            return None
    
    def _get_adaptive_system_prompt(self, market_condition: MarketCondition) -> str:
        """Get system prompt adapted to market condition."""
        base_prompt = """You are an expert adaptive forex trading analyst with deep expertise in profiting from ALL market conditions - trending, sideways, volatile, and breakout markets."""
        
        condition_specific = {
            MarketCondition.STRONG_TREND_UP: """
            CURRENT MARKET: Strong Uptrend
            STRATEGY FOCUS: Trend following with tight stops, ride the momentum
            PROFIT APPROACH: Look for pullback entries, breakout continuations
            RISK MANAGEMENT: Trail stops aggressively, take partial profits
            """,
            MarketCondition.WEAK_TREND_UP: """
            CURRENT MARKET: Weak Uptrend
            STRATEGY FOCUS: Conservative trend following with wider stops
            PROFIT APPROACH: Enter on dips, exit at resistance
            RISK MANAGEMENT: Smaller position sizes, quick profit taking
            """,
            MarketCondition.SIDEWAYS: """
            CURRENT MARKET: Sideways/Range-bound
            STRATEGY FOCUS: Mean reversion, buy support/sell resistance
            PROFIT APPROACH: Fade extremes, scalp the range
            RISK MANAGEMENT: Tight stops outside range, quick scalps
            """,
            MarketCondition.VOLATILE: """
            CURRENT MARKET: High Volatility
            STRATEGY FOCUS: Breakout trading, momentum scalping
            PROFIT APPROACH: Trade volatility expansions and contractions
            RISK MANAGEMENT: Reduce position sizes, wider stops
            """,
            MarketCondition.BREAKOUT: """
            CURRENT MARKET: Breakout Conditions
            STRATEGY FOCUS: Early breakout entry, momentum following
            PROFIT APPROACH: Enter on initial breakout, ride momentum
            RISK MANAGEMENT: Stop below breakout level, scale out profits
            """
        }
        
        return base_prompt + condition_specific.get(market_condition, condition_specific[MarketCondition.SIDEWAYS]) + """
        
        RESPOND IN JSON FORMAT:
        {
            "signal": "BUY|SELL|HOLD",
            "confidence": 0.0-1.0,
            "entry_price": precise_entry_level,
            "stop_loss": risk_management_level,
            "take_profit": profit_target,
            "reasoning": "detailed_market_analysis",
            "risk_level": "LOW|MEDIUM|HIGH",
            "alternative_entry": optional_better_entry,
            "trailing_stop": optional_trailing_stop_level
        }
        """
    
    def _create_adaptive_prompt(self, pair: str, market_data: Dict, market_analysis: MarketAnalysis) -> str:
        """Create adaptive prompt based on market conditions."""
        indicators = market_data['indicators']
        structure = market_data['structure']
        current_price = market_data['current_price']
        
        return f"""
        ADAPTIVE FOREX ANALYSIS - PROFIT IN ANY CONDITION
        
        Pair: {pair}
        Current Price: {current_price:.5f}
        Market Condition: {market_analysis.condition.value}
        Recommended Strategy: {market_analysis.recommended_strategy.value}
        
        MARKET ANALYSIS:
        - Trend Strength: {market_analysis.trend_strength:.2f} (-1=strong down, +1=strong up)
        - Volatility: {market_analysis.volatility:.4f}
        - Momentum: {market_analysis.momentum:.2f}
        - Mean Reversion Signal: {market_analysis.mean_reversion_signal:.2f}
        - Breakout Probability: {market_analysis.breakout_probability:.2f}
        - Support Strength: {market_analysis.support_strength:.2f}
        - Resistance Strength: {market_analysis.resistance_strength:.2f}
        
        MULTI-TIMEFRAME INDICATORS:
        M1: RSI={indicators.get('m1_rsi', 50):.1f}, SMA5={indicators.get('m1_sma_5', 0):.5f}, SMA20={indicators.get('m1_sma_20', 0):.5f}
        M5: RSI={indicators.get('m5_rsi', 50):.1f}, SMA10={indicators.get('m5_sma_10', 0):.5f}, SMA50={indicators.get('m5_sma_50', 0):.5f}
        H1: RSI={indicators.get('h1_rsi', 50):.1f}, SMA20={indicators.get('h1_sma_20', 0):.5f}
        
        MARKET STRUCTURE:
        - Range Bound: {structure.get('range_bound', False)}
        - Range Top: {structure.get('range_top', 0):.5f}
        - Range Bottom: {structure.get('range_bottom', 0):.5f}
        - Higher Highs Count: {structure.get('higher_highs', 0)}
        - Higher Lows Count: {structure.get('higher_lows', 0)}
        
        ADAPTIVE REQUIREMENTS:
        1. PROFIT IN ANY CONDITION - trending, sideways, volatile
        2. Adjust strategy to current market condition
        3. Use appropriate risk/reward for market type
        4. Consider multi-timeframe alignment
        5. Factor in support/resistance strength
        6. Provide alternative entry if main entry fails
        7. Include trailing stops for trending markets
        
        STRATEGY SELECTION:
        - Trending Markets: Follow trends, use momentum
        - Sideways Markets: Mean reversion, range trading
        - Volatile Markets: Breakout trading, wider stops
        - Low Volatility: Scalping, tight ranges
        
        Generate profitable trading signal adapted to current conditions.
        """
    
    def _calculate_trend_strength(self, indicators: Dict, structure: Dict) -> float:
        """Calculate trend strength from -1 (strong down) to +1 (strong up)."""
        try:
            # Moving average alignment
            ma_alignment = 0
            if indicators.get('m1_sma_5', 0) > indicators.get('m1_sma_20', 0):
                ma_alignment += 0.3
            if indicators.get('m5_sma_10', 0) > indicators.get('m5_sma_50', 0):
                ma_alignment += 0.4
            if indicators.get('timeframe_alignment', 0) > 0:
                ma_alignment += 0.3
            
            # Market structure
            structure_score = 0
            hh = structure.get('higher_highs', 0)
            hl = structure.get('higher_lows', 0)
            lh = structure.get('lower_highs', 0)
            ll = structure.get('lower_lows', 0)
            
            if hh > 0 and hl > 0:
                structure_score = min(0.5, (hh + hl) / 10)
            elif lh > 0 and ll > 0:
                structure_score = -min(0.5, (lh + ll) / 10)
            
            # MACD alignment
            macd_score = 0
            m1_macd = indicators.get('m1_macd', 0)
            m5_macd = indicators.get('m5_macd', 0)
            
            if m1_macd > 0 and m5_macd > 0:
                macd_score = 0.2
            elif m1_macd < 0 and m5_macd < 0:
                macd_score = -0.2
            
            total_strength = ma_alignment + structure_score + macd_score
            return max(-1, min(1, total_strength))
            
        except Exception:
            return 0
    
    def _calculate_momentum(self, indicators: Dict) -> float:
        """Calculate momentum from -1 to +1."""
        try:
            # RSI momentum
            m1_rsi = indicators.get('m1_rsi', 50)
            m5_rsi = indicators.get('m5_rsi', 50)
            
            rsi_momentum = ((m1_rsi - 50) / 50) * 0.3 + ((m5_rsi - 50) / 50) * 0.2
            
            # MACD momentum
            m1_macd = indicators.get('m1_macd', 0)
            m5_macd = indicators.get('m5_macd', 0)
            
            macd_momentum = (m1_macd * 100) * 0.3 + (m5_macd * 100) * 0.2
            
            total_momentum = rsi_momentum + macd_momentum
            return max(-1, min(1, total_momentum))
            
        except Exception:
            return 0
    
    def _calculate_mean_reversion_signal(self, indicators: Dict) -> float:
        """Calculate mean reversion signal strength."""
        try:
            # Bollinger Bands position
            bb = indicators.get('m1_bb', {})
            current_price = indicators.get('m1_sma_5', 0)
            
            if bb and 'upper' in bb and 'lower' in bb:
                bb_position = (current_price - bb['middle']) / (bb['upper'] - bb['lower'])
                
                # RSI extremes
                rsi = indicators.get('m1_rsi', 50)
                rsi_extreme = 0
                if rsi > 75:
                    rsi_extreme = (rsi - 75) / 25  # Overbought
                elif rsi < 25:
                    rsi_extreme = -(25 - rsi) / 25  # Oversold
                
                return max(-1, min(1, bb_position + rsi_extreme))
            
            return 0
            
        except Exception:
            return 0
    
    def _determine_market_condition(self, trend_strength: float, volatility: float, 
                                   momentum: float, breakout_probability: float) -> MarketCondition:
        """Determine current market condition."""
        try:
            # Strong trends
            if abs(trend_strength) > 0.6:
                if trend_strength > 0:
                    return MarketCondition.STRONG_TREND_UP
                else:
                    return MarketCondition.STRONG_TREND_DOWN
            
            # Weak trends
            elif abs(trend_strength) > 0.3:
                if trend_strength > 0:
                    return MarketCondition.WEAK_TREND_UP
                else:
                    return MarketCondition.WEAK_TREND_DOWN
            
            # High volatility
            elif volatility > self.volatility_threshold * 2:
                return MarketCondition.VOLATILE
            
            # Breakout conditions
            elif breakout_probability > 0.7:
                return MarketCondition.BREAKOUT
            
            # Default to sideways
            else:
                return MarketCondition.SIDEWAYS
                
        except Exception:
            return MarketCondition.SIDEWAYS
    
    def _recommend_strategy(self, market_condition: MarketCondition, 
                           volatility: float, momentum: float) -> TradingStrategy:
        """Recommend trading strategy based on market conditions."""
        strategy_map = {
            MarketCondition.STRONG_TREND_UP: TradingStrategy.TREND_FOLLOWING,
            MarketCondition.STRONG_TREND_DOWN: TradingStrategy.TREND_FOLLOWING,
            MarketCondition.WEAK_TREND_UP: TradingStrategy.CONSERVATIVE,
            MarketCondition.WEAK_TREND_DOWN: TradingStrategy.CONSERVATIVE,
            MarketCondition.SIDEWAYS: TradingStrategy.MEAN_REVERSION,
            MarketCondition.VOLATILE: TradingStrategy.BREAKOUT,
            MarketCondition.BREAKOUT: TradingStrategy.BREAKOUT
        }
        
        base_strategy = strategy_map.get(market_condition, TradingStrategy.CONSERVATIVE)
        
        # Adjust for high volatility
        if volatility > self.volatility_threshold * 3:
            return TradingStrategy.SCALPING
        
        return base_strategy
    
    def _calculate_adaptive_position_size(self, market_analysis: MarketAnalysis) -> float:
        """Calculate position size based on market conditions."""
        base_size = 1.0
        
        # Adjust for volatility
        volatility_adjustment = max(0.3, 1 - market_analysis.volatility * 10)
        
        # Adjust for confidence
        confidence_adjustment = market_analysis.confidence
        
        # Adjust for market condition
        condition_adjustment = {
            MarketCondition.STRONG_TREND_UP: 1.2,
            MarketCondition.STRONG_TREND_DOWN: 1.2,
            MarketCondition.WEAK_TREND_UP: 0.8,
            MarketCondition.WEAK_TREND_DOWN: 0.8,
            MarketCondition.SIDEWAYS: 1.0,
            MarketCondition.VOLATILE: 0.6,
            MarketCondition.BREAKOUT: 1.1
        }.get(market_analysis.condition, 1.0)
        
        return base_size * volatility_adjustment * confidence_adjustment * condition_adjustment
    
    def _determine_time_horizon(self, market_analysis: MarketAnalysis) -> str:
        """Determine appropriate time horizon for the trade."""
        if market_analysis.condition in [MarketCondition.STRONG_TREND_UP, MarketCondition.STRONG_TREND_DOWN]:
            return "medium"  # Hold for trend continuation
        elif market_analysis.condition == MarketCondition.SIDEWAYS:
            return "scalp"  # Quick in and out
        elif market_analysis.condition == MarketCondition.VOLATILE:
            return "short"  # Capture volatility moves
        elif market_analysis.condition == MarketCondition.BREAKOUT:
            return "short"  # Capture initial breakout
        else:
            return "short"
    
    def _validate_signal(self, signal: AdaptiveSignal) -> bool:
        """Validate signal quality and risk parameters."""
        try:
            # Check confidence threshold
            if signal.confidence < self.min_confidence_threshold:
                return False
            
            # Check daily trade limit
            today = datetime.now().strftime('%Y-%m-%d')
            if self.daily_trade_count.get(today, 0) >= self.max_daily_trades:
                return False
            
            # Check risk/reward ratio
            if signal.signal_type in ['BUY', 'SELL']:
                risk = abs(signal.entry_price - signal.stop_loss)
                reward = abs(signal.take_profit - signal.entry_price)
                
                if risk <= 0 or reward / risk < 1.0:  # Minimum 1:1 RR
                    return False
            
            # Check price levels are reasonable
            price_levels = [signal.entry_price, signal.stop_loss, signal.take_profit]
            if any(level <= 0 for level in price_levels):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _print_adaptive_signal(self, signal: AdaptiveSignal):
        """Print adaptive signal with enhanced information."""
        timestamp = datetime.fromisoformat(signal.timestamp).strftime('%H:%M:%S')
        
        # Market condition emoji
        condition_emoji = {
            MarketCondition.STRONG_TREND_UP: "📈",
            MarketCondition.STRONG_TREND_DOWN: "📉", 
            MarketCondition.SIDEWAYS: "↔️",
            MarketCondition.VOLATILE: "⚡",
            MarketCondition.BREAKOUT: "🚀"
        }
        
        # Strategy emoji
        strategy_emoji = {
            TradingStrategy.TREND_FOLLOWING: "🌊",
            TradingStrategy.MEAN_REVERSION: "🔄",
            TradingStrategy.BREAKOUT: "💥",
            TradingStrategy.SCALPING: "⚡",
            TradingStrategy.CONSERVATIVE: "🛡️"
        }
        
        signal_emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡'}.get(signal.signal_type, '❓')
        
        print(f"\n{signal_emoji} [{timestamp}] {signal.currency_pair} - {signal.signal_type}")
        print(f"   {condition_emoji.get(signal.market_condition, '📊')} Market: {signal.market_condition.value}")
        print(f"   {strategy_emoji.get(signal.strategy_used, '📋')} Strategy: {signal.strategy_used.value}")
        print(f"   💡 Confidence: {signal.confidence:.1%}")
        print(f"   🎯 Profit Probability: {signal.profit_probability:.1%}")
        print(f"   📍 Entry: {signal.entry_price:.5f}")
        print(f"   🛑 Stop: {signal.stop_loss:.5f}")
        print(f"   🎯 Target: {signal.take_profit:.5f}")
        print(f"   ⏰ Horizon: {signal.time_horizon}")
        print(f"   📊 Position Size: {signal.position_size_recommendation:.2f}x")
        print(f"   🧠 Reasoning: {signal.reasoning[:100]}...")
    
    # Placeholder methods for technical calculations
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI."""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not rsi.empty else 50
        except:
            return 50
    
    def _calculate_macd(self, prices: pd.Series) -> float:
        """Calculate MACD."""
        try:
            ema12 = prices.ewm(span=12).mean()
            ema26 = prices.ewm(span=26).mean()
            macd = ema12 - ema26
            return macd.iloc[-1] if not macd.empty else 0
        except:
            return 0
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Dict:
        """Calculate Bollinger Bands."""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            return {
                'upper': (sma + 2 * std).iloc[-1],
                'middle': sma.iloc[-1],
                'lower': (sma - 2 * std).iloc[-1]
            }
        except:
            return {'upper': 0, 'middle': 0, 'lower': 0}
    
    # Additional placeholder methods would be implemented here
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range."""
        try:
            high = data['mid_h'].astype(float)
            low = data['mid_l'].astype(float)
            close = data['mid_c'].astype(float)
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            return atr.iloc[-1] if not atr.empty else 0.001
        except:
            return 0.001
    
    def _calculate_timeframe_alignment(self, short: float, medium: float, long: float) -> float:
        """Calculate timeframe alignment score."""
        return 1 if short > medium > long else -1 if short < medium < long else 0
    
    def _should_analyze_pair(self, pair: str) -> bool:
        """Check if pair should be analyzed."""
        return True  # Placeholder
    
    def _reset_daily_counters_if_needed(self):
        """Reset daily counters if new day."""
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.daily_trade_count:
            self.daily_trade_count = {today: 0}
    
    def _identify_price_patterns(self, data: pd.DataFrame) -> Dict:
        """Identify price action patterns."""
        try:
            patterns = {}
            close = data['mid_c'].astype(float)
            high = data['mid_h'].astype(float)
            low = data['mid_l'].astype(float)
            
            # Doji patterns
            patterns['doji_count'] = self._count_doji_candles(data)
            
            # Hammer/shooting star patterns
            patterns['hammer_count'] = self._count_hammer_candles(data)
            
            # Engulfing patterns
            patterns['engulfing'] = self._detect_engulfing_patterns(data)
            
            return patterns
        except:
            return {}
    
    def _find_resistance_levels(self, highs: pd.Series) -> List[float]:
        """Find resistance levels from swing highs."""
        try:
            resistance_levels = []
            for i in range(2, len(highs) - 2):
                if (highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i-2] and
                    highs.iloc[i] > highs.iloc[i+1] and highs.iloc[i] > highs.iloc[i+2]):
                    resistance_levels.append(highs.iloc[i])
            
            return sorted(resistance_levels, reverse=True)[:5]  # Top 5 levels
        except:
            return []
    
    def _find_support_levels(self, lows: pd.Series) -> List[float]:
        """Find support levels from swing lows."""
        try:
            support_levels = []
            for i in range(2, len(lows) - 2):
                if (lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i-2] and
                    lows.iloc[i] < lows.iloc[i+1] and lows.iloc[i] < lows.iloc[i+2]):
                    support_levels.append(lows.iloc[i])
            
            return sorted(support_levels)[:5]  # Bottom 5 levels
        except:
            return []
    
    def _calculate_level_strength(self, levels: List[float], current_price: float, level_type: str) -> float:
        """Calculate strength of support/resistance levels."""
        try:
            if not levels:
                return 0
            
            if level_type == 'support':
                closest_level = max([level for level in levels if level < current_price], default=0)
            else:  # resistance
                closest_level = min([level for level in levels if level > current_price], default=float('inf'))
            
            if closest_level == 0 or closest_level == float('inf'):
                return 0
            
            distance = abs(current_price - closest_level) / current_price
            strength = max(0, 1 - distance * 100)  # Closer = stronger
            
            return min(1, strength)
        except:
            return 0
    
    def _count_higher_highs(self, highs: pd.Series) -> int:
        """Count higher highs in recent price action."""
        try:
            count = 0
            for i in range(1, min(10, len(highs))):  # Last 10 periods
                if highs.iloc[-i] > highs.iloc[-i-1]:
                    count += 1
            return count
        except:
            return 0
    
    def _count_higher_lows(self, lows: pd.Series) -> int:
        """Count higher lows in recent price action."""
        try:
            count = 0
            for i in range(1, min(10, len(lows))):  # Last 10 periods
                if lows.iloc[-i] > lows.iloc[-i-1]:
                    count += 1
            return count
        except:
            return 0
    
    def _count_lower_highs(self, highs: pd.Series) -> int:
        """Count lower highs in recent price action."""
        try:
            count = 0
            for i in range(1, min(10, len(highs))):  # Last 10 periods
                if highs.iloc[-i] < highs.iloc[-i-1]:
                    count += 1
            return count
        except:
            return 0
    
    def _count_lower_lows(self, lows: pd.Series) -> int:
        """Count lower lows in recent price action."""
        try:
            count = 0
            for i in range(1, min(10, len(lows))):  # Last 10 periods
                if lows.iloc[-i] < lows.iloc[-i-1]:
                    count += 1
            return count
        except:
            return 0
    
    def _detect_range_bound_market(self, data: pd.DataFrame) -> bool:
        """Detect if market is range-bound."""
        try:
            close = data['mid_c'].astype(float)
            high = data['mid_h'].astype(float)
            low = data['mid_l'].astype(float)
            
            # Calculate range over last 20 periods
            recent_high = high.tail(20).max()
            recent_low = low.tail(20).min()
            current_price = close.iloc[-1]
            
            range_size = (recent_high - recent_low) / current_price
            
            # Consider range-bound if range is small and price is oscillating
            return range_size < 0.01  # 1% range
        except:
            return False
    
    def _find_range_top(self, data: pd.DataFrame) -> float:
        """Find the top of the current range."""
        try:
            high = data['mid_h'].astype(float)
            return high.tail(20).max()
        except:
            return 0
    
    def _find_range_bottom(self, data: pd.DataFrame) -> float:
        """Find the bottom of the current range."""
        try:
            low = data['mid_l'].astype(float)
            return low.tail(20).min()
        except:
            return 0
    
    def _calculate_breakout_probability(self, structure: Dict, patterns: Dict) -> float:
        """Calculate probability of a breakout."""
        try:
            probability = 0
            
            # Range compression increases breakout probability
            if structure.get('range_bound', False):
                probability += 0.3
            
            # Volatility compression
            if structure.get('range_top', 0) - structure.get('range_bottom', 0) < 0.01:
                probability += 0.2
            
            # Pattern-based signals
            if patterns.get('doji_count', 0) > 2:
                probability += 0.2
            
            # Market structure signals
            if structure.get('higher_highs', 0) > 3 or structure.get('lower_lows', 0) > 3:
                probability += 0.3
            
            return min(1, probability)
        except:
            return 0
    
    def _calculate_market_confidence(self, trend_strength: float, volatility: float, 
                                   support_strength: float, resistance_strength: float) -> float:
        """Calculate overall market confidence."""
        try:
            # Base confidence from trend clarity
            trend_confidence = abs(trend_strength)
            
            # Volatility adjustment (moderate volatility is good)
            volatility_confidence = 1 - min(1, abs(volatility - 0.01) * 50)
            
            # Support/resistance strength
            level_confidence = (support_strength + resistance_strength) / 2
            
            # Weighted average
            total_confidence = (trend_confidence * 0.4 + 
                              volatility_confidence * 0.3 + 
                              level_confidence * 0.3)
            
            return max(0, min(1, total_confidence))
        except:
            return 0.5
    
    def _calculate_profit_probability(self, market_analysis: MarketAnalysis, signal_data: Dict) -> float:
        """Calculate probability of profit for the signal."""
        try:
            base_probability = market_analysis.confidence
            
            # Adjust based on market condition
            condition_multiplier = {
                MarketCondition.STRONG_TREND_UP: 1.2,
                MarketCondition.STRONG_TREND_DOWN: 1.2,
                MarketCondition.WEAK_TREND_UP: 0.9,
                MarketCondition.WEAK_TREND_DOWN: 0.9,
                MarketCondition.SIDEWAYS: 0.8,
                MarketCondition.VOLATILE: 0.7,
                MarketCondition.BREAKOUT: 1.1
            }.get(market_analysis.condition, 1.0)
            
            # Adjust for signal confidence
            signal_confidence = signal_data.get('confidence', 0.5)
            
            # Calculate risk/reward ratio impact
            try:
                entry = signal_data.get('entry_price', 0)
                stop = signal_data.get('stop_loss', 0)
                target = signal_data.get('take_profit', 0)
                
                if entry and stop and target:
                    risk = abs(entry - stop)
                    reward = abs(target - entry)
                    rr_ratio = reward / risk if risk > 0 else 1
                    rr_multiplier = min(1.3, 0.5 + rr_ratio * 0.2)
                else:
                    rr_multiplier = 1.0
            except:
                rr_multiplier = 1.0
            
            probability = base_probability * condition_multiplier * signal_confidence * rr_multiplier
            return max(0.3, min(0.95, probability))  # Cap between 30% and 95%
        except:
            return 0.6
    
    def _save_adaptive_signal(self, signal: AdaptiveSignal):
        """Save adaptive signal to file."""
        try:
            signals_file = f"logs/adaptive_signals_{datetime.now().strftime('%Y%m%d')}.json"
            
            os.makedirs("logs", exist_ok=True)
            
            signals = []
            if os.path.exists(signals_file):
                with open(signals_file, 'r') as f:
                    signals = json.load(f)
            
            signal_dict = {
                'timestamp': signal.timestamp,
                'currency_pair': signal.currency_pair,
                'signal_type': signal.signal_type,
                'confidence': signal.confidence,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'reasoning': signal.reasoning,
                'market_condition': signal.market_condition.value,
                'strategy_used': signal.strategy_used.value,
                'risk_level': signal.risk_level,
                'position_size_recommendation': signal.position_size_recommendation,
                'time_horizon': signal.time_horizon,
                'profit_probability': signal.profit_probability,
                'alternative_entry': signal.alternative_entry,
                'trailing_stop': signal.trailing_stop
            }
            
            signals.append(signal_dict)
            
            with open(signals_file, 'w') as f:
                json.dump(signals, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error saving adaptive signal: {e}")
    
    # Pattern detection helpers
    def _count_doji_candles(self, data: pd.DataFrame) -> int:
        """Count doji candles in recent data."""
        try:
            count = 0
            for i in range(max(0, len(data) - 10), len(data)):
                open_price = float(data.iloc[i]['mid_o'])
                close_price = float(data.iloc[i]['mid_c'])
                high_price = float(data.iloc[i]['mid_h'])
                low_price = float(data.iloc[i]['mid_l'])
                
                body_size = abs(close_price - open_price)
                total_range = high_price - low_price
                
                # Doji if body is less than 10% of total range
                if total_range > 0 and body_size / total_range < 0.1:
                    count += 1
            
            return count
        except:
            return 0
    
    def _count_hammer_candles(self, data: pd.DataFrame) -> int:
        """Count hammer/shooting star candles."""
        try:
            count = 0
            for i in range(max(0, len(data) - 10), len(data)):
                open_price = float(data.iloc[i]['mid_o'])
                close_price = float(data.iloc[i]['mid_c'])
                high_price = float(data.iloc[i]['mid_h'])
                low_price = float(data.iloc[i]['mid_l'])
                
                body_size = abs(close_price - open_price)
                upper_shadow = high_price - max(open_price, close_price)
                lower_shadow = min(open_price, close_price) - low_price
                
                # Hammer pattern: long lower shadow, short upper shadow
                if (lower_shadow > 2 * body_size and upper_shadow < body_size):
                    count += 1
                # Shooting star: long upper shadow, short lower shadow  
                elif (upper_shadow > 2 * body_size and lower_shadow < body_size):
                    count += 1
            
            return count
        except:
            return 0
    
    def _detect_engulfing_patterns(self, data: pd.DataFrame) -> int:
        """Detect bullish/bearish engulfing patterns."""
        try:
            count = 0
            for i in range(1, min(len(data), 10)):
                prev_open = float(data.iloc[-i-1]['mid_o'])
                prev_close = float(data.iloc[-i-1]['mid_c'])
                curr_open = float(data.iloc[-i]['mid_o'])
                curr_close = float(data.iloc[-i]['mid_c'])
                
                # Bullish engulfing
                if (prev_close < prev_open and curr_close > curr_open and
                    curr_open < prev_close and curr_close > prev_open):
                    count += 1
                # Bearish engulfing
                elif (prev_close > prev_open and curr_close < curr_open and
                      curr_open > prev_close and curr_close < prev_open):
                    count += 1
            
            return count
        except:
            return 0
    
    # Additional methods would be implemented for complete functionality
    def stop_adaptive_analysis(self):
        """Stop the adaptive analysis."""
        self.is_running = False
        print("🛑 Adaptive analysis stopped")

def main():
    """Example usage."""
    try:
        analyzer = AdaptiveTradingAnalyzer(update_interval=60)
        analyzer.start_adaptive_analysis(['EUR_USD', 'GBP_USD'])
        
        while True:
            time.sleep(300)  # Summary every 5 minutes
            print(f"\n📊 Active signals: {len(analyzer.signals_history)}")
            
    except KeyboardInterrupt:
        analyzer.stop_adaptive_analysis()

if __name__ == "__main__":
    main()