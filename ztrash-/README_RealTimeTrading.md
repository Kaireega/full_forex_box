# Real-Time Forex Trading Analyzer with OpenAI

This module provides minute-by-minute OpenAI-powered analysis for forex trading decisions, focusing on precise entry and exit point predictions.

## 🎯 Features

### 🤖 AI-Powered Analysis
- **Minute-level predictions** using OpenAI GPT-4
- **Entry/Exit point recommendations** with specific price levels
- **Confidence scoring** for each trading signal
- **Risk assessment** for every trade recommendation
- **Market sentiment analysis** in real-time

### 📊 Technical Integration
- **Real-time OANDA data** with 1-minute candles
- **Technical indicators**: RSI, MACD, Moving Averages, Bollinger Bands
- **Support/Resistance levels** calculation
- **Price action analysis** with recent market movements
- **Volatility assessment** for position sizing

### 🎮 Multiple Interfaces
- **Console Mode**: Real-time terminal output
- **Web Dashboard**: Beautiful browser interface
- **Background Mode**: Silent operation with file logging
- **API Endpoints**: For custom integrations

## 🚀 Quick Start

### Set Your OpenAI API Key
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Start Trading Analyzer

#### Option 1: Console Mode (Real-time terminal output)
```bash
# Using quick-start script
python start_trading_analyzer.py --mode console

# Using main start script
./start.sh trading-analyzer

# With custom parameters
python start_trading_analyzer.py --mode console --pairs EUR_USD GBP_USD --interval 30 --duration 60
```

#### Option 2: Web Dashboard (Beautiful browser interface)
```bash
# Start web dashboard
python start_trading_analyzer.py --mode web

# Or using start script
./start.sh trading-web

# Access at: http://localhost:5001
```

#### Option 3: Background Mode (Silent logging)
```bash
python start_trading_analyzer.py --mode background --pairs EUR_USD USD_JPY
```

#### Option 4: Quick Test (2-minute test run)
```bash
python start_trading_analyzer.py --mode test

# Or using start script
./start.sh trading-test
```

## 📊 Web Dashboard Features

### Real-Time Interface
- **Live status indicators** with animated updates
- **Auto-refresh** every 5 seconds
- **Signal visualization** with color-coded recommendations
- **Session statistics** and performance metrics
- **Mobile-responsive** design

### Dashboard Sections
1. **Status Bar**: Analyzer status, current time, last update
2. **Controls**: Start/stop analyzer, manual refresh
3. **Summary Panel**: Total signals, confidence averages, active pairs
4. **Recent Signals**: Latest trading recommendations
5. **High Confidence Signals**: Filtered high-quality signals

### Access Points
- **Main Dashboard**: http://localhost:5001
- **API Status**: http://localhost:5001/api/status
- **Live Signals**: http://localhost:5001/api/signals
- **Summary Data**: http://localhost:5001/api/summary

## 🎛️ Configuration Options

### Command Line Parameters

```bash
python start_trading_analyzer.py [OPTIONS]

Options:
  --mode {console,web,background,test}  Analysis mode (default: console)
  --pairs PAIR1 PAIR2 ...               Currency pairs (default: EUR_USD GBP_USD USD_JPY)
  --interval SECONDS                    Update interval (default: 60)
  --duration MINUTES                    Duration in minutes (default: 0=unlimited)
  --log-file FILE                       Log file for background mode
```

### Currency Pairs
- **Major Pairs**: EUR_USD, GBP_USD, USD_JPY, USD_CHF
- **Cross Pairs**: EUR_GBP, GBP_JPY, AUD_USD, NZD_USD
- **Custom Selection**: Any OANDA-supported pair

### Update Intervals
- **1 minute (60s)**: Standard real-time analysis
- **30 seconds**: High-frequency testing
- **2+ minutes**: Conservative analysis for longer-term signals

## 📈 Trading Signal Format

### Signal Structure
```python
{
    "timestamp": "2025-01-22T10:30:00",
    "currency_pair": "EUR_USD",
    "signal_type": "BUY",           # BUY, SELL, HOLD, EXIT
    "confidence": 0.85,             # 0.0 to 1.0
    "entry_price": 1.04567,         # Specific entry level
    "stop_loss": 1.04367,           # Risk management level
    "take_profit": 1.04867,         # Profit target
    "reasoning": "Strong bullish momentum with RSI oversold bounce...",
    "market_conditions": "Trending market with high volatility",
    "risk_level": "MEDIUM"          # LOW, MEDIUM, HIGH
}
```

### Signal Types
- **🟢 BUY**: Long position recommendation
- **🔴 SELL**: Short position recommendation  
- **🟡 HOLD**: Wait for better opportunity
- **🚪 EXIT**: Close existing positions

### Confidence Levels
- **80-100%**: High confidence (recommended for trading)
- **70-79%**: Medium confidence (consider with other factors)
- **50-69%**: Low confidence (monitor only)
- **<50%**: Very low confidence (avoid)

## 🎯 Signal Analysis Process

### 1. Data Collection (Every Minute)
```python
# Minute-level OANDA data
- 1-minute candles (last 60 minutes)
- Current bid/ask prices
- Volume information
- Market volatility metrics
```

### 2. Technical Analysis
```python
# Calculated indicators
- Moving Averages: 5, 10, 20 periods
- RSI: 14-period Relative Strength Index
- MACD: 12/26 exponential moving average convergence divergence
- Bollinger Bands: 20-period with 2 standard deviations
- Support/Resistance: Dynamic levels from recent price action
```

### 3. OpenAI Analysis Prompt
```text
FOREX TRADING ANALYSIS REQUEST

Currency Pair: EUR_USD
Current Time: 2025-01-22 10:30:15
Current Price: 1.04567

TECHNICAL INDICATORS:
- Moving Averages: MA5=1.04523, MA10=1.04501, MA20=1.04445
- RSI: 68.45
- MACD: 0.00023
- Bollinger Bands: Upper=1.04789, Middle=1.04567, Lower=1.04345
- Support Level: 1.04234
- Resistance Level: 1.04789

MARKET CONTEXT:
- 20-minute price change: 0.00134
- Volatility: 0.00756

RECENT PRICE ACTION:
10min ago: 🟢 O:1.04534 H:1.04578 L:1.04521 C:1.04567
9min ago: 🔴 O:1.04567 H:1.04578 L:1.04534 C:1.04545
...

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
```

### 4. AI Response Processing
```json
{
    "signal": "BUY",
    "confidence": 0.82,
    "entry_price": 1.04570,
    "stop_loss": 1.04470,
    "take_profit": 1.04720,
    "reasoning": "Strong bullish momentum confirmed by price breaking above 20-period MA with RSI showing upward momentum but not overbought. MACD positive crossover indicates trend continuation. Entry at current resistance turned support.",
    "market_conditions": "Trending bullish market with moderate volatility",
    "risk_level": "MEDIUM"
}
```

## 💾 Data Storage

### Signal Logging
All signals are automatically saved to JSON files:
```
logs/trading_signals_YYYYMMDD.json
```

### File Format
```json
[
    {
        "timestamp": "2025-01-22T10:30:00",
        "currency_pair": "EUR_USD",
        "signal_type": "BUY",
        "confidence": 0.82,
        "entry_price": 1.04570,
        "stop_loss": 1.04470,
        "take_profit": 1.04720,
        "reasoning": "Strong bullish momentum...",
        "market_conditions": "Trending bullish market",
        "risk_level": "MEDIUM"
    }
]
```

### Log File Management
- **Daily files**: New file created each day
- **Automatic cleanup**: Old files can be archived
- **JSON format**: Easy to parse and analyze
- **External access**: Monitor signals from other applications

## 🔌 API Integration

### Web API Endpoints

#### Get Analyzer Status
```bash
GET http://localhost:5001/api/status
```
Response:
```json
{
    "running": true,
    "timestamp": "2025-01-22T10:30:00"
}
```

#### Start Analyzer
```bash
POST http://localhost:5001/api/start
```
Response:
```json
{
    "success": true,
    "message": "Analyzer started successfully"
}
```

#### Stop Analyzer
```bash
POST http://localhost:5001/api/stop
```

#### Get Current Signals
```bash
GET http://localhost:5001/api/signals
```
Response:
```json
{
    "signals": [
        {
            "timestamp": "2025-01-22T10:30:00",
            "currency_pair": "EUR_USD",
            "signal_type": "BUY",
            "confidence": 0.82,
            "entry_price": 1.04570,
            "stop_loss": 1.04470,
            "take_profit": 1.04720,
            "reasoning": "Strong bullish momentum...",
            "market_conditions": "Trending bullish market",
            "risk_level": "MEDIUM"
        }
    ]
}
```

#### Get Session Summary
```bash
GET http://localhost:5001/api/summary
```
Response:
```json
{
    "total_signals": 15,
    "signal_types": {"BUY": 6, "SELL": 4, "HOLD": 5},
    "average_confidence": 0.756,
    "high_confidence_signals": 8,
    "currency_pairs": {"EUR_USD": 8, "GBP_USD": 4, "USD_JPY": 3}
}
```

## 🛠️ Advanced Usage

### Custom Integration
```python
from analysis.realtime_trading_analyzer import RealtimeTradingAnalyzer

# Initialize with custom settings
analyzer = RealtimeTradingAnalyzer(
    update_interval=30,  # 30-second updates
)

# Start analysis for specific pairs
pairs = ['EUR_USD', 'GBP_USD']
analyzer.start_realtime_analysis(pairs)

# Get signals programmatically
signals = analyzer.get_current_signals()
for signal in signals:
    if signal.confidence > 0.8 and signal.signal_type in ['BUY', 'SELL']:
        print(f"High confidence {signal.signal_type} signal for {signal.currency_pair}")
        print(f"Entry: {signal.entry_price}, Target: {signal.take_profit}")

# Stop when done
analyzer.stop_realtime_analysis()
```

### Risk Management Integration
```python
# Example: Position sizing based on signal confidence and risk level
def calculate_position_size(signal, account_balance, risk_per_trade=0.02):
    # Adjust position size based on confidence and risk level
    confidence_multiplier = signal.confidence
    
    risk_multiplier = {
        'LOW': 0.5,
        'MEDIUM': 1.0,
        'HIGH': 1.5
    }.get(signal.risk_level, 1.0)
    
    # Calculate stop loss distance
    stop_distance = abs(signal.entry_price - signal.stop_loss)
    
    # Position size calculation
    risk_amount = account_balance * risk_per_trade * confidence_multiplier * risk_multiplier
    position_size = risk_amount / stop_distance
    
    return position_size
```

### Alert System Integration
```python
def check_for_alerts():
    signals = analyzer.get_current_signals()
    
    for signal in signals[-5:]:  # Check last 5 signals
        if (signal.confidence >= 0.85 and 
            signal.signal_type in ['BUY', 'SELL'] and
            signal.risk_level != 'HIGH'):
            
            # Send alert (email, SMS, webhook, etc.)
            send_trading_alert(signal)
```

## 📱 Monitoring and Alerts

### Real-Time Monitoring
- **Console output**: Live signal updates in terminal
- **Web dashboard**: Visual interface with auto-refresh
- **Log files**: Persistent storage for analysis
- **API endpoints**: Integration with external systems

### Performance Metrics
- **Signal frequency**: Signals per hour/day
- **Confidence distribution**: Quality of predictions
- **Currency pair activity**: Most active markets
- **Success tracking**: When integrated with execution

### Custom Alerts
Set up custom alerts based on:
- **High confidence signals** (>80%)
- **Specific currency pairs**
- **Signal types** (BUY/SELL only)
- **Risk levels** (exclude HIGH risk)
- **Market conditions** (trending vs ranging)

## 🚨 Important Disclaimers

### Risk Warning
- **AI predictions are not guarantees** of future market movements
- **Always conduct your own analysis** before making trading decisions
- **Use proper risk management** with every trade
- **Start with small position sizes** when testing signals
- **Monitor performance** and adjust strategy accordingly

### Technical Limitations
- **Market volatility** can affect signal quality
- **News events** may not be immediately reflected
- **API rate limits** may occasionally delay updates
- **Internet connectivity** required for real-time data
- **OpenAI API costs** apply for each analysis request

### Best Practices
- **Combine with other analysis** methods
- **Use demo accounts** for initial testing
- **Monitor signal performance** over time
- **Adjust parameters** based on market conditions
- **Maintain trading discipline** regardless of AI recommendations

## 🔧 Troubleshooting

### Common Issues

#### "OpenAI API key not found"
```bash
export OPENAI_API_KEY="your-api-key-here"
# Verify with: echo $OPENAI_API_KEY
```

#### "OANDA API connection failed"
- Check internet connection
- Verify OANDA credentials in `constants/defs.py`
- Ensure OANDA account is active

#### "No signals generated"
- Check OpenAI API key and billing
- Verify currency pairs are valid
- Check for error messages in console

#### "Web dashboard not loading"
```bash
# Check if port 5001 is available
lsof -i :5001

# Try different port
python web_trading_dashboard.py  # Edit port in file
```

### Performance Optimization
- **Reduce update frequency** for lower API costs
- **Filter currency pairs** to focus on most liquid markets
- **Adjust confidence thresholds** to reduce noise
- **Use background mode** for resource efficiency

### Debug Mode
```bash
# Run with debug output
python start_trading_analyzer.py --mode console --interval 30 --duration 5

# Check log files
tail -f logs/trading_signals_*.json

# Monitor API usage
grep "tokens_used" logs/trading_signals_*.json
```

This comprehensive real-time trading analyzer gives you minute-by-minute OpenAI-powered insights for forex trading decisions. Use it responsibly and always combine AI predictions with your own market analysis and risk management strategies!