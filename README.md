# full_forex_box

Full-stack forex trading platform with OANDA streaming, OpenAI analysis, economic calendars, automated bots, and unified web dashboards.

---

## Features

- **Flask REST API** — headlines, account data, economic calendars, pair data
- **Stream bot** — real-time OANDA price streaming and candle workers
- **Trading bot** — automated trade management
- **OpenAI analysis** — AI-powered market reports and strategy suggestions
- **Unified dashboard** — glassmorphism Flask UI on port 5001
- **React dashboard** — charts, calendars, and technicals (`forex-dash/`)
- **Web scraping** — Bloomberg, ForexFactory, TradingEconomics, Investing.com
- **Jupyter exploration** — strategy backtests and research notebooks

---

## Tech stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python 3.9+, Flask, Flask-CORS |
| AI | OpenAI API |
| Trading | OANDA API, custom stream workers |
| Frontend | React (CRA), Chart.js, HTML/CSS dashboards |
| Data | MongoDB (optional), JSON, Jupyter |

---

## Quick start

### 1. Install

```bash
git clone https://github.com/Kaireega/full_forex_box.git
cd full_forex_box
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys
```

### 2. Run components

| Component | Command | URL |
|-----------|---------|-----|
| Full system | `./start.sh all` | — |
| Flask API | `python server.py` | http://localhost:5000 |
| Unified dashboard | `python start_unified_dashboard.py` | http://localhost:5001 |
| Trading bot | `python run_bot.py` | — |
| React dashboard | `cd forex-dash && npm install && npm start` | http://localhost:3000 |

### 3. Automated setup

```bash
chmod +x start.sh
./start.sh setup    # Install dependencies
./start.sh all      # Start all services
```

See [`SETUP_README.md`](SETUP_README.md) for detailed setup instructions and [`UNIFIED_DASHBOARD_README.md`](UNIFIED_DASHBOARD_README.md) for dashboard documentation.

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OANDA_API_KEY` | Yes | OANDA API bearer token |
| `OANDA_ACCOUNT_ID` | Yes | OANDA account ID |
| `OANDA_URL` | No | Default: practice API |
| `OPENAI_API_KEY` | For AI features | OpenAI API key |
| `MONGODB_URI` | Optional | MongoDB connection string |

---

## Project structure

```
full_forex_box/
├── server.py                 # Flask REST API (port 5000)
├── run_bot.py                # Trading bot launcher
├── setup.py, start.sh        # Automated setup scripts
├── unified_dashboard/        # Unified Flask dashboard (port 5001)
├── forex-dash/               # React CRA frontend
├── bot/, stream_bot/         # Trading and streaming bots
├── analysis/                 # OpenAI market analysis
├── scraping/                 # Economic calendar scrapers
├── simulation/, exploration/ # Backtests and notebooks
└── constants/defs.py         # API configuration (uses env vars)
```

---

## Related projects

- [Automated_trading_bot](https://github.com/Kaireega/Automated_trading_bot) — multi-strategy trading bot
- [swing-trader](https://github.com/Kaireega/swing-trader) — Bollinger Band streaming bot
- [notificactionn-bot](https://github.com/Kaireega/notificactionn-bot) — AI-assisted trading with notifications

---

## Disclaimer

Forex trading carries significant financial risk. Use OANDA's practice account for development and testing.

---

## Author

**Kai'ree Gay** — [GitHub](https://github.com/Kaireega)
