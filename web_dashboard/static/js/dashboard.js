// Web Trading Dashboard JavaScript

let isSystemRunning = false;
let refreshInterval = null;
let settings = {
    tradingMode: 'hybrid',
    analysisMode: 'adaptive',
    confidenceThreshold: 0.7,
    updateInterval: 60
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    updateTime();
    setInterval(updateTime, 1000);
    loadSettings();
    refreshData();
});

// Update current time
function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString();
}

// Update system status
function updateSystemStatus(running) {
    const systemIndicator = document.getElementById('system-status');
    const systemText = document.getElementById('system-status-text');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    
    if (running) {
        systemIndicator.className = 'status-indicator status-running';
        systemText.textContent = 'System Running';
        startBtn.disabled = true;
        stopBtn.disabled = false;
        isSystemRunning = true;
        
        // Start auto-refresh
        if (refreshInterval) clearInterval(refreshInterval);
        refreshInterval = setInterval(refreshData, settings.updateInterval * 1000);
    } else {
        systemIndicator.className = 'status-indicator status-stopped';
        systemText.textContent = 'System Stopped';
        startBtn.disabled = false;
        stopBtn.disabled = true;
        isSystemRunning = false;
        
        // Stop auto-refresh
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
    }
}

// Start trading system
async function startSystem() {
    try {
        showLoading('start');
        
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateSystemStatus(true);
            showNotification('Trading system started successfully!', 'success');
        } else {
            showNotification('Failed to start system: ' + result.error, 'error');
        }
    } catch (error) {
        showNotification('Error starting system: ' + error.message, 'error');
    } finally {
        hideLoading('start');
    }
}

// Stop trading system
async function stopSystem() {
    try {
        showLoading('stop');
        
        const response = await fetch('/api/stop', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            updateSystemStatus(false);
            showNotification('Trading system stopped successfully!', 'info');
        } else {
            showNotification('Failed to stop system: ' + result.error, 'error');
        }
    } catch (error) {
        showNotification('Error stopping system: ' + error.message, 'error');
    } finally {
        hideLoading('stop');
    }
}

// Refresh data
async function refreshData() {
    try {
        showLoading('refresh');
        
        // Get system status
        const statusResponse = await fetch('/api/status');
        const statusData = await statusResponse.json();
        updateSystemStatus(statusData.is_running);
        
        // Update component statuses
        updateComponentStatus('stream-bot', statusData.stream_bot_running);
        updateComponentStatus('analysis', statusData.analysis_running);
        
        // Get signals
        const signalsResponse = await fetch('/api/signals');
        const signalsData = await signalsResponse.json();
        updateSignals(signalsData.signals);
        
        // Get summary
        const summaryResponse = await fetch('/api/summary');
        const summaryData = await summaryResponse.json();
        updateSummary(summaryData);
        
        // Get performance metrics
        const performanceResponse = await fetch('/api/performance');
        const performanceData = await performanceResponse.json();
        updatePerformance(performanceData);
        
        document.getElementById('last-update').textContent = 
            'Last Update: ' + new Date().toLocaleTimeString();
            
    } catch (error) {
        showNotification('Error refreshing data: ' + error.message, 'error');
    } finally {
        hideLoading('refresh');
    }
}

// Update component status
function updateComponentStatus(component, running) {
    const indicator = document.getElementById(`${component}-status`);
    const text = document.getElementById(`${component}-status-text`);
    
    if (running) {
        indicator.className = 'status-indicator status-running';
        text.textContent = component === 'stream-bot' ? 'Stream Bot' : 'AI Analysis';
    } else {
        indicator.className = 'status-indicator status-stopped';
        text.textContent = component === 'stream-bot' ? 'Stream Bot' : 'AI Analysis';
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
    const highConfSignals = signals.filter(s => s.confidence >= settings.confidenceThreshold).slice(-5).reverse();
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
        document.getElementById('open-trades').textContent = '0';
        document.getElementById('daily-trades').textContent = '0';
        return;
    }
    
    document.getElementById('total-signals').textContent = summary.total_signals || 0;
    document.getElementById('avg-confidence').textContent = 
        ((summary.average_confidence || 0) * 100).toFixed(0) + '%';
    document.getElementById('high-confidence').textContent = summary.high_confidence_signals || 0;
    document.getElementById('active-pairs').textContent = 
        Object.keys(summary.currency_pairs || {}).length;
    document.getElementById('open-trades').textContent = summary.open_trades || 0;
    document.getElementById('daily-trades').textContent = summary.daily_trades || 0;
}

// Update performance metrics
function updatePerformance(performance) {
    const container = document.getElementById('performance-metrics');
    
    if (!performance || performance.message) {
        container.innerHTML = '<p style="opacity: 0.7;">Performance metrics will appear here once the system is running.</p>';
        return;
    }
    
    container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div class="summary-item">
                <div class="summary-value">${performance.win_rate || 0}%</div>
                <div class="summary-label">Win Rate</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">${performance.profit_factor || 0}</div>
                <div class="summary-label">Profit Factor</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">${performance.max_drawdown || 0}%</div>
                <div class="summary-label">Max Drawdown</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">${performance.total_return || 0}%</div>
                <div class="summary-label">Total Return</div>
            </div>
        </div>
    `;
}

// Show settings modal
function showSettings() {
    document.getElementById('settings-modal').style.display = 'block';
    
    // Populate current settings
    document.getElementById('trading-mode').value = settings.tradingMode;
    document.getElementById('analysis-mode').value = settings.analysisMode;
    document.getElementById('confidence-threshold').value = settings.confidenceThreshold;
    document.getElementById('confidence-value').textContent = (settings.confidenceThreshold * 100) + '%';
    document.getElementById('update-interval').value = settings.updateInterval;
}

// Close settings modal
function closeSettings() {
    document.getElementById('settings-modal').style.display = 'none';
}

// Save settings
async function saveSettings() {
    try {
        settings.tradingMode = document.getElementById('trading-mode').value;
        settings.analysisMode = document.getElementById('analysis-mode').value;
        settings.confidenceThreshold = parseFloat(document.getElementById('confidence-threshold').value);
        settings.updateInterval = parseInt(document.getElementById('update-interval').value);
        
        // Save to localStorage
        localStorage.setItem('dashboard-settings', JSON.stringify(settings));
        
        // Update confidence value display
        document.getElementById('confidence-value').textContent = (settings.confidenceThreshold * 100) + '%';
        
        // Update refresh interval if system is running
        if (isSystemRunning && refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = setInterval(refreshData, settings.updateInterval * 1000);
        }
        
        closeSettings();
        showNotification('Settings saved successfully!', 'success');
        
    } catch (error) {
        showNotification('Error saving settings: ' + error.message, 'error');
    }
}

// Load settings from localStorage
function loadSettings() {
    try {
        const saved = localStorage.getItem('dashboard-settings');
        if (saved) {
            settings = { ...settings, ...JSON.parse(saved) };
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Show loading state
function showLoading(button) {
    const btn = document.getElementById(`${button}-btn`);
    const text = document.getElementById(`${button}-btn-text`);
    const loading = document.getElementById(`${button}-loading`);
    
    text.style.display = 'none';
    loading.style.display = 'inline-block';
    btn.disabled = true;
}

// Hide loading state
function hideLoading(button) {
    const btn = document.getElementById(`${button}-btn`);
    const text = document.getElementById(`${button}-btn-text`);
    const loading = document.getElementById(`${button}-loading`);
    
    text.style.display = 'inline';
    loading.style.display = 'none';
    btn.disabled = false;
}

// Show notification
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    // Show notification
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => container.removeChild(notification), 300);
    }, 5000);
}

// Handle confidence threshold slider
document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('confidence-threshold');
    const value = document.getElementById('confidence-value');
    
    if (slider && value) {
        slider.addEventListener('input', function() {
            value.textContent = (this.value * 100) + '%';
        });
    }
});

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('settings-modal');
    if (event.target === modal) {
        closeSettings();
    }
} 