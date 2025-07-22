# Forex Trading System Setup Guide

This guide will help you set up and start all components of the forex trading system, including the new OpenAI analysis features.

## 🚀 Quick Start

### For Linux/macOS Users:
```bash
# Make setup script executable (first time only)
chmod +x start.sh

# Full system setup and start all services
./start.sh setup

# Or for quick setup without demos
./start.sh quick-setup

# Start all services
./start.sh all
```

### For Windows Users:
```cmd
# Full system setup and start all services
start.bat setup

# Or for quick setup without demos
start.bat quick-setup

# Start all services
start.bat all
```

### Using Python Setup Script Directly:
```bash
# Full automated setup
python setup.py --all

# Quick setup (no demos or data collection)
python setup.py --quick

# Individual components
python setup.py --install-deps
python setup.py --check-config
python setup.py --init-db
python setup.py --start-server
python setup.py --openai-demo
```

## 📋 Prerequisites

### Required Software:
- **Python 3.7+** (recommended: Python 3.9+)
- **pip** (Python package manager)
- **Git** (for version control)

### Required API Keys:
- **OANDA API** credentials (for forex data)
- **OpenAI API Key** (for AI analysis features)

### Optional:
- **Jupyter Notebook** (for analysis notebooks)
- **Node.js** (for additional web features)

## 🔧 Setup Methods

### Method 1: Automated Setup (Recommended)

#### Linux/macOS:
```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd forex-trading-system

# Run full automated setup
./start.sh setup
```

#### Windows:
```cmd
# Clone the repository (if not already done)
git clone <repository-url>
cd forex-trading-system

# Run full automated setup
start.bat setup
```

This will:
- ✅ Check system requirements
- ✅ Install Python dependencies
- ✅ Initialize database
- ✅ Set up instrument collection
- ✅ Test API connections
- ✅ Start all services
- ✅ Run OpenAI demo (if API key is set)

### Method 2: Manual Step-by-Step Setup

#### Step 1: Install Dependencies
```bash
# Linux/macOS
./start.sh install

# Windows
start.bat install

# Or directly with pip
pip install -r requirements.txt
```

#### Step 2: Set Environment Variables
```bash
# Linux/macOS
export OPENAI_API_KEY="your-openai-api-key-here"

# Windows
set OPENAI_API_KEY=your-openai-api-key-here
```

#### Step 3: Configure OANDA API
Edit `constants/defs.py` with your OANDA credentials:
```python
OANDA_URL = "https://api-fxpractice.oanda.com/v3"  # or live URL
ACCOUNT_ID = "your-account-id"
SECURE_HEADER = {
    "Authorization": "Bearer your-access-token"
}
```

#### Step 4: Initialize Database
```bash
python setup.py --init-db
```

#### Step 5: Test Configuration
```bash
# Linux/macOS
./start.sh check

# Windows
start.bat check
```

### Method 3: Development Setup

For development and testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run tests
python test_openai_analysis.py

# Start individual components for development
python server.py          # Web server
python run_bot.py         # Trading bot
python main.py            # Main analysis system
```

## 🎮 System Control Commands

### Quick Start Scripts

#### Linux/macOS (`./start.sh`):
```bash
./start.sh setup         # Full system setup
./start.sh quick-setup   # Quick setup (no demos)
./start.sh all           # Start all services
./start.sh server        # Start web server only
./start.sh bot           # Start trading bot only
./start.sh stream        # Start data streaming only
./start.sh openai-demo   # Run OpenAI analysis demo
./start.sh test          # Run test suite
./start.sh check         # Check system status
./start.sh stop          # Stop all services
./start.sh logs          # Show recent logs
./start.sh help          # Show help
```

#### Windows (`start.bat`):
```cmd
start.bat setup         # Full system setup
start.bat quick-setup   # Quick setup (no demos)
start.bat all           # Start all services
start.bat server        # Start web server only
start.bat bot           # Start trading bot only
start.bat stream        # Start data streaming only
start.bat openai-demo   # Run OpenAI analysis demo
start.bat test          # Run test suite
start.bat check         # Check system status
start.bat stop          # Stop all services
start.bat logs          # Show recent logs
start.bat help          # Show help
```

### Python Setup Script (`python setup.py`):
```bash
python setup.py --all              # Complete setup and start
python setup.py --quick            # Quick setup without demos
python setup.py --install-deps     # Install dependencies only
python setup.py --check-config     # Check configuration
python setup.py --init-db          # Initialize database
python setup.py --start-server     # Start web server
python setup.py --start-bot        # Start trading bot
python setup.py --start-stream     # Start data streaming
python setup.py --openai-demo      # Run OpenAI demo
python setup.py --collect-data     # Start data collection
```

## 🌐 Access Points

After setup, you can access:

- **Web Interface**: http://localhost:5000
- **Jupyter Notebooks**: `jupyter notebook analysis/`
- **Logs**: `logs/setup_YYYYMMDD_HHMMSS.log`
- **OpenAI Demo**: `python test_openai_analysis.py`

## 🔍 System Status

### Check if Everything is Running:
```bash
# Linux/macOS
./start.sh check

# Windows
start.bat check

# Direct Python
python setup.py --check-config
```

### View Logs:
```bash
# Show recent setup logs
./start.sh logs        # Linux/macOS
start.bat logs         # Windows

# Monitor live logs
tail -f logs/setup_*.log  # Linux/macOS
```

### Stop All Services:
```bash
./start.sh stop        # Linux/macOS
start.bat stop         # Windows

# Or manually
pkill -f "server.py"    # Linux/macOS
pkill -f "run_bot.py"   # Linux/macOS
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required for OpenAI features
export OPENAI_API_KEY="sk-your-openai-api-key"

# Optional: Custom configuration
export OANDA_ENVIRONMENT="practice"  # or "live"
export LOG_LEVEL="INFO"
export DATABASE_URL="mongodb://localhost:27017"
```

### Configuration Files

#### `constants/defs.py` - OANDA API Configuration
```python
OANDA_URL = "https://api-fxpractice.oanda.com/v3"
ACCOUNT_ID = "your-account-id"
SECURE_HEADER = {
    "Authorization": "Bearer your-access-token"
}
```

#### `requirements.txt` - Python Dependencies
Automatically maintained. Key packages:
- `openai>=1.58.1` - OpenAI API client
- `pandas` - Data manipulation
- `requests` - HTTP client
- `flask` - Web framework

## 🧪 Testing

### Run All Tests:
```bash
# Using start scripts
./start.sh test         # Linux/macOS
start.bat test          # Windows

# Direct execution
python test_openai_analysis.py
python api_tests.py
python scraping_tests.py
```

### Test Individual Components:

#### OpenAI Analysis:
```bash
python test_openai_analysis.py
```

#### Basic System Test:
```python
# Test imports
python -c "
from api.openai_api import OpenAIAnalyzer
from analysis.openai_analysis import ForexOpenAIAnalysis
print('✅ All imports successful')
"
```

## 🚨 Troubleshooting

### Common Issues:

#### 1. "OPENAI_API_KEY not found"
```bash
# Set the environment variable
export OPENAI_API_KEY="your-api-key-here"  # Linux/macOS
set OPENAI_API_KEY=your-api-key-here       # Windows
```

#### 2. "OANDA API connection failed"
- Check your credentials in `constants/defs.py`
- Verify your OANDA account is active
- Check if you're using practice vs live API endpoints

#### 3. "Port 5000 already in use"
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9  # Linux/macOS
netstat -ano | findstr :5000   # Windows (then use taskkill)

# Or use a different port
python server.py --port 8000
```

#### 4. "Dependencies installation failed"
```bash
# Update pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Use conda if pip fails
conda install --file requirements.txt
```

#### 5. "Database connection failed"
- Check if MongoDB is running (if using MongoDB)
- Verify database configuration
- Check file permissions for SQLite databases

### Getting Help:

#### View Detailed Logs:
```bash
# Find latest log file
ls -la logs/

# View specific log
cat logs/setup_YYYYMMDD_HHMMSS.log

# Monitor in real-time
tail -f logs/setup_*.log
```

#### Check System Status:
```bash
./start.sh check    # Complete system status
python setup.py --check-config  # Configuration check only
```

#### Debug Mode:
```bash
# Run with debug output
python setup.py --all --debug

# Run individual components in foreground
python server.py     # Web server
python run_bot.py    # Trading bot
```

## 📚 Next Steps

After successful setup:

1. **Explore the Web Interface**: Visit http://localhost:5000
2. **Try OpenAI Analysis**: Run `./start.sh openai-demo`
3. **Open Jupyter Notebooks**: `jupyter notebook analysis/`
4. **Configure Trading Parameters**: Edit trading bot settings
5. **Set up Alerts**: Configure email/SMS notifications
6. **Monitor Performance**: Check logs and metrics

## 🔄 Daily Operations

### Starting the System:
```bash
# Quick daily startup
./start.sh all       # Linux/macOS
start.bat all        # Windows
```

### Stopping the System:
```bash
# Clean shutdown
./start.sh stop      # Linux/macOS
start.bat stop       # Windows
```

### Health Checks:
```bash
# Morning health check
./start.sh check     # Linux/macOS
start.bat check      # Windows
```

### Backup and Maintenance:
```bash
# Backup configuration and logs
tar -czf backup_$(date +%Y%m%d).tar.gz constants/ logs/ *.py

# Update dependencies
pip install -r requirements.txt --upgrade

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete
```

## 🎯 Performance Tips

### Optimize for Production:
1. **Use environment variables** for sensitive data
2. **Set up log rotation** to manage disk space
3. **Monitor resource usage** (CPU, memory, network)
4. **Use caching** for frequently accessed data
5. **Set up monitoring alerts** for system health

### Scale for High Volume:
1. **Use multiple worker processes** for web server
2. **Implement database connection pooling**
3. **Set up load balancing** for multiple instances
4. **Use Redis** for caching and session management
5. **Optimize database queries** and indexing

This completes your comprehensive setup guide! The system is now ready for forex trading analysis with full OpenAI integration.