#!/usr/bin/env python3
"""
Web Dashboard for Real-time Forex Trading Signals

This module provides a web interface to view real-time trading signals
and manage the OpenAI-powered trading analyzer.
"""

import sys
import os
import json
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request
from typing import Dict, List

# Add project root to path
sys.path.append("./")

from analysis.realtime_trading_analyzer import RealtimeTradingAnalyzer

app = Flask(__name__)
analyzer = None
analyzer_thread = None

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Forex Trading Dashboard - OpenAI Powered</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .status-bar {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            margin: 5px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-running {
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        
        .status-stopped {
            background: #f44336;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .controls {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            margin: 0 10px;
            font-size: 16px;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #45a049;
        }
        
        .btn-stop {
            background: #f44336;
        }
        
        .btn-stop:hover {
            background: #da190b;
        }
        
        .signals-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .signals-panel {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .signals-panel h3 {
            margin-bottom: 15px;
            color: #FFD700;
        }
        
        .signal-item {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .signal-buy {
            border-left-color: #4CAF50;
        }
        
        .signal-sell {
            border-left-color: #f44336;
        }
        
        .signal-hold {
            border-left-color: #FF9800;
        }
        
        .signal-exit {
            border-left-color: #9C27B0;
        }
        
        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .signal-type {
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .signal-confidence {
            background: rgba(255,255,255,0.2);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        .signal-details {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            font-size: 0.9em;
        }
        
        .signal-price {
            text-align: center;
        }
        
        .signal-reasoning {
            margin-top: 10px;
            font-size: 0.85em;
            opacity: 0.8;
        }
        
        .summary-panel {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .summary-item {
            text-align: center;
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 8px;
        }
        
        .summary-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #FFD700;
        }
        
        .summary-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            opacity: 0.7;
        }
        
        @media (max-width: 768px) {
            .signals-container {
                grid-template-columns: 1fr;
            }
            
            .signal-details {
                grid-template-columns: 1fr;
                gap: 5px;
            }
            
            .status-bar {
                flex-direction: column;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI-Powered Forex Trading Dashboard</h1>
            <p>Real-time minute-based analysis with OpenAI predictions</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator" id="analyzer-status"></div>
                <span id="analyzer-status-text">Analyzer Status</span>
            </div>
            <div class="status-item">
                <span id="current-time">--:--:--</span>
            </div>
            <div class="status-item">
                <span id="last-update">Last Update: --</span>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="startAnalyzer()">Start Analyzer</button>
            <button class="btn btn-stop" onclick="stopAnalyzer()">Stop Analyzer</button>
            <button class="btn" onclick="refreshData()">Refresh Data</button>
        </div>
        
        <div class="summary-panel">
            <h3>📊 Session Summary</h3>
            <div class="summary-grid" id="summary-grid">
                <div class="summary-item">
                    <div class="summary-value" id="total-signals">0</div>
                    <div class="summary-label">Total Signals</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value" id="avg-confidence">0%</div>
                    <div class="summary-label">Avg Confidence</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value" id="high-confidence">0</div>
                    <div class="summary-label">High Confidence</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value" id="active-pairs">0</div>
                    <div class="summary-label">Active Pairs</div>
                </div>
            </div>
        </div>
        
        <div class="signals-container">
            <div class="signals-panel">
                <h3>🔄 Recent Signals</h3>
                <div id="recent-signals">
                    <p style="opacity: 0.7;">No signals yet. Start the analyzer to begin generating signals.</p>
                </div>
            </div>
            
            <div class="signals-panel">
                <h3>⚡ High Confidence Signals</h3>
                <div id="high-confidence-signals">
                    <p style="opacity: 0.7;">High confidence signals will appear here.</p>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Powered by OpenAI GPT-4 | Real-time Forex Analysis</p>
            <p style="font-size: 0.8em; margin-top: 5px;">⚠️ AI predictions are for informational purposes only. Always conduct your own analysis.</p>
        </div>
    </div>

    <script>
        let isAnalyzerRunning = false;
        
        // Update current time
        function updateTime() {
            const now = new Date();
            document.getElementById('current-time').textContent = now.toLocaleTimeString();
        }
        
        // Update analyzer status
        function updateStatus(running) {
            const statusIndicator = document.getElementById('analyzer-status');
            const statusText = document.getElementById('analyzer-status-text');
            
            if (running) {
                statusIndicator.className = 'status-indicator status-running';
                statusText.textContent = 'Analyzer Running';
            } else {
                statusIndicator.className = 'status-indicator status-stopped';
                statusText.textContent = 'Analyzer Stopped';
            }
            
            isAnalyzerRunning = running;
        }
        
        // Start analyzer
        async function startAnalyzer() {
            try {
                const response = await fetch('/api/start', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    updateStatus(true);
                    showNotification('Analyzer started successfully!', 'success');
                } else {
                    showNotification('Failed to start analyzer: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('Error starting analyzer: ' + error.message, 'error');
            }
        }
        
        // Stop analyzer
        async function stopAnalyzer() {
            try {
                const response = await fetch('/api/stop', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    updateStatus(false);
                    showNotification('Analyzer stopped successfully!', 'info');
                } else {
                    showNotification('Failed to stop analyzer: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('Error stopping analyzer: ' + error.message, 'error');
            }
        }
        
        // Refresh data
        async function refreshData() {
            try {
                // Get analyzer status
                const statusResponse = await fetch('/api/status');
                const statusData = await statusResponse.json();
                updateStatus(statusData.running);
                
                // Get signals
                const signalsResponse = await fetch('/api/signals');
                const signalsData = await signalsResponse.json();
                updateSignals(signalsData.signals);
                
                // Get summary
                const summaryResponse = await fetch('/api/summary');
                const summaryData = await summaryResponse.json();
                updateSummary(summaryData);
                
                document.getElementById('last-update').textContent = 
                    'Last Update: ' + new Date().toLocaleTimeString();
                    
            } catch (error) {
                showNotification('Error refreshing data: ' + error.message, 'error');
            }
        }
        
        // Update signals display
        function updateSignals(signals) {
            const recentContainer = document.getElementById('recent-signals');
            const highConfidenceContainer = document.getElementById('high-confidence-signals');
            
            if (!signals || signals.length === 0) {
                recentContainer.innerHTML = '<p style="opacity: 0.7;">No signals yet.</p>';
                highConfidenceContainer.innerHTML = '<p style="opacity: 0.7;">No high confidence signals yet.</p>';
                return;
            }
            
            // Recent signals (last 5)
            const recentSignals = signals.slice(-5).reverse();
            recentContainer.innerHTML = recentSignals.map(signal => createSignalHTML(signal)).join('');
            
            // High confidence signals
            const highConfSignals = signals.filter(s => s.confidence >= 0.8).slice(-5).reverse();
            if (highConfSignals.length > 0) {
                highConfidenceContainer.innerHTML = highConfSignals.map(signal => createSignalHTML(signal)).join('');
            } else {
                highConfidenceContainer.innerHTML = '<p style="opacity: 0.7;">No high confidence signals yet.</p>';
            }
        }
        
        // Create HTML for a signal
        function createSignalHTML(signal) {
            const timestamp = new Date(signal.timestamp).toLocaleTimeString();
            const signalClass = 'signal-' + signal.signal_type.toLowerCase();
            const emoji = {
                'BUY': '🟢',
                'SELL': '🔴',
                'HOLD': '🟡',
                'EXIT': '🚪'
            }[signal.signal_type] || '❓';
            
            return `
                <div class="signal-item ${signalClass}">
                    <div class="signal-header">
                        <div class="signal-type">${emoji} ${signal.currency_pair} - ${signal.signal_type}</div>
                        <div class="signal-confidence">${(signal.confidence * 100).toFixed(0)}%</div>
                    </div>
                    <div class="signal-details">
                        <div class="signal-price">
                            <strong>Entry:</strong><br>${signal.entry_price.toFixed(5)}
                        </div>
                        <div class="signal-price">
                            <strong>Stop Loss:</strong><br>${signal.stop_loss.toFixed(5)}
                        </div>
                        <div class="signal-price">
                            <strong>Take Profit:</strong><br>${signal.take_profit.toFixed(5)}
                        </div>
                    </div>
                    <div class="signal-reasoning">
                        <strong>Risk:</strong> ${signal.risk_level} | 
                        <strong>Time:</strong> ${timestamp}<br>
                        ${signal.reasoning.substring(0, 150)}...
                    </div>
                </div>
            `;
        }
        
        // Update summary
        function updateSummary(summary) {
            if (summary.message) {
                // No signals yet
                document.getElementById('total-signals').textContent = '0';
                document.getElementById('avg-confidence').textContent = '0%';
                document.getElementById('high-confidence').textContent = '0';
                document.getElementById('active-pairs').textContent = '0';
                return;
            }
            
            document.getElementById('total-signals').textContent = summary.total_signals || 0;
            document.getElementById('avg-confidence').textContent = 
                ((summary.average_confidence || 0) * 100).toFixed(0) + '%';
            document.getElementById('high-confidence').textContent = summary.high_confidence_signals || 0;
            document.getElementById('active-pairs').textContent = 
                Object.keys(summary.currency_pairs || {}).length;
        }
        
        // Show notification (simple implementation)
        function showNotification(message, type) {
            // For now, just use alert. In production, use a proper notification system
            console.log(`${type.toUpperCase()}: ${message}`);
        }
        
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            updateTime();
            setInterval(updateTime, 1000);
            refreshData();
            setInterval(refreshData, 5000); // Auto-refresh every 5 seconds
        });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Serve the main dashboard."""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def get_status():
    """Get analyzer status."""
    global analyzer
    return jsonify({
        'running': analyzer is not None and analyzer.is_running,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/start', methods=['POST'])
def start_analyzer():
    """Start the real-time analyzer."""
    global analyzer, analyzer_thread
    
    try:
        if analyzer is not None and analyzer.is_running:
            return jsonify({'success': False, 'error': 'Analyzer is already running'})
        
        # Initialize analyzer
        analyzer = RealtimeTradingAnalyzer()
        
        # Start analyzer thread
        analyzer_thread = analyzer.start_realtime_analysis(['EUR_USD', 'GBP_USD', 'USD_JPY'])
        
        return jsonify({'success': True, 'message': 'Analyzer started successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_analyzer():
    """Stop the real-time analyzer."""
    global analyzer
    
    try:
        if analyzer is None or not analyzer.is_running:
            return jsonify({'success': False, 'error': 'Analyzer is not running'})
        
        analyzer.stop_realtime_analysis()
        
        return jsonify({'success': True, 'message': 'Analyzer stopped successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/signals')
def get_signals():
    """Get current trading signals."""
    global analyzer
    
    try:
        if analyzer is None:
            return jsonify({'signals': []})
        
        signals = analyzer.get_current_signals()
        
        # Convert signals to dict format
        signals_data = []
        for signal in signals:
            signals_data.append({
                'timestamp': signal.timestamp,
                'currency_pair': signal.currency_pair,
                'signal_type': signal.signal_type,
                'confidence': signal.confidence,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'reasoning': signal.reasoning,
                'market_conditions': signal.market_conditions,
                'risk_level': signal.risk_level
            })
        
        return jsonify({'signals': signals_data})
        
    except Exception as e:
        return jsonify({'signals': [], 'error': str(e)})

@app.route('/api/summary')
def get_summary():
    """Get trading signals summary."""
    global analyzer
    
    try:
        if analyzer is None:
            return jsonify({'message': 'Analyzer not initialized'})
        
        summary = analyzer.get_signal_summary()
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting Forex Trading Dashboard...")
    print("📊 Access the dashboard at: http://localhost:5001")
    print("🤖 Make sure your OpenAI API key is set!")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=False)