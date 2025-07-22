#!/usr/bin/env python3
"""
Utility methods for the Unified Trading Analyzer

This module contains helper methods that are used by the unified trading analyzer
to keep the main file focused and manageable.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from analysis.unified_trading_analyzer import MarketCondition, TradingStrategy, MarketAnalysis

def get_adaptive_system_prompt(market_condition: MarketCondition) -> str:
    """Get system prompt adapted to market condition."""
    base_prompt = """You are an expert adaptive forex trading analyst with deep expertise in profiting from ALL market conditions."""
    
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

def create_adaptive_prompt(pair: str, market_data: Dict, market_analysis: MarketAnalysis) -> str:
    """Create adaptive prompt based on market conditions."""
    indicators = market_data['indicators']
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
    
    Generate profitable trading signal adapted to current conditions.
    """

def calculate_trend_strength(indicators: Dict, structure: Dict) -> float:
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
        
        total_strength = ma_alignment + structure_score
        return max(-1, min(1, total_strength))
    except Exception:
        return 0

def calculate_momentum(indicators: Dict) -> float:
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

def calculate_mean_reversion_signal(indicators: Dict) -> float:
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
                rsi_extreme = (rsi - 75) / 25
            elif rsi < 25:
                rsi_extreme = -(25 - rsi) / 25
            
            return max(-1, min(1, bb_position + rsi_extreme))
        
        return 0
    except Exception:
        return 0

def determine_market_condition(trend_strength: float, volatility: float, 
                              momentum: float, breakout_probability: float,
                              trend_threshold: float = 0.3, 
                              volatility_threshold: float = 0.015) -> MarketCondition:
    """Determine current market condition."""
    try:
        # Strong trends
        if abs(trend_strength) > 0.6:
            if trend_strength > 0:
                return MarketCondition.STRONG_TREND_UP
            else:
                return MarketCondition.STRONG_TREND_DOWN
        
        # Weak trends
        elif abs(trend_strength) > trend_threshold:
            if trend_strength > 0:
                return MarketCondition.WEAK_TREND_UP
            else:
                return MarketCondition.WEAK_TREND_DOWN
        
        # High volatility
        elif volatility > volatility_threshold * 2:
            return MarketCondition.VOLATILE
        
        # Breakout conditions
        elif breakout_probability > 0.7:
            return MarketCondition.BREAKOUT
        
        # Default to sideways
        else:
            return MarketCondition.SIDEWAYS
    except Exception:
        return MarketCondition.SIDEWAYS

def recommend_strategy(market_condition: MarketCondition, 
                      volatility: float, momentum: float,
                      volatility_threshold: float = 0.015) -> TradingStrategy:
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
    if volatility > volatility_threshold * 3:
        return TradingStrategy.SCALPING
    
    return base_strategy

def calculate_adaptive_position_size(market_analysis: MarketAnalysis) -> float:
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

def determine_time_horizon(market_analysis: MarketAnalysis) -> str:
    """Determine appropriate time horizon for the trade."""
    if market_analysis.condition in [MarketCondition.STRONG_TREND_UP, MarketCondition.STRONG_TREND_DOWN]:
        return "medium"
    elif market_analysis.condition == MarketCondition.SIDEWAYS:
        return "scalp"
    elif market_analysis.condition == MarketCondition.VOLATILE:
        return "short"
    elif market_analysis.condition == MarketCondition.BREAKOUT:
        return "short"
    else:
        return "short"

def calculate_profit_probability(market_analysis: MarketAnalysis, signal_data: Dict) -> float:
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
        return max(0.3, min(0.95, probability))
    except:
        return 0.6

def calculate_market_confidence(trend_strength: float, volatility: float, 
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

def calculate_breakout_probability(structure: Dict, patterns: Dict) -> float:
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

# Market structure helper functions
def find_resistance_levels(highs: pd.Series) -> List[float]:
    """Find resistance levels from swing highs."""
    try:
        resistance_levels = []
        for i in range(2, len(highs) - 2):
            if (highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i-2] and
                highs.iloc[i] > highs.iloc[i+1] and highs.iloc[i] > highs.iloc[i+2]):
                resistance_levels.append(highs.iloc[i])
        
        return sorted(resistance_levels, reverse=True)[:5]
    except:
        return []

def find_support_levels(lows: pd.Series) -> List[float]:
    """Find support levels from swing lows."""
    try:
        support_levels = []
        for i in range(2, len(lows) - 2):
            if (lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i-2] and
                lows.iloc[i] < lows.iloc[i+1] and lows.iloc[i] < lows.iloc[i+2]):
                support_levels.append(lows.iloc[i])
        
        return sorted(support_levels)[:5]
    except:
        return []

def calculate_level_strength(levels: List[float], current_price: float, level_type: str) -> float:
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
        strength = max(0, 1 - distance * 100)
        
        return min(1, strength)
    except:
        return 0

def count_higher_highs(highs: pd.Series) -> int:
    """Count higher highs in recent price action."""
    try:
        count = 0
        for i in range(1, min(10, len(highs))):
            if highs.iloc[-i] > highs.iloc[-i-1]:
                count += 1
        return count
    except:
        return 0

def count_higher_lows(lows: pd.Series) -> int:
    """Count higher lows in recent price action."""
    try:
        count = 0
        for i in range(1, min(10, len(lows))):
            if lows.iloc[-i] > lows.iloc[-i-1]:
                count += 1
        return count
    except:
        return 0

def count_lower_highs(highs: pd.Series) -> int:
    """Count lower highs in recent price action."""
    try:
        count = 0
        for i in range(1, min(10, len(highs))):
            if highs.iloc[-i] < highs.iloc[-i-1]:
                count += 1
        return count
    except:
        return 0

def count_lower_lows(lows: pd.Series) -> int:
    """Count lower lows in recent price action."""
    try:
        count = 0
        for i in range(1, min(10, len(lows))):
            if lows.iloc[-i] < lows.iloc[-i-1]:
                count += 1
        return count
    except:
        return 0

def detect_range_bound_market(data: pd.DataFrame) -> bool:
    """Detect if market is range-bound."""
    try:
        close = data['mid_c'].astype(float)
        high = data['mid_h'].astype(float)
        low = data['mid_l'].astype(float)
        
        recent_high = high.tail(20).max()
        recent_low = low.tail(20).min()
        current_price = close.iloc[-1]
        
        range_size = (recent_high - recent_low) / current_price
        
        return range_size < 0.01
    except:
        return False

def find_range_top(data: pd.DataFrame) -> float:
    """Find the top of the current range."""
    try:
        high = data['mid_h'].astype(float)
        return high.tail(20).max()
    except:
        return 0

def find_range_bottom(data: pd.DataFrame) -> float:
    """Find the bottom of the current range."""
    try:
        low = data['mid_l'].astype(float)
        return low.tail(20).min()
    except:
        return 0

# Pattern detection functions
def count_doji_candles(data: pd.DataFrame) -> int:
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
            
            if total_range > 0 and body_size / total_range < 0.1:
                count += 1
        
        return count
    except:
        return 0

def count_hammer_candles(data: pd.DataFrame) -> int:
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
            
            # Hammer or shooting star patterns
            if (lower_shadow > 2 * body_size and upper_shadow < body_size) or \
               (upper_shadow > 2 * body_size and lower_shadow < body_size):
                count += 1
        
        return count
    except:
        return 0

def detect_engulfing_patterns(data: pd.DataFrame) -> int:
    """Detect bullish/bearish engulfing patterns."""
    try:
        count = 0
        for i in range(1, min(len(data), 10)):
            prev_open = float(data.iloc[-i-1]['mid_o'])
            prev_close = float(data.iloc[-i-1]['mid_c'])
            curr_open = float(data.iloc[-i]['mid_o'])
            curr_close = float(data.iloc[-i]['mid_c'])
            
            # Bullish or bearish engulfing
            if ((prev_close < prev_open and curr_close > curr_open and
                curr_open < prev_close and curr_close > prev_open) or
                (prev_close > prev_open and curr_close < curr_open and
                 curr_open > prev_close and curr_close < prev_open)):
                count += 1
        
        return count
    except:
        return 0