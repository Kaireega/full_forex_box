// Comprehensive Forex Trading Dashboard JavaScript

// Global variables
let priceChart = null;
let currentPair = 'EUR_USD';
let currentGranularity = 'H1';
let currentCount = 100;
let updateInterval = null;
let systemRunning = false;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    updateTime();
    setInterval(updateTime, 1000);
    setInterval(loadAccountData, 60000); // Update account data every minute
});

// Initialize dashboard
function initializeDashboard() {
    loadSystemStatus();
    loadAccountData();
    setDefaultDates();
    showNotification('Dashboard loaded successfully!', 'success');
}

// Update current time
function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString();
}

// Tab navigation
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab content
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load specific data based on tab
    switch(tabName) {
        case 'charts':
            loadChartData();
            break;
        case 'technicals':
            loadTechnicalData();
            break;
        case 'calendars':
            setDefaultDates();
            break;
        case 'analysis':
            loadComprehensiveAnalysis();
            break;
        case 'trades':
            loadTradeData();
            break;
        case 'alerts':
            loadTradeAlerts();
            break;
        case 'account':
            loadAccountData();
            break;
    }
}

// ============================================================================
// SYSTEM CONTROL FUNCTIONS
// ============================================================================

async function startSystem() {
    const startBtn = document.getElementById('start-btn');
    const startText = document.getElementById('start-btn-text');
    const startLoading = document.getElementById('start-loading');
    
    startText.style.display = 'none';
    startLoading.style.display = 'inline-block';
    startBtn.disabled = true;
    
    try {
        // Call the backend to start all systems
        const response = await fetch('/api/system/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            systemRunning = true;
            document.getElementById('stop-btn').disabled = false;
            startBtn.disabled = true;
            
            // Immediately refresh system status to show updated indicators
            await loadSystemStatus();
            startDataUpdates();
            
            showNotification('All systems started successfully!', 'success');
        } else {
            throw new Error(result.message || 'Failed to start systems');
        }
    } catch (error) {
        showNotification('Failed to start system: ' + error.message, 'error');
    } finally {
        startText.style.display = 'inline';
        startLoading.style.display = 'none';
    }
}

async function stopSystem() {
    const stopBtn = document.getElementById('stop-btn');
    const stopText = document.getElementById('stop-btn-text');
    const stopLoading = document.getElementById('stop-loading');
    
    stopText.style.display = 'none';
    stopLoading.style.display = 'inline-block';
    stopBtn.disabled = true;
    
    try {
        // Call the backend to stop all systems
        const response = await fetch('/api/system/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            systemRunning = false;
            document.getElementById('start-btn').disabled = false;
            stopBtn.disabled = true;
            
            updateSystemStatus(false);
            stopDataUpdates();
            
            showNotification('All systems stopped successfully!', 'info');
        } else {
            throw new Error(result.message || 'Failed to stop systems');
        }
    } catch (error) {
        showNotification('Failed to stop system: ' + error.message, 'error');
    } finally {
        stopText.style.display = 'inline';
        stopLoading.style.display = 'none';
    }
}

function refreshData() {
    const refreshBtn = document.getElementById('refresh-btn');
    const refreshText = document.getElementById('refresh-btn-text');
    const refreshLoading = document.getElementById('refresh-loading');
    
    refreshText.style.display = 'none';
    refreshLoading.style.display = 'inline-block';
    
    Promise.all([
        loadSystemStatus(),
        loadAccountData(),
        loadChartData(),
        loadTechnicalData()
    ]).then(() => {
        showNotification('Data refreshed successfully!', 'success');
    }).catch(error => {
        showNotification('Failed to refresh data: ' + error.message, 'error');
    }).finally(() => {
        refreshText.style.display = 'inline';
        refreshLoading.style.display = 'none';
    });
}

function startDataUpdates() {
    if (updateInterval) clearInterval(updateInterval);
    updateInterval = setInterval(() => {
        // Always refresh system status to show current state
        loadSystemStatus();
        if (systemRunning) {
            loadAccountData();
            updateSummaryData();
        }
    }, 5000); // Update every 5 seconds
}

function stopDataUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

// ============================================================================
// SYSTEM STATUS FUNCTIONS
// ============================================================================

async function loadSystemStatus() {
    try {
        const response = await fetch('/api/system/status');
        const status = await response.json();
        
        updateSystemStatus(status.running);
        updateStatusIndicators(status);
        
        return status;
    } catch (error) {
        console.error('Error loading system status:', error);
        updateSystemStatus(false);
    }
}

function updateSystemStatus(running) {
    systemRunning = running;
    const statusIndicator = document.getElementById('system-status');
    const statusText = document.getElementById('system-status-text');
    
    if (running) {
        statusIndicator.className = 'status-indicator status-running';
        statusText.textContent = 'System Running';
    } else {
        statusIndicator.className = 'status-indicator status-stopped';
        statusText.textContent = 'System Stopped';
    }
}

function updateStatusIndicators(status) {
    // Update stream bot status
    const streamBotIndicator = document.getElementById('stream-bot-status');
    const streamBotText = document.getElementById('stream-bot-status-text');
    
    if (status.stream_bot) {
        streamBotIndicator.className = 'status-indicator status-running';
        streamBotText.textContent = 'Stream Bot Running';
    } else {
        streamBotIndicator.className = 'status-indicator status-stopped';
        streamBotText.textContent = 'Stream Bot Stopped';
    }
    
    // Update AI analysis status
    const analysisIndicator = document.getElementById('analysis-status');
    const analysisText = document.getElementById('analysis-status-text');
    
    if (status.ai_analysis) {
        analysisIndicator.className = 'status-indicator status-running';
        analysisText.textContent = 'AI Analysis Running';
    } else {
        analysisIndicator.className = 'status-indicator status-stopped';
        analysisText.textContent = 'AI Analysis Stopped';
    }
    
    // Update data streaming status
    const dataStreamingIndicator = document.getElementById('data-streaming-status');
    const dataStreamingText = document.getElementById('data-streaming-status-text');
    
    if (status.data_streaming) {
        dataStreamingIndicator.className = 'status-indicator status-running';
        dataStreamingText.textContent = 'Data Streaming';
    } else {
        dataStreamingIndicator.className = 'status-indicator status-stopped';
        dataStreamingText.textContent = 'Data Stopped';
    }
    
    // Update last update time
    document.getElementById('last-update').textContent = 'Last Update: ' + new Date().toLocaleTimeString();
}

// ============================================================================
// CHART FUNCTIONS
// ============================================================================

async function loadChartData() {
    const pair = document.getElementById('pair-selector').value;
    const granularity = document.getElementById('granularity-selector').value;
    const count = document.getElementById('count-selector').value;
    
    currentPair = pair;
    currentGranularity = granularity;
    currentCount = parseInt(count);
    
    try {
        const response = await fetch(`/api/prices/${pair}/${granularity}/${count}`);
        const data = await response.json();
        
        if (data && data.candles) {
            createPriceChart(data.candles);
            updateChartInfo(data.candles);
        } else {
            showNotification('No price data available', 'error');
        }
    } catch (error) {
        console.error('Error loading chart data:', error);
        showNotification('Failed to load chart data', 'error');
    }
}

function createPriceChart(candles) {
    const ctx = document.getElementById('price-chart').getContext('2d');
    
    // Destroy existing chart
    if (priceChart) {
        priceChart.destroy();
    }
    
    const chartType = document.getElementById('chart-type').value;
    
    const chartData = {
        labels: candles.map(candle => new Date(candle.time)),
        datasets: [{
            label: currentPair,
            data: candles.map(candle => ({
                x: new Date(candle.time),
                o: parseFloat(candle.mid.o),
                h: parseFloat(candle.mid.h),
                l: parseFloat(candle.mid.l),
                c: parseFloat(candle.mid.c)
            })),
            borderColor: '#4ade80',
            backgroundColor: 'rgba(74, 222, 128, 0.1)',
            borderWidth: 1
        }]
    };
    
    const config = {
        type: chartType === 'candlestick' ? 'candlestick' : chartType,
        data: chartData,
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
                    type: 'time',
                    time: {
                        unit: getTimeUnit(currentGranularity)
                    },
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
    };
    
    priceChart = new Chart(ctx, config);
}

function updateChartType() {
    if (priceChart) {
        loadChartData();
    }
}

function getTimeUnit(granularity) {
    switch(granularity) {
        case 'M1': return 'minute';
        case 'M5': return 'minute';
        case 'M15': return 'minute';
        case 'M30': return 'minute';
        case 'H1': return 'hour';
        case 'H4': return 'hour';
        case 'D': return 'day';
        default: return 'hour';
    }
}

function updateChartInfo(candles) {
    if (candles.length === 0) return;
    
    const latest = candles[candles.length - 1];
    const previous = candles[candles.length - 2];
    
    const currentPrice = parseFloat(latest.mid.c);
    const previousPrice = parseFloat(previous.mid.c);
    const change = currentPrice - previousPrice;
    const changePercent = (change / previousPrice) * 100;
    
    const high = Math.max(...candles.map(c => parseFloat(c.mid.h)));
    const low = Math.min(...candles.map(c => parseFloat(c.mid.l)));
    
    document.getElementById('current-price').textContent = currentPrice.toFixed(5);
    document.getElementById('price-change').textContent = `${change >= 0 ? '+' : ''}${change.toFixed(5)} (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)`;
    document.getElementById('price-change').style.color = change >= 0 ? '#4ade80' : '#f44336';
    document.getElementById('price-high').textContent = high.toFixed(5);
    document.getElementById('price-low').textContent = low.toFixed(5);
}

// ============================================================================
// TECHNICAL ANALYSIS FUNCTIONS
// ============================================================================

async function loadTechnicalData() {
    const pair = document.getElementById('tech-pair-selector').value;
    const granularity = document.getElementById('tech-granularity-selector').value;
    
    try {
        // Load technical indicators
        const techResponse = await fetch(`/api/technicals/${pair}/${granularity}`);
        const techData = await techResponse.json();
        
        if (techData.error) {
            throw new Error(techData.error);
        }
        
        displayTechnicalIndicators(techData);
        
        // Load candlestick patterns
        const patternResponse = await fetch(`/api/patterns/${pair}/${granularity}`);
        const patternData = await patternResponse.json();
        
        if (patternData.error) {
            throw new Error(patternData.error);
        }
        
        displayCandlestickPatterns(patternData);
        
    } catch (error) {
        console.error('Error loading technical data:', error);
        showNotification('Failed to load technical data', 'error');
    }
}

function displayTechnicalIndicators(data) {
    const container = document.getElementById('technical-indicators');
    
    const indicators = [
        { name: 'RSI', value: data.rsi, color: data.rsi < 30 ? '#4ade80' : data.rsi > 70 ? '#f44336' : '#ff9800' },
        { name: 'MACD', value: data.macd, color: '#60a5fa' },
        { name: 'MACD Signal', value: data.macd_signal, color: '#60a5fa' },
        { name: 'EMA 20', value: data.ema_20, color: '#4ade80' },
        { name: 'EMA 50', value: data.ema_50, color: '#ff9800' },
        { name: 'EMA 200', value: data.ema_200, color: '#9c27b0' },
        { name: 'SMA 20', value: data.sma_20, color: '#4ade80' },
        { name: 'SMA 50', value: data.sma_50, color: '#ff9800' },
        { name: 'Bollinger Upper', value: data.bollinger_upper, color: '#f44336' },
        { name: 'Bollinger Lower', value: data.bollinger_lower, color: '#4ade80' },
        { name: 'Stochastic K', value: data.stoch_k, color: '#60a5fa' },
        { name: 'Stochastic D', value: data.stoch_d, color: '#ff9800' },
        { name: 'ATR', value: data.atr, color: '#9c27b0' },
        { name: 'ADX', value: data.adx, color: '#e91e63' }
    ];
    
    container.innerHTML = indicators.map(indicator => `
        <div class="indicator-item">
            <span class="indicator-name">${indicator.name}:</span>
            <span class="indicator-value" style="color: ${indicator.color}">${indicator.value}</span>
        </div>
    `).join('');
}

function displayCandlestickPatterns(data) {
    const container = document.getElementById('candlestick-patterns');
    
    const patterns = [
        { name: 'Doji', detected: data.doji },
        { name: 'Hammer', detected: data.hammer },
        { name: 'Shooting Star', detected: data.shooting_star },
        { name: 'Bullish Engulfing', detected: data.engulfing_bullish },
        { name: 'Bearish Engulfing', detected: data.engulfing_bearish },
        { name: 'Morning Star', detected: data.morning_star },
        { name: 'Evening Star', detected: data.evening_star },
        { name: 'Three White Soldiers', detected: data.three_white_soldiers },
        { name: 'Three Black Crows', detected: data.three_black_crows }
    ];
    
    container.innerHTML = patterns.map(pattern => `
        <div class="pattern-item">
            <span class="pattern-name">${pattern.name}:</span>
            <span class="pattern-status ${pattern.detected ? 'detected' : 'not-detected'}">
                ${pattern.detected ? '✅ Detected' : '❌ Not Detected'}
            </span>
        </div>
    `).join('');
}

// ============================================================================
// CALENDAR FUNCTIONS
// ============================================================================

function setDefaultDates() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    document.getElementById('te-start-date').value = today.toISOString().split('T')[0];
    document.getElementById('te-end-date').value = tomorrow.toISOString().split('T')[0];
    
    document.getElementById('ff-month').value = today.toISOString().slice(0, 7);
}

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
        
        displayTECalendar(data);
    } catch (error) {
        console.error('Error loading TE calendar:', error);
        showNotification('Failed to load TradingEconomics calendar', 'error');
    }
}

function displayTECalendar(data) {
    const container = document.getElementById('te-calendar-data');
    
    if (!data || data.length === 0) {
        container.innerHTML = '<p style="opacity: 0.7;">No calendar events found for the selected dates.</p>';
        return;
    }
    
    container.innerHTML = data.map(event => `
        <div class="calendar-item">
            <div class="calendar-time">${event.time || event.date || 'N/A'}</div>
            <div class="calendar-title">${event.event}</div>
            <div class="calendar-impact ${event.impact?.toLowerCase() || 'low'}">${event.impact || 'Low'}</div>
            <div class="calendar-currency">${event.currency}</div>
            ${event.actual || event.forecast ? `
                <div class="calendar-data">
                    <span>Actual: ${event.actual || 'N/A'}</span>
                    <span>Forecast: ${event.forecast || 'N/A'}</span>
                    <span>Previous: ${event.previous || 'N/A'}</span>
                </div>
            ` : ''}
        </div>
    `).join('');
}

async function loadFFCalendar() {
    const monthInput = document.getElementById('ff-month').value;
    
    if (!monthInput) {
        showNotification('Please select a month', 'error');
        return;
    }
    
    try {
        const months = ["Jan.", "Feb.", "Mar.", "Apr.", "May.", "Jun.", "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."];
        const [year, month] = monthInput.split("-");
        const monthIndex = parseInt(month, 10) - 1;
        const formattedMonth = `${months[monthIndex]}${year}`;
        
        const response = await fetch(`/api/ff/calendar/${formattedMonth}`);
        const data = await response.json();
        
        displayFFCalendar(data);
    } catch (error) {
        console.error('Error loading FF calendar:', error);
        showNotification('Failed to load ForexFactory calendar', 'error');
    }
}

function displayFFCalendar(data) {
    const container = document.getElementById('ff-calendar-data');
    
    if (!data || data.length === 0) {
        container.innerHTML = '<p style="opacity: 0.7;">No calendar events found for the selected month.</p>';
        return;
    }
    
    container.innerHTML = data.map(event => `
        <div class="calendar-item">
            <div class="calendar-time">${event.time || event.date || 'N/A'}</div>
            <div class="calendar-title">${event.event}</div>
            <div class="calendar-impact ${event.impact?.toLowerCase() || 'low'}">${event.impact || 'Low'}</div>
            <div class="calendar-currency">${event.currency}</div>
            ${event.actual || event.forecast ? `
                <div class="calendar-data">
                    <span>Actual: ${event.actual || 'N/A'}</span>
                    <span>Forecast: ${event.forecast || 'N/A'}</span>
                    <span>Previous: ${event.previous || 'N/A'}</span>
                </div>
            ` : ''}
        </div>
    `).join('');
}

// ============================================================================
// COMPREHENSIVE ANALYSIS FUNCTIONS
// ============================================================================

async function loadComprehensiveAnalysis() {
    const pair = document.getElementById('analysis-pair-selector').value;
    
    try {
        const response = await fetch(`/api/analysis/${pair}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayTechnicalAnalysis(data.technical);
        displayPriceAction(data.price_action);
        displayTradingRecommendation(data.recommendation, data);
        
    } catch (error) {
        console.error('Error loading comprehensive analysis:', error);
        showNotification('Failed to load comprehensive analysis', 'error');
    }
}

function displayTechnicalAnalysis(technical) {
    const container = document.getElementById('technical-analysis');
    
    container.innerHTML = `
        <div class="analysis-item">
            <div class="analysis-label">Trend:</div>
            <div class="analysis-value ${technical.trend}">${technical.trend.toUpperCase()}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">RSI:</div>
            <div class="analysis-value ${technical.rsi_signal}">${technical.rsi} (${technical.rsi_signal})</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">MACD Signal:</div>
            <div class="analysis-value ${technical.macd_signal}">${technical.macd_signal.toUpperCase()}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Support:</div>
            <div class="analysis-value">${technical.support}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Resistance:</div>
            <div class="analysis-value">${technical.resistance}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Volatility (ATR):</div>
            <div class="analysis-value">${technical.volatility}</div>
        </div>
    `;
}

function displayPriceAction(priceAction) {
    const container = document.getElementById('price-action-analysis');
    
    container.innerHTML = `
        <div class="analysis-item">
            <div class="analysis-label">Price Change:</div>
            <div class="analysis-value ${priceAction.direction}">${priceAction.change_percent >= 0 ? '+' : ''}${priceAction.change_percent}%</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Direction:</div>
            <div class="analysis-value ${priceAction.direction}">${priceAction.direction.toUpperCase()}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Body Size:</div>
            <div class="analysis-value">${priceAction.body_size.toFixed(5)}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Wick Size:</div>
            <div class="analysis-value">${priceAction.wick_size.toFixed(5)}</div>
        </div>
    `;
}

function displayTradingRecommendation(recommendation, data) {
    const container = document.getElementById('trading-recommendation');
    
    const recommendationClass = recommendation === 'BUY' ? 'buy' : recommendation === 'SELL' ? 'sell' : 'hold';
    
    container.innerHTML = `
        <div class="recommendation-main">
            <div class="recommendation-signal ${recommendationClass}">${recommendation}</div>
            <div class="recommendation-confidence">High Confidence</div>
        </div>
        <div class="recommendation-details">
            <div class="analysis-item">
                <div class="analysis-label">Patterns Detected:</div>
                <div class="analysis-value">${data.patterns.length > 0 ? data.patterns.join(', ') : 'None'}</div>
            </div>
            <div class="analysis-item">
                <div class="analysis-label">Analysis Time:</div>
                <div class="analysis-value">${new Date(data.timestamp).toLocaleString()}</div>
            </div>
        </div>
    `;
}

// ============================================================================
// TRADE EXECUTION FUNCTIONS
// ============================================================================

function loadTradeData() {
    populateTradePairSelector();
    loadOpenTrades();
    loadPositions();
}

function populateTradePairSelector() {
    const selector = document.getElementById('trade-pair');
    if (selector.children.length <= 1) {
        const pairs = [
            "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD",
            "USD_CAD", "NZD_USD", "EUR_GBP", "EUR_JPY", "GBP_JPY"
        ];
        
        pairs.forEach(pair => {
            const option = document.createElement('option');
            option.value = pair;
            option.textContent = pair.replace('_', '/');
            selector.appendChild(option);
        });
    }
}

// Trade form submission
document.getElementById('place-trade-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        pair: document.getElementById('trade-pair').value,
        direction: document.getElementById('trade-direction').value,
        units: parseInt(document.getElementById('trade-units').value),
        stop_loss: document.getElementById('trade-stop-loss').value || null,
        take_profit: document.getElementById('trade-take-profit').value || null
    };
    
    try {
        const response = await fetch('/api/trade/place', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Trade placed successfully!', 'success');
            document.getElementById('place-trade-form').reset();
            loadOpenTrades();
            loadAccountData();
        } else {
            showNotification('Failed to place trade: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error placing trade:', error);
        showNotification('Failed to place trade', 'error');
    }
});

async function loadOpenTrades() {
    try {
        const response = await fetch('/api/trade/open');
        const result = await response.json();
        
        const container = document.getElementById('open-trades-list');
        
        if (!result.success) {
            container.innerHTML = '<p style="opacity: 0.7;">Failed to load open trades.</p>';
            return;
        }
        
        if (!result.trades || result.trades.length === 0) {
            container.innerHTML = '<p style="opacity: 0.7;">No open trades found.</p>';
            return;
        }
        
        container.innerHTML = result.trades.map(trade => `
            <div class="trade-item">
                <div class="trade-info">
                    <div class="trade-pair">${trade.instrument}</div>
                    <div class="trade-direction ${trade.currentUnits > 0 ? 'buy' : 'sell'}">
                        ${trade.currentUnits > 0 ? 'BUY' : 'SELL'} ${Math.abs(trade.currentUnits)} units
                    </div>
                    <div class="trade-price">Entry: ${trade.price}</div>
                    <div class="trade-unrealized-pl ${trade.unrealizedPL >= 0 ? 'positive' : 'negative'}">
                        P&L: ${trade.unrealizedPL}
                    </div>
                </div>
                <button class="close-trade-btn" onclick="closeTrade('${trade.id}')">Close</button>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading open trades:', error);
        document.getElementById('open-trades-list').innerHTML = '<p style="opacity: 0.7;">Failed to load open trades.</p>';
    }
}

async function loadPositions() {
    try {
        const response = await fetch('/api/positions');
        const result = await response.json();
        
        const container = document.getElementById('positions-list');
        
        if (!result.success) {
            container.innerHTML = '<p style="opacity: 0.7;">Failed to load positions.</p>';
            return;
        }
        
        if (!result.positions || result.positions.length === 0) {
            container.innerHTML = '<p style="opacity: 0.7;">No positions found.</p>';
            return;
        }
        
        container.innerHTML = result.positions.map(position => `
            <div class="trade-item">
                <div class="trade-info">
                    <div class="trade-pair">${position.instrument}</div>
                    <div class="trade-direction ${position.long.units > 0 ? 'buy' : 'sell'}">
                        ${position.long.units > 0 ? 'LONG' : 'SHORT'} ${Math.abs(position.long.units || position.short.units)} units
                    </div>
                    <div class="trade-price">Avg Price: ${position.long.averagePrice || position.short.averagePrice}</div>
                    <div class="trade-unrealized-pl ${position.unrealizedPL >= 0 ? 'positive' : 'negative'}">
                        P&L: ${position.unrealizedPL}
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading positions:', error);
        document.getElementById('positions-list').innerHTML = '<p style="opacity: 0.7;">Failed to load positions.</p>';
    }
}

async function closeTrade(tradeId) {
    try {
        const response = await fetch(`/api/trade/close/${tradeId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Trade closed successfully!', 'success');
            loadOpenTrades();
            loadAccountData();
        } else {
            showNotification('Failed to close trade: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error closing trade:', error);
        showNotification('Failed to close trade', 'error');
    }
}

// ============================================================================
// TRADE ALERTS FUNCTIONS
// ============================================================================

async function loadTradeAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const result = await response.json();
        
        const container = document.getElementById('trade-alerts-list');
        
        if (!result.success) {
            container.innerHTML = '<p style="opacity: 0.7;">Failed to load trade alerts.</p>';
            return;
        }
        
        if (!result.alerts || result.alerts.length === 0) {
            container.innerHTML = '<p style="opacity: 0.7;">No trade alerts available. Start the comprehensive strategy to generate alerts.</p>';
            return;
        }
        
        container.innerHTML = result.alerts.map(alert => `
            <div class="alert-item">
                <div class="alert-header">
                    <div class="alert-pair">${alert.pair}</div>
                    <div class="alert-signal ${alert.signal.toLowerCase()}">${alert.signal}</div>
                </div>
                <div class="alert-details">
                    <div>Units: ${alert.units}</div>
                    <div>Stop Loss: ${alert.stop_loss || 'None'}</div>
                    <div>Take Profit: ${alert.take_profit || 'None'}</div>
                    <div>Confidence: ${(alert.confidence * 100).toFixed(1)}%</div>
                </div>
                <div class="alert-reasoning">${alert.reasoning}</div>
                <div class="alert-actions">
                    <button class="execute-alert-btn" onclick="executeTradeAlert('${alert.id}')" ${alert.status === 'executed' ? 'disabled' : ''}>
                        ${alert.status === 'executed' ? 'Executed' : 'Execute Trade'}
                    </button>
                    <span class="alert-status ${alert.status}">${alert.status}</span>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading trade alerts:', error);
        document.getElementById('trade-alerts-list').innerHTML = '<p style="opacity: 0.7;">Failed to load trade alerts.</p>';
    }
}

async function executeTradeAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/${alertId}/execute`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Trade alert executed successfully!', 'success');
            loadTradeAlerts();
            loadAccountData();
        } else {
            showNotification('Failed to execute trade alert: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error executing trade alert:', error);
        showNotification('Failed to execute trade alert', 'error');
    }
}

// ============================================================================
// ACCOUNT FUNCTIONS
// ============================================================================

async function loadAccountData() {
    try {
        const response = await fetch('/api/account');
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error);
        }
        
        const account = result.account;
        
        // Update account summary
        document.getElementById('account-id').textContent = account.id || 'N/A';
        document.getElementById('account-balance').textContent = account.balance || 'N/A';
        document.getElementById('account-nav').textContent = account.NAV || 'N/A';
        document.getElementById('account-open-trades').textContent = account.openTradeCount || '0';
        document.getElementById('account-unrealized-pl').textContent = account.unrealizedPL || '0';
        document.getElementById('account-margin-closeout').textContent = account.marginCloseoutPercent || 'N/A';
        document.getElementById('account-last-transaction').textContent = account.lastTransactionID || 'N/A';
        
        // Update summary panel
        updateSummaryData();
        
    } catch (error) {
        console.error('Error loading account data:', error);
        // Don't show error notification for account data as it might not be critical
    }
}

function updateSummaryData() {
    // Update summary values with mock data for now
    document.getElementById('total-signals').textContent = Math.floor(Math.random() * 50) + 10;
    document.getElementById('avg-confidence').textContent = (Math.random() * 30 + 70).toFixed(1) + '%';
    document.getElementById('high-confidence').textContent = Math.floor(Math.random() * 20) + 5;
    document.getElementById('active-pairs').textContent = Math.floor(Math.random() * 8) + 2;
    document.getElementById('open-trades').textContent = Math.floor(Math.random() * 5);
    document.getElementById('daily-trades').textContent = Math.floor(Math.random() * 15) + 3;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

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

function showSettings() {
    document.getElementById('settings-modal').style.display = 'block';
}

function closeSettings() {
    document.getElementById('settings-modal').style.display = 'none';
}

function saveSettings() {
    const tradingMode = document.getElementById('trading-mode').value;
    const analysisMode = document.getElementById('analysis-mode').value;
    const confidenceThreshold = document.getElementById('confidence-threshold').value;
    const updateInterval = document.getElementById('update-interval').value;
    
    // Save settings (implement as needed)
    localStorage.setItem('tradingMode', tradingMode);
    localStorage.setItem('analysisMode', analysisMode);
    localStorage.setItem('confidenceThreshold', confidenceThreshold);
    localStorage.setItem('updateInterval', updateInterval);
    
    showNotification('Settings saved successfully!', 'success');
    closeSettings();
}

// Update confidence threshold display
document.getElementById('confidence-threshold').addEventListener('input', function() {
    document.getElementById('confidence-value').textContent = (this.value * 100).toFixed(0) + '%';
});

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('settings-modal');
    if (event.target === modal) {
        closeSettings();
    }
} 