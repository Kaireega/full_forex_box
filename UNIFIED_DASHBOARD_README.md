# 🚀 Unified Forex Trading Dashboard

A comprehensive real-time forex trading system that combines all analysis logic into one unified strategy for intraday trading patterns. This dashboard merges the functionality of both `web_dashboard` and `forex-dash` components while maintaining all their features and applying the beautiful styling of the web dashboard.

## ✨ Features

### 🤖 Trading System Control
- **Real-time Trading System**: Start/stop the unified trading system
- **Multiple Trading Modes**: Stream Bot Only, AI Analysis Only, Hybrid, AI Enhanced
- **Analysis Modes**: Basic, Adaptive, Comprehensive
- **Live Signal Generation**: Real-time trading signals with confidence scores
- **Performance Tracking**: Win rate, profit factor, drawdown analysis

### 📈 Price Charts & Technical Analysis
- **Interactive Charts**: Real-time price charts with Chart.js
- **Multiple Timeframes**: M1, M5, M15, M30, H1, H4, D1
- **Technical Indicators**: RSI, MACD, EMA, Bollinger Bands, Stochastic, ATR
- **Account Summary**: Real-time account balance and P&L

### 📊 Comprehensive Analysis
- **Multi-timeframe Analysis**: Analyze trends across different timeframes
- **Pattern Recognition**: Candlestick patterns, chart patterns, support/resistance
- **Risk Analysis**: Position sizing, risk management, stop-loss calculation
- **AI Integration**: OpenAI analysis for enhanced decision making

### 📅 Economic Calendars
- **TradingEconomics Calendar**: Economic events with impact levels
- **ForexFactory Calendar**: Market-moving news and events
- **Date Range Selection**: Customizable date ranges for calendar data

### 🎨 Beautiful UI
- **Modern Design**: Glassmorphism design with gradient backgrounds
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live data updates without page refresh
- **Tab Navigation**: Organized sections for different functionalities

## 🏗️ Architecture

The unified dashboard consists of several key components:

### Backend (Flask)
- **`unified_dashboard/app.py`**: Main Flask application with all API endpoints
- **`analysis/comprehensive_trading_strategy.py`**: Unified trading strategy
- **API Integration**: OANDA API, OpenAI API, economic data sources

### Frontend (HTML/CSS/JavaScript)
- **`unified_dashboard/templates/dashboard.html`**: Main dashboard interface
- **`unified_dashboard/static/css/dashboard.css`**: Styling with glassmorphism design
- **`unified_dashboard/static/js/dashboard.js`**: Interactive functionality

### Trading Strategy
- **Technical Analysis**: Multiple indicators and pattern recognition
- **Fundamental Analysis**: Economic calendar integration
- **AI Analysis**: OpenAI-powered market analysis
- **Risk Management**: Position sizing and stop-loss calculation

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# Ensure you have API credentials configured
# - OANDA API key (required)
# - OpenAI API key (optional, for AI analysis)
```

### 2. Start the Dashboard
```bash
# Run the startup script
python start_unified_dashboard.py
```

### 3. Access the Dashboard
Open your browser and navigate to: `http://localhost:5001`

## 📋 Dashboard Sections

### 🤖 Trading System Tab
- **System Controls**: Start/stop the trading system
- **Trading Summary**: Real-time statistics and metrics
- **Recent Signals**: Latest trading signals with details
- **High Confidence Signals**: Filtered high-confidence signals
- **Performance Metrics**: Win rate, profit factor, drawdown

### 📈 Price Charts Tab
- **Chart Controls**: Select currency pair, timeframe, candle count
- **Interactive Chart**: Real-time price chart with technical indicators
- **Account Summary**: Account balance, P&L, open trades

### 📊 Technical Analysis Tab
- **Technical Controls**: Select pair and timeframe
- **Indicator Display**: RSI, MACD, EMA, Bollinger Bands, etc.
- **Pattern Recognition**: Detected chart patterns

### 📅 Economic Calendars Tab
- **TradingEconomics**: Economic events with impact levels
- **ForexFactory**: Market news and events
- **Date Selection**: Customizable date ranges

### 🔍 Comprehensive Analysis Tab
- **Analysis Controls**: Select currency pair for detailed analysis
- **Comprehensive Analysis**: Multi-factor market analysis
- **Pattern Analysis**: Technical pattern recognition
- **Risk Analysis**: Risk assessment and management

## ⚙️ Configuration

### Trading Modes
- **Hybrid**: Combines Stream Bot with AI Analysis (recommended)
- **Stream Bot Only**: Uses only the stream bot for signals
- **AI Analysis Only**: Uses only AI analysis for signals
- **AI Enhanced**: AI-enhanced stream bot signals

### Analysis Modes
- **Adaptive**: Automatically adjusts analysis based on market conditions
- **Basic**: Basic technical analysis only
- **Comprehensive**: Full analysis including AI and fundamental factors

### Strategy Modes
- **Conservative**: Lower risk, higher signal strength requirements
- **Moderate**: Balanced risk and reward (default)
- **Aggressive**: Higher risk, more frequent signals
- **Adaptive**: Automatically adjusts based on performance

## 🔧 API Endpoints

### Trading System
- `GET /api/status` - Get system status
- `POST /api/start` - Start trading system
- `POST /api/stop` - Stop trading system
- `GET /api/signals` - Get recent signals
- `GET /api/summary` - Get trading summary
- `GET /api/performance` - Get performance metrics

### Charts & Technicals
- `GET /api/options` - Get available pairs and timeframes
- `GET /api/prices/{pair}/{granularity}/{count}` - Get price data
- `GET /api/technicals/{pair}/{tf}` - Get technical indicators
- `GET /api/account` - Get account summary

### Economic Calendars
- `GET /api/te/calendar/{start}/{end}` - TradingEconomics calendar
- `GET /api/ff/calendar/{start}` - ForexFactory calendar

### Analysis
- `GET /api/analysis/comprehensive/{pair}` - Comprehensive analysis
- `GET /api/analysis/patterns/{pair}` - Pattern analysis
- `GET /api/analysis/risk/{pair}` - Risk analysis

## 🎯 Trading Strategy

The comprehensive trading strategy combines multiple analysis methods:

### Technical Analysis
- **Multi-timeframe Analysis**: Analyzes trends across M15, H1, H4
- **Indicator Confluence**: RSI, MACD, EMA, Bollinger Bands, Stochastic
- **Support/Resistance**: Dynamic level identification
- **Volatility Analysis**: ATR-based volatility measurement

### Pattern Recognition
- **Candlestick Patterns**: Doji, Hammer, Shooting Star, etc.
- **Chart Patterns**: Head & Shoulders, Triangles, Flags, etc.
- **Price Action**: Breakouts, reversals, continuations

### Fundamental Analysis
- **Economic Calendar**: High-impact economic events
- **News Sentiment**: Market-moving news analysis
- **Correlation Analysis**: Currency pair correlations

### AI/ML Analysis
- **OpenAI Integration**: Market sentiment and analysis
- **Pattern Recognition**: Advanced pattern detection
- **Risk Assessment**: AI-powered risk evaluation

### Risk Management
- **Position Sizing**: Risk-based position calculation
- **Stop Loss**: ATR-based stop loss placement
- **Take Profit**: Risk-reward ratio optimization
- **Maximum Positions**: Limit concurrent positions

## 📊 Performance Tracking

The system tracks comprehensive performance metrics:

- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Total Return**: Overall portfolio return
- **Sharpe Ratio**: Risk-adjusted returns
- **Average Trade**: Average profit/loss per trade

## 🔒 Security & Risk Management

### Risk Controls
- **Maximum Daily Trades**: Limits daily trading activity
- **Position Size Limits**: Prevents over-leveraging
- **Stop Loss Protection**: Automatic stop loss placement
- **Account Protection**: Maximum loss limits

### API Security
- **Credential Management**: Secure API key storage
- **Rate Limiting**: Prevents API abuse
- **Error Handling**: Graceful error recovery

## 🛠️ Development

### Project Structure
```
unified_dashboard/
├── app.py                 # Main Flask application
├── templates/
│   └── dashboard.html     # Dashboard template
└── static/
    ├── css/
    │   └── dashboard.css  # Styling
    └── js/
        └── dashboard.js   # Frontend logic

analysis/
├── comprehensive_trading_strategy.py  # Main strategy
├── unified_trading_system.py         # Trading system
├── unified_trading_analyzer.py       # Analysis engine
└── realtime_trading_analyzer.py      # Real-time analysis

start_unified_dashboard.py            # Startup script
```

### Adding New Features
1. **Backend**: Add new endpoints in `unified_dashboard/app.py`
2. **Frontend**: Add UI components in `dashboard.html`
3. **Styling**: Add CSS in `dashboard.css`
4. **Logic**: Add JavaScript in `dashboard.js`

## 🐛 Troubleshooting

### Common Issues

**Dashboard won't start**
- Check if all dependencies are installed
- Verify API credentials are configured
- Check if port 5001 is available

**No trading signals**
- Ensure trading system is started
- Check API connectivity
- Verify market hours

**Charts not loading**
- Check OANDA API credentials
- Verify internet connection
- Check browser console for errors

**Economic calendar not working**
- Verify TradingEconomics API access
- Check date format (YYYY-MM-DD)
- Ensure proper API endpoints

### Logs
Check the console output for detailed error messages and system status.

## 📈 Performance Optimization

### System Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ recommended
- **Storage**: 1GB+ free space
- **Network**: Stable internet connection

### Optimization Tips
- Use conservative mode for lower resource usage
- Limit concurrent positions
- Adjust update intervals based on needs
- Monitor system resources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and informational purposes only. Trading forex involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results. Always conduct your own research and consider consulting with a financial advisor before making trading decisions.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Check the logs for error messages
- Ensure all dependencies are properly installed

---

**Happy Trading! 🚀📈** 