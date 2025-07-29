#!/usr/bin/env python3
"""
Comprehensive Forex Trading Dashboard
Combines forex-dash and web_dashboard functionality with enhanced features
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import sys
from datetime import datetime, timedelta
import threading
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from api.oanda_api import OandaApi
from scraping.tradingeconomics_calendar import fx_calendar
from scraping.forexfactory_calendar import forexfactory_calendar
from technicals.indicators import TechnicalIndicators
from technicals.patterns import PatternRecognition
from shared_data_store import get_shared_store, TradeAlert

app = Flask(__name__)

# Initialize APIs and services
oanda_api = OandaApi()
technical_indicators = TechnicalIndicators()
pattern_recognition = PatternRecognition()
shared_store = get_shared_store()

# Global state
system_status = {
    'running': False,
    'last_update': None,
    'stream_bot': False,
    'ai_analysis': False,
    'data_streaming': False
}

# System control functions
def start_all_systems():
    """Start all trading systems"""
    try:
        import subprocess
        import os
        
        # Start system coordinator
        coordinator_process = subprocess.Popen([
            'python3', '-c',
            'import sys; sys.path.append("./"); from system_coordinator import SystemCoordinator; import threading; import signal; signal.signal(signal.SIGINT, lambda s, f: sys.exit(0)); signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0)); coordinator = SystemCoordinator(); thread = threading.Thread(target=coordinator.start, daemon=True); thread.start(); print("✅ System Coordinator started"); import time; time.sleep(3600)'
        ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Save PID file
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.system_coordinator.pid'), 'w') as f:
            f.write(str(coordinator_process.pid))
        
        # Start comprehensive strategy
        strategy_process = subprocess.Popen([
            'python3', '-c',
            'import sys; sys.path.append("./"); from analysis.comprehensive_trading_strategy import ComprehensiveTradingStrategy, StrategyMode; import signal; signal.signal(signal.SIGINT, lambda s, f: sys.exit(0)); signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0)); strategy = ComprehensiveTradingStrategy(mode=StrategyMode.MODERATE, pairs=["EUR_USD", "GBP_USD", "USD_JPY", "USD_CAD", "AUD_USD"], risk_per_trade=0.02, max_positions=5); print("🤖 Comprehensive Trading Strategy Starting..."); strategy.start_strategy(); import time; time.sleep(3600)'
        ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Save PID file
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.comprehensive_strategy.pid'), 'w') as f:
            f.write(str(strategy_process.pid))
        
        # Start data streaming
        streaming_process = subprocess.Popen([
            'python3', '-c',
            'import sys; sys.path.append("./"); from stream_example.streamer import run_streamer; run_streamer()'
        ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Save PID file
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.data_streaming.pid'), 'w') as f:
            f.write(str(streaming_process.pid))
        
        # Start stream bot
        bot_process = subprocess.Popen([
            'python3', '-c',
            'import sys; sys.path.append("./"); from stream_bot.stream_bot import run_bot; print("🤖 Stream Bot Starting..."); run_bot()'
        ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Save PID file
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.stream_bot.pid'), 'w') as f:
            f.write(str(bot_process.pid))
        
        system_status['running'] = True
        system_status['stream_bot'] = True
        system_status['ai_analysis'] = True
        system_status['data_streaming'] = True
        system_status['last_update'] = datetime.now()
        
        return True
    except Exception as e:
        print(f"Error starting systems: {e}")
        return False

def stop_all_systems():
    """Stop all trading systems"""
    try:
        import subprocess
        import os
        
        # Kill all Python processes related to our systems
        subprocess.run(['pkill', '-f', 'system_coordinator'], check=False)
        subprocess.run(['pkill', '-f', 'comprehensive_trading_strategy'], check=False)
        subprocess.run(['pkill', '-f', 'streamer'], check=False)
        subprocess.run(['pkill', '-f', 'stream_bot'], check=False)
        
        # Remove PID files from project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pid_files = [
            os.path.join(project_root, '.system_coordinator.pid'),
            os.path.join(project_root, '.comprehensive_strategy.pid'),
            os.path.join(project_root, '.data_streaming.pid'),
            os.path.join(project_root, '.stream_bot.pid')
        ]
        for pid_file in pid_files:
            if os.path.exists(pid_file):
                os.remove(pid_file)
        
        system_status['running'] = False
        system_status['stream_bot'] = False
        system_status['ai_analysis'] = False
        system_status['data_streaming'] = False
        system_status['last_update'] = datetime.now()
        
        return True
    except Exception as e:
        print(f"Error stopping systems: {e}")
        return False

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/options')
def get_options():
    """Get available options for currency pairs, granularities, etc."""
    try:
        pairs = [
            {"value": "EUR_USD", "text": "EUR/USD"},
            {"value": "GBP_USD", "text": "GBP/USD"},
            {"value": "USD_JPY", "text": "USD/JPY"},
            {"value": "USD_CHF", "text": "USD/CHF"},
            {"value": "AUD_USD", "text": "AUD/USD"},
            {"value": "USD_CAD", "text": "USD/CAD"},
            {"value": "NZD_USD", "text": "NZD/USD"},
            {"value": "EUR_GBP", "text": "EUR/GBP"},
            {"value": "EUR_JPY", "text": "EUR/JPY"},
            {"value": "GBP_JPY", "text": "GBP/JPY"}
        ]
        
        granularities = [
            {"value": "M1", "text": "1 Minute"},
            {"value": "M5", "text": "5 Minutes"},
            {"value": "M15", "text": "15 Minutes"},
            {"value": "M30", "text": "30 Minutes"},
            {"value": "H1", "text": "1 Hour"},
            {"value": "H4", "text": "4 Hours"},
            {"value": "D", "text": "Daily"}
        ]
        
        return jsonify({
            'pairs': pairs,
            'granularities': granularities
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prices/<pair>/<granularity>/<count>')
def get_prices(pair, granularity, count):
    """Get price data for charts"""
    try:
        count = int(count)
        data = oanda_api.web_api_candles(pair, granularity, count)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/technicals/<pair>/<granularity>')
def get_technicals(pair, granularity):
    """Get technical indicators"""
    try:
        # Get price data
        df = oanda_api.get_candles_df(pair, granularity=granularity, count=100)
        if df is None or df.empty:
            return jsonify({'error': 'No price data available'}), 404
        
        # Calculate technical indicators
        df = technical_indicators.calculate_all_indicators(df)
        
        # Get latest values
        latest = df.iloc[-1]
        
        technicals = {
            'rsi': round(latest.get('RSI_14', 0), 2),
            'macd': round(latest.get('MACD', 0), 5),
            'macd_signal': round(latest.get('SIGNAL_MD', 0), 5),
            'macd_histogram': round(latest.get('HIST', 0), 5),
            'ema_20': round(latest.get('EMA_20', 0), 5),
            'ema_50': round(latest.get('EMA_50', 0), 5),
            'ema_200': round(latest.get('EMA_200', 0), 5),
            'sma_20': round(latest.get('SMA_20', 0), 5),
            'sma_50': round(latest.get('SMA_50', 0), 5),
            'bollinger_upper': round(latest.get('BB_UP', 0), 5),
            'bollinger_lower': round(latest.get('BB_LW', 0), 5),
            'bollinger_middle': round(latest.get('BB_MA', 0), 5),
            'stoch_k': round(latest.get('Stochastic', 0), 2),
            'stoch_d': round(latest.get('Stoch_D', 0), 2),
            'atr': round(latest.get('ATR_14', 0), 5),
            'adx': round(latest.get('ADX', 0), 2)
        }
        
        return jsonify(technicals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patterns/<pair>/<granularity>')
def get_patterns(pair, granularity):
    """Get candlestick patterns"""
    try:
        # Get price data
        df = oanda_api.get_candles_df(pair, granularity=granularity, count=100)
        if df is None or df.empty:
            print(f"No price data available for {pair} {granularity}")
            return jsonify({'error': 'No price data available'}), 404
        
        # Simple pattern recognition without complex calculations
        try:
            # Calculate basic candle properties
            df['body_size'] = abs(df['mid_c'] - df['mid_o'])
            df['total_range'] = df['mid_h'] - df['mid_l']
            df['body_perc'] = (df['body_size'] / df['total_range']) * 100
            df['direction'] = [1 if c >= o else -1 for c, o in zip(df['mid_c'], df['mid_o'])]
            
            # Get latest candle
            latest = df.iloc[-1]
            
            # Simple pattern detection
            patterns = {
                'doji': bool(latest['body_perc'] < 10),
                'hammer': bool(latest['body_perc'] < 30 and latest['direction'] == 1),
                'shooting_star': bool(latest['body_perc'] < 30 and latest['direction'] == -1),
                'engulfing_bullish': False,  # Would need previous candle data
                'engulfing_bearish': False,  # Would need previous candle data
                'morning_star': False,  # Would need previous candles
                'evening_star': False,  # Would need previous candles
                'hanging_man': bool(latest['body_perc'] < 30 and latest['direction'] == -1),
                'spinning_top': bool(10 < latest['body_perc'] < 40)
            }
        except Exception as e:
            print(f"Simple pattern recognition error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Pattern recognition error: {str(e)}'}), 500
        
        return jsonify(patterns)
    except Exception as e:
        print(f"Error in patterns endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/te/calendar/<start>/<end>')
def te_calendar(start, end):
    """Get TradingEconomics calendar data"""
    try:
        data = fx_calendar(start, end)
        return jsonify(data)
    except Exception as e:
        # Return sample data on error
        sample_data = [
            {
                "date": "2025-01-06T10:00:00Z",
                "time": "10:00",
                "currency": "USD",
                "impact": "High",
                "event": "Non-Farm Payrolls",
                "actual": "185K",
                "forecast": "180K",
                "previous": "173K"
            },
            {
                "date": "2025-01-06T14:00:00Z", 
                "time": "14:00",
                "currency": "EUR",
                "impact": "Medium",
                "event": "ECB President Speech",
                "actual": "",
                "forecast": "",
                "previous": ""
            }
        ]
        return jsonify(sample_data)

@app.route('/api/ff/calendar/<month>')
def ff_calendar(month):
    """Get ForexFactory calendar data"""
    try:
        data = forexfactory_calendar(month)
        return jsonify(data)
    except Exception as e:
        # Return sample data on error
        sample_data = [
            {
                "date": "2025-01-06",
                "time": "13:30",
                "currency": "USD",
                "impact": "High",
                "event": "Non-Farm Employment Change",
                "actual": "185K",
                "forecast": "180K",
                "previous": "173K"
            },
            {
                "date": "2025-01-06",
                "time": "15:00", 
                "currency": "EUR",
                "impact": "Medium",
                "event": "ECB President Lagarde Speech",
                "actual": "",
                "forecast": "",
                "previous": ""
            }
        ]
        return jsonify(sample_data)

# ============================================================================
# TRADE EXECUTION ENDPOINTS
# ============================================================================

@app.route('/api/trade/place', methods=['POST'])
def place_trade():
    """Place a new trade"""
    try:
        data = request.get_json()
        pair = data.get('pair')
        units = int(data.get('units', 1000))
        direction = data.get('direction', 'buy')
        stop_loss = data.get('stop_loss')
        take_profit = data.get('take_profit')
        
        # Convert direction to OANDA format
        oanda_direction = 'long' if direction == 'buy' else 'short'
        
        result = oanda_api.place_trade(
            pair_name=pair,
            units=units,
            direction=oanda_direction,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        return jsonify({'success': True, 'trade_id': result.get('id')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trade/close/<trade_id>', methods=['POST'])
def close_trade(trade_id):
    """Close a specific trade"""
    try:
        result = oanda_api.close_trade(trade_id)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trade/open')
def get_open_trades():
    """Get all open trades"""
    try:
        trades = oanda_api.get_open_trades()
        return jsonify({'success': True, 'trades': trades})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/positions')
def get_positions():
    """Get all positions"""
    try:
        positions = oanda_api.get_positions()
        return jsonify({'success': True, 'positions': positions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/account')
def get_account():
    """Get account information"""
    try:
        account = oanda_api.get_account_summary()
        return jsonify({'success': True, 'account': account})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# SYSTEM STATUS ENDPOINTS
# ============================================================================

@app.route('/api/system/status')
def get_system_status():
    """Get overall system status"""
    try:
        import subprocess
        
        # Check PID files in project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        def check_pid_file(pid_file_name):
            pid_file_path = os.path.join(project_root, pid_file_name)
            if os.path.exists(pid_file_path):
                try:
                    with open(pid_file_path, 'r') as f:
                        pid = int(f.read().strip())
                    # Check if process is running
                    result = subprocess.run(['ps', '-p', str(pid)], capture_output=True, text=True)
                    return result.returncode == 0
                except:
                    return False
            return False
        
        # Check each system
        stream_bot_running = check_pid_file('.stream_bot.pid')
        comprehensive_strategy_running = check_pid_file('.comprehensive_strategy.pid')
        data_streaming_running = check_pid_file('.data_streaming.pid')
        system_coordinator_running = check_pid_file('.system_coordinator.pid')
        
        # Update global status
        system_status['stream_bot'] = stream_bot_running
        system_status['ai_analysis'] = comprehensive_strategy_running
        system_status['data_streaming'] = data_streaming_running
        system_status['running'] = any([stream_bot_running, comprehensive_strategy_running, data_streaming_running, system_coordinator_running])
        system_status['last_update'] = datetime.now()
        
        status = {
            'running': system_status['running'],
            'last_update': system_status['last_update'],
            'stream_bot': stream_bot_running,
            'ai_analysis': comprehensive_strategy_running,
            'data_streaming': data_streaming_running
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get trade alerts from comprehensive strategy"""
    try:
        alerts = shared_store.get_trade_alerts()
        return jsonify({'success': True, 'alerts': alerts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/alerts/<alert_id>/execute', methods=['POST'])
def execute_alert(alert_id):
    """Execute a trade alert"""
    try:
        # Find the alert
        alerts = shared_store.get_trade_alerts()
        alert = next((a for a in alerts if a.id == alert_id), None)
        
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'})
        
        # Execute the trade
        result = oanda_api.place_trade(
            pair_name=alert.pair,
            units=alert.units,
            direction=alert.signal.lower(),
            stop_loss=alert.stop_loss,
            take_profit=alert.take_profit
        )
        
        # Update alert status
        shared_store.update_trade_alert_status(alert_id, 'executed')
        
        return jsonify({'success': True, 'trade_id': result.get('id')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# REAL-TIME DATA ENDPOINTS
# ============================================================================

@app.route('/api/realtime/<pair>')
def get_realtime_data(pair):
    """Get real-time price data"""
    try:
        # Get latest candle
        df = oanda_api.get_candles_df(pair, granularity='M1', count=1)
        if df is None or df.empty:
            return jsonify({'error': 'No data available'}), 404
        
        latest = df.iloc[-1]
        
        data = {
            'pair': pair,
            'timestamp': latest.name.isoformat(),
            'open': float(latest['mid_o']),
            'high': float(latest['mid_h']),
            'low': float(latest['mid_l']),
            'close': float(latest['mid_c']),
            'volume': int(latest.get('volume', 0))
        }
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/<pair>')
def get_comprehensive_analysis(pair):
    """Get comprehensive analysis for a pair"""
    try:
        # Get price data
        df = oanda_api.get_candles_df(pair, granularity='H1', count=100)
        if df is None or df.empty:
            return jsonify({'error': 'No price data available'}), 404
        
        # Calculate technical indicators
        df = technical_indicators.calculate_all_indicators(df)
        
        # Simple pattern recognition
        try:
            # Calculate basic candle properties
            df['body_size'] = abs(df['mid_c'] - df['mid_o'])
            df['total_range'] = df['mid_h'] - df['mid_l']
            df['body_perc'] = (df['body_size'] / df['total_range']) * 100
            df['direction'] = [1 if c >= o else -1 for c, o in zip(df['mid_c'], df['mid_o'])]
            
            # Get latest values
            latest = df.iloc[-1]
            
            # Technical analysis (simplified)
            technical = {
                'trend': 'bullish' if latest.get('EMA_20', 0) > latest.get('EMA_50', 0) else 'bearish',
                'rsi': round(latest.get('RSI_14', 0), 2),
                'rsi_signal': 'oversold' if latest.get('RSI_14', 0) < 30 else 'overbought' if latest.get('RSI_14', 0) > 70 else 'neutral',
                'macd_signal': 'bullish' if latest.get('HIST', 0) > 0 else 'bearish',
                'support': round(latest.get('BB_LW', 0), 5),
                'resistance': round(latest.get('BB_UP', 0), 5),
                'volatility': round(latest.get('ATR_14', 0), 5)
            }
            
            # Simple pattern analysis
            patterns = []
            if latest['body_perc'] < 10:
                patterns.append('Doji')
            if latest['body_perc'] < 30 and latest['direction'] == 1:
                patterns.append('Hammer')
            if latest['body_perc'] < 30 and latest['direction'] == -1:
                patterns.append('Shooting Star')
            if 10 < latest['body_perc'] < 40:
                patterns.append('Spinning Top')
        except Exception as e:
            technical = {'trend': 'unknown', 'rsi': 0, 'rsi_signal': 'neutral', 'macd_signal': 'neutral', 'support': 0, 'resistance': 0, 'volatility': 0}
            patterns = []
        
        # Price action
        price_change = ((latest['mid_c'] - latest['mid_o']) / latest['mid_o']) * 100
        price_action = {
            'change_percent': round(price_change, 2),
            'direction': 'up' if price_change > 0 else 'down',
            'body_size': abs(latest['mid_c'] - latest['mid_o']),
            'wick_size': latest['mid_h'] - latest['mid_l']
        }
        
        analysis = {
            'pair': pair,
            'timestamp': str(latest.name) if hasattr(latest.name, 'isoformat') else str(latest.name),
            'technical': technical,
            'patterns': patterns,
            'price_action': price_action,
            'recommendation': 'BUY' if technical['trend'] == 'bullish' and technical['rsi_signal'] != 'overbought' else 'SELL' if technical['trend'] == 'bearish' and technical['rsi_signal'] != 'oversold' else 'HOLD'
        }
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/start', methods=['POST'])
def start_system():
    """Start all trading systems"""
    try:
        success = start_all_systems()
        if success:
            return jsonify({'status': 'success', 'message': 'All systems started successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to start systems'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    """Stop all trading systems"""
    try:
        success = stop_all_systems()
        if success:
            return jsonify({'status': 'success', 'message': 'All systems stopped successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to stop systems'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 