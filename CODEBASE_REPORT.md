# Comprehensive Forex Trading System Codebase Report

## System Overview

This is a sophisticated forex trading system that combines real-time data streaming, technical analysis, AI-powered insights, and automated trading capabilities. The system is designed for intraday trading with multiple analysis modes and risk management features.

## Architecture Overview

The system follows a modular architecture with the following main components:

1. **API Layer** - External data sources (OANDA, OpenAI)
2. **Data Collection** - Historical and real-time data gathering
3. **Analysis Engine** - Technical, fundamental, and AI analysis
4. **Trading Engine** - Signal generation and trade execution
5. **Dashboard** - Web-based monitoring and control interface
6. **Database** - MongoDB for data persistence
7. **Streaming** - Real-time price data processing

---

## 1. API LAYER

### 1.1 OANDA API (`api/oanda_api.py`)

**Purpose**: Interface with OANDA forex trading platform for market data and trade execution.

#### Key Functions:

**`__init__()`**
- **Input**: None
- **Output**: Initialized OANDA API client with session headers
- **Function**: Sets up HTTP session with OANDA authentication

**`make_request(url, verb='get', code=200, params=None, data=None, headers=None)`**
- **Input**: URL endpoint, HTTP method, expected status code, parameters, data payload
- **Output**: Tuple (success_boolean, response_data)
- **Function**: Generic HTTP request handler for OANDA API calls

**`get_account_summary()`**
- **Input**: None
- **Output**: Account information dictionary
- **Function**: Retrieves current account balance, margin, and trading status

**`get_account_instruments()`**
- **Input**: None
- **Output**: List of available trading instruments
- **Function**: Gets all available currency pairs and their specifications

**`fetch_candles(pair_name, count=10, granularity="H1", price="MBA", date_f=None, date_t=None)`**
- **Input**: Currency pair, candle count, timeframe, price type, date range
- **Output**: List of candle data or None
- **Function**: Retrieves historical price data in OHLCV format

**`get_candles_df(pair_name, **kwargs)`**
- **Input**: Currency pair, keyword arguments for fetch_candles
- **Output**: Pandas DataFrame with OHLCV data
- **Function**: Converts raw candle data to pandas DataFrame format

**`place_trade(pair_name, units, direction, stop_loss=None, take_profit=None)`**
- **Input**: Currency pair, position size, direction (BUY/SELL), stop loss, take profit
- **Output**: Trade ID if successful, None if failed
- **Function**: Executes market orders with optional risk management

**`close_trade(trade_id)`**
- **Input**: Trade ID
- **Output**: Boolean success status
- **Function**: Closes an open trade position

**`get_open_trade(trade_id)`**
- **Input**: Trade ID
- **Output**: OpenTrade object or None
- **Function**: Retrieves details of an open trade

### 1.2 OpenAI API (`api/openai_api.py`)

**Purpose**: AI-powered market analysis using OpenAI's GPT models.

#### Key Functions:

**`__init__(api_key=None)`**
- **Input**: OpenAI API key (optional, can use environment variable)
- **Output**: Initialized OpenAI client
- **Function**: Sets up OpenAI client for API calls

**`analyze_forex_data(data, analysis_type="general")`**
- **Input**: Pandas DataFrame with forex data, analysis type
- **Output**: Dictionary with analysis results
- **Function**: Performs AI analysis on forex data with different analysis types

**`analyze_news_sentiment(news_data)`**
- **Input**: List of news events with titles and descriptions
- **Output**: Sentiment analysis results dictionary
- **Function**: Analyzes economic news sentiment and market impact

**`comprehensive_market_report(currency_pairs, include_news=True, analysis_types=['general', 'technical'])`**
- **Input**: List of currency pairs, news flag, analysis types
- **Output**: Comprehensive market report dictionary
- **Function**: Generates multi-pair market analysis with news integration

---

## 2. DATA COLLECTION LAYER

### 2.1 Data Collection (`infrastructure/collect_data.py`)

**Purpose**: Historical data collection and storage for analysis.

#### Key Functions:

**`save_file(final_df, file_prefix, granularity, pair)`**
- **Input**: DataFrame, file prefix, timeframe, currency pair
- **Output**: None (saves to pickle file)
- **Function**: Saves processed data to disk with deduplication and sorting

**`fetch_candles(pair, granularity, date_f, date_t, api)`**
- **Input**: Currency pair, timeframe, start date, end date, API client
- **Output**: DataFrame with candle data or None
- **Function**: Fetches candles with retry logic (3 attempts)

**`collect_data(pair, granularity, date_f, date_t, file_prefix, api)`**
- **Input**: Currency pair, timeframe, date range, file prefix, API client
- **Output**: None (saves data to files)
- **Function**: Collects historical data in chunks to avoid API limits

**`run_collection(ic, api)`**
- **Input**: Instrument collection, API client
- **Output**: None
- **Function**: Main data collection orchestrator for all currency pairs and timeframes

### 2.2 Instrument Collection (`infrastructure/instrument_collection.py`)

**Purpose**: Manages available trading instruments and their specifications.

#### Key Functions:

**`LoadInstruments(data_path)`**
- **Input**: Path to data directory
- **Output**: None
- **Function**: Loads instrument specifications from saved files

**`CreateDB(instruments)`**
- **Input**: List of instruments from API
- **Output**: None
- **Function**: Creates database entries for instruments

---

## 3. ANALYSIS ENGINE

### 3.1 Comprehensive Trading Strategy (`analysis/comprehensive_trading_strategy.py`)

**Purpose**: Unified trading strategy combining all analysis types.

#### Key Classes:

**`StrategyMode` (Enum)**
- Values: CONSERVATIVE, MODERATE, AGGRESSIVE, ADAPTIVE
- **Function**: Defines risk tolerance levels

**`TimeFrame` (Enum)**
- Values: M1, M5, M15, M30, H1, H4, D1
- **Function**: Defines available trading timeframes

**`MarketCondition` (dataclass)**
- **Fields**: trend, volatility, momentum, strength, support_levels, resistance_levels, key_levels
- **Function**: Encapsulates market state analysis

**`SignalStrength` (dataclass)**
- **Fields**: technical_score, fundamental_score, ai_score, pattern_score, overall_score, confidence, risk_level
- **Function**: Quantifies signal quality across multiple dimensions

**`ComprehensiveSignal` (dataclass)**
- **Fields**: timestamp, pair, signal_type, entry_price, stop_loss, take_profit, position_size, signal_strength, market_condition
- **Function**: Complete trading signal with all analysis components

#### Key Functions:

**`analyze_market_condition(data, timeframe)`**
- **Input**: Price data DataFrame, timeframe
- **Output**: MarketCondition object
- **Function**: Analyzes current market conditions and key levels

**`calculate_signal_strength(technical_analysis, fundamental_analysis, ai_analysis, pattern_analysis)`**
- **Input**: Analysis results from different sources
- **Output**: SignalStrength object
- **Function**: Combines multiple analysis scores into overall signal strength

**`generate_trading_signal(pair, data, settings, mode)`**
- **Input**: Currency pair, price data, trade settings, strategy mode
- **Output**: ComprehensiveSignal object or None
- **Function**: Generates complete trading signals with risk management

### 3.2 Technical Indicators (`technicals/indicators.py`)

**Purpose**: Technical analysis indicators for price data.

#### Key Functions:

**`BollingerBands(df, n=20, s=2)`**
- **Input**: DataFrame, period, standard deviation multiplier
- **Output**: DataFrame with BB_MA, BB_UP, BB_LW, BB_Signal columns
- **Function**: Calculates Bollinger Bands with buy/sell signals

**`ATR(df, n=14)`**
- **Input**: DataFrame, period
- **Output**: DataFrame with ATR column
- **Function**: Calculates Average True Range for volatility measurement

**`RSI(df, n=14)`**
- **Input**: DataFrame, period
- **Output**: DataFrame with RSI column
- **Function**: Calculates Relative Strength Index

**`MACD(df, n_slow=26, n_fast=12, n_signal=9)`**
- **Input**: DataFrame, slow period, fast period, signal period
- **Output**: DataFrame with MACD, SIGNAL_MD, HIST columns
- **Function**: Calculates MACD indicator with signal line and histogram

**`moving_average_crossover(df, short_window=20, long_window=60)`**
- **Input**: DataFrame, short MA period, long MA period
- **Output**: DataFrame with Short_MA, Long_MA, MA_Signal columns
- **Function**: Generates MA crossover signals

**`heikin_ashi(df)`**
- **Input**: DataFrame
- **Output**: DataFrame with Heikin-Ashi candle data
- **Function**: Converts regular candles to Heikin-Ashi format

**`momentum_reversal(df)`**
- **Input**: DataFrame
- **Output**: DataFrame with Stochastic and Momentum_Signal columns
- **Function**: Identifies momentum reversal patterns

**`candlestick_patterns(df)`**
- **Input**: DataFrame
- **Output**: DataFrame with pattern detection columns
- **Function**: Identifies bullish/bearish engulfing patterns

**`role_reversal(df)`**
- **Input**: DataFrame
- **Output**: DataFrame with support/resistance and reversal signals
- **Function**: Identifies support/resistance breakouts

### 3.3 Pattern Recognition (`technicals/patterns.py`)

**Purpose**: Advanced pattern recognition for chart analysis.

#### Key Functions:

**`detect_candlestick_patterns(df)`**
- **Input**: DataFrame with OHLC data
- **Output**: DataFrame with pattern columns
- **Function**: Detects various candlestick patterns

**`detect_chart_patterns(df)`**
- **Input**: DataFrame with price data
- **Output**: DataFrame with pattern columns
- **Function**: Detects chart patterns like triangles, flags, etc.

---

## 4. TRADING ENGINE

### 4.1 Stream Bot (`stream_bot/stream_bot.py`)

**Purpose**: Real-time price streaming and processing.

#### Key Functions:

**`run_bot()`**
- **Input**: None
- **Output**: None (runs indefinitely)
- **Function**: Main orchestrator for streaming bot components

**Data Flow**:
1. Loads trade settings
2. Initializes shared price dictionaries
3. Starts price streamer thread
4. Starts price processor threads for each pair
5. Starts candle worker threads (commented out)
6. Runs main loop until interrupted

### 4.2 Price Processor (`stream_bot/price_processor.py`)

**Purpose**: Processes real-time price data into candles.

#### Key Functions:

**`process_price_update(price_data)`**
- **Input**: Raw price data from stream
- **Output**: Processed candle data
- **Function**: Converts tick data to OHLC candles

### 4.3 Candle Worker (`stream_bot/candle_worker.py`)

**Purpose**: Analyzes completed candles for trading signals.

#### Key Functions:

**`analyze_candle(candle_data, settings)`**
- **Input**: Candle data, trade settings
- **Output**: Trade decision or None
- **Function**: Applies technical analysis to generate signals

### 4.4 Trade Worker (`stream_bot/trade_worker.py`)

**Purpose**: Executes trading decisions.

#### Key Functions:

**`execute_trade(decision)`**
- **Input**: Trade decision object
- **Output**: Trade execution result
- **Function**: Places trades via OANDA API

---

## 5. DASHBOARD LAYER

### 5.1 Unified Dashboard (`unified_dashboard/app.py`)

**Purpose**: Web-based dashboard for system monitoring and control.

#### Key Endpoints:

**`/` (dashboard)**
- **Input**: None
- **Output**: HTML dashboard page
- **Function**: Serves main dashboard interface

**`/api/status`**
- **Input**: None
- **Output**: JSON system status
- **Function**: Returns trading system status

**`/api/start`**
- **Input**: JSON with trading mode and settings
- **Output**: JSON response
- **Function**: Starts trading system

**`/api/stop`**
- **Input**: None
- **Output**: JSON response
- **Function**: Stops trading system

**`/api/candles/<pair>/<granularity>`**
- **Input**: Currency pair, timeframe
- **Output**: JSON candle data
- **Function**: Returns historical price data

**`/api/analysis/<pair>/<granularity>`**
- **Input**: Currency pair, timeframe
- **Output**: JSON analysis results
- **Function**: Returns technical analysis

**`/api/calendar/tradingeconomics`**
- **Input**: Date range parameters
- **Output**: JSON economic calendar data
- **Function**: Returns economic events

**`/api/calendar/forexfactory`**
- **Input**: Date range parameters
- **Output**: JSON news calendar data
- **Function**: Returns forex factory news

**`/api/signals`**
- **Input**: None
- **Output**: JSON trading signals
- **Function**: Returns recent trading signals

**`/api/performance`**
- **Input**: None
- **Output**: JSON performance metrics
- **Function**: Returns trading performance statistics

---

## 6. DATABASE LAYER

### 6.1 Data Database (`db/db.py`)

**Purpose**: MongoDB interface for data persistence.

#### Collections:
- `forex_sample`: Sample data collection
- `forex_calendar`: Economic calendar data
- `forex_instruments`: Trading instruments data

#### Key Functions:

**`__init__()`**
- **Input**: None
- **Output**: Initialized MongoDB client
- **Function**: Connects to MongoDB database

**`test_connection()`**
- **Input**: None
- **Output**: List of collection names
- **Function**: Tests database connectivity

**`add_one(collection, ob)`**
- **Input**: Collection name, document object
- **Output**: None
- **Function**: Inserts single document

**`add_many(collection, list_ob)`**
- **Input**: Collection name, list of documents
- **Output**: None
- **Function**: Inserts multiple documents

**`query_single(collection, **kwargs)`**
- **Input**: Collection name, query parameters
- **Output**: Single document or None
- **Function**: Finds single document matching criteria

**`query_all(collection, **kwargs)`**
- **Input**: Collection name, query parameters
- **Output**: List of documents
- **Function**: Finds all documents matching criteria

**`query_distinct(collection, key)`**
- **Input**: Collection name, field name
- **Output**: List of distinct values
- **Function**: Returns unique values for specified field

**`delete_many(collection, **kwargs)`**
- **Input**: Collection name, query parameters
- **Output**: None
- **Function**: Deletes documents matching criteria

---

## 7. DATA MODELS

### 7.1 Trade Decision (`models/trade_decision.py`)

**Purpose**: Encapsulates trading decision data.

#### Fields:
- `gain`: Expected profit
- `loss`: Expected loss
- `signal`: BUY/SELL signal
- `sl`: Stop loss price
- `tp`: Take profit price
- `pair`: Currency pair

### 7.2 Trade Settings (`models/trade_settings.py`)

**Purpose**: Configurable trading parameters.

#### Fields:
- `n_ma`: Moving average period
- `n_std`: Standard deviation multiplier
- `maxspread`: Maximum allowed spread
- `mingain`: Minimum profit target
- `riskreward`: Risk-reward ratio
- `atr_multiplier`: ATR multiplier for stop loss
- `atr_period`: ATR calculation period
- `rsi_period`: RSI calculation period
- `rsi_overbought`: RSI overbought threshold
- `rsi_oversold`: RSI oversold threshold

### 7.3 Instrument (`models/instrument.py`)

**Purpose**: Trading instrument specifications.

#### Fields:
- `name`: Instrument name
- `type`: Instrument type
- `displayName`: Display name
- `pipLocation`: Pip location
- `tradeUnitsPrecision`: Trade units precision
- `displayPrecision`: Display precision

### 7.4 Open Trade (`models/open_trade.py`)

**Purpose**: Open trade position data.

#### Fields:
- `id`: Trade ID
- `instrument`: Currency pair
- `price`: Entry price
- `currentUnits`: Current position size
- `unrealizedPL`: Unrealized profit/loss
- `marginUsed`: Margin used

---

## 8. SCRAPING LAYER

### 8.1 Economic Calendars

**Purpose**: Scrapes economic data from various sources.

#### TradingEconomics (`scraping/tradingeconomics_calendar.py`)
- **Function**: Scrapes economic calendar from TradingEconomics
- **Output**: Economic events with impact levels

#### ForexFactory (`scraping/forexfactory_calendar.py`)
- **Function**: Scrapes news calendar from ForexFactory
- **Output**: Market-moving news events

#### Bloomberg (`scraping/bloomberg_com.py`)
- **Function**: Scrapes financial news from Bloomberg
- **Output**: Financial news articles

#### Investing.com (`scraping/investing_com.py`)
- **Function**: Scrapes market data from Investing.com
- **Output**: Market analysis and data

---

## 9. DATA FLOW SUMMARY

### 9.1 Real-time Trading Flow

1. **Price Streaming**: OANDA API → Price Streamer → Price Processor
2. **Candle Formation**: Price Processor → Candle Worker
3. **Signal Generation**: Candle Worker → Technical Analysis → Trade Decision
4. **Trade Execution**: Trade Decision → Trade Worker → OANDA API
5. **Database Storage**: All components → MongoDB

### 9.2 Analysis Flow

1. **Data Collection**: OANDA API → Data Collection → Pickle Files
2. **Technical Analysis**: Price Data → Technical Indicators → Signal Generation
3. **AI Analysis**: Price Data + News → OpenAI API → Market Insights
4. **Fundamental Analysis**: Economic Calendars → News Analysis → Market Impact
5. **Unified Analysis**: All Analysis Types → Comprehensive Strategy → Trading Signals

### 9.3 Dashboard Flow

1. **Data Requests**: Frontend → Flask API → Backend Components
2. **Real-time Updates**: WebSocket/SSE → Frontend Updates
3. **System Control**: Frontend → API Endpoints → Trading System
4. **Performance Tracking**: Trading System → Database → Dashboard Display

---

## 10. CONFIGURATION

### 10.1 Constants (`constants/defs.py`)

**API Configuration**:
- `API_KEY`: OANDA API key
- `ACCOUNT_ID`: OANDA account ID
- `OANDA_URL`: OANDA API base URL

**Database Configuration**:
- `MONGO_CONN_STR`: MongoDB connection string

**Trading Constants**:
- `SELL = -1`: Sell direction constant
- `BUY = 1`: Buy direction constant
- `NONE = 0`: No position constant

**Currency Pairs**:
- Comprehensive list of supported forex pairs with Investing.com IDs

---

## 11. STARTUP SCRIPTS

### 11.1 Main Entry Point (`main.py`)

**Purpose**: System initialization and orchestration.

#### Functions:

**`db_tests()`**
- **Input**: None
- **Output**: None
- **Function**: Tests database functionality

**`openai_analysis_demo()`**
- **Input**: None
- **Output**: None (prints results)
- **Function**: Demonstrates OpenAI analysis capabilities

**`__main__`**:
- **Input**: None
- **Output**: None
- **Function**: Main system startup sequence

### 11.2 Setup Scripts

**`start.sh`** (Linux/macOS):
- **Function**: Automated setup and startup script
- **Features**: Dependency installation, configuration, service startup

**`start.bat`** (Windows):
- **Function**: Windows equivalent of start.sh
- **Features**: Same functionality as shell script

**`setup.py`**:
- **Function**: Python-based setup utility
- **Features**: Cross-platform setup automation

---

## 12. SYSTEM INTEGRATION

### 12.1 Component Dependencies

```
Main Entry Point (main.py)
├── API Layer (OANDA, OpenAI)
├── Data Collection (Historical Data)
├── Stream Bot (Real-time Processing)
├── Analysis Engine (Technical, AI, Fundamental)
├── Trading Engine (Signal Generation, Execution)
├── Dashboard (Web Interface)
└── Database (MongoDB)
```

### 12.2 Data Flow Architecture

```
External APIs (OANDA, OpenAI, Economic Data)
    ↓
Data Collection & Processing
    ↓
Analysis Engine (Technical + AI + Fundamental)
    ↓
Signal Generation & Risk Management
    ↓
Trade Execution (OANDA API)
    ↓
Performance Tracking & Database Storage
    ↓
Dashboard Display & Control
```

### 12.3 Threading Model

- **Price Streamer**: Single thread for all pairs
- **Price Processors**: One thread per currency pair
- **Candle Workers**: One thread per pair (optional)
- **Trade Worker**: Single thread for trade execution
- **Dashboard**: Flask web server thread
- **Analysis**: Background threads for AI analysis

---

## 13. RISK MANAGEMENT

### 13.1 Position Sizing
- ATR-based stop loss calculation
- Risk-reward ratio enforcement
- Maximum position size limits
- Account balance percentage limits

### 13.2 Stop Loss & Take Profit
- Dynamic stop loss based on volatility
- Take profit targets based on risk-reward
- Trailing stop loss capabilities
- Break-even adjustments

### 13.3 Risk Controls
- Maximum spread limits
- Minimum profit targets
- Maximum drawdown limits
- Correlation-based position limits

---

## 14. PERFORMANCE MONITORING

### 14.1 Metrics Tracked
- Win rate percentage
- Profit factor
- Maximum drawdown
- Sharpe ratio
- Total return
- Number of trades
- Average trade duration

### 14.2 Logging
- Trade execution logs
- Error logs
- Performance logs
- System status logs

---

This comprehensive forex trading system provides a complete solution for automated trading with multiple analysis types, real-time processing, risk management, and web-based monitoring. The modular architecture allows for easy extension and customization of individual components while maintaining system integrity.