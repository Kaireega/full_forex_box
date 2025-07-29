#!/bin/bash

# Simple Forex Trading System Control Script
# Usage: ./start.sh [start|stop|check|logs]

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Python 3 exists
check_python() {
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    print_status "Python 3 found"
}

# Start all systems
start_systems() {
    print_header "Starting Forex Trading System"
    check_python
    
    print_status "Starting System Coordinator..."
    python3 -c "
import sys
sys.path.append('./')
from system_coordinator import SystemCoordinator
import threading
import signal

def signal_handler(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

coordinator = SystemCoordinator()
thread = threading.Thread(target=coordinator.start, daemon=True)
thread.start()
print('✅ System Coordinator started')
import time
time.sleep(3600)
" &
    echo $! > .system_coordinator.pid
    
    print_status "Starting Comprehensive Trading Strategy..."
    python3 -c "
import sys
sys.path.append('./')
from analysis.comprehensive_trading_strategy import ComprehensiveTradingStrategy, StrategyMode
import signal

def signal_handler(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

strategy = ComprehensiveTradingStrategy(
    mode=StrategyMode.MODERATE,
    pairs=['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CAD', 'AUD_USD'],
    risk_per_trade=0.02,
    max_positions=5
)
print('🤖 Comprehensive Trading Strategy Starting...')
strategy.start_strategy()
import time
time.sleep(3600)
" &
    echo $! > .comprehensive_strategy.pid
    
    print_status "Starting Data Streaming..."
    python3 -c "
import sys
sys.path.append('./')
from stream_example.streamer import run_streamer
run_streamer()
" &
    echo $! > .data_streaming.pid
    
    print_status "Starting Stream Bot..."
    python3 -c "
import sys
sys.path.append('./')
from stream_bot.stream_bot import run_bot
print('🤖 Stream Bot Starting...')
run_bot()
" &
    echo $! > .stream_bot.pid
    
    print_status "Starting Comprehensive Dashboard..."
    python3 start_comprehensive_dashboard.py &
    echo $! > .comprehensive_dashboard.pid
    
    sleep 3
    print_status "All systems started successfully!"
    print_status "Dashboard: http://localhost:5001"
    print_status "Press Ctrl+C to stop all services"
    
    # Keep running and handle Ctrl+C
    trap 'echo ""; print_status "Shutting down..."; stop_systems; exit 0' INT TERM
    while true; do
        sleep 1
    done
}

# Stop all systems
stop_systems() {
    print_header "Stopping All Services"
    
    # Stop by PID files
    for pid_file in .system_coordinator.pid .comprehensive_strategy.pid .data_streaming.pid .stream_bot.pid .comprehensive_dashboard.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
            fi
            rm -f "$pid_file"
        fi
    done
    
    # Kill any remaining Python processes
    pkill -f "system_coordinator" 2>/dev/null || true
    pkill -f "comprehensive_trading_strategy" 2>/dev/null || true
    pkill -f "streamer" 2>/dev/null || true
    pkill -f "stream_bot" 2>/dev/null || true
    pkill -f "app.py" 2>/dev/null || true
    pkill -f "start_comprehensive_dashboard" 2>/dev/null || true
    
    sleep 1
    
    # Force kill if needed
    pkill -9 -f "comprehensive_dashboard" 2>/dev/null || true
    pkill -9 -f "stream_bot" 2>/dev/null || true
    pkill -9 -f "system_coordinator" 2>/dev/null || true
    
    print_status "All services stopped"
}

# Check system status
check_status() {
    print_header "System Status"
    
    # Check each service
    services=(
        "System Coordinator:.system_coordinator.pid"
        "Comprehensive Strategy:.comprehensive_strategy.pid"
        "Data Streaming:.data_streaming.pid"
        "Stream Bot:.stream_bot.pid"
        "Comprehensive Dashboard:.comprehensive_dashboard.pid"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r name pid_file <<< "$service"
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                print_status "$name: Running (PID: $pid)"
            else
                print_warning "$name: Not running"
                rm -f "$pid_file"
            fi
        else
            print_warning "$name: Not running"
        fi
    done
    
    # Check dashboard
    if curl -s http://localhost:5001 >/dev/null 2>&1; then
        print_status "Dashboard: Running (http://localhost:5001)"
    else
        print_warning "Dashboard: Not accessible"
    fi
    
    # Check environment
    if [ -n "$OPENAI_API_KEY" ]; then
        print_status "OpenAI API Key: Set"
    else
        print_warning "OpenAI API Key: Not set"
    fi
}

# Show logs
show_logs() {
    print_header "Recent Logs"
    
    if [ -d "logs" ]; then
        echo "=== System Coordinator Log ==="
        tail -10 logs/system_coordinator.log 2>/dev/null || echo "No system coordinator logs"
        echo ""
        
        echo "=== Comprehensive Strategy Log ==="
        tail -10 logs/comprehensive_trading_strategy.log 2>/dev/null || echo "No strategy logs"
        echo ""
        
        echo "=== Stream Bot Log ==="
        tail -10 logs/stream_bot.log 2>/dev/null || echo "No stream bot logs"
            echo ""
        
        echo "=== Dashboard Log ==="
        tail -10 logs/shared_data_store.log 2>/dev/null || echo "No dashboard logs"
    else
        print_warning "No logs directory found"
    fi
}

# Main script logic
case "${1:-}" in
    "start")
        start_systems
        ;;
    "stop")
        stop_systems
        ;;
    "check")
        check_status
        ;;
    "logs")
        show_logs
        ;;
    *)
        print_header "Forex Trading System Control"
        echo ""
        echo "Usage: ./start.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  start  - Start all trading systems"
        echo "  stop   - Stop all running services"
        echo "  check  - Check system status"
        echo "  logs   - Show recent logs"
        echo ""
        echo "Examples:"
        echo "  ./start.sh start   # Start all systems"
        echo "  ./start.sh stop    # Stop all systems"
        echo "  ./start.sh check   # Check status"
        echo "  ./start.sh logs    # View logs"
        ;;
esac