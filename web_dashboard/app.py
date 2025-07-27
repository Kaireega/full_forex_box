#!/usr/bin/env python3
"""
Web Dashboard Server for Unified Trading System

This Flask application serves the web dashboard and provides API endpoints
for controlling the unified trading system.
"""

import sys
import os
import json
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from typing import Dict, Optional

# Add project root to path
sys.path.append("../")

from analysis.unified_trading_system import UnifiedTradingSystem, TradingMode
from analysis.unified_trading_analyzer import AnalysisMode

app = Flask(__name__)

# Global trading system instance
trading_system = None
system_thread = None

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
    """Serve the main dashboard."""
    return render_template('dashboard.html')

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

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'system_running': trading_system is not None and trading_system.is_running
    })

if __name__ == '__main__':
    print("🌐 Starting Web Dashboard Server...")
    print("📊 Access the dashboard at: http://localhost:5001")
    print("🔧 API endpoints available at: http://localhost:5001/api/")
    print("💚 Health check at: http://localhost:5001/health")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=False) 