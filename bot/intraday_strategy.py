import pandas as pd
import numpy as np
import pytz
from datetime import datetime, timedelta
from models.trade_decision import TradeDecision
from technicals.indicators import BollingerBands, ATR, RSI, MACD, EMA, ADX, heikin_ashi, identify_pin_bar
from technicals.patterns import apply_patterns
import constants.defs as defs

class IntradayStrategy:
    """
    Enhanced intraday trading strategy with focus on:
    - Intraday breakouts and reversals
    - Session-based filters
    - Momentum shifts
    - Volatility-based entries
    - Time-based risk management
    """
    
    def __init__(self):
        self.session_times = {
            'london_open': '08:00',
            'london_close': '16:00',
            'ny_open': '13:00',
            'ny_close': '21:00',
            'tokyo_open': '00:00',
            'tokyo_close': '08:00'
        }
        
    def is_session_active(self, timestamp, session='london_ny'):
        """Check if major trading session is active"""
        eastern = pytz.timezone('US/Eastern')
        utc = pytz.UTC
        
        if timestamp.tzinfo is None:
            timestamp = utc.localize(timestamp)
        
        eastern_time = timestamp.astimezone(eastern)
        hour = eastern_time.hour
        
        if session == 'london_ny':
            return 8 <= hour <= 16  # London-NY overlap
        elif session == 'ny_only':
            return 13 <= hour <= 21  # NY session
        elif session == 'london_only':
            return 8 <= hour <= 16  # London session
        elif session == 'tokyo':
            return 0 <= hour <= 8  # Tokyo session
        
        return True
    
    def detect_intraday_breakout(self, df, lookback=20):
        """Detect intraday breakouts from consolidation"""
        if len(df) < lookback:
            return False, 0
            
        recent_high = df['mid_h'].rolling(lookback).max().iloc[-1]
        recent_low = df['mid_l'].rolling(lookback).min().iloc[-1]
        current_price = df['mid_c'].iloc[-1]
        
        # Calculate breakout thresholds
        breakout_up = recent_high + (recent_high - recent_low) * 0.1
        breakout_down = recent_low - (recent_high - recent_low) * 0.1
        
        if current_price > breakout_up:
            return True, 1  # Bullish breakout
        elif current_price < breakout_down:
            return True, -1  # Bearish breakout
            
        return False, 0
    
    def detect_momentum_shift(self, df, period=5):
        """Detect momentum shifts using RSI and MACD"""
        if len(df) < period + 10:
            return False, 0
            
        # RSI momentum
        rsi_current = df['RSI_14'].iloc[-1]
        rsi_prev = df['RSI_14'].iloc[-period]
        
        # MACD momentum
        macd_current = df['MACD_HIST'].iloc[-1]
        macd_prev = df['MACD_HIST'].iloc[-period]
        
        # Volume confirmation (if available)
        volume_increasing = True
        if 'volume' in df.columns:
            current_vol = df['volume'].iloc[-1]
            avg_vol = df['volume'].rolling(period).mean().iloc[-1]
            volume_increasing = current_vol > avg_vol * 1.2
        
        # Bullish momentum shift
        if (rsi_current > rsi_prev and macd_current > macd_prev and 
            rsi_current < 70 and volume_increasing):
            return True, 1
            
        # Bearish momentum shift
        if (rsi_current < rsi_prev and macd_current < macd_prev and 
            rsi_current > 30 and volume_increasing):
            return True, -1
            
        return False, 0
    
    def detect_reversal_pattern(self, df):
        """Detect intraday reversal patterns"""
        if len(df) < 3:
            return False, 0
            
        # Get last 3 candles
        last_3 = df.tail(3)
        
        # Double top/bottom pattern
        highs = last_3['mid_h'].values
        lows = last_3['mid_l'].values
        
        # Double top (bearish reversal)
        if (highs[0] > highs[1] and abs(highs[0] - highs[2]) < 0.0001 and 
            highs[1] < highs[0] and highs[1] < highs[2]):
            return True, -1
            
        # Double bottom (bullish reversal)
        if (lows[0] < lows[1] and abs(lows[0] - lows[2]) < 0.0001 and 
            lows[1] > lows[0] and lows[1] > lows[2]):
            return True, 1
            
        # Pin bar reversal
        if df['PIN_BAR_BULL'].iloc[-1]:
            return True, 1
        elif df['PIN_BAR_BEAR'].iloc[-1]:
            return True, -1
            
        return False, 0
    
    def calculate_intraday_support_resistance(self, df, lookback=50):
        """Calculate intraday support and resistance levels"""
        if len(df) < lookback:
            return None, None
            
        recent_data = df.tail(lookback)
        
        # Find pivot points
        highs = recent_data['mid_h'].values
        lows = recent_data['mid_l'].values
        
        # Resistance (recent highs)
        resistance_levels = []
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                resistance_levels.append(highs[i])
        
        # Support (recent lows)
        support_levels = []
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                support_levels.append(lows[i])
        
        if resistance_levels:
            resistance = max(resistance_levels)
        else:
            resistance = df['mid_h'].max()
            
        if support_levels:
            support = min(support_levels)
        else:
            support = df['mid_l'].min()
            
        return support, resistance
    
    def get_intraday_signal(self, df, trade_settings, timestamp):
        """Main intraday signal generation"""
        if len(df) < 50:
            return defs.NONE
            
        current_row = df.iloc[-1]
        
        # Session filter
        if not self.is_session_active(timestamp, 'london_ny'):
            return defs.NONE
        
        # Volatility filter
        atr = current_row[f"ATR_{trade_settings.atr_period}"]
        avg_atr = df[f"ATR_{trade_settings.atr_period}"].rolling(20).mean().iloc[-1]
        volatility_ok = 0.7 < (atr / avg_atr) < 2.0
        
        if not volatility_ok:
            return defs.NONE
        
        # Spread filter
        if current_row.SPREAD > trade_settings.maxspread:
            return defs.NONE
        
        # Detect patterns
        breakout_detected, breakout_direction = self.detect_intraday_breakout(df)
        momentum_shift, momentum_direction = self.detect_momentum_shift(df)
        reversal_detected, reversal_direction = self.detect_reversal_pattern(df)
        
        # Get support/resistance levels
        support, resistance = self.calculate_intraday_support_resistance(df)
        
        # Entry conditions for LONG
        long_conditions = [
            current_row.mid_c > current_row['EMA_10'],
            current_row['EMA_10'] > current_row['EMA_30'],
            current_row['RSI_14'] < 65,
            current_row['MACD_HIST'] > 0,
            current_row['ADX_14'] > 20,
            current_row['HA_Close'] > current_row['HA_Open_3MEAN']
        ]
        
        # Entry conditions for SHORT
        short_conditions = [
            current_row.mid_c < current_row['EMA_10'],
            current_row['EMA_10'] < current_row['EMA_30'],
            current_row['RSI_14'] > 35,
            current_row['MACD_HIST'] < 0,
            current_row['ADX_14'] > 20,
            current_row['HA_Close'] < current_row['HA_Open_3MEAN']
        ]
        
        # Pattern confirmation
        long_pattern = (breakout_detected and breakout_direction == 1) or \
                      (momentum_shift and momentum_direction == 1) or \
                      (reversal_detected and reversal_direction == 1)
        
        short_pattern = (breakout_detected and breakout_direction == -1) or \
                       (momentum_shift and momentum_direction == -1) or \
                       (reversal_detected and reversal_direction == -1)
        
        # Final signal generation
        if all(long_conditions) and long_pattern:
            return defs.BUY
        elif all(short_conditions) and short_pattern:
            return defs.SELL
            
        return defs.NONE
    
    def calculate_intraday_stop_loss(self, df, signal, trade_settings):
        """Calculate intraday-specific stop loss"""
        current_row = df.iloc[-1]
        atr = current_row[f"ATR_{trade_settings.atr_period}"]
        
        if signal == defs.BUY:
            # Tighter stop for intraday
            stop_loss = current_row.mid_c - (atr * 1.2)
            # Don't go below recent low
            recent_low = df['mid_l'].tail(5).min()
            stop_loss = max(stop_loss, recent_low - (atr * 0.5))
            
        elif signal == defs.SELL:
            # Tighter stop for intraday
            stop_loss = current_row.mid_c + (atr * 1.2)
            # Don't go above recent high
            recent_high = df['mid_h'].tail(5).max()
            stop_loss = min(stop_loss, recent_high + (atr * 0.5))
        else:
            return 0.0
            
        return stop_loss
    
    def calculate_intraday_take_profit(self, df, signal, stop_loss, trade_settings):
        """Calculate intraday-specific take profit"""
        current_row = df.iloc[-1]
        atr = current_row[f"ATR_{trade_settings.atr_period}"]
        
        if signal == defs.BUY:
            risk = current_row.mid_c - stop_loss
            take_profit = current_row.mid_c + (risk * trade_settings.riskreward)
            
        elif signal == defs.SELL:
            risk = stop_loss - current_row.mid_c
            take_profit = current_row.mid_c - (risk * trade_settings.riskreward)
        else:
            return 0.0
            
        return take_profit