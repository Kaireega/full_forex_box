# Intraday Trading Bot System

## Overview

This enhanced intraday trading system is specifically designed for fast-paced, short-term trading with focus on intraday patterns, session awareness, and dynamic risk management. The system operates on M1 timeframes for maximum responsiveness and includes sophisticated pattern recognition for breakouts, reversals, and momentum shifts.

## Key Features

### 🚀 **Fast Response Times**
- **M1 timeframe** for maximum responsiveness
- **15-second update intervals** for real-time signal processing
- **Session-aware trading** to focus on high-liquidity periods

### 📊 **Advanced Pattern Recognition**
- **Breakout patterns**: Range, channel, triangle, flag/pennant breakouts
- **Reversal patterns**: Double top/bottom, head & shoulders, V-reversals, pin bars
- **Momentum patterns**: RSI/MACD divergence, momentum exhaustion
- **Support/Resistance levels**: Dynamic calculation of key levels

### 🎯 **Intraday-Specific Features**
- **Session filtering**: London-NY overlap focus (8 AM - 4 PM ET)
- **Dynamic position sizing**: Based on signal strength and volatility
- **Tighter risk management**: Intraday-specific stop losses and take profits
- **Auto position closure**: End-of-day position management

### 📈 **Enhanced Risk Management**
- **Volatility-based position sizing**: Adjusts based on current ATR
- **Signal strength weighting**: Stronger signals get larger positions
- **Daily loss limits**: Maximum 2% daily loss per pair
- **Concurrent trade limits**: Maximum 3 simultaneous trades

## System Architecture

```
intraday_trading_system/
├── bot/
│   ├── intraday_strategy.py      # Core intraday strategy logic
│   ├── intraday_bot.py          # Main intraday bot implementation
│   └── intraday_settings.json   # Intraday-specific configuration
├── technicals/
│   └── intraday_patterns.py     # Advanced pattern recognition
├── run_intraday_bot.py          # Bot runner with safety checks
└── INTRADAY_TRADING_README.md   # This documentation
```

## Installation & Setup

### 1. Prerequisites
```bash
# Ensure you have the base trading system installed
pip install -r requirements.txt

# Additional dependencies for intraday trading
pip install numpy pandas pytz python-dateutil
```

### 2. Configuration
1. **API Setup**: Ensure your OANDA API credentials are configured
2. **Settings**: Review and adjust `bot/intraday_settings.json`
3. **Risk Management**: Set appropriate risk levels for your account

### 3. Configuration Options

#### Trading Pairs
The system is configured for major forex pairs:
- **EUR_USD**: Most liquid, tight spreads
- **GBP_USD**: Good volatility, clear patterns
- **USD_JPY**: Yen pairs, different characteristics
- **USD_CHF**: Safe haven currency
- **AUD_USD**: Commodity currency

#### Risk Settings
```json
{
    "trade_risk": 0.5,           // Base risk per trade (0.5%)
    "max_daily_trades": 10,      // Maximum trades per day
    "max_concurrent_trades": 3,  // Maximum simultaneous trades
    "min_signal_strength": 0.6,  // Minimum signal strength to trade
    "auto_close_end_of_day": true // Auto-close positions at end of day
}
```

## Usage

### Starting the Intraday Bot

```bash
# Run the intraday bot
python run_intraday_bot.py
```

### Monitoring

The bot provides comprehensive logging:
- **Main log**: `logs/intraday_main.log`
- **Error log**: `logs/intraday_error.log`
- **Pair-specific logs**: `logs/intraday_{PAIR}.log`

### Key Log Messages

```
✅ Active trading hours detected
📊 Processing intraday signals for: ['EUR_USD', 'GBP_USD']
🎯 Intraday Signal: BUY EUR_USD @ 1.0850 | SL: 1.0830 | TP: 1.0890
💰 Position size: 0.75% (signal strength: 0.85)
```

## Strategy Details

### Signal Generation Process

1. **Session Filter**: Only trade during London-NY overlap (8 AM - 4 PM ET)
2. **Volatility Filter**: Check if current ATR is within acceptable range
3. **Pattern Detection**: Identify breakouts, reversals, and momentum patterns
4. **Technical Confirmation**: Verify with RSI, MACD, ADX, and Heikin Ashi
5. **Signal Strength**: Calculate overall signal strength (0-1)
6. **Position Sizing**: Adjust position size based on signal strength and volatility

### Pattern Recognition

#### Breakout Patterns
- **Range Breakout**: Price breaks above/below horizontal range
- **Channel Breakout**: Price breaks out of trend channel
- **Triangle Breakout**: Price breaks from converging lines
- **Flag/Pennant**: Strong move followed by consolidation breakout

#### Reversal Patterns
- **Double Top/Bottom**: Two peaks/troughs at similar levels
- **Head & Shoulders**: Three-peak reversal pattern
- **V-Reversal**: Sharp directional change
- **Pin Bar**: Single candle reversal with long wick

#### Momentum Patterns
- **RSI Divergence**: Price and RSI moving in opposite directions
- **MACD Divergence**: Price and MACD histogram divergence
- **Momentum Exhaustion**: Overbought/oversold conditions

### Risk Management

#### Position Sizing
```python
# Dynamic position sizing formula
position_size = base_risk * signal_strength * volatility_factor

# Volatility adjustment
if current_atr > avg_atr * 1.5:
    volatility_factor = 0.7  # Reduce size in high volatility
elif current_atr < avg_atr * 0.7:
    volatility_factor = 1.2  # Increase size in low volatility
```

#### Stop Loss Calculation
```python
# Intraday-specific stop loss
if signal == BUY:
    stop_loss = current_price - (atr * 1.2)
    # Don't go below recent low
    stop_loss = max(stop_loss, recent_low - (atr * 0.5))
```

#### Take Profit Calculation
```python
# Risk-reward based take profit
risk = entry_price - stop_loss
take_profit = entry_price + (risk * risk_reward_ratio)
```

## Performance Monitoring

### Key Metrics to Track

1. **Win Rate**: Target > 55%
2. **Risk-Reward Ratio**: Target > 2:1
3. **Average Trade Duration**: Typically 15-60 minutes
4. **Daily P&L**: Monitor for consistency
5. **Maximum Drawdown**: Keep under 5%

### Performance Logging

The system automatically logs:
- Trade entries and exits
- Signal strength and pattern types
- Position sizes and risk levels
- Daily statistics and P&L

## Safety Features

### 1. **Session Awareness**
- Only trades during active hours
- Automatically closes positions before market close
- Weekend protection

### 2. **Risk Limits**
- Maximum daily loss per pair: 2%
- Maximum concurrent trades: 3
- Maximum daily trades: 10
- Minimum signal strength: 0.6

### 3. **Error Handling**
- Graceful shutdown on errors
- Position cleanup on exit
- Comprehensive error logging

### 4. **Market Conditions**
- Spread filtering
- Volatility filtering
- Liquidity checks

## Customization

### Adding New Patterns

To add custom patterns, extend the `IntradayPatterns` class:

```python
def detect_custom_pattern(self, df: pd.DataFrame) -> Dict:
    """Detect your custom pattern"""
    # Your pattern logic here
    return {
        'detected': True,
        'direction': 1,  # 1 for bullish, -1 for bearish
        'strength': 0.8  # 0-1 strength
    }
```

### Modifying Risk Parameters

Edit `bot/intraday_settings.json`:

```json
{
    "trade_risk": 0.3,           // Reduce risk
    "min_signal_strength": 0.7,  // Require stronger signals
    "max_daily_trades": 5        // Fewer trades per day
}
```

### Adding New Pairs

Add new pairs to the settings:

```json
{
    "USD_CAD": {
        "n_ma": 5,
        "n_std": 1.4,
        "maxspread": 0.00025,
        "mingain": 0.00045,
        "riskreward": 2.0,
        "atr_period": 5,
        "rsi_period": 9
    }
}
```

## Troubleshooting

### Common Issues

1. **No signals generated**
   - Check if within trading hours
   - Verify signal strength threshold
   - Check volatility conditions

2. **High number of false signals**
   - Increase `min_signal_strength`
   - Adjust pattern thresholds
   - Review technical indicator settings

3. **Positions not closing**
   - Check API connectivity
   - Verify position management logic
   - Review error logs

### Debug Mode

Enable debug logging by modifying the log level in the bot:

```python
# In intraday_bot.py
self.logs[key].logger.setLevel(logging.DEBUG)
```

## Best Practices

### 1. **Start Small**
- Begin with small position sizes
- Test with paper trading first
- Gradually increase risk as you gain confidence

### 2. **Monitor Performance**
- Track daily P&L
- Monitor win rate and risk-reward
- Review pattern effectiveness

### 3. **Risk Management**
- Never risk more than 2% per trade
- Use proper position sizing
- Set realistic profit targets

### 4. **Market Conditions**
- Avoid trading during major news events
- Be aware of market holidays
- Monitor for unusual volatility

## Support

For issues or questions:
1. Check the error logs first
2. Review the configuration settings
3. Test with paper trading
4. Monitor system performance

## Disclaimer

This trading system is for educational purposes. Past performance does not guarantee future results. Always:
- Test thoroughly before live trading
- Use proper risk management
- Never risk more than you can afford to lose
- Consider consulting with a financial advisor

---

**Happy Trading! 🚀📈**