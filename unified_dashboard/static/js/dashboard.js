// Unified Forex Trading Dashboard JavaScript

// Global variables
let priceChart = null;
let updateInterval = null;
let currentTab = 'trading';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Unified Forex Trading Dashboard...');
    
    // Set up initial state
    updateTime();
    loadOptions();
    loadAccountData();
    
    // Start update intervals
    setInterval(updateTime, 1000);
    setInterval(updateStatus, 5000);
    setInterval(refreshData, 30000);
    
    // Initial status check
    updateStatus();
});

// ============================================================================
// TAB NAVIGATION
// ============================================================================

function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    const selectedTab = document.getElementById(tabName + '-tab');
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to selected tab button
    const selectedButton = document.querySelector(`[onclick="showTab('${tabName}')"]`);
    if (selectedButton) {
        selectedButton.classList.add('active');
    }
    
    currentTab = tabName;
    
    // Load data for the selected tab
    switch(tabName) {
        case 'trading':
            updateStatus();
            break;
        case 'charts':
            loadChartData();
            break;
        case 'technicals':
            loadTechnicals();
            break;
        case 'calendars':
            // Calendars are loaded on demand
            break;
        case 'analysis':
            loadComprehensiveAnalysis();
            break;
    }
}

// ============================================================================
// TRADING SYSTEM CONTROL
// ============================================================================

async function startSystem() {
    const startBtn = document.getElementById('start-btn');
    const startText = document.getElementById('start-btn-text');
    const startLoading = document.getElementById('start-loading');
    
    // Show loading state
    startText.style.display = 'none';
    startLoading.style.display = 'inline-block';
    startBtn.disabled = true;
    
    try {
        const settings = await getSettings();
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('System started successfully!', 'success');
            updateStatus();
        } else {
            showNotification('Failed to start system: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error starting system:', error);
        showNotification('Error starting system: ' + error.message, 'error');
    } finally {
        // Reset button state
        startText.style.display = 'inline';
        startLoading.style.display = 'none';
        startBtn.disabled = false;
    }
}

async function stopSystem() {
    const stopBtn = document.getElementById('stop-btn');
    const stopText = document.getElementById('stop-btn-text');
    const stopLoading = document.getElementById('stop-loading');
    
    // Show loading state
    stopText.style.display = 'none';
    stopLoading.style.display = 'inline-block';
    stopBtn.disabled = true;
    
    try {
        const response = await fetch('/api/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('System stopped successfully!', 'success');
            updateStatus();
        } else {
            showNotification('Failed to stop system: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error stopping system:', error);
        showNotification('Error stopping system: ' + error.message, 'error');
    } finally {
        // Reset button state
        stopText.style.display = 'inline';
        stopLoading.style.display = 'none';
        stopBtn.disabled = false;
    }
}

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        // Update status indicators
        const systemStatus = document.getElementById('system-status');
        const systemStatusText = document.getElementById('system-status-text');
        const streamBotStatus = document.getElementById('stream-bot-status');
        const streamBotStatusText = document.getElementById('stream-bot-status-text');
        const analysisStatus = document.getElementById('analysis-status');
        const analysisStatusText = document.getElementById('analysis-status-text');
        
        // System status
        if (status.is_running) {
            systemStatus.className = 'status-indicator status-running';
            systemStatusText.textContent = 'System Running';
        } else {
            systemStatus.className = 'status-indicator status-stopped';
            systemStatusText.textContent = 'System Stopped';
        }
        
        // Stream bot status
        if (status.stream_bot_running) {
            streamBotStatus.className = 'status-indicator status-running';
            streamBotStatusText.textContent = 'Stream Bot Running';
        } else {
            streamBotStatus.className = 'status-indicator status-stopped';
            streamBotStatusText.textContent = 'Stream Bot Stopped';
        }
        
        // Analysis status
        if (status.analysis_running) {
            analysisStatus.className = 'status-indicator status-running';
            analysisStatusText.textContent = 'AI Analysis Running';
        } else {
            analysisStatus.className = 'status-indicator status-stopped';
            analysisStatusText.textContent = 'AI Analysis Stopped';
        }
        
        // Update control buttons
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        
        if (status.is_running) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
        
        // Update last update time
        document.getElementById('last-update').textContent = 'Last Update: ' + new Date().toLocaleTimeString();
        
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

async function refreshData() {
    if (currentTab === 'trading') {
        await updateStatus();
        await loadSummary();
        await loadSignals();
        await loadPerformance();
    }
}

// ============================================================================
// SUMMARY AND SIGNALS
// ============================================================================

async function loadSummary() {
    try {
        const response = await fetch('/api/summary');
        const data = await response.json();
        
        if (data.message) {
            return; // System not running
        }
        
        // Update summary values
        document.getElementById('total-signals').textContent = data.total_signals || 0;
        document.getElementById('avg-confidence').textContent = Math.round((data.average_confidence || 0) * 100) + '%';
        document.getElementById('high-confidence').textContent = data.high_confidence_signals || 0;
        document.getElementById('active-pairs').textContent = Object.keys(data.currency_pairs || {}).length;
        document.getElementById('open-trades').textContent = data.open_trades || 0;
        document.getElementById('daily-trades').textContent = data.daily_trades || 0;
        
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

async function loadSignals() {
    try {
        const response = await fetch('/api/signals');
        const data = await response.json();
        
        const recentSignalsContainer = document.getElementById('recent-signals');
        const highConfidenceContainer = document.getElementById('high-confidence-signals');
        
        if (data.signals && data.signals.length > 0) {
            // Display recent signals
            recentSignalsContainer.innerHTML = data.signals.slice(0, 5).map(signal => createSignalHTML(signal)).join('');
            
            // Display high confidence signals
            const highConfidenceSignals = data.signals.filter(signal => signal.confidence >= 0.8);
            if (highConfidenceSignals.length > 0) {
                highConfidenceContainer.innerHTML = highConfidenceSignals.slice(0, 3).map(signal => createSignalHTML(signal)).join('');
            } else {
                highConfidenceContainer.innerHTML = '<p style="opacity: 0.7;">No high confidence signals yet.</p>';
            }
        } else {
            recentSignalsContainer.innerHTML = '<p style="opacity: 0.7;">No signals yet. Start the system to begin generating signals.</p>';
            highConfidenceContainer.innerHTML = '<p style="opacity: 0.7;">High confidence signals will appear here.</p>';
        }
        
    } catch (error) {
        console.error('Error loading signals:', error);
    }
}

function createSignalHTML(signal) {
    const signalClass = `signal-${signal.signal_type.toLowerCase()}`;
    const confidencePercent = Math.round(signal.confidence * 100);
    
    return `
        <div class="signal-item ${signalClass}">
            <div class="signal-header">
                <span class="signal-type">${signal.signal_type} ${signal.currency_pair}</span>
                <span class="signal-confidence">${confidencePercent}%</span>
            </div>
            <div class="signal-details">
                <div class="signal-price">
                    <div>Entry: ${signal.entry_price}</div>
                </div>
                <div class="signal-price">
                    <div>SL: ${signal.stop_loss}</div>
                </div>
                <div class="signal-price">
                    <div>TP: ${signal.take_profit}</div>
                </div>
            </div>
            <div class="signal-reasoning">${signal.reasoning || 'No reasoning provided'}</div>
        </div>
    `;
}

async function loadPerformance() {
    try {
        const response = await fetch('/api/performance');
        const data = await response.json();
        
        const performanceContainer = document.getElementById('performance-metrics');
        
        if (data.message) {
            performanceContainer.innerHTML = '<p style="opacity: 0.7;">Performance metrics will appear here once the system is running.</p>';
            return;
        }
        
        performanceContainer.innerHTML = `
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-value">${data.win_rate}%</div>
                    <div class="summary-label">Win Rate</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">${data.profit_factor}</div>
                    <div class="summary-label">Profit Factor</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">${data.max_drawdown}%</div>
                    <div class="summary-label">Max Drawdown</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">${data.total_return}%</div>
                    <div class="summary-label">Total Return</div>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading performance:', error);
    }
}

// ============================================================================
// SETTINGS
// ============================================================================

async function getSettings() {
    try {
        const response = await fetch('/api/settings');
        const settings = await response.json();
        
        // Update form values
        document.getElementById('trading-mode').value = settings.trading_mode;
        document.getElementById('analysis-mode').value = settings.analysis_mode;
        document.getElementById('confidence-threshold').value = settings.confidence_threshold;
        document.getElementById('confidence-value').textContent = Math.round(settings.confidence_threshold * 100) + '%';
        document.getElementById('update-interval').value = settings.update_interval;
        
        return settings;
    } catch (error) {
        console.error('Error loading settings:', error);
        return {
            trading_mode: 'hybrid',
            analysis_mode: 'adaptive',
            confidence_threshold: 0.7,
            update_interval: 60
        };
    }
}

function showSettings() {
    getSettings();
    document.getElementById('settings-modal').style.display = 'block';
}

function closeSettings() {
    document.getElementById('settings-modal').style.display = 'none';
}

async function saveSettings() {
    try {
        const settings = {
            trading_mode: document.getElementById('trading-mode').value,
            analysis_mode: document.getElementById('analysis-mode').value,
            confidence_threshold: parseFloat(document.getElementById('confidence-threshold').value),
            update_interval: parseInt(document.getElementById('update-interval').value)
        };
        
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Settings saved successfully!', 'success');
            closeSettings();
        } else {
            showNotification('Failed to save settings: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showNotification('Error saving settings: ' + error.message, 'error');
    }
}

// Update confidence value display
document.getElementById('confidence-threshold').addEventListener('input', function() {
    const value = Math.round(this.value * 100);
    document.getElementById('confidence-value').textContent = value + '%';
});

// ============================================================================
// PRICE CHARTS
// ============================================================================

async function loadOptions() {
    try {
        const response = await fetch('/api/options');
        const options = await response.json();
        
        // Populate selectors
        populateSelector('pair-selector', options.pairs);
        populateSelector('granularity-selector', options.granularities);
        populateSelector('tech-pair-selector', options.pairs);
        populateSelector('tech-granularity-selector', options.granularities);
        populateSelector('analysis-pair-selector', options.pairs);
        
        // Set default values
        if (options.pairs.length > 0) {
            document.getElementById('pair-selector').value = options.pairs[0].value;
            document.getElementById('tech-pair-selector').value = options.pairs[0].value;
            document.getElementById('analysis-pair-selector').value = options.pairs[0].value;
        }
        if (options.granularities.length > 0) {
            document.getElementById('granularity-selector').value = options.granularities[0].value;
            document.getElementById('tech-granularity-selector').value = options.granularities[0].value;
        }
        
    } catch (error) {
        console.error('Error loading options:', error);
    }
}

function populateSelector(selectorId, options) {
    const selector = document.getElementById(selectorId);
    selector.innerHTML = '<option value="">Select...</option>';
    
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.title;
        selector.appendChild(optionElement);
    });
}

async function loadChartData() {
    const pair = document.getElementById('pair-selector').value;
    const granularity = document.getElementById('granularity-selector').value;
    const count = document.getElementById('count-selector').value;
    
    if (!pair || !granularity) {
        showNotification('Please select both pair and granularity', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/prices/${pair}/${granularity}/${count}`);
        const data = await response.json();
        
        if (data.candles && data.candles.length > 0) {
            createPriceChart(data.candles, pair, granularity);
        } else {
            showNotification('No price data available', 'error');
        }
    } catch (error) {
        console.error('Error loading chart data:', error);
        showNotification('Error loading chart data: ' + error.message, 'error');
    }
}

function createPriceChart(candles, pair, granularity) {
    const ctx = document.getElementById('price-chart').getContext('2d');
    
    // Destroy existing chart
    if (priceChart) {
        priceChart.destroy();
    }
    
    // Prepare data
    const labels = candles.map(candle => new Date(candle.time).toLocaleString());
    const prices = candles.map(candle => parseFloat(candle.mid.c));
    
    // Create new chart
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${pair} (${granularity})`,
                data: prices,
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: 'white'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: 'white'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    ticks: {
                        color: 'white'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

async function loadAccountData() {
    try {
        const response = await fetch('/api/account');
        const data = await response.json();
        
        const accountContainer = document.getElementById('account-data');
        
        if (data.account) {
            accountContainer.innerHTML = `
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="summary-value">${data.account.currency}</div>
                        <div class="summary-label">Currency</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">${parseFloat(data.account.balance).toFixed(2)}</div>
                        <div class="summary-label">Balance</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">${parseFloat(data.account.pl).toFixed(2)}</div>
                        <div class="summary-label">P&L</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">${data.account.openTradeCount}</div>
                        <div class="summary-label">Open Trades</div>
                    </div>
                </div>
            `;
        } else {
            accountContainer.innerHTML = '<p style="opacity: 0.7;">Account data not available.</p>';
        }
    } catch (error) {
        console.error('Error loading account data:', error);
    }
}

// ============================================================================
// TECHNICAL ANALYSIS
// ============================================================================

async function loadTechnicals() {
    const pair = document.getElementById('tech-pair-selector').value;
    const granularity = document.getElementById('tech-granularity-selector').value;
    
    if (!pair || !granularity) {
        showNotification('Please select both pair and granularity', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/technicals/${pair}/${granularity}`);
        const data = await response.json();
        
        const technicalsContainer = document.getElementById('technicals-container');
        
        if (data.technicals && data.technicals.length > 0) {
            technicalsContainer.innerHTML = data.technicals.map(tech => `
                <div class="technical-item">
                    <div class="technical-name">${tech.name}</div>
                    <div class="technical-value">${tech.value}</div>
                    <div class="technical-description">${tech.description || 'No description available'}</div>
                </div>
            `).join('');
        } else {
            technicalsContainer.innerHTML = '<p style="opacity: 0.7;">No technical indicators available for this pair/timeframe.</p>';
        }
    } catch (error) {
        console.error('Error loading technicals:', error);
        showNotification('Error loading technicals: ' + error.message, 'error');
    }
}

// ============================================================================
// ECONOMIC CALENDARS
// ============================================================================

async function loadTECalendar() {
    const startDate = document.getElementById('te-start-date').value;
    const endDate = document.getElementById('te-end-date').value;
    
    if (!startDate || !endDate) {
        showNotification('Please select both start and end dates', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/te/calendar/${startDate}/${endDate}`);
        const data = await response.json();
        
        const calendarContainer = document.getElementById('te-calendar-data');
        
        if (data && data.length > 0) {
            calendarContainer.innerHTML = data.map(event => `
                <div class="calendar-item">
                    <div class="calendar-time">${event.time}</div>
                    <div class="calendar-title">${event.title}</div>
                    <div class="calendar-impact">Impact: ${event.impact}</div>
                    <div class="calendar-currency">Currency: ${event.currency}</div>
                </div>
            `).join('');
        } else {
            calendarContainer.innerHTML = '<p style="opacity: 0.7;">No economic events found for the selected date range.</p>';
        }
    } catch (error) {
        console.error('Error loading TE calendar:', error);
        showNotification('Error loading TradingEconomics calendar: ' + error.message, 'error');
    }
}

async function loadFFCalendar() {
    const month = document.getElementById('ff-month').value;
    
    if (!month) {
        showNotification('Please select a month', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/ff/calendar/${month}`);
        const data = await response.json();
        
        const calendarContainer = document.getElementById('ff-calendar-data');
        
        if (data && data.length > 0) {
            calendarContainer.innerHTML = data.map(event => `
                <div class="calendar-item">
                    <div class="calendar-time">${event.time}</div>
                    <div class="calendar-title">${event.title}</div>
                    <div class="calendar-impact">Impact: ${event.impact}</div>
                    <div class="calendar-currency">Currency: ${event.currency}</div>
                </div>
            `).join('');
        } else {
            calendarContainer.innerHTML = '<p style="opacity: 0.7;">No economic events found for the selected month.</p>';
        }
    } catch (error) {
        console.error('Error loading FF calendar:', error);
        showNotification('Error loading ForexFactory calendar: ' + error.message, 'error');
    }
}

// ============================================================================
// COMPREHENSIVE ANALYSIS
// ============================================================================

async function loadComprehensiveAnalysis() {
    const pair = document.getElementById('analysis-pair-selector').value;
    
    if (!pair) {
        showNotification('Please select a currency pair', 'error');
        return;
    }
    
    try {
        // Load comprehensive analysis
        const compResponse = await fetch(`/api/analysis/comprehensive/${pair}`);
        const compData = await compResponse.json();
        
        const compContainer = document.getElementById('comprehensive-analysis');
        if (compData.error) {
            compContainer.innerHTML = '<p style="opacity: 0.7;">Comprehensive analysis not available. Start the trading system first.</p>';
        } else {
            compContainer.innerHTML = `
                <div class="analysis-item">
                    <div class="analysis-title">Analysis Summary</div>
                    <div class="analysis-value">${compData.summary || 'No summary available'}</div>
                    <div class="analysis-description">${compData.description || 'No description available'}</div>
                </div>
            `;
        }
        
        // Load pattern analysis
        const patternResponse = await fetch(`/api/analysis/patterns/${pair}`);
        const patternData = await patternResponse.json();
        
        const patternContainer = document.getElementById('pattern-analysis');
        if (patternData.patterns && patternData.patterns.length > 0) {
            patternContainer.innerHTML = patternData.patterns.map(pattern => `
                <div class="analysis-item">
                    <div class="analysis-title">${pattern.name}</div>
                    <div class="analysis-value">${pattern.value}</div>
                    <div class="analysis-description">${pattern.description}</div>
                </div>
            `).join('');
        } else {
            patternContainer.innerHTML = '<p style="opacity: 0.7;">No patterns detected.</p>';
        }
        
        // Load risk analysis
        const riskResponse = await fetch(`/api/analysis/risk/${pair}`);
        const riskData = await riskResponse.json();
        
        const riskContainer = document.getElementById('risk-analysis');
        if (riskData.error) {
            riskContainer.innerHTML = '<p style="opacity: 0.7;">Risk analysis not available. Start the trading system first.</p>';
        } else {
            riskContainer.innerHTML = `
                <div class="analysis-item">
                    <div class="analysis-title">Risk Level</div>
                    <div class="analysis-value">${riskData.risk_level || 'Unknown'}</div>
                    <div class="analysis-description">${riskData.description || 'No risk description available'}</div>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading analysis:', error);
        showNotification('Error loading analysis: ' + error.message, 'error');
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString();
}

function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Hide and remove notification
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            container.removeChild(notification);
        }, 300);
    }, 5000);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('settings-modal');
    if (event.target === modal) {
        closeSettings();
    }
} 