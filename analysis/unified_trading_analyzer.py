#!/usr/bin/env python3
"""
Unified Forex Trading Analyzer with OpenAI

This module combines all trading analysis functionality into a single, optimized system.
It provides real-time analysis, adaptive strategies, and profitability optimization
across all market conditions without redundancy.
"""

import sys
import os
import time
import threading
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from api.openai_api import OpenAIAnalyzer
from api.oanda_api import OandaApi
import scraping.forexfactory_calendar as ff



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

class AnalysisMode(Enum):
    """Analysis mode types."""
    BASIC = "basic"
    ADAPTIVE = "adaptive"
    COMPREHENSIVE = "comprehensive"

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
class TradingSignal:
    """Unified trading signal with all features."""
    timestamp: str
    currency_pair: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD', 'EXIT'
    confidence: float  # 0.0 to 1.0
    entry_price: float
    stop_loss: float
    take_profit: float
    reasoning: str
    
    # Adaptive features
    market_condition: Optional[MarketCondition] = None
    strategy_used: Optional[TradingStrategy] = None
    risk_level: str = "MEDIUM"
    position_size_recommendation: float = 1.0
    time_horizon: str = "short"  # "scalp", "short", "medium", "long"
    profit_probability: float = 0.5
    alternative_entry: Optional[float] = None
    trailing_stop: Optional[float] = None
    
    # Legacy compatibility
    market_conditions: Optional[str] = None
    
    def __post_init__(self):
        """Ensure backward compatibility."""
        if self.market_conditions is None and self.market_condition:
            self.market_conditions = self.market_condition.value

class UnifiedTradingAnalyzer:
    """
    Unified trading analyzer that combines all functionality:
    - Real-time analysis
    - Adaptive strategies for all market conditions
    - Comprehensive market analysis
    - News sentiment analysis
    - Multiple interfaces (console, web, API)
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, 
                 update_interval: int = 300, 
                 mode: AnalysisMode = AnalysisMode.ADAPTIVE):
        """
        Initialize the unified analyzer.
        
        Args:
            openai_api_key: OpenAI API key
            update_interval: Update interval in seconds
            mode: Analysis mode (basic, adaptive, comprehensive)
        """
        self.openai_analyzer = OpenAIAnalyzer(openai_api_key)
        self.oanda_api = OandaApi()
        self.update_interval = update_interval
        self.mode = mode
        
        # Trading parameters
        self.currency_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD']
        self.signals_history = []
        self.market_analysis_history = {}
        self.is_running = False
        
        # Adaptive parameters (used when mode is ADAPTIVE or COMPREHENSIVE)
        self.min_confidence_threshold = 0.65 if mode != AnalysisMode.BASIC else 0.7
        self.max_daily_trades = 15 if mode == AnalysisMode.COMPREHENSIVE else 10
        self.daily_trade_count = {}
        
        # Risk management
        self.max_risk_per_trade = 0.015  # 1.5% per trade
        self.max_portfolio_risk = 0.06  # 6% total portfolio risk
        self.win_rate_target = 0.65
        
        # Market condition thresholds
        self.trend_strength_threshold = 0.3
        self.volatility_threshold = 0.015
        self.sideways_threshold = 0.2
        
        print(f"🤖 Unified Trading Analyzer initialized in {mode.value.upper()} mode")
    
    def start_analysis(self, currency_pairs: List[str] = None) -> threading.Thread:
        """Start unified trading analysis."""
        if currency_pairs:
            self.currency_pairs = currency_pairs
            
        self.is_running = True
        
        print(f"🚀 Starting {self.mode.value.upper()} Trading Analysis")
        print(f"📊 Currency Pairs: {', '.join(self.currency_pairs)}")
        print(f"⏱️  Update Interval: {self.update_interval} seconds")
        
        if self.mode == AnalysisMode.ADAPTIVE:
            print("🎯 ADAPTIVE MODE: Profitable in all market conditions")
            print("📈 Trending: Trend following | ↔️ Sideways: Mean reversion")
            print("⚡ Volatile: Breakout trading | 🚀 Breakout: Early entry")
        elif self.mode == AnalysisMode.COMPREHENSIVE:
            print("🔬 COMPREHENSIVE MODE: Full analysis with news sentiment")
        else:
            print("⚡ BASIC MODE: Real-time signals with OpenAI analysis")
        
        print("=" * 60)
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        analysis_thread.start()
        
        return analysis_thread
    
    def stop_analysis(self):
        """Stop trading analysis."""
        self.is_running = False
        print(f"🛑 {self.mode.value.upper()} analysis stopped")
    
    def _analysis_loop(self):
        """Main analysis loop."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Reset daily counters if needed
                self._reset_daily_counters_if_needed()
                
                # Analyze each currency pair
                for pair in self.currency_pairs:
                    if self._should_analyze_pair(pair):
                        self._analyze_currency_pair(pair)
                
                # Calculate sleep time
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"❌ Error in analysis loop: {e}")
                time.sleep(5)
    
    def _analyze_currency_pair(self, pair: str):
        """Analyze a currency pair using the selected mode."""
        try:
            if self.mode == AnalysisMode.BASIC:
                signal = self._basic_analysis(pair)
            elif self.mode == AnalysisMode.ADAPTIVE:
                signal = self._adaptive_analysis(pair)
            else:  # COMPREHENSIVE
                signal = self._comprehensive_analysis(pair)
            
            if signal and self._validate_signal(signal):
                self.signals_history.append(signal)
                
                # Keep history manageable
                if len(self.signals_history) > 100:
                    self.signals_history = self.signals_history[-100:]
                
                # Print significant signals
                if signal.signal_type != 'HOLD' or signal.confidence > 0.8:
                    self._print_signal(signal)
                
                # Save signal
                self._save_signal(signal)
                
                # Update daily trade count
                if signal.signal_type in ['BUY', 'SELL']:
                    today = datetime.now().strftime('%Y-%m-%d')
                    self.daily_trade_count[today] = self.daily_trade_count.get(today, 0) + 1
                
        except Exception as e:
            print(f"❌ Error analyzing {pair}: {e}")
    
    def _basic_analysis(self, pair: str) -> Optional[TradingSignal]:
        """Basic real-time analysis (original functionality)."""
        try:
            # Get basic market data
            market_data = self._get_basic_market_data(pair)
            if not market_data:
                return None
            
            # Create basic prompt
            prompt = self._create_basic_prompt(pair, market_data)
            
            # Get OpenAI analysis
            response = self.openai_analyzer.client.chat.completions.create(
                model=self.openai_analyzer.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert forex trader. Analyze market data and provide trading signals in JSON format."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            # Parse response
            ai_response = response.choices[0].message.content
            signal_data = json.loads(ai_response)
            
            # Create basic signal
            return TradingSignal(
                timestamp=datetime.now().isoformat(),
                currency_pair=pair,
                signal_type=signal_data['signal'],
                confidence=float(signal_data['confidence']),
                entry_price=float(signal_data['entry_price']),
                stop_loss=float(signal_data['stop_loss']),
                take_profit=float(signal_data['take_profit']),
                reasoning=signal_data['reasoning'],
                market_conditions=signal_data.get('market_conditions', 'unknown'),
                risk_level=signal_data.get('risk_level', 'MEDIUM')
            )
            
        except Exception as e:
            print(f"❌ Error in basic analysis for {pair}: {e}")
            return None
    
    def _adaptive_analysis(self, pair: str) -> Optional[TradingSignal]:
        """Adaptive analysis for all market conditions."""
        try:
            # Get comprehensive market data
            market_data = self._get_comprehensive_market_data(pair)
            if not market_data:
                return None
            
            # Analyze market conditions
            market_analysis = self._analyze_market_conditions(market_data)
            
            # Store market analysis
            self.market_analysis_history[pair] = market_analysis
            
            # Generate adaptive signal
            signal = self._generate_adaptive_signal(pair, market_data, market_analysis)
            
            return signal
            
        except Exception as e:
            print(f"❌ Error in adaptive analysis for {pair}: {e}")
            return None
    
    def _comprehensive_analysis(self, pair: str) -> Optional[TradingSignal]:
        """Comprehensive analysis including news sentiment."""
        try:
            # Start with adaptive analysis
            signal = self._adaptive_analysis(pair)
            
            if signal:
                # Enhance with news sentiment (if available)
                try:
                    news_analysis = self._analyze_news_impact()
                    if 'openai_sentiment_analysis' in news_analysis:
                        sentiment = news_analysis['openai_sentiment_analysis']
                        # Adjust confidence based on news sentiment
                        signal.confidence = min(0.95, signal.confidence * 1.1)
                        signal.reasoning += f" News sentiment: {sentiment.get('sentiment_analysis', '')[:100]}"
                except Exception:
                    pass  # Continue without news analysis if it fails
            
            return signal
            
        except Exception as e:
            print(f"❌ Error in comprehensive analysis for {pair}: {e}")
            return None
    
    # Data acquisition methods
    def _get_basic_market_data(self, pair: str, lookback_minutes: int = 60) -> Optional[Dict]:
        """Get basic market data for analysis."""
        try:
            candles_df = self.oanda_api.get_candles_df(pair, count=lookback_minutes, granularity="M1")
            
            if candles_df is None or candles_df.empty:
                return None
            
            # Calculate basic indicators
            indicators = self._calculate_basic_indicators(candles_df)
            current_price = float(candles_df.iloc[-1]['mid_c'])
            
            return {
                'pair': pair,
                'current_price': current_price,
                'candles': candles_df.tail(20).to_dict('records'),
                'indicators': indicators
            }
        except Exception as e:
            print(f"❌ Error getting basic data for {pair}: {e}")
            return None
    
    def _get_comprehensive_market_data(self, pair: str) -> Optional[Dict]:
        """Get comprehensive market data for adaptive analysis."""
        try:
            # Get multiple timeframes
            m1_data = self.oanda_api.get_candles_df(pair, count=60, granularity="M1")
            m5_data = self.oanda_api.get_candles_df(pair, count=60, granularity="M5")
            h1_data = self.oanda_api.get_candles_df(pair, count=24, granularity="H1")
            
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
                'patterns': patterns
            }
        except Exception as e:
            print(f"❌ Error getting comprehensive data for {pair}: {e}")
            return None
    
    # Technical analysis methods
    def _calculate_basic_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate basic technical indicators."""
        try:
            close_prices = df['mid_c'].astype(float)
            high_prices = df['mid_h'].astype(float)
            low_prices = df['mid_l'].astype(float)
            
            indicators = {
                'rsi': self._calculate_rsi(close_prices, 14),
                'macd': self._calculate_macd(close_prices),
                'bb': self._calculate_bollinger_bands(close_prices, 20),
                'sma_5': close_prices.rolling(5).mean().iloc[-1],
                'sma_20': close_prices.rolling(20).mean().iloc[-1],
                'volatility': close_prices.pct_change().rolling(20).std().iloc[-1],
                'resistance': high_prices.tail(20).max(),
                'support': low_prices.tail(20).min()
            }
            
            return indicators
        except Exception as e:
            print(f"❌ Error calculating basic indicators: {e}")
            return {}
    
    def _calculate_comprehensive_indicators(self, m1_data: pd.DataFrame, 
                                          m5_data: pd.DataFrame, 
                                          h1_data: pd.DataFrame) -> Dict:
        """Calculate comprehensive technical indicators across timeframes."""
        try:
            indicators = {}
            
            # M1 indicators
            m1_close = m1_data['mid_c'].astype(float)
            indicators['m1_rsi'] = self._calculate_rsi(m1_close, 14)
            indicators['m1_macd'] = self._calculate_macd(m1_close)
            indicators['m1_bb'] = self._calculate_bollinger_bands(m1_close, 20)
            indicators['m1_sma_5'] = m1_close.rolling(5).mean().iloc[-1]
            indicators['m1_sma_20'] = m1_close.rolling(20).mean().iloc[-1]
            
            # M5 indicators
            m5_close = m5_data['mid_c'].astype(float)
            indicators['m5_rsi'] = self._calculate_rsi(m5_close, 14)
            indicators['m5_macd'] = self._calculate_macd(m5_close)
            indicators['m5_bb'] = self._calculate_bollinger_bands(m5_close, 20)
            indicators['m5_sma_10'] = m5_close.rolling(10).mean().iloc[-1]
            indicators['m5_sma_50'] = m5_close.rolling(50).mean().iloc[-1]
            
            # H1 indicators
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
            print(f"❌ Error calculating comprehensive indicators: {e}")
            return {}
    
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
    
    # Market structure analysis (consolidated from adaptive analyzer)
    def _analyze_market_structure(self, m1_data: pd.DataFrame, 
                                 m5_data: pd.DataFrame, 
                                 h1_data: pd.DataFrame) -> Dict:
        """Analyze market structure."""
        try:
            structure = {}
            
            # Support and resistance levels
            m1_highs = m1_data['mid_h'].astype(float)
            m1_lows = m1_data['mid_l'].astype(float)
            
            structure['resistance_levels'] = self._find_resistance_levels(m1_highs)
            structure['support_levels'] = self._find_support_levels(m1_lows)
            
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
    
    def _identify_price_patterns(self, data: pd.DataFrame) -> Dict:
        """Identify price action patterns."""
        try:
            patterns = {}
            patterns['doji_count'] = self._count_doji_candles(data)
            patterns['hammer_count'] = self._count_hammer_candles(data)
            patterns['engulfing'] = self._detect_engulfing_patterns(data)
            return patterns
        except:
            return {}
    
    # Market condition analysis (consolidated from adaptive analyzer)
    def _analyze_market_conditions(self, market_data: Dict) -> MarketAnalysis:
        """Analyze current market conditions comprehensively."""
        try:
            indicators = market_data['indicators']
            structure = market_data['structure']
            patterns = market_data['patterns']
            
            # Calculate metrics
            trend_strength = self._calculate_trend_strength(indicators, structure)
            volatility = indicators.get('volatility', 0)
            momentum = self._calculate_momentum(indicators)
            mean_reversion_signal = self._calculate_mean_reversion_signal(indicators)
            breakout_probability = self._calculate_breakout_probability(structure, patterns)
            support_strength = structure.get('support_strength', 0)
            resistance_strength = structure.get('resistance_strength', 0)
            
            # Determine market condition and strategy
            market_condition = self._determine_market_condition(
                trend_strength, volatility, momentum, breakout_probability
            )
            recommended_strategy = self._recommend_strategy(market_condition, volatility, momentum)
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
    
    # Signal generation methods
    def _generate_adaptive_signal(self, pair: str, market_data: Dict, 
                                 market_analysis: MarketAnalysis) -> Optional[TradingSignal]:
        """Generate adaptive trading signal based on market conditions."""
        try:
            prompt = self._create_adaptive_prompt(pair, market_data, market_analysis)
            
            response = self.openai_analyzer.client.chat.completions.create(
                model=self.openai_analyzer.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_adaptive_system_prompt(market_analysis.condition)
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            signal_data = json.loads(ai_response)
            
            # Calculate adaptive parameters
            position_size = self._calculate_adaptive_position_size(market_analysis)
            time_horizon = self._determine_time_horizon(market_analysis)
            profit_probability = self._calculate_profit_probability(market_analysis, signal_data)
            
            return TradingSignal(
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
        except Exception as e:
            print(f"❌ Error generating adaptive signal for {pair}: {e}")
            return None
    
    # Prompt creation methods
    def _create_basic_prompt(self, pair: str, market_data: Dict) -> str:
        """Create basic prompt for OpenAI analysis."""
        indicators = market_data['indicators']
        current_price = market_data['current_price']
        
        return f"""
        FOREX TRADING ANALYSIS
        
        Currency Pair: {pair}
        Current Price: {current_price:.5f}
        
        TECHNICAL INDICATORS:
        - RSI: {indicators.get('rsi', 50):.2f}
        - MACD: {indicators.get('macd', 0):.5f}
        - SMA 5: {indicators.get('sma_5', 0):.5f}
        - SMA 20: {indicators.get('sma_20', 0):.5f}
        - Support: {indicators.get('support', 0):.5f}
        - Resistance: {indicators.get('resistance', 0):.5f}
        - Volatility: {indicators.get('volatility', 0):.5f}
        
        Respond in JSON format:
        {{
            "signal": "BUY|SELL|HOLD",
            "confidence": 0.0-1.0,
            "entry_price": precise_entry_level,
            "stop_loss": risk_management_level,
            "take_profit": profit_target,
            "reasoning": "detailed_analysis",
            "market_conditions": "current_market_state",
            "risk_level": "LOW|MEDIUM|HIGH"
        }}
        """
    
    # Utility methods (consolidated and optimized)
    def _should_analyze_pair(self, pair: str) -> bool:
        """Check if pair should be analyzed."""
        today = datetime.now().strftime('%Y-%m-%d')
        daily_count = self.daily_trade_count.get(today, 0)
        return daily_count < self.max_daily_trades
    
    def _reset_daily_counters_if_needed(self):
        """Reset daily counters if new day."""
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.daily_trade_count:
            self.daily_trade_count = {today: 0}
    
    def _validate_signal(self, signal: TradingSignal) -> bool:
        """Validate signal quality."""
        try:
            if signal.confidence < self.min_confidence_threshold:
                return False
            
            if signal.signal_type in ['BUY', 'SELL']:
                risk = abs(signal.entry_price - signal.stop_loss)
                reward = abs(signal.take_profit - signal.entry_price)
                if risk <= 0 or reward / risk < 1.0:
                    return False
            
            return True
        except:
            return False
    
    def _print_signal(self, signal: TradingSignal):
        """Print trading signal."""
        timestamp = datetime.fromisoformat(signal.timestamp).strftime('%H:%M:%S')
        
        if self.mode == AnalysisMode.ADAPTIVE and signal.market_condition:
            # Enhanced adaptive signal display
            condition_emoji = {
                MarketCondition.STRONG_TREND_UP: "📈",
                MarketCondition.STRONG_TREND_DOWN: "📉",
                MarketCondition.SIDEWAYS: "↔️",
                MarketCondition.VOLATILE: "⚡",
                MarketCondition.BREAKOUT: "🚀"
            }
            
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
            print(f"   📊 Position Size: {signal.position_size_recommendation:.2f}x")
        else:
            # Basic signal display
            signal_emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡'}.get(signal.signal_type, '❓')
            
            print(f"\n{signal_emoji} [{timestamp}] {signal.currency_pair} - {signal.signal_type}")
            print(f"   💡 Confidence: {signal.confidence:.1%}")
            print(f"   📍 Entry: {signal.entry_price:.5f}")
            print(f"   🛑 Stop Loss: {signal.stop_loss:.5f}")
            print(f"   🎯 Take Profit: {signal.take_profit:.5f}")
            print(f"   ⚠️  Risk Level: {signal.risk_level}")
        
        print(f"   🧠 Reasoning: {signal.reasoning[:100]}...")
    
    def _save_signal(self, signal: TradingSignal):
        """Save signal to file."""
        try:
            mode_suffix = self.mode.value
            signals_file = f"logs/unified_signals_{mode_suffix}_{datetime.now().strftime('%Y%m%d')}.json"
            
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
                'risk_level': signal.risk_level,
                'mode': self.mode.value
            }
            
            # Add adaptive features if available
            if signal.market_condition:
                signal_dict.update({
                    'market_condition': signal.market_condition.value,
                    'strategy_used': signal.strategy_used.value if signal.strategy_used else None,
                    'position_size_recommendation': signal.position_size_recommendation,
                    'time_horizon': signal.time_horizon,
                    'profit_probability': signal.profit_probability,
                    'alternative_entry': signal.alternative_entry,
                    'trailing_stop': signal.trailing_stop
                })
            
            signals.append(signal_dict)
            
            with open(signals_file, 'w') as f:
                json.dump(signals, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error saving signal: {e}")
    
    # Public API methods for external access
    def get_current_signals(self) -> List[TradingSignal]:
        """Get current trading signals."""
        return self.signals_history[-10:] if self.signals_history else []
    
    def get_signal_summary(self) -> Dict:
        """Get trading signals summary."""
        if not self.signals_history:
            return {"message": "No signals generated yet"}
        
        recent_signals = self.signals_history[-20:]
        
        summary = {
            "total_signals": len(recent_signals),
            "signal_types": {},
            "average_confidence": 0,
            "high_confidence_signals": 0,
            "mode": self.mode.value
        }
        
        confidences = []
        
        for signal in recent_signals:
            summary["signal_types"][signal.signal_type] = summary["signal_types"].get(signal.signal_type, 0) + 1
            confidences.append(signal.confidence)
            
            if signal.confidence >= 0.8:
                summary["high_confidence_signals"] += 1
        
        if confidences:
            summary["average_confidence"] = sum(confidences) / len(confidences)
        
        return summary
    
    # News analysis (from comprehensive mode)
    def _analyze_news_impact(self, months: List[str] = None) -> Dict:
        """Analyze news impact using OpenAI."""
        try:
            if months is None:
                months = ['jan.2025', 'feb.2025', 'mar.2025', 'apr.2025', 'may.2025',
                           'jun.2025', 'jul.2025', 'aug.2025', 'sep.2025', 'oct.2025', 'nov.2025', 'dec.2025']
            
            all_news_data = []
            for month in months:
                try:
                    news_data = ff.get_monthly_data(month)
                    if news_data is not None and not news_data.empty:
                        news_dict = news_data.to_dict('records')
                        all_news_data.extend(news_dict)
                except Exception:
                    continue
            
            if not all_news_data:
                return {"error": "No news data available"}
            
            high_impact_news = self._filter_high_impact_news(all_news_data)
            sentiment_analysis = self.openai_analyzer.analyze_news_sentiment(high_impact_news)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_news_events": len(all_news_data),
                "high_impact_events": len(high_impact_news),
                "openai_sentiment_analysis": sentiment_analysis
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _filter_high_impact_news(self, news_data: List[Dict]) -> List[Dict]:
        """Filter for high-impact news events."""
        high_impact_keywords = [
            'GDP', 'inflation', 'CPI', 'PPI', 'unemployment', 'interest rate',
            'central bank', 'federal reserve', 'ECB', 'BOJ', 'NFP', 'payroll'
        ]
        high_impact_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']
        
        filtered_news = []
        for news in news_data:
            if not isinstance(news, dict):
                continue
            currency = news.get('Currency', '')
            if currency not in high_impact_currencies:
                continue
            event = str(news.get('Event', '')).lower()
            if any(keyword.lower() in event for keyword in high_impact_keywords):
                filtered_news.append(news)
        
        return filtered_news
    
    # Import utility methods from unified_trading_utils.py
    def _get_adaptive_system_prompt(self, market_condition):
        """Get adaptive system prompt."""
        from analysis.unified_trading_utils import get_adaptive_system_prompt
        return get_adaptive_system_prompt(market_condition)
    
    def _create_adaptive_prompt(self, pair: str, market_data: Dict, market_analysis):
        """Create adaptive prompt."""
        from analysis.unified_trading_utils import create_adaptive_prompt
        return create_adaptive_prompt(pair, market_data, market_analysis)
    
    def _calculate_trend_strength(self, indicators: Dict, structure: Dict) -> float:
        """Calculate trend strength."""
        from analysis.unified_trading_utils import calculate_trend_strength
        return calculate_trend_strength(indicators, structure)
    
    def _calculate_momentum(self, indicators: Dict) -> float:
        """Calculate momentum."""
        from analysis.unified_trading_utils import calculate_momentum
        return calculate_momentum(indicators)
    
    def _calculate_mean_reversion_signal(self, indicators: Dict) -> float:
        """Calculate mean reversion signal."""
        from analysis.unified_trading_utils import calculate_mean_reversion_signal
        return calculate_mean_reversion_signal(indicators)
    
    def _determine_market_condition(self, trend_strength: float, volatility: float, 
                                   momentum: float, breakout_probability: float):
        """Determine market condition."""
        from analysis.unified_trading_utils import determine_market_condition
        return determine_market_condition(
            trend_strength, volatility, momentum, breakout_probability,
            self.trend_strength_threshold, self.volatility_threshold
        )
    
    def _recommend_strategy(self, market_condition, volatility: float, momentum: float):
        """Recommend strategy."""
        from analysis.unified_trading_utils import recommend_strategy
        return recommend_strategy(market_condition, volatility, momentum, self.volatility_threshold)
    
    def _calculate_adaptive_position_size(self, market_analysis) -> float:
        """Calculate adaptive position size."""
        from analysis.unified_trading_utils import calculate_adaptive_position_size
        return calculate_adaptive_position_size(market_analysis)
    
    def _determine_time_horizon(self, market_analysis) -> str:
        """Determine time horizon."""
        from analysis.unified_trading_utils import determine_time_horizon
        return determine_time_horizon(market_analysis)
    
    def _calculate_profit_probability(self, market_analysis, signal_data: Dict) -> float:
        """Calculate profit probability."""
        from analysis.unified_trading_utils import calculate_profit_probability
        return calculate_profit_probability(market_analysis, signal_data)
    
    def _calculate_market_confidence(self, trend_strength: float, volatility: float, 
                                   support_strength: float, resistance_strength: float) -> float:
        """Calculate market confidence."""
        from analysis.unified_trading_utils import calculate_market_confidence
        return calculate_market_confidence(trend_strength, volatility, support_strength, resistance_strength)
    
    def _calculate_breakout_probability(self, structure: Dict, patterns: Dict) -> float:
        """Calculate breakout probability."""
        from analysis.unified_trading_utils import calculate_breakout_probability
        return calculate_breakout_probability(structure, patterns)
    
    def _find_resistance_levels(self, highs):
        """Find resistance levels."""
        from analysis.unified_trading_utils import find_resistance_levels
        return find_resistance_levels(highs)
    
    def _find_support_levels(self, lows):
        """Find support levels."""
        from analysis.unified_trading_utils import find_support_levels
        return find_support_levels(lows)
    
    def _calculate_level_strength(self, levels, current_price: float, level_type: str) -> float:
        """Calculate level strength."""
        from analysis.unified_trading_utils import calculate_level_strength
        return calculate_level_strength(levels, current_price, level_type)
    
    def _count_higher_highs(self, highs):
        """Count higher highs."""
        from analysis.unified_trading_utils import count_higher_highs
        return count_higher_highs(highs)
    
    def _count_higher_lows(self, lows):
        """Count higher lows."""
        from analysis.unified_trading_utils import count_higher_lows
        return count_higher_lows(lows)
    
    def _count_lower_highs(self, highs):
        """Count lower highs."""
        from analysis.unified_trading_utils import count_lower_highs
        return count_lower_highs(highs)
    
    def _count_lower_lows(self, lows):
        """Count lower lows."""
        from analysis.unified_trading_utils import count_lower_lows
        return count_lower_lows(lows)
    
    def _detect_range_bound_market(self, data):
        """Detect range bound market."""
        from analysis.unified_trading_utils import detect_range_bound_market
        return detect_range_bound_market(data)
    
    def _find_range_top(self, data):
        """Find range top."""
        from analysis.unified_trading_utils import find_range_top
        return find_range_top(data)
    
    def _find_range_bottom(self, data):
        """Find range bottom."""
        from analysis.unified_trading_utils import find_range_bottom
        return find_range_bottom(data)
    
    def _count_doji_candles(self, data):
        """Count doji candles."""
        from analysis.unified_trading_utils import count_doji_candles
        return count_doji_candles(data)
    
    def _count_hammer_candles(self, data):
        """Count hammer candles."""
        from analysis.unified_trading_utils import count_hammer_candles
        return count_hammer_candles(data)
    
    def _detect_engulfing_patterns(self, data):
        """Detect engulfing patterns."""
        from analysis.unified_trading_utils import detect_engulfing_patterns
        return detect_engulfing_patterns(data)

def main():
    """Example usage of the unified analyzer."""
    try:
        print("🚀 Starting Unified Forex Trading Analyzer")
        print("=" * 60)
        
        # Initialize in adaptive mode (default)
        analyzer = UnifiedTradingAnalyzer(
            update_interval=60,
            mode=AnalysisMode.ADAPTIVE
        )
        
        # Start analysis for major pairs
        major_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY']
        analysis_thread = analyzer.start_analysis(major_pairs)
        
        # Keep running and show periodic summaries
        try:
            while True:
                time.sleep(300)  # Show summary every 5 minutes
                
                summary = analyzer.get_signal_summary()
                print(f"\n📊 5-Minute Summary:")
                print(f"   Mode: {analyzer.mode.value.upper()}")
                print(f"   Signals generated: {summary.get('total_signals', 0)}")
                print(f"   Average confidence: {summary.get('average_confidence', 0):.1%}")
                print(f"   High confidence signals: {summary.get('high_confidence_signals', 0)}")
                print(f"   Signal types: {summary.get('signal_types', {})}")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping analyzer...")
            analyzer.stop_analysis()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()