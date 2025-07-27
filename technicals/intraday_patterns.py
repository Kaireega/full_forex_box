import pandas as pd
import numpy as np
from typing import Tuple, Dict, List

class IntradayPatterns:
    """
    Enhanced intraday pattern recognition with focus on:
    - Breakout patterns
    - Reversal patterns
    - Momentum patterns
    - Volume confirmation
    - Support/Resistance levels
    """
    
    def __init__(self):
        self.pattern_thresholds = {
            'breakout_threshold': 0.1,  # 10% of range
            'reversal_threshold': 0.05,  # 5% of range
            'momentum_threshold': 0.02,  # 2% of range
            'volume_threshold': 1.2,     # 20% above average
            'consolidation_threshold': 0.03  # 3% range for consolidation
        }
    
    def detect_breakout_patterns(self, df: pd.DataFrame, lookback: int = 20) -> Dict:
        """
        Detect various breakout patterns:
        - Range breakout
        - Channel breakout
        - Triangle breakout
        - Flag/pennant breakout
        """
        if len(df) < lookback:
            return {'breakout': False, 'direction': 0, 'strength': 0}
        
        patterns = {
            'range_breakout': self._detect_range_breakout(df, lookback),
            'channel_breakout': self._detect_channel_breakout(df, lookback),
            'triangle_breakout': self._detect_triangle_breakout(df, lookback),
            'flag_breakout': self._detect_flag_breakout(df, lookback)
        }
        
        # Aggregate results
        breakout_detected = any(p['detected'] for p in patterns.values())
        directions = [p['direction'] for p in patterns.values() if p['detected']]
        strengths = [p['strength'] for p in patterns.values() if p['detected']]
        
        if breakout_detected:
            # Use the strongest signal
            max_strength_idx = strengths.index(max(strengths))
            direction = directions[max_strength_idx]
            strength = strengths[max_strength_idx]
        else:
            direction = 0
            strength = 0
        
        return {
            'breakout': breakout_detected,
            'direction': direction,
            'strength': strength,
            'patterns': patterns
        }
    
    def _detect_range_breakout(self, df: pd.DataFrame, lookback: int) -> Dict:
        """Detect breakout from horizontal range"""
        recent_data = df.tail(lookback)
        
        # Calculate range
        range_high = recent_data['mid_h'].max()
        range_low = recent_data['mid_l'].min()
        range_size = range_high - range_low
        
        current_price = df['mid_c'].iloc[-1]
        breakout_threshold = range_size * self.pattern_thresholds['breakout_threshold']
        
        # Check for breakout
        if current_price > range_high + breakout_threshold:
            strength = (current_price - range_high) / range_size
            return {'detected': True, 'direction': 1, 'strength': min(strength, 1.0)}
        elif current_price < range_low - breakout_threshold:
            strength = (range_low - current_price) / range_size
            return {'detected': True, 'direction': -1, 'strength': min(strength, 1.0)}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def _detect_channel_breakout(self, df: pd.DataFrame, lookback: int) -> Dict:
        """Detect breakout from price channel"""
        if len(df) < lookback:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        # Calculate channel lines
        highs = df['mid_h'].tail(lookback).values
        lows = df['mid_l'].tail(lookback).values
        
        # Simple linear regression for channel lines
        x = np.arange(len(highs))
        
        # Upper channel (resistance)
        high_slope, high_intercept = np.polyfit(x, highs, 1)
        upper_channel = high_slope * (len(highs) - 1) + high_intercept
        
        # Lower channel (support)
        low_slope, low_intercept = np.polyfit(x, lows, 1)
        lower_channel = low_slope * (len(lows) - 1) + low_intercept
        
        current_price = df['mid_c'].iloc[-1]
        channel_width = upper_channel - lower_channel
        breakout_threshold = channel_width * self.pattern_thresholds['breakout_threshold']
        
        # Check for breakout
        if current_price > upper_channel + breakout_threshold:
            strength = (current_price - upper_channel) / channel_width
            return {'detected': True, 'direction': 1, 'strength': min(strength, 1.0)}
        elif current_price < lower_channel - breakout_threshold:
            strength = (lower_channel - current_price) / channel_width
            return {'detected': True, 'direction': -1, 'strength': min(strength, 1.0)}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def _detect_triangle_breakout(self, df: pd.DataFrame, lookback: int) -> Dict:
        """Detect breakout from triangle pattern"""
        if len(df) < lookback:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        recent_data = df.tail(lookback)
        
        # Calculate converging lines
        highs = recent_data['mid_h'].values
        lows = recent_data['mid_l'].values
        x = np.arange(len(highs))
        
        # Upper line (descending)
        high_slope, high_intercept = np.polyfit(x, highs, 1)
        
        # Lower line (ascending)
        low_slope, low_intercept = np.polyfit(x, lows, 1)
        
        # Check if lines are converging (triangle)
        if high_slope < 0 and low_slope > 0:
            # Calculate intersection point
            intersection_x = (low_intercept - high_intercept) / (high_slope - low_slope)
            
            # If intersection is in the future, it's a valid triangle
            if intersection_x > len(highs):
                current_price = df['mid_c'].iloc[-1]
                upper_line = high_slope * (len(highs) - 1) + high_intercept
                lower_line = low_slope * (len(lows) - 1) + low_intercept
                
                triangle_width = upper_line - lower_line
                breakout_threshold = triangle_width * self.pattern_thresholds['breakout_threshold']
                
                # Check for breakout
                if current_price > upper_line + breakout_threshold:
                    strength = (current_price - upper_line) / triangle_width
                    return {'detected': True, 'direction': 1, 'strength': min(strength, 1.0)}
                elif current_price < lower_line - breakout_threshold:
                    strength = (lower_line - current_price) / triangle_width
                    return {'detected': True, 'direction': -1, 'strength': min(strength, 1.0)}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def _detect_flag_breakout(self, df: pd.DataFrame, lookback: int) -> Dict:
        """Detect breakout from flag/pennant pattern"""
        if len(df) < lookback:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        # Look for strong move followed by consolidation
        recent_data = df.tail(lookback)
        
        # Check for strong initial move
        first_half = recent_data.iloc[:lookback//2]
        second_half = recent_data.iloc[lookback//2:]
        
        initial_move = first_half['mid_c'].iloc[-1] - first_half['mid_c'].iloc[0]
        consolidation_range = second_half['mid_h'].max() - second_half['mid_l'].min()
        
        # Flag pattern: strong move followed by small consolidation
        if abs(initial_move) > consolidation_range * 2:
            current_price = df['mid_c'].iloc[-1]
            consolidation_high = second_half['mid_h'].max()
            consolidation_low = second_half['mid_l'].min()
            
            breakout_threshold = consolidation_range * self.pattern_thresholds['breakout_threshold']
            
            # Check for breakout
            if current_price > consolidation_high + breakout_threshold:
                strength = (current_price - consolidation_high) / consolidation_range
                return {'detected': True, 'direction': 1, 'strength': min(strength, 1.0)}
            elif current_price < consolidation_low - breakout_threshold:
                strength = (consolidation_low - current_price) / consolidation_range
                return {'detected': True, 'direction': -1, 'strength': min(strength, 1.0)}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def detect_reversal_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Detect reversal patterns:
        - Double top/bottom
        - Head and shoulders
        - V-shaped reversal
        - Pin bar reversal
        """
        patterns = {
            'double_top_bottom': self._detect_double_top_bottom(df),
            'head_shoulders': self._detect_head_shoulders(df),
            'v_reversal': self._detect_v_reversal(df),
            'pin_bar': self._detect_pin_bar_reversal(df)
        }
        
        # Aggregate results
        reversal_detected = any(p['detected'] for p in patterns.values())
        directions = [p['direction'] for p in patterns.values() if p['detected']]
        strengths = [p['strength'] for p in patterns.values() if p['detected']]
        
        if reversal_detected:
            max_strength_idx = strengths.index(max(strengths))
            direction = directions[max_strength_idx]
            strength = strengths[max_strength_idx]
        else:
            direction = 0
            strength = 0
        
        return {
            'reversal': reversal_detected,
            'direction': direction,
            'strength': strength,
            'patterns': patterns
        }
    
    def _detect_double_top_bottom(self, df: pd.DataFrame) -> Dict:
        """Detect double top/bottom pattern"""
        if len(df) < 10:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        # Look for two peaks/troughs at similar levels
        highs = df['mid_h'].tail(10).values
        lows = df['mid_l'].tail(10).values
        
        # Find local maxima and minima
        peaks = []
        troughs = []
        
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                peaks.append((i, highs[i]))
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                troughs.append((i, lows[i]))
        
        # Check for double top
        if len(peaks) >= 2:
            peak1, peak2 = peaks[-2], peaks[-1]
            if abs(peak1[1] - peak2[1]) < (peak1[1] * 0.001):  # Within 0.1%
                # Check if there's a trough between peaks
                trough_between = any(t[0] > peak1[0] and t[0] < peak2[0] for t in troughs)
                if trough_between:
                    strength = 1.0 - (abs(peak1[1] - peak2[1]) / peak1[1])
                    return {'detected': True, 'direction': -1, 'strength': strength}
        
        # Check for double bottom
        if len(troughs) >= 2:
            trough1, trough2 = troughs[-2], troughs[-1]
            if abs(trough1[1] - trough2[1]) < (trough1[1] * 0.001):  # Within 0.1%
                # Check if there's a peak between troughs
                peak_between = any(p[0] > trough1[0] and p[0] < trough2[0] for p in peaks)
                if peak_between:
                    strength = 1.0 - (abs(trough1[1] - trough2[1]) / trough1[1])
                    return {'detected': True, 'direction': 1, 'strength': strength}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def _detect_head_shoulders(self, df: pd.DataFrame) -> Dict:
        """Detect head and shoulders pattern"""
        if len(df) < 15:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        # This is a simplified H&S detection
        # In practice, you'd want more sophisticated pattern recognition
        highs = df['mid_h'].tail(15).values
        
        # Look for three peaks with middle peak higher
        peaks = []
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                peaks.append((i, highs[i]))
        
        if len(peaks) >= 3:
            left_shoulder, head, right_shoulder = peaks[-3], peaks[-2], peaks[-1]
            
            # Check H&S pattern: left shoulder < head > right shoulder
            if (left_shoulder[1] < head[1] and head[1] > right_shoulder[1] and
                abs(left_shoulder[1] - right_shoulder[1]) < (left_shoulder[1] * 0.01)):
                strength = 0.8
                return {'detected': True, 'direction': -1, 'strength': strength}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def _detect_v_reversal(self, df: pd.DataFrame) -> Dict:
        """Detect V-shaped reversal pattern"""
        if len(df) < 10:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        recent_data = df.tail(10)
        prices = recent_data['mid_c'].values
        
        # Look for sharp decline followed by sharp recovery (or vice versa)
        mid_point = len(prices) // 2
        
        first_half_trend = prices[mid_point] - prices[0]
        second_half_trend = prices[-1] - prices[mid_point]
        
        # V-shaped reversal: strong move down followed by strong move up
        if first_half_trend < -0.001 and second_half_trend > 0.001:
            strength = min(abs(first_half_trend) + abs(second_half_trend), 1.0)
            return {'detected': True, 'direction': 1, 'strength': strength}
        
        # Inverted V: strong move up followed by strong move down
        elif first_half_trend > 0.001 and second_half_trend < -0.001:
            strength = min(abs(first_half_trend) + abs(second_half_trend), 1.0)
            return {'detected': True, 'direction': -1, 'strength': strength}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def _detect_pin_bar_reversal(self, df: pd.DataFrame) -> Dict:
        """Detect pin bar reversal pattern"""
        if len(df) < 3:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        current_candle = df.iloc[-1]
        
        # Calculate candle properties
        body_size = abs(current_candle['mid_c'] - current_candle['mid_o'])
        total_range = current_candle['mid_h'] - current_candle['mid_l']
        
        if total_range == 0:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        body_percentage = body_size / total_range
        
        # Pin bar: small body with long wick
        if body_percentage < 0.3:
            upper_wick = current_candle['mid_h'] - max(current_candle['mid_c'], current_candle['mid_o'])
            lower_wick = min(current_candle['mid_c'], current_candle['mid_o']) - current_candle['mid_l']
            
            # Bullish pin bar: long lower wick
            if lower_wick > body_size * 2 and upper_wick < body_size:
                strength = min(lower_wick / total_range, 1.0)
                return {'detected': True, 'direction': 1, 'strength': strength}
            
            # Bearish pin bar: long upper wick
            elif upper_wick > body_size * 2 and lower_wick < body_size:
                strength = min(upper_wick / total_range, 1.0)
                return {'detected': True, 'direction': -1, 'strength': strength}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def detect_momentum_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Detect momentum patterns:
        - Momentum divergence
        - Momentum convergence
        - Momentum exhaustion
        """
        if len(df) < 20:
            return {'momentum': False, 'direction': 0, 'strength': 0}
        
        # Calculate momentum indicators
        rsi = df['RSI_14'].tail(10).values if 'RSI_14' in df.columns else None
        macd = df['MACD_HIST'].tail(10).values if 'MACD_HIST' in df.columns else None
        prices = df['mid_c'].tail(10).values
        
        patterns = {
            'rsi_divergence': self._detect_rsi_divergence(prices, rsi) if rsi is not None else {'detected': False},
            'macd_divergence': self._detect_macd_divergence(prices, macd) if macd is not None else {'detected': False},
            'momentum_exhaustion': self._detect_momentum_exhaustion(df)
        }
        
        # Aggregate results
        momentum_detected = any(p['detected'] for p in patterns.values())
        directions = [p['direction'] for p in patterns.values() if p['detected']]
        strengths = [p['strength'] for p in patterns.values() if p['detected']]
        
        if momentum_detected:
            max_strength_idx = strengths.index(max(strengths))
            direction = directions[max_strength_idx]
            strength = strengths[max_strength_idx]
        else:
            direction = 0
            strength = 0
        
        return {
            'momentum': momentum_detected,
            'direction': direction,
            'strength': strength,
            'patterns': patterns
        }
    
    def _detect_rsi_divergence(self, prices: np.ndarray, rsi: np.ndarray) -> Dict:
        """Detect RSI divergence with price"""
        if len(prices) < 5 or len(rsi) < 5:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        # Check for bullish divergence: price makes lower low, RSI makes higher low
        if (prices[-1] < prices[-3] and rsi[-1] > rsi[-3] and 
            prices[-3] < prices[-5] and rsi[-3] > rsi[-5]):
            strength = min(abs(prices[-1] - prices[-3]) / prices[-3], 1.0)
            return {'detected': True, 'direction': 1, 'strength': strength}
        
        # Check for bearish divergence: price makes higher high, RSI makes lower high
        elif (prices[-1] > prices[-3] and rsi[-1] < rsi[-3] and 
              prices[-3] > prices[-5] and rsi[-3] < rsi[-5]):
            strength = min(abs(prices[-1] - prices[-3]) / prices[-3], 1.0)
            return {'detected': True, 'direction': -1, 'strength': strength}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def _detect_macd_divergence(self, prices: np.ndarray, macd: np.ndarray) -> Dict:
        """Detect MACD divergence with price"""
        if len(prices) < 5 or len(macd) < 5:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        # Check for bullish divergence: price makes lower low, MACD makes higher low
        if (prices[-1] < prices[-3] and macd[-1] > macd[-3] and 
            prices[-3] < prices[-5] and macd[-3] > macd[-5]):
            strength = min(abs(prices[-1] - prices[-3]) / prices[-3], 1.0)
            return {'detected': True, 'direction': 1, 'strength': strength}
        
        # Check for bearish divergence: price makes higher high, MACD makes lower high
        elif (prices[-1] > prices[-3] and macd[-1] < macd[-3] and 
              prices[-3] > prices[-5] and macd[-3] < macd[-5]):
            strength = min(abs(prices[-1] - prices[-3]) / prices[-3], 1.0)
            return {'detected': True, 'direction': -1, 'strength': strength}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def _detect_momentum_exhaustion(self, df: pd.DataFrame) -> Dict:
        """Detect momentum exhaustion patterns"""
        if len(df) < 10:
            return {'detected': False, 'direction': 0, 'strength': 0}
        
        recent_data = df.tail(10)
        
        # Check for overbought/oversold conditions
        if 'RSI_14' in recent_data.columns:
            current_rsi = recent_data['RSI_14'].iloc[-1]
            
            # Overbought exhaustion
            if current_rsi > 80:
                return {'detected': True, 'direction': -1, 'strength': 0.8}
            
            # Oversold exhaustion
            elif current_rsi < 20:
                return {'detected': True, 'direction': 1, 'strength': 0.8}
        
        return {'detected': False, 'direction': 0, 'strength': 0}
    
    def get_support_resistance_levels(self, df: pd.DataFrame, lookback: int = 50) -> Dict:
        """Calculate dynamic support and resistance levels"""
        if len(df) < lookback:
            return {'support': None, 'resistance': None, 'levels': []}
        
        recent_data = df.tail(lookback)
        
        # Find pivot points
        highs = recent_data['mid_h'].values
        lows = recent_data['mid_l'].values
        
        resistance_levels = []
        support_levels = []
        
        # Find resistance levels (peaks)
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                resistance_levels.append(highs[i])
        
        # Find support levels (troughs)
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                support_levels.append(lows[i])
        
        # Group nearby levels
        resistance_levels = self._group_nearby_levels(resistance_levels, 0.001)
        support_levels = self._group_nearby_levels(support_levels, 0.001)
        
        current_price = df['mid_c'].iloc[-1]
        
        # Find nearest levels
        nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price)) if resistance_levels else None
        nearest_support = min(support_levels, key=lambda x: abs(x - current_price)) if support_levels else None
        
        return {
            'support': nearest_support,
            'resistance': nearest_resistance,
            'levels': {
                'resistance': resistance_levels,
                'support': support_levels
            }
        }
    
    def _group_nearby_levels(self, levels: List[float], threshold: float) -> List[float]:
        """Group nearby price levels"""
        if not levels:
            return []
        
        levels = sorted(levels)
        grouped = []
        current_group = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_group[-1]) <= threshold:
                current_group.append(level)
            else:
                # Use average of group
                grouped.append(sum(current_group) / len(current_group))
                current_group = [level]
        
        # Add last group
        if current_group:
            grouped.append(sum(current_group) / len(current_group))
        
        return grouped