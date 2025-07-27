import json
import time
from datetime import datetime, timedelta
import pytz
from bot.candle_manager import CandleManager
from bot.intraday_strategy import IntradayStrategy
from bot.trade_manager import place_trade
from infrastructure.log_wrapper import LogWrapper
from models.trade_settings import TradeSettings
from api.oanda_api import OandaApi
import constants.defs as defs
from dateutil import parser
import pandas as pd
import os


class IntradayBot:
    """
    Enhanced intraday trading bot with:
    - Faster response times (M1/M5 timeframes)
    - Session-aware trading
    - Intraday pattern recognition
    - Dynamic position sizing
    - Real-time risk management
    """
    
    ERROR_LOG = "intraday_error"
    MAIN_LOG = "intraday_main"
    GRANULARITY = "M1"  # Faster timeframe for intraday
    SLEEP = 15  # Faster updates
    
    def __init__(self):
        self.load_settings()
        self.setup_logs()
        
        self.api = OandaApi()
        self.strategy = IntradayStrategy()
        self.candle_manager = CandleManager(
            self.api, 
            self.trade_settings, 
            self.log_message, 
            IntradayBot.GRANULARITY
        )
        
        self.last_logged_positions = {}
        self.active_trades = {}
        self.daily_stats = {
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'pnl': 0.0
        }
        
        self.log_to_main("Intraday Bot started")
        self.log_to_error("Intraday Bot started")
        
    def load_settings(self):
        """Load intraday-specific settings"""
        with open("./bot/intraday_settings.json", "r") as f:
            data = json.loads(f.read())
            self.trade_settings = {k: TradeSettings(v, k) for k, v in data['pairs'].items()}
            self.trade_risk = data['trade_risk']
            self.intraday_config = data.get('intraday_config', {})
    
    def setup_logs(self):
        """Setup logging for intraday bot"""
        self.logs = {}
        for k in self.trade_settings.keys():
            self.logs[k] = LogWrapper(f"intraday_{k}")
            self.log_message(f"{self.trade_settings[k]}", k)
        self.logs[IntradayBot.ERROR_LOG] = LogWrapper(IntradayBot.ERROR_LOG)
        self.logs[IntradayBot.MAIN_LOG] = LogWrapper(IntradayBot.MAIN_LOG)
        self.log_to_main(f"Intraday Bot started with {TradeSettings.settings_to_str(self.trade_settings)}")
    
    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)
    
    def log_to_main(self, msg):
        self.log_message(msg, IntradayBot.MAIN_LOG)
    
    def log_to_error(self, msg):
        self.log_message(msg, IntradayBot.ERROR_LOG)
    
    def is_trading_hours(self):
        """Check if we're in active trading hours"""
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check if we're in active hours (London-NY overlap)
        hour = now.hour
        return 8 <= hour <= 16
    
    def should_close_positions(self):
        """Check if we should close positions (end of day)"""
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        
        # Close positions 30 minutes before market close
        hour = now.hour
        minute = now.minute
        return hour == 15 and minute >= 30
    
    def get_dynamic_position_size(self, pair, signal_strength):
        """Calculate dynamic position size based on signal strength and volatility"""
        base_risk = self.trade_risk
        
        # Adjust based on signal strength (0-1)
        adjusted_risk = base_risk * signal_strength
        
        # Adjust based on current volatility
        current_atr = self.get_current_atr(pair)
        avg_atr = self.get_average_atr(pair)
        
        if current_atr > avg_atr * 1.5:
            adjusted_risk *= 0.7  # Reduce size in high volatility
        elif current_atr < avg_atr * 0.7:
            adjusted_risk *= 1.2  # Increase size in low volatility
        
        return max(0.1, min(adjusted_risk, 2.0))  # Clamp between 0.1 and 2.0
    
    def get_current_atr(self, pair):
        """Get current ATR for position sizing"""
        try:
            candles = self.api.get_candles(pair, count=20, granularity=IntradayBot.GRANULARITY)
            if candles and len(candles) > 0:
                df = pd.DataFrame(candles)
                atr_period = self.trade_settings[pair].atr_period
                return self.calculate_atr(df, atr_period)
        except Exception as e:
            self.log_to_error(f"Error getting ATR for {pair}: {e}")
        return 0.001
    
    def get_average_atr(self, pair):
        """Get average ATR for comparison"""
        try:
            candles = self.api.get_candles(pair, count=100, granularity=IntradayBot.GRANULARITY)
            if candles and len(candles) > 0:
                df = pd.DataFrame(candles)
                atr_period = self.trade_settings[pair].atr_period
                atr_values = []
                for i in range(atr_period, len(df)):
                    atr_values.append(self.calculate_atr(df.iloc[:i+1], atr_period))
                return sum(atr_values) / len(atr_values) if atr_values else 0.001
        except Exception as e:
            self.log_to_error(f"Error getting average ATR for {pair}: {e}")
        return 0.001
    
    def calculate_atr(self, df, period):
        """Calculate ATR for a given period"""
        if len(df) < period:
            return 0.001
        
        high_low = df['mid_h'] - df['mid_l']
        high_close = abs(df['mid_h'] - df['mid_c'].shift())
        low_close = abs(df['mid_l'] - df['mid_c'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(period).mean().iloc[-1]
    
    def process_intraday_signals(self, triggered):
        """Process intraday trading signals"""
        if len(triggered) > 0:
            self.log_message(f"Processing intraday signals for: {triggered}", IntradayBot.MAIN_LOG)
            
            for pair in triggered:
                try:
                    # Check if we should be trading
                    if not self.is_trading_hours():
                        self.log_message(f"Outside trading hours for {pair}", pair)
                        continue
                    
                    # Get latest candles
                    last_time = self.candle_manager.timings[pair].last_time
                    candles = self.api.get_candles(pair, count=100, granularity=IntradayBot.GRANULARITY)
                    
                    if not candles or len(candles) < 50:
                        continue
                    
                    # Convert to DataFrame and add technical indicators
                    df = pd.DataFrame(candles)
                    df = self.add_technical_indicators(df, pair)
                    
                    # Get intraday signal
                    signal = self.strategy.get_intraday_signal(df, self.trade_settings[pair], last_time)
                    
                    if signal != defs.NONE:
                        # Calculate signal strength
                        signal_strength = self.calculate_signal_strength(df, signal)
                        
                        # Get dynamic position size
                        position_size = self.get_dynamic_position_size(pair, signal_strength)
                        
                        # Calculate stop loss and take profit
                        stop_loss = self.strategy.calculate_intraday_stop_loss(df, signal, self.trade_settings[pair])
                        take_profit = self.strategy.calculate_intraday_take_profit(
                            df, signal, stop_loss, self.trade_settings[pair]
                        )
                        
                        # Create trade decision
                        trade_decision = self.create_trade_decision(
                            pair, signal, stop_loss, take_profit, position_size, last_time
                        )
                        
                        if trade_decision:
                            self.log_message(f"Intraday Signal: {trade_decision}", pair)
                            self.log_to_main(f"Intraday Signal: {trade_decision}")
                            
                            # Place the trade
                            place_trade(trade_decision, self.api, self.log_message, self.log_to_error, position_size)
                            
                            # Track the trade
                            self.active_trades[trade_decision.id] = {
                                'pair': pair,
                                'signal': signal,
                                'entry_time': last_time,
                                'stop_loss': stop_loss,
                                'take_profit': take_profit
                            }
                
                except Exception as e:
                    self.log_to_error(f"Error processing {pair}: {e}")
    
    def add_technical_indicators(self, df, pair):
        """Add technical indicators to DataFrame"""
        try:
            # Basic indicators
            df['EMA_10'] = EMA(df['mid_c'], 10)
            df['EMA_30'] = EMA(df['mid_c'], 30)
            df['EMA_100'] = EMA(df['mid_c'], 100)
            
            # RSI
            df['RSI_14'] = RSI(df['mid_c'], 14)
            
            # MACD
            macd_data = MACD(df['mid_c'])
            df['MACD'] = macd_data['MACD']
            df['MACD_SIGNAL'] = macd_data['SIGNAL']
            df['MACD_HIST'] = macd_data['HIST']
            
            # ADX
            df['ADX_14'] = ADX(df, 14)
            df['ADX_14_SMOOTH'] = df['ADX_14'].rolling(3).mean()
            
            # ATR
            atr_period = self.trade_settings[pair].atr_period
            df[f'ATR_{atr_period}'] = ATR(df, atr_period)
            
            # Heikin Ashi
            ha_data = heikin_ashi(df)
            df['HA_Open'] = ha_data['HA_Open']
            df['HA_High'] = ha_data['HA_High']
            df['HA_Low'] = ha_data['HA_Low']
            df['HA_Close'] = ha_data['HA_Close']
            
            # Heikin Ashi averages
            df['HA_Open_3MEAN'] = df['HA_Open'].rolling(3).mean()
            df['HA_Open_3MAX'] = df['HA_Open'].rolling(3).max()
            df['HA_Open_3MIN'] = df['HA_Open'].rolling(3).min()
            
            # Patterns
            df = apply_patterns(df)
            
            # Spread
            df['SPREAD'] = df['ask_c'] - df['bid_c']
            
            # Gain calculation
            df['GAIN'] = abs(df['mid_c'] - df['mid_c'].shift(1))
            
            # Session filter
            df['session_ny_london'] = True  # Simplified for now
            
        except Exception as e:
            self.log_to_error(f"Error adding indicators for {pair}: {e}")
        
        return df
    
    def calculate_signal_strength(self, df, signal):
        """Calculate signal strength (0-1) based on multiple factors"""
        if len(df) < 20:
            return 0.5
        
        current_row = df.iloc[-1]
        
        # Base strength
        strength = 0.5
        
        # Trend alignment
        if signal == defs.BUY:
            if current_row['EMA_10'] > current_row['EMA_30'] > current_row['EMA_100']:
                strength += 0.2
        else:  # SELL
            if current_row['EMA_10'] < current_row['EMA_30'] < current_row['EMA_100']:
                strength += 0.2
        
        # RSI confirmation
        if signal == defs.BUY and 30 < current_row['RSI_14'] < 60:
            strength += 0.1
        elif signal == defs.SELL and 40 < current_row['RSI_14'] < 70:
            strength += 0.1
        
        # MACD confirmation
        if signal == defs.BUY and current_row['MACD_HIST'] > 0:
            strength += 0.1
        elif signal == defs.SELL and current_row['MACD_HIST'] < 0:
            strength += 0.1
        
        # ADX strength
        if current_row['ADX_14'] > 25:
            strength += 0.1
        
        return min(1.0, strength)
    
    def create_trade_decision(self, pair, signal, stop_loss, take_profit, position_size, timestamp):
        """Create a trade decision object"""
        try:
            from models.trade_decision import TradeDecision
            
            return TradeDecision(
                pair=pair,
                signal=signal,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timestamp=timestamp,
                units=position_size * 10000  # Convert to units
            )
        except Exception as e:
            self.log_to_error(f"Error creating trade decision: {e}")
            return None
    
    def run(self):
        """Main bot loop"""
        self.log_to_main("Starting intraday bot loop")
        
        while True:
            try:
                # Check if we should be trading
                if not self.is_trading_hours():
                    time.sleep(60)  # Sleep longer outside trading hours
                    continue
                
                # Check if we should close positions
                if self.should_close_positions():
                    self.log_to_main("Closing positions for end of day")
                    self.close_all_positions()
                
                # Process signals
                triggered = self.candle_manager.update_timings()
                self.process_intraday_signals(triggered)
                
                # Update active trades
                self.update_active_trades()
                
                # Log daily stats
                self.log_daily_stats()
                
                time.sleep(IntradayBot.SLEEP)
                
            except Exception as error:
                self.log_to_error(f"CRASH: {error}")
                time.sleep(60)  # Wait before retrying
    
    def close_all_positions(self):
        """Close all open positions"""
        try:
            positions = self.api.get_positions()
            for position in positions:
                if position['long']['units'] != '0' or position['short']['units'] != '0':
                    self.api.close_position(position['instrument'])
                    self.log_to_main(f"Closed position for {position['instrument']}")
        except Exception as e:
            self.log_to_error(f"Error closing positions: {e}")
    
    def update_active_trades(self):
        """Update status of active trades"""
        # This would typically check trade status and update tracking
        pass
    
    def log_daily_stats(self):
        """Log daily trading statistics"""
        # This would log daily performance metrics
        pass