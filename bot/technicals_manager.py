import pandas as pd
import pytz
from models.trade_decision import TradeDecision
from technicals.indicators import BollingerBands, ATR, RSI, MACD, EMA, ADX, heikin_ashi, identify_pin_bar
from technicals.patterns import apply_patterns

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)
from api.oanda_api import OandaApi
from models.trade_settings import TradeSettings
import constants.defs as defs

ADDROWS = 20

def apply_signal(row, trade_settings: TradeSettings):
    # Trend Configuration
    primary_trend_up = row['EMA_10'] > row['EMA_30']
    secondary_trend_up = row['EMA_10'] > row['EMA_100']
    
    # Dynamic ADX Threshold
    adx_smooth = row['ADX_14_SMOOTH']
    trend_strength = adx_smooth > 22
    
    # Adaptive Volatility Filter
    atr_ratio = row[f"ATR_{trade_settings.atr_period}"] / row['average_atr']
    volatility_ok = 0.8 < atr_ratio < 1.5
    
    # Price Action Patterns
    bullish_pattern = row['ENGULFING'] or row['PIN_BAR_BULL'] or (row['HA_Close'] > row['HA_Open_3MAX'])
    bearish_pattern = row['ENGULFING'] or row['PIN_BAR_BEAR'] or (row['HA_Close'] < row['HA_Open_3MIN'])
    
    # Momentum Configuration
    rsi_mid = 40 if primary_trend_up else 60
    rsi_ok = (row[f"RSI_{trade_settings.rsi_period}"] < rsi_mid) if primary_trend_up else (row[f"RSI_{trade_settings.rsi_period}"] > rsi_mid)
    
    macd_hist = row['MACD_HIST']
    macd_ok = (macd_hist > 0) if primary_trend_up else (macd_hist < 0)
    
    # Session Filter
    session_ok = row['session_ny_london']
    
    # Entry Conditions
    long_conditions = all([
        row.SPREAD <= trade_settings.maxspread,
        row.GAIN >= trade_settings.mingain * 0.8,
        trend_strength,
        primary_trend_up,
        bullish_pattern,
        rsi_ok,
        macd_ok,
        session_ok,
        volatility_ok,
        row.mid_c > row['EMA_10'],
        row['HA_Close'] > row['HA_Open_3MEAN']
    ])
    
    short_conditions = all([
        row.SPREAD <= trade_settings.maxspread,
        row.GAIN >= trade_settings.mingain * 0.8,
        trend_strength,
        not primary_trend_up,
        bearish_pattern,
        rsi_ok,
        macd_ok,
        session_ok,
        volatility_ok,
        row.mid_c < row['EMA_10'],
        row['HA_Close'] < row['HA_Open_3MEAN']
    ])
    
    if long_conditions:
        return defs.BUY
    elif short_conditions:
        return defs.SELL
    
    return defs.NONE

def apply_SL(row, trade_settings: TradeSettings):
    """Adaptive trailing stop with volatility bands"""
    atr = row[f"ATR_{trade_settings.atr_period}"]
    if row.SIGNAL == defs.BUY:
        return max(
            row.mid_c - (atr * 1.5),
            row.mid_l - (atr * 0.3)
        )
    elif row.SIGNAL == defs.SELL:
        return min(
            row.mid_c + (atr * 1.5),
            row.mid_h + (atr * 0.3)
        )
    return 0.0

def process_candles(df: pd.DataFrame, pair, trade_settings: TradeSettings, log_message):
    df = df.copy().reset_index(drop=True)
    df['PAIR'] = pair
    df['SPREAD'] = df.ask_c - df.bid_c

    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], utc=True)
        eastern_tz = pytz.timezone('US/Eastern')
        df['time'] = df['time'].dt.tz_convert(eastern_tz)
        df['hour'] = df['time'].dt.hour
        df['session_ny_london'] = df['hour'].between(6, 13)  # Expanded session
        df['time'] = df['time'].dt.strftime('%I:%M %p')
        
    df = apply_patterns(df)
    
    # Calculate indicators
    df = BollingerBands(df, trade_settings.n_ma, trade_settings.n_std)
    df = ATR(df, trade_settings.atr_period)
    df = RSI(df, trade_settings.rsi_period)
    df = MACD(df).assign(MACD_HIST=lambda x: x.MACD - x.SIGNAL_MD)
    df = heikin_ashi(df)
    
    # EMAs
    df['EMA_10'] = EMA(df, 10)
    df['EMA_30'] = EMA(df, 30)
    df['EMA_100'] = EMA(df, 100)
    
    # ADX Smoothing
    df['ADX_14'] = ADX(df)
    df['ADX_14_SMOOTH'] = df['ADX_14'].rolling(5).mean()
    
    # Heikin Ashi Features
    df['HA_Open_3MAX'] = df['HA_Open'].rolling(3).max()
    df['HA_Open_3MIN'] = df['HA_Open'].rolling(3).min()
    df['HA_Open_3MEAN'] = df['HA_Open'].rolling(3).mean()
    
    df = identify_pin_bar(df)
    df['average_atr'] = df[f"ATR_{trade_settings.atr_period}"].rolling(50).mean()
    
    df['GAIN'] = abs(df.mid_c - df.BB_MA)
    df['SIGNAL'] = df.apply(apply_signal, axis=1, trade_settings=trade_settings)
    df['SL'] = df.apply(apply_SL, axis=1, trade_settings=trade_settings)
    df['LOSS'] = abs(df.mid_c - df.SL)

    log_cols = [
        'PAIR', 'time', 'mid_c', 'EMA_10', 'EMA_30', 'EMA_100', 'ADX_14_SMOOTH',
        f"RSI_{trade_settings.rsi_period}", 'MACD_HIST', 'HA_Close', 'HA_Open', 
        'session_ny_london', 'ENGULFING', 'PIN_BAR_BULL', 'PIN_BAR_BEAR', 
        'SL', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL'
    ]

    log_message(f"process_candles:\n{df[log_cols].tail()}", pair)
    return df[log_cols].iloc[-1]


def fetch_candles(pair, row_count, candle_time, granularity, api: OandaApi, log_message):
    """
    Fetches the required number of candles for the specified pair and granularity.
    """
    df = api.get_candles_df(pair, count=row_count, granularity=granularity)

    if df is None or df.shape[0] == 0:
        log_message("tech_manager fetch_candles failed to get candles", pair)
        return None
    
    if df.iloc[-1].time != candle_time:
        log_message(f"tech_manager fetch_candles {df.iloc[-1].time} not correct", pair)
        return None

    return df


def get_trade_decision(candle_time, pair, granularity, api: OandaApi, trade_settings: TradeSettings, log_message):
    """
    Determines the trade decision based on the latest market data and trade settings.
    """
    max_rows = trade_settings.n_ma + ADDROWS

    log_message(f"tech_manager: max_rows:{max_rows} candle_time:{candle_time} granularity:{granularity}", pair)

    df = fetch_candles(pair, max_rows, candle_time, granularity, api, log_message)

    if df is not None:
        last_row = process_candles(df, pair, trade_settings, log_message)
        return TradeDecision(last_row)

    return None

