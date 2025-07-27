#!/usr/bin/env python3
"""
Unified Dashboard Server - Comprehensive Forex Trading System

This Flask application serves a unified dashboard that combines:
- Real-time trading system control
- Price charts and technical analysis
- Economic calendars
- Comprehensive trading analysis
- All functionality from both web_dashboard and forex-dash
"""

import sys
import os
import json
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from typing import Dict, Optional
import http

# Add project root to path
sys.path.append("../")

# Import trading system components
from analysis.unified_trading_system import UnifiedTradingSystem, TradingMode
from analysis.unified_trading_analyzer import AnalysisMode

# Import API components
from api.oanda_api import OandaApi
from api.web_options import get_options

# Import scraping components
from scraping.bloomberg_com import bloomberg_com
from scraping.forexfactory_calendar import get_monthly_data
from scraping.tradingeconomics_calendar import fx_calendar
from scraping.investing_com import get_pair

app = Flask(__name__)
CORS(app)

# Global trading system instance
trading_system = None
system_thread = None

def get_response(data):
    """Helper function to format API responses."""
    if data is None:
        return jsonify(dict(message='error getting data')), http.HTTPStatus.NOT_FOUND
    else:
        return jsonify(data)

def get_trading_mode(mode_str: str) -> TradingMode:
    """Convert string to TradingMode enum."""
    mode_map = {
        'stream_bot_only': TradingMode.STREAM_BOT_ONLY,
        'analysis_only': TradingMode.ANALYSIS_ONLY,
        'hybrid': TradingMode.HYBRID,
        'ai_enhanced': TradingMode.AI_ENHANCED
    }
    return mode_map.get(mode_str, TradingMode.HYBRID)

def get_analysis_mode(mode_str: str) -> AnalysisMode:
    """Convert string to AnalysisMode enum."""
    mode_map = {
        'basic': AnalysisMode.BASIC,
        'adaptive': AnalysisMode.ADAPTIVE,
        'comprehensive': AnalysisMode.COMPREHENSIVE
    }
    return mode_map.get(mode_str, AnalysisMode.ADAPTIVE)

@app.route('/')
def dashboard():
    """Serve the main unified dashboard."""
    return render_template('dashboard.html')

# ============================================================================
# TRADING SYSTEM CONTROL ENDPOINTS
# ============================================================================

@app.route('/api/status')
def get_status():
    """Get system status."""
    try:
        if trading_system is None:
            return jsonify({
                'is_running': False,
                'stream_bot_running': False,
                'analysis_running': False,
                'message': 'System not initialized'
            })
        
        status = trading_system.get_status()
        return jsonify({
            'is_running': trading_system.is_running,
            'stream_bot_running': trading_system.is_running,
            'analysis_running': trading_system.analysis_available and trading_system.is_running,
            'mode': status['mode'],
            'pairs': status['pairs'],
            'open_trades': status['open_trades'],
            'daily_trades': status['daily_trades'],
            'total_trades': status['total_trades']
        })
    except Exception as e:
        return jsonify({
            'is_running': False,
            'stream_bot_running': False,
            'analysis_running': False,
            'error': str(e)
        })

@app.route('/api/start', methods=['POST'])
def start_system():
    """Start the unified trading system."""
    global trading_system, system_thread
    
    try:
        if trading_system is not None and trading_system.is_running:
            return jsonify({'success': False, 'error': 'System is already running'})
        
        # Get settings from request
        data = request.get_json() or {}
        trading_mode = get_trading_mode(data.get('tradingMode', 'hybrid'))
        analysis_mode = get_analysis_mode(data.get('analysisMode', 'adaptive'))
        
        print(f"🚀 Starting unified trading system...")
        print(f"📊 Mode: {trading_mode.value}")
        print(f"🤖 Analysis Mode: {analysis_mode.value}")
        
        # Initialize trading system
        trading_system = UnifiedTradingSystem(
            mode=trading_mode,
            analysis_mode=analysis_mode
        )
        
        # Start trading system in a separate thread
        system_thread = trading_system.start_trading()
        
        return jsonify({
            'success': True, 
            'message': f'Trading system started in {trading_mode.value} mode'
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error starting system: {error_details}")
        return jsonify({
            'success': False, 
            'error': f'Failed to start system: {str(e)}',
            'details': error_details
        })

@app.route('/api/stop', methods=['POST'])
def stop_system():
    """Stop the unified trading system."""
    global trading_system, system_thread
    
    try:
        if trading_system is None or not trading_system.is_running:
            return jsonify({'success': False, 'error': 'System is not running'})
        
        trading_system.stop_trading()
        
        # Wait for thread to finish
        if system_thread and system_thread.is_alive():
            system_thread.join(timeout=5)
        
        trading_system = None
        system_thread = None
        
        return jsonify({'success': True, 'message': 'Trading system stopped'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/signals')
def get_signals():
    """Get recent trading signals."""
    try:
        if trading_system is None or not trading_system.is_running:
            return jsonify({'signals': [], 'message': 'System not running'})
        
        # Get signals from trading system
        signals = []
        if hasattr(trading_system, 'trade_history'):
            # Convert unified trade decisions to signal format
            for decision in trading_system.trade_history[-20:]:  # Last 20 signals
                signal = {
                    'timestamp': decision.timestamp,
                    'currency_pair': decision.pair,
                    'signal_type': decision.signal,
                    'confidence': decision.confidence,
                    'entry_price': decision.entry_price,
                    'stop_loss': decision.stop_loss,
                    'take_profit': decision.take_profit,
                    'reasoning': decision.reasoning,
                    'risk_level': decision.risk_level
                }
                signals.append(signal)
        
        return jsonify({'signals': signals})
        
    except Exception as e:
        return jsonify({'signals': [], 'error': str(e)})

@app.route('/api/summary')
def get_summary():
    """Get trading summary statistics."""
    try:
        if trading_system is None or not trading_system.is_running:
            return jsonify({'message': 'System not running'})
        
        # Calculate summary statistics
        signals = trading_system.trade_history if hasattr(trading_system, 'trade_history') else []
        
        if not signals:
            return jsonify({'message': 'No signals yet'})
        
        # Calculate statistics
        total_signals = len(signals)
        confidences = [s.confidence for s in signals if hasattr(s, 'confidence')]
        average_confidence = sum(confidences) / len(confidences) if confidences else 0
        high_confidence_signals = len([c for c in confidences if c >= 0.8])
        
        # Get unique currency pairs
        currency_pairs = list(set(s.pair for s in signals))
        
        # Get status for additional metrics
        status = trading_system.get_status()
        
        return jsonify({
            'total_signals': total_signals,
            'average_confidence': average_confidence,
            'high_confidence_signals': high_confidence_signals,
            'currency_pairs': {pair: True for pair in currency_pairs},
            'open_trades': status.get('open_trades', 0),
            'daily_trades': status.get('daily_trades', 0)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/performance')
def get_performance():
    """Get performance metrics."""
    try:
        if trading_system is None or not trading_system.is_running:
            return jsonify({'message': 'System not running'})
        
        # This would typically calculate performance from trade history
        # For now, return placeholder metrics
        return jsonify({
            'win_rate': 65.5,  # Placeholder
            'profit_factor': 1.8,  # Placeholder
            'max_drawdown': 12.3,  # Placeholder
            'total_return': 23.7  # Placeholder
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or update system settings."""
    if request.method == 'GET':
        try:
            if trading_system is None:
                return jsonify({
                    'trading_mode': 'hybrid',
                    'analysis_mode': 'adaptive',
                    'confidence_threshold': 0.7,
                    'update_interval': 60
                })
            
            return jsonify({
                'trading_mode': trading_system.mode.value,
                'analysis_mode': trading_system.analysis_mode.value,
                'confidence_threshold': trading_system.min_confidence_threshold,
                'update_interval': 60  # Fixed for now
            })
            
        except Exception as e:
            return jsonify({'error': str(e)})
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if trading_system is not None:
                # Update trading system settings
                if 'confidence_threshold' in data:
                    trading_system.min_confidence_threshold = data['confidence_threshold']
                
                return jsonify({'success': True, 'message': 'Settings updated'})
            else:
                return jsonify({'success': False, 'error': 'System not running'})
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# FOREX-DASH API ENDPOINTS (PRICE CHARTS, TECHNICALS, CALENDARS)
# ============================================================================

@app.route('/api/test')
def test():
    return jsonify(dict(message='hello'))

@app.route("/api/headlines")
def headlines():
    return get_response(bloomberg_com())

@app.route("/api/account")
def account():
    return get_response(OandaApi().get_account_summary())

@app.route("/api/options")
def options():
    return get_response(get_options())

@app.route("/api/technicals/<pair>/<tf>")
def technicals(pair, tf):
    return get_response(get_pair(pair, tf))

@app.route("/api/prices/<pair>/<granularity>/<count>")
def prices(pair, granularity, count):
    return get_response(OandaApi().web_api_candles(pair, granularity, count))

@app.route("/api/te/calendar/<start>/<end>")
def te_calendar(start, end):
    try:
        data = fx_calendar(start, end)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/ff/calendar/<start>")
def ff_calendar(start):
    try:
        data = get_monthly_data(start)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# TRADE EXECUTION ENDPOINTS
# ============================================================================

@app.route('/api/trade/place', methods=['POST'])
def place_trade():
    """Place a new trade."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        # Extract trade parameters
        pair = data.get('pair')
        direction = data.get('direction')  # 'buy' or 'sell'
        units = data.get('units', 1000)
        stop_loss = data.get('stop_loss')
        take_profit = data.get('take_profit')
        
        if not pair or not direction:
            return jsonify({'success': False, 'error': 'Missing pair or direction'})
        
        # Convert direction to OANDA format
        oanda_direction = 1 if direction.lower() == 'buy' else -1
        
        # Place trade using OANDA API
        api = OandaApi()
        result = api.place_trade(
            pair_name=pair,
            units=units,
            direction=oanda_direction,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        if result and 'orderFillTransaction' in result:
            return jsonify({
                'success': True,
                'trade_id': result['orderFillTransaction']['id'],
                'message': f'Trade placed successfully: {direction.upper()} {units} {pair}'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to place trade'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trade/close/<trade_id>', methods=['POST'])
def close_trade(trade_id):
    """Close an existing trade."""
    try:
        api = OandaApi()
        result = api.close_trade(trade_id)
        
        if result and 'orderFillTransaction' in result:
            return jsonify({
                'success': True,
                'message': f'Trade {trade_id} closed successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to close trade'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trade/open')
def get_open_trades():
    """Get all open trades."""
    try:
        api = OandaApi()
        trades = api.get_open_trades()
        
        if trades and 'trades' in trades:
            return jsonify({'trades': trades['trades']})
        else:
            return jsonify({'trades': []})
            
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/trade/<trade_id>')
def get_trade(trade_id):
    """Get specific trade details."""
    try:
        api = OandaApi()
        trade = api.get_open_trade(trade_id)
        
        if trade:
            return jsonify({'trade': trade})
        else:
            return jsonify({'error': 'Trade not found'})
            
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/positions')
def get_positions():
    """Get all open positions."""
    try:
        api = OandaApi()
        positions = api.get_positions()
        
        if positions and 'positions' in positions:
            return jsonify({'positions': positions['positions']})
        else:
            return jsonify({'positions': []})
            
    except Exception as e:
        return jsonify({'error': str(e)})

# ============================================================================
# COMPREHENSIVE ANALYSIS ENDPOINTS
# ============================================================================

@app.route('/api/analysis/comprehensive/<pair>')
def comprehensive_analysis(pair):
    """Get comprehensive analysis for a specific pair."""
    try:
        if trading_system is None or not trading_system.is_running:
            return jsonify({'error': 'Trading system not running'})
        
        # Get comprehensive analysis from trading system
        analysis = trading_system.get_comprehensive_analysis(pair)
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/analysis/patterns/<pair>')
def pattern_analysis(pair):
    """Get pattern analysis for a specific pair."""
    try:
        # This would integrate with your pattern recognition logic
        # For now, return placeholder data
        patterns = {
            'candlestick_patterns': [],
            'chart_patterns': [],
            'support_resistance': [],
            'trend_analysis': {}
        }
        return jsonify(patterns)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/analysis/risk/<pair>')
def risk_analysis(pair):
    """Get risk analysis for a specific pair."""
    try:
        if trading_system is None:
            return jsonify({'error': 'Trading system not running'})
        
        # Get risk metrics from trading system
        risk_metrics = trading_system.get_risk_analysis(pair)
        return jsonify(risk_metrics)
        
    except Exception as e:
        return jsonify({'error': str(e)})

# ============================================================================
# HEALTH AND UTILITY ENDPOINTS
# ============================================================================

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'system_running': trading_system is not None and trading_system.is_running,
        'version': '1.0.0',
        'features': [
            'unified_trading_system',
            'price_charts',
            'technical_analysis',
            'economic_calendars',
            'comprehensive_analysis'
        ]
    })

if __name__ == '__main__':
    print("🌐 Starting Unified Dashboard Server...")
    print("📊 Access the dashboard at: http://localhost:5001")
    print("🔧 API endpoints available at: http://localhost:5001/api/")
    print("💚 Health check at: http://localhost:5001/health")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=False) 