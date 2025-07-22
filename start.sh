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

# Function to check if a port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
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
    echo "  test          - Run test suite"
    echo "  check         - Check system status"
    echo "  stop          - Stop all running services"
    echo "  logs          - Show recent logs"
    echo "  install       - Install dependencies only"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./start.sh setup         # Full system setup"
    echo "  ./start.sh all           # Start all services"
    echo "  ./start.sh server        # Start web server only"
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
    
    # Kill any remaining Python processes that might be related
    pkill -f "server.py" 2>/dev/null || true
    pkill -f "run_bot.py" 2>/dev/null || true
    pkill -f "streamer" 2>/dev/null || true
    
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
    
    # Run OpenAI tests if available
    if [ -f "test_openai_analysis.py" ]; then
        print_status "Running OpenAI analysis tests..."
        python3 test_openai_analysis.py
    fi
    
    # Run API tests if available
    if [ -f "api_tests.py" ]; then
        print_status "Running API tests..."
        python3 api_tests.py
    fi
    
    # Run scraping tests if available
    if [ -f "scraping_tests.py" ]; then
        print_status "Running scraping tests..."
        python3 scraping_tests.py
    fi
    
    print_status "Test suite completed ✅"
}

# Main script logic
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
        print_status "All services started! Press Ctrl+C to stop all services"
        
        # Set up signal handler to stop services on Ctrl+C
        trap 'stop_services; exit 0' INT TERM
        
        # Keep script running
        while true; do
            sleep 1
        done
        ;;
    
    "openai-demo")
        check_requirements
        run_openai_demo
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