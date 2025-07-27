#!/bin/bash

# Forex Trading System Quick Start Script
# This script provides quick commands to start various components of the system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN | grep -i python >/dev/null
}

# Function to display help
show_help() {
    print_header "🚀 Forex Trading System Quick Start"
    echo ""
    echo "Usage: ./start.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup         - Full system setup (equivalent to python setup.py --all)"
    echo "  quick-setup   - Quick setup without demos (python setup.py --quick)"
    echo "  server        - Start web server only"
    echo "  bot           - Start trading bot only"
    echo "  stream        - Start data streaming only"
    echo "  all           - Start all services (server, bot, streaming)"
    echo "  openai-demo   - Run OpenAI analysis demo"
    echo "  analyzer      - Start unified trading analyzer (adaptive mode - DEFAULT)"
    echo "  basic         - Start basic real-time analyzer"
    echo "  comprehensive - Start comprehensive analyzer with news sentiment"
    echo "  web           - Start unified web dashboard"
    echo "  adaptability-test - Test market condition adaptability"
    echo "  profitability-test - Test profitability across market conditions"
    echo "  unified       - Start unified trading system (stream_bot + analysis integration)"
    echo "  hybrid        - Start hybrid trading (stream_bot + AI analysis)"
    echo "  ai-enhanced   - Start AI-enhanced trading (AI-first with stream_bot backup)"
    echo "  stream-bot-only - Start stream_bot-only trading (technical analysis)"
    echo "  analysis-only - Start analysis-only trading (AI-powered only)"
    echo "  web-dashboard - Start web dashboard server"
    echo "  unified-dashboard - Start unified dashboard (recommended)"
    echo "  modern        - Start modern services (unified system + web dashboard)"
    echo "  test          - Run test suite"
    echo "  check         - Check system status"
    echo "  stop          - Stop all running services"
    echo "  logs          - Show recent logs"
    echo "  install       - Install dependencies only"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./start.sh setup         # Full system setup"
    echo "  ./start.sh unified-dashboard # Start unified dashboard (recommended)"
    echo "  ./start.sh modern        # Start modern services (unified system + web dashboard)"
    echo "  ./start.sh all           # Start all services (legacy + modern)"
    echo "  ./start.sh unified       # Start unified trading system"
    echo "  ./start.sh web-dashboard # Start web dashboard"
    echo "  ./start.sh check         # Check system status"
    echo ""
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_status "Python version: $python_version"
    
    # Check pip
    if ! command_exists pip3; then
        print_warning "pip3 not found, trying pip"
        if ! command_exists pip; then
            print_error "pip is required but not installed"
            exit 1
        fi
    fi
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_status "System requirements check passed ✅"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if command_exists pip3; then
        pip3 install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    
    print_status "Dependencies installed ✅"
}

# Function to check environment variables
check_env_vars() {
    print_status "Checking environment variables..."
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_warning "OPENAI_API_KEY not set - OpenAI features will be unavailable"
        print_warning "Set it with: export OPENAI_API_KEY='your-api-key-here'"
    else
        print_status "OPENAI_API_KEY is set ✅"
    fi
}

# Function to start web server
start_server() {
    print_status "Starting web server..."
    
    if port_in_use 5000; then
        print_warning "Port 5000 is already in use"
        return 1
    fi
    
    if [ ! -f "server.py" ]; then
        print_error "server.py not found"
        return 1
    fi
    
    print_status "Web server starting on http://localhost:5000"
    python3 server.py &
    SERVER_PID=$!
    echo $SERVER_PID > .server.pid
    
    # Wait a moment and check if server started
    sleep 2
    if kill -0 $SERVER_PID 2>/dev/null; then
        print_status "Web server started successfully (PID: $SERVER_PID) ✅"
        return 0
    else
        print_error "Failed to start web server"
        return 1
    fi
}

# Function to start trading bot
start_bot() {
    print_status "Starting trading bot..."
    
    if [ ! -f "run_bot.py" ]; then
        print_error "run_bot.py not found"
        return 1
    fi
    
    python3 run_bot.py &
    BOT_PID=$!
    echo $BOT_PID > .bot.pid
    
    # Wait a moment and check if bot started
    sleep 2
    if kill -0 $BOT_PID 2>/dev/null; then
        print_status "Trading bot started successfully (PID: $BOT_PID) ✅"
        return 0
    else
        print_error "Failed to start trading bot"
        return 1
    fi
}

# Function to start data streaming
start_streaming() {
    print_status "Starting data streaming..."
    
    python3 -c "
import sys
sys.path.append('./')
from stream_example.streamer import run_streamer
run_streamer()
" &
    STREAM_PID=$!
    echo $STREAM_PID > .stream.pid
    
    # Wait a moment and check if streaming started
    sleep 2
    if kill -0 $STREAM_PID 2>/dev/null; then
        print_status "Data streaming started successfully (PID: $STREAM_PID) ✅"
        return 0
    else
        print_error "Failed to start data streaming"
        return 1
    fi
}

# Function to start unified trading system
start_unified_trading() {
    print_status "Starting unified trading system..."
    
    if [ ! -f "analysis/unified_trading_system.py" ]; then
        print_error "analysis/unified_trading_system.py not found"
        return 1
    fi
    
    python3 analysis/unified_trading_system.py --mode hybrid &
    UNIFIED_PID=$!
    echo $UNIFIED_PID > .unified.pid
    
    # Wait a moment and check if unified system started
    sleep 2
    if kill -0 $UNIFIED_PID 2>/dev/null; then
        print_status "Unified trading system started successfully (PID: $UNIFIED_PID) ✅"
        return 0
    else
        print_error "Failed to start unified trading system"
        return 1
    fi
}

# Function to start hybrid trading
start_hybrid_trading() {
    print_status "Starting hybrid trading (bot + AI analysis)..."
    
    if [ ! -f "analysis/unified_trading_system.py" ]; then
        print_error "analysis/unified_trading_system.py not found"
        return 1
    fi
    
    python3 analysis/unified_trading_system.py --mode hybrid --analysis-mode adaptive &
    HYBRID_PID=$!
    echo $HYBRID_PID > .hybrid.pid
    
    # Wait a moment and check if hybrid system started
    sleep 2
    if kill -0 $HYBRID_PID 2>/dev/null; then
        print_status "Hybrid trading system started successfully (PID: $HYBRID_PID) ✅"
        return 0
    else
        print_error "Failed to start hybrid trading system"
        return 1
    fi
}

# Function to start AI-enhanced trading
start_ai_enhanced_trading() {
    print_status "Starting AI-enhanced trading (AI-first with bot backup)..."
    
    if [ ! -f "analysis/unified_trading_system.py" ]; then
        print_error "analysis/unified_trading_system.py not found"
        return 1
    fi
    
    python3 analysis/unified_trading_system.py --mode ai_enhanced --analysis-mode comprehensive &
    AI_ENHANCED_PID=$!
    echo $AI_ENHANCED_PID > .ai_enhanced.pid
    
    # Wait a moment and check if AI-enhanced system started
    sleep 2
    if kill -0 $AI_ENHANCED_PID 2>/dev/null; then
        print_status "AI-enhanced trading system started successfully (PID: $AI_ENHANCED_PID) ✅"
        return 0
    else
        print_error "Failed to start AI-enhanced trading system"
        return 1
    fi
}

# Function to start bot-only trading
start_bot_only_trading() {
    print_status "Starting bot-only trading (original technical analysis)..."
    
    if [ ! -f "analysis/unified_trading_system.py" ]; then
        print_error "analysis/unified_trading_system.py not found"
        return 1
    fi
    
    python3 analysis/unified_trading_system.py --mode bot_only &
    BOT_ONLY_PID=$!
    echo $BOT_ONLY_PID > .bot_only.pid
    
    # Wait a moment and check if bot-only system started
    sleep 2
    if kill -0 $BOT_ONLY_PID 2>/dev/null; then
        print_status "Bot-only trading system started successfully (PID: $BOT_ONLY_PID) ✅"
        return 0
    else
        print_error "Failed to start bot-only trading system"
        return 1
    fi
}

# Function to start stream-bot-only trading
start_stream_bot_only_trading() {
    print_status "Starting stream-bot-only trading (technical analysis)..."
    
    if [ ! -f "analysis/unified_trading_system.py" ]; then
        print_error "analysis/unified_trading_system.py not found"
        return 1
    fi
    
    python3 analysis/unified_trading_system.py --mode stream_bot_only &
    STREAM_BOT_ONLY_PID=$!
    echo $STREAM_BOT_ONLY_PID > .stream_bot_only.pid
    
    # Wait a moment and check if stream-bot-only system started
    sleep 2
    if kill -0 $STREAM_BOT_ONLY_PID 2>/dev/null; then
        print_status "Stream-bot-only trading system started successfully (PID: $STREAM_BOT_ONLY_PID) ✅"
        return 0
    else
        print_error "Failed to start stream-bot-only trading system"
        return 1
    fi
}

# Function to start web dashboard
start_web_dashboard() {
    print_status "Starting web dashboard server..."
    
    if port_in_use 5001; then
        print_warning "Port 5001 is already in use"
        return 1
    fi
    
    if [ ! -f "web_dashboard/app.py" ]; then
        print_error "web_dashboard/app.py not found"
        return 1
    fi
    
    cd web_dashboard
    python3 app.py &
    WEB_DASHBOARD_PID=$!
    echo $WEB_DASHBOARD_PID > ../.web_dashboard.pid
    cd ..
    
    # Wait a moment and check if web dashboard started
    sleep 2
    if kill -0 $WEB_DASHBOARD_PID 2>/dev/null; then
        print_status "Web dashboard started successfully (PID: $WEB_DASHBOARD_PID) ✅"
        print_status "Access at: http://localhost:5001"
        return 0
    else
        print_error "Failed to start web dashboard"
        return 1
    fi
}

# Function to start unified dashboard
start_unified_dashboard() {
    print_status "Starting unified dashboard server..."
    
    if port_in_use 5001; then
        print_warning "Port 5001 is already in use"
        return 1
    fi
    
    if [ ! -f "start_unified_dashboard.py" ]; then
        print_error "start_unified_dashboard.py not found"
        return 1
    fi
    
    python3 start_unified_dashboard.py &
    UNIFIED_DASHBOARD_PID=$!
    echo $UNIFIED_DASHBOARD_PID > .unified_dashboard.pid
    
    # Wait a moment and check if unified dashboard started
    sleep 3
    if kill -0 $UNIFIED_DASHBOARD_PID 2>/dev/null; then
        print_status "Unified dashboard started successfully (PID: $UNIFIED_DASHBOARD_PID) ✅"
        print_status "Access at: http://localhost:5001"
        return 0
    else
        print_error "Failed to start unified dashboard"
        return 1
    fi
}

# Function to start analysis-only trading
start_analysis_only_trading() {
    print_status "Starting analysis-only trading (AI-powered only)..."
    
    if [ ! -f "analysis/unified_trading_system.py" ]; then
        print_error "analysis/unified_trading_system.py not found"
        return 1
    fi
    
    python3 analysis/unified_trading_system.py --mode analysis_only --analysis-mode adaptive &
    ANALYSIS_ONLY_PID=$!
    echo $ANALYSIS_ONLY_PID > .analysis_only.pid
    
    # Wait a moment and check if analysis-only system started
    sleep 2
    if kill -0 $ANALYSIS_ONLY_PID 2>/dev/null; then
        print_status "Analysis-only trading system started successfully (PID: $ANALYSIS_ONLY_PID) ✅"
        return 0
    else
        print_error "Failed to start analysis-only trading system"
        return 1
    fi
}

# Function to stop all services
stop_services() {
    print_status "Stopping all services..."
    
    # Stop server
    if [ -f ".server.pid" ]; then
        SERVER_PID=$(cat .server.pid)
        if kill -0 $SERVER_PID 2>/dev/null; then
            kill $SERVER_PID
            print_status "Web server stopped"
        fi
        rm -f .server.pid
    fi
    
    # Stop bot
    if [ -f ".bot.pid" ]; then
        BOT_PID=$(cat .bot.pid)
        if kill -0 $BOT_PID 2>/dev/null; then
            kill $BOT_PID
            print_status "Trading bot stopped"
        fi
        rm -f .bot.pid
    fi
    
    # Stop streaming
    if [ -f ".stream.pid" ]; then
        STREAM_PID=$(cat .stream.pid)
        if kill -0 $STREAM_PID 2>/dev/null; then
            kill $STREAM_PID
            print_status "Data streaming stopped"
        fi
        rm -f .stream.pid
    fi
    
    # Stop unified trading system
    if [ -f ".unified.pid" ]; then
        UNIFIED_PID=$(cat .unified.pid)
        if kill -0 $UNIFIED_PID 2>/dev/null; then
            kill $UNIFIED_PID
            print_status "Unified trading system stopped"
        fi
        rm -f .unified.pid
    fi
    
    # Stop hybrid trading system
    if [ -f ".hybrid.pid" ]; then
        HYBRID_PID=$(cat .hybrid.pid)
        if kill -0 $HYBRID_PID 2>/dev/null; then
            kill $HYBRID_PID
            print_status "Hybrid trading system stopped"
        fi
        rm -f .hybrid.pid
    fi
    
    # Stop AI-enhanced trading system
    if [ -f ".ai_enhanced.pid" ]; then
        AI_ENHANCED_PID=$(cat .ai_enhanced.pid)
        if kill -0 $AI_ENHANCED_PID 2>/dev/null; then
            kill $AI_ENHANCED_PID
            print_status "AI-enhanced trading system stopped"
        fi
        rm -f .ai_enhanced.pid
    fi
    
    # Stop stream-bot-only trading system
    if [ -f ".stream_bot_only.pid" ]; then
        STREAM_BOT_ONLY_PID=$(cat .stream_bot_only.pid)
        if kill -0 $STREAM_BOT_ONLY_PID 2>/dev/null; then
            kill $STREAM_BOT_ONLY_PID
            print_status "Stream-bot-only trading system stopped"
        fi
        rm -f .stream_bot_only.pid
    fi
    
    # Stop web dashboard
    if [ -f ".web_dashboard.pid" ]; then
        WEB_DASHBOARD_PID=$(cat .web_dashboard.pid)
        if kill -0 $WEB_DASHBOARD_PID 2>/dev/null; then
            kill $WEB_DASHBOARD_PID
            print_status "Web dashboard stopped"
        fi
        rm -f .web_dashboard.pid
    fi
    
    # Stop unified dashboard
    if [ -f ".unified_dashboard.pid" ]; then
        UNIFIED_DASHBOARD_PID=$(cat .unified_dashboard.pid)
        if kill -0 $UNIFIED_DASHBOARD_PID 2>/dev/null; then
            kill $UNIFIED_DASHBOARD_PID
            print_status "Unified dashboard stopped"
        fi
        rm -f .unified_dashboard.pid
    fi
    
    # Stop analysis-only trading system
    if [ -f ".analysis_only.pid" ]; then
        ANALYSIS_ONLY_PID=$(cat .analysis_only.pid)
        if kill -0 $ANALYSIS_ONLY_PID 2>/dev/null; then
            kill $ANALYSIS_ONLY_PID
            print_status "Analysis-only trading system stopped"
        fi
        rm -f .analysis_only.pid
    fi
    
    # Kill any remaining Python processes that might be related
    pkill -f "server.py" 2>/dev/null || true
    pkill -f "run_bot.py" 2>/dev/null || true
    pkill -f "streamer" 2>/dev/null || true
    pkill -f "unified_trading_system.py" 2>/dev/null || true
    
    print_status "All services stopped ✅"
}

# Function to check system status
check_status() {
    print_header "📊 System Status Check"
    echo ""
    
    # Check web server
    if port_in_use 5000; then
        print_status "Web Server: Running on http://localhost:5000 ✅"
    else
        print_warning "Web Server: Not running ❌"
    fi
    
    # Check if bot is running
    if [ -f ".bot.pid" ]; then
        BOT_PID=$(cat .bot.pid)
        if kill -0 $BOT_PID 2>/dev/null; then
            print_status "Trading Bot: Running (PID: $BOT_PID) ✅"
        else
            print_warning "Trading Bot: Not running ❌"
            rm -f .bot.pid
        fi
    else
        print_warning "Trading Bot: Not running ❌"
    fi
    
    # Check if streaming is running
    if [ -f ".stream.pid" ]; then
        STREAM_PID=$(cat .stream.pid)
        if kill -0 $STREAM_PID 2>/dev/null; then
            print_status "Data Streaming: Running (PID: $STREAM_PID) ✅"
        else
            print_warning "Data Streaming: Not running ❌"
            rm -f .stream.pid
        fi
    else
        print_warning "Data Streaming: Not running ❌"
    fi
    
    # Check unified trading system
    if [ -f ".unified.pid" ]; then
        UNIFIED_PID=$(cat .unified.pid)
        if kill -0 $UNIFIED_PID 2>/dev/null; then
            print_status "Unified Trading System: Running (PID: $UNIFIED_PID) ✅"
        else
            print_warning "Unified Trading System: Not running ❌"
            rm -f .unified.pid
        fi
    else
        print_warning "Unified Trading System: Not running ❌"
    fi
    
    # Check hybrid trading system
    if [ -f ".hybrid.pid" ]; then
        HYBRID_PID=$(cat .hybrid.pid)
        if kill -0 $HYBRID_PID 2>/dev/null; then
            print_status "Hybrid Trading System: Running (PID: $HYBRID_PID) ✅"
        else
            print_warning "Hybrid Trading System: Not running ❌"
            rm -f .hybrid.pid
        fi
    else
        print_warning "Hybrid Trading System: Not running ❌"
    fi
    
    # Check stream-bot-only trading system
    if [ -f ".stream_bot_only.pid" ]; then
        STREAM_BOT_ONLY_PID=$(cat .stream_bot_only.pid)
        if kill -0 $STREAM_BOT_ONLY_PID 2>/dev/null; then
            print_status "Stream-Bot-Only Trading System: Running (PID: $STREAM_BOT_ONLY_PID) ✅"
        else
            print_warning "Stream-Bot-Only Trading System: Not running ❌"
            rm -f .stream_bot_only.pid
        fi
    else
        print_warning "Stream-Bot-Only Trading System: Not running ❌"
    fi
    
    # Check web dashboard
    if port_in_use 5001; then
        print_status "Web Dashboard: Running on http://localhost:5001 ✅"
    else
        print_warning "Web Dashboard: Not running ❌"
    fi
    
    # Check unified dashboard
    if [ -f ".unified_dashboard.pid" ]; then
        UNIFIED_DASHBOARD_PID=$(cat .unified_dashboard.pid)
        if kill -0 $UNIFIED_DASHBOARD_PID 2>/dev/null; then
            print_status "Unified Dashboard: Running (PID: $UNIFIED_DASHBOARD_PID) ✅"
        else
            print_warning "Unified Dashboard: Not running ❌"
            rm -f .unified_dashboard.pid
        fi
    else
        print_warning "Unified Dashboard: Not running ❌"
    fi
    
    # Check AI-enhanced trading system
    if [ -f ".ai_enhanced.pid" ]; then
        AI_ENHANCED_PID=$(cat .ai_enhanced.pid)
        if kill -0 $AI_ENHANCED_PID 2>/dev/null; then
            print_status "AI-Enhanced Trading System: Running (PID: $AI_ENHANCED_PID) ✅"
        else
            print_warning "AI-Enhanced Trading System: Not running ❌"
            rm -f .ai_enhanced.pid
        fi
    else
        print_warning "AI-Enhanced Trading System: Not running ❌"
    fi
    
    # Check environment variables
    check_env_vars
    
    # Check if log files exist
    if [ -d "logs" ]; then
        log_count=$(ls logs/ | wc -l)
        print_status "Log files: $log_count files in logs/ directory"
    else
        print_warning "Logs directory not found"
    fi
    
    echo ""
}

# Function to show recent logs
show_logs() {
    print_status "Showing recent logs..."
    
    if [ -d "logs" ]; then
        # Find the most recent setup log
        latest_log=$(ls -t logs/setup_*.log 2>/dev/null | head -1)
        if [ -n "$latest_log" ]; then
            print_status "Latest setup log: $latest_log"
            echo ""
            tail -20 "logs/$latest_log"
        else
            print_warning "No setup logs found"
        fi
    else
        print_warning "Logs directory not found"
    fi
}

# Function to run OpenAI demo
run_openai_demo() {
    print_status "Running OpenAI analysis demo..."
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY not set. Set it with:"
        print_error "export OPENAI_API_KEY='your-api-key-here'"
        return 1
    fi
    
    if [ ! -f "test_openai_analysis.py" ]; then
        print_error "test_openai_analysis.py not found"
        return 1
    fi
    
    python3 test_openai_analysis.py
}

# Function to run tests
run_tests() {
    print_status "Running test suite..."
    
    if [ -f "test_openai_analysis.py" ]; then
        print_status "Running OpenAI analysis tests..."
        python3 test_openai_analysis.py
    fi
    
    if [ -f "api_tests.py" ]; then
        print_status "Running API tests..."
        python3 api_tests.py
    fi
    
    if [ -f "scraping_tests.py" ]; then
        print_status "Running scraping tests..."
        python3 scraping_tests.py
    fi
    
    print_status "Test suite completed"
}

# Main command handling
case "${1:-help}" in
    "setup")
        print_header "🚀 Full System Setup"
        check_requirements
        python3 setup.py --all
        ;;
    
    "quick-setup")
        print_header "⚡ Quick System Setup"
        check_requirements
        python3 setup.py --quick
        ;;
    
    "server")
        check_requirements
        start_server
        print_status "Press Ctrl+C to stop the server"
        wait
        ;;
    
    "bot")
        check_requirements
        start_bot
        print_status "Press Ctrl+C to stop the bot"
        wait
        ;;
    
    "stream")
        check_requirements
        start_streaming
        print_status "Press Ctrl+C to stop streaming"
        wait
        ;;
    
    "all")
        print_header "🚀 Starting All Services"
        check_requirements
        start_server
        start_bot
        start_streaming
        start_web_dashboard
        print_status "All services started! Press Ctrl+C to stop all services"
        print_status "Web Dashboard: http://localhost:5001"
        print_status "Legacy Server: http://localhost:5000"
        
        # Set up signal handler to stop services on Ctrl+C
        trap 'stop_services; exit 0' INT TERM
        
        # Keep script running
        while true; do
            sleep 1
        done
        ;;
    
    "unified")
        check_requirements
        start_unified_trading
        print_status "Press Ctrl+C to stop the unified trading system"
        wait
        ;;
    
    "hybrid")
        check_requirements
        start_hybrid_trading
        print_status "Press Ctrl+C to stop the hybrid trading system"
        wait
        ;;
    
    "ai-enhanced")
        check_requirements
        start_ai_enhanced_trading
        print_status "Press Ctrl+C to stop the AI-enhanced trading system"
        wait
        ;;
    
    "stream-bot-only")
        check_requirements
        start_stream_bot_only_trading
        print_status "Press Ctrl+C to stop the stream-bot-only trading system"
        wait
        ;;
    
    "web-dashboard")
        check_requirements
        start_web_dashboard
        print_status "Press Ctrl+C to stop the web dashboard server"
        wait
        ;;
    
    "unified-dashboard")
        check_requirements
        start_unified_dashboard
        print_status "Press Ctrl+C to stop the unified dashboard server"
        wait
        ;;
    
    "modern")
        print_header "🚀 Starting Modern Services (Unified System + Web Dashboard)"
        check_requirements
        start_unified_trading
        start_web_dashboard
        print_status "Modern services started! Press Ctrl+C to stop all services"
        print_status "Web Dashboard: http://localhost:5001"
        
        # Set up signal handler to stop services on Ctrl+C
        trap 'stop_services; exit 0' INT TERM
        
        # Keep script running
        while true; do
            sleep 1
        done
        ;;
    
    "analysis-only")
        check_requirements
        start_analysis_only_trading
        print_status "Press Ctrl+C to stop the analysis-only trading system"
        wait
        ;;
    
    "openai-demo")
        check_requirements
        run_openai_demo
        ;;
    
    "analyzer")
        check_requirements
        print_status "Starting unified trading analyzer (adaptive mode)..."
        python3 start_unified_analyzer.py --mode adaptive
        ;;
    
    "basic")
        check_requirements
        print_status "Starting basic real-time analyzer..."
        python3 start_unified_analyzer.py --mode basic
        ;;
    
    "comprehensive")
        check_requirements
        print_status "Starting comprehensive analyzer with news sentiment..."
        python3 start_unified_analyzer.py --mode comprehensive
        ;;
    
    "web")
        check_requirements
        print_status "Starting unified web dashboard..."
        python3 start_unified_analyzer.py --web
        ;;
    
    "adaptability-test")
        check_requirements
        print_status "Testing market condition adaptability..."
        python3 start_unified_analyzer.py --test adaptability
        ;;
    
    "profitability-test")
        check_requirements
        print_status "Testing profitability across market conditions..."
        python3 start_unified_analyzer.py --test profitability
        ;;
    
    "test")
        check_requirements
        run_tests
        ;;
    
    "check")
        check_status
        ;;
    
    "stop")
        stop_services
        ;;
    
    "logs")
        show_logs
        ;;
    
    "install")
        check_requirements
        install_dependencies
        ;;
    
    "help"|"--help"|"-h")
        show_help
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac