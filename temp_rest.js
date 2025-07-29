let priceChart = null;
let chartStreamingInterval = null;
let aiAnalysisInterval = null;
let realTimeUpdatesActive = false;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    updateTime();
    setInterval(updateTime, 1000);
    loadSystemStatus();
    startDataUpdates();
    
    // Set default dates for calendars
    setDefaultDates();
    
    // Initialize trade form
    initializeTradeForm();
    
    // Initialize streaming capabilities
    initializeStreaming();
}

function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString();
}

// ============================================================================
// STREAMING INITIALIZATION
// ============================================================================

function initializeStreaming() {
    // Initialize streaming state
    realTimeUpdatesActive = false;
    
    // Set up event listeners for streaming controls
    const startStreamingBtn = document.querySelector('button[onclick="startChartStreaming()"]');
    const stopStreamingBtn = document.querySelector('button[onclick="stopChartStreaming()"]');
    
    if (startStreamingBtn) startStreamingBtn.disabled = false;
    if (stopStreamingBtn) stopStreamingBtn.disabled = true;
}

// ============================================================================
// ENHANCED AI ANALYSIS FUNCTIONS
// ============================================================================

async function loadEnhancedAIAnalysis() {
    const pair = document.getElementById('ai-pair').value;
    const analysisContainer = document.getElementById('ai-full-analysis');
    const technicalContainer = document.getElementById('technical-indicators');
    const fundamentalContainer = document.getElementById('fundamental-events');
    const streamingContainer = document.getElementById('streaming-status');
    const recommendationContainer = document.getElementById('ai-recommendation');
    
    // Show loading state
    analysisContainer.innerHTML = '<div class="loading-spinner">🔄 Loading enhanced AI analysis...</div>';
    technicalContainer.innerHTML = '<div class="loading-spinner">Loading technical data...</div>';
    fundamentalContainer.innerHTML = '<div class="loading-spinner">Loading fundamental data...</div>';
    streamingContainer.innerHTML = '<div class="loading-spinner">Checking streaming status...</div>';
    recommendationContainer.innerHTML = '<div class="loading-spinner">Generating recommendation...</div>';
    
    try {
        const response = await fetch(`/api/enhanced-ai-analysis/${pair}`);
        const data = await response.json();
        
        if (data && !data.error) {
            // Update analysis metadata
            document.getElementById('analysis-timestamp').textContent = `Last Update: ${new Date(data.timestamp).toLocaleString()}`;
            document.getElementById('data-sources').textContent = `Data Sources: ${data.analysis_metadata.data_sources.join(', ')}`;
            document.getElementById('confidence-score').textContent = `Confidence: ${(data.analysis_metadata.confidence_score * 100).toFixed(1)}%`;
            
            // Display AI report
            analysisContainer.innerHTML = `
                <div class="ai-report">
                    <div class="report-header">
                        <h5>🤖 AI Analysis for ${pair}</h5>
                        <span class="report-time">${new Date(data.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="report-content">
                        ${data.ai_report.replace(/\n/g, '<br>')}
                    </div>
                </div>
            `;
            
            // Display technical indicators
            if (data.technical_data && data.technical_data.indicators) {
                const indicators = data.technical_data.indicators;
                technicalContainer.innerHTML = `
                    <div class="indicators-grid">
                        <div class="indicator-item">
                            <span class="indicator-label">Current Price:</span>
                            <span class="indicator-value">${indicators.current_price || 'N/A'}</span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">SMA 20:</span>
                            <span class="indicator-value">${indicators.sma_20 ? indicators.sma_20.toFixed(5) : 'N/A'}</span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">SMA 50:</span>
                            <span class="indicator-value">${indicators.sma_50 ? indicators.sma_50.toFixed(5) : 'N/A'}</span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">RSI:</span>
                            <span class="indicator-value ${indicators.rsi_signal === 'overbought' ? 'text-danger' : indicators.rsi_signal === 'oversold' ? 'text-success' : ''}">${indicators.rsi ? indicators.rsi.toFixed(2) : 'N/A'}</span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">Trend:</span>
                            <span class="indicator-value ${indicators.price_trend === 'bullish' ? 'text-success' : 'text-danger'}">${indicators.price_trend || 'N/A'}</span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">RSI Signal:</span>
                            <span class="indicator-value">${indicators.rsi_signal || 'N/A'}</span>
                        </div>
                    </div>
                `;
            } else {
                technicalContainer.innerHTML = '<p style="color: #e53e3e;">Technical data not available</p>';
            }
            
            // Display fundamental events
            if (data.fundamental_data && !data.fundamental_data.error) {
                const ffEvents = data.fundamental_data.forexfactory_events || [];
                const teEvents = data.fundamental_data.tradingeconomics_events || [];
                
                let fundamentalHtml = '<div class="fundamental-events">';
                
                if (ffEvents.length > 0) {
                    fundamentalHtml += '<h6>ForexFactory Events:</h6><ul>';
                    ffEvents.forEach(event => {
                        fundamentalHtml += `<li><strong>${event.Currency}</strong>: ${event.Event} (${event.Impact})</li>`;
                    });
                    fundamentalHtml += '</ul>';
                }
                
                if (teEvents.length > 0) {
                    fundamentalHtml += '<h6>TradingEconomics Events:</h6><ul>';
                    teEvents.forEach(event => {
                        fundamentalHtml += `<li><strong>${event.Currency}</strong>: ${event.Event} (${event.Impact})</li>`;
                    });
                    fundamentalHtml += '</ul>';
                }
                
                if (ffEvents.length === 0 && teEvents.length === 0) {
                    fundamentalHtml += '<p>No recent fundamental events</p>';
                }
                
                fundamentalHtml += '</div>';
                fundamentalContainer.innerHTML = fundamentalHtml;
            } else {
                fundamentalContainer.innerHTML = '<p style="color: #e53e3e;">Fundamental data not available</p>';
            }
            
            // Display streaming status
            if (data.streaming_data) {
                streamingContainer.innerHTML = `
                    <div class="streaming-status">
                        <div class="status-item">
                            <span class="status-indicator active"></span>
                            <span>Streaming Active</span>
                        </div>
                        <div class="status-item">
                            <span>Data Source: ${data.analysis_metadata.data_sources.includes('stream_bot') ? 'Stream Bot' : 'OANDA API'}</span>
                        </div>
                    </div>
                `;
            } else {
                streamingContainer.innerHTML = `
                    <div class="streaming-status">
                        <div class="status-item">
                            <span class="status-indicator inactive"></span>
                            <span>Streaming Inactive</span>
                        </div>
                        <div class="status-item">
                            <span>Using OANDA API data</span>
                        </div>
                    </div>
                `;
            }
            
            // Extract and display recommendation
            const reportText = data.ai_report.toLowerCase();
            let recommendation = 'HOLD';
            let recommendationClass = 'text-warning';
            
            if (reportText.includes('buy') || reportText.includes('long')) {
                recommendation = 'BUY';
                recommendationClass = 'text-success';
            } else if (reportText.includes('sell') || reportText.includes('short')) {
                recommendation = 'SELL';
                recommendationClass = 'text-danger';
            }
            
            recommendationContainer.innerHTML = `
                <div class="recommendation">
                    <div class="recommendation-signal ${recommendationClass}">
                        <h3>${recommendation}</h3>
                    </div>
                    <div class="recommendation-summary">
                        <p>${data.ai_report.split('.')[0]}.</p>
                    </div>
                </div>
            `;
            
        } else {
            analysisContainer.innerHTML = `<p style="color: #e53e3e;">Error: ${data.error || 'Unknown error'}</p>`;
            technicalContainer.innerHTML = '<p style="color: #e53e3e;">Technical data error</p>';
            fundamentalContainer.innerHTML = '<p style="color: #e53e3e;">Fundamental data error</p>';
            streamingContainer.innerHTML = '<p style="color: #e53e3e;">Streaming status error</p>';
            recommendationContainer.innerHTML = '<p style="color: #e53e3e;">Recommendation error</p>';
        }
    } catch (error) {
        console.error('Error loading enhanced AI analysis:', error);
        analysisContainer.innerHTML = '<p style="color: #e53e3e;">Error loading enhanced AI analysis</p>';
        technicalContainer.innerHTML = '<p style="color: #e53e3e;">Technical data error</p>';
        fundamentalContainer.innerHTML = '<p style="color: #e53e3e;">Fundamental data error</p>';
        streamingContainer.innerHTML = '<p style="color: #e53e3e;">Streaming status error</p>';
        recommendationContainer.innerHTML = '<p style="color: #e53e3e;">Recommendation error</p>';
    }
}

function startRealTimeUpdates() {
    if (realTimeUpdatesActive) return;
    
    realTimeUpdatesActive = true;
    const pair = document.getElementById('ai-pair').value;
    
    // Start periodic AI analysis updates
    aiAnalysisInterval = setInterval(() => {
        loadEnhancedAIAnalysis();
    }, 30000); // Update every 30 seconds
    
    // Update button states
    document.querySelector('button[onclick="startRealTimeUpdates()"]').disabled = true;
    document.querySelector('button[onclick="stopRealTimeUpdates()"]').disabled = false;
    
    showNotification('Real-time AI updates started', 'success');
}

function stopRealTimeUpdates() {
    if (!realTimeUpdatesActive) return;
    
    realTimeUpdatesActive = false;
    
    // Stop periodic updates
    if (aiAnalysisInterval) {
        clearInterval(aiAnalysisInterval);
        aiAnalysisInterval = null;
    }
    
    // Update button states
    document.querySelector('button[onclick="startRealTimeUpdates()"]').disabled = false;
    document.querySelector('button[onclick="stopRealTimeUpdates()"]').disabled = true;
    
    showNotification('Real-time AI updates stopped', 'info');
}

// ============================================================================
// ENHANCED CHART FUNCTIONS WITH STREAMING
// ============================================================================

async function loadStreamingChartData() {
    const pair = document.getElementById('chart-pair').value;
    const timeframe = document.getElementById('chart-timeframe').value;
    
    try {
        const response = await fetch(`/api/streaming-candles/${pair}/${timeframe}`);
        const data = await response.json();
        
        if (data && data.candles && data.candles.length > 0) {
            createEnhancedCandlestickChart(data.candles, pair, data.streaming);
            updateChartInfo(data.candles);
            
            // Show streaming status
            const streamingStatus = data.streaming ? '🟢 Live Streaming' : '🔴 Historical Data';
            showNotification(`Chart loaded: ${streamingStatus}`, 'info');
        } else {
            document.getElementById('price-chart').innerHTML = '<p style="text-align: center; color: #a0aec0;">No streaming data available</p>';
        }
    } catch (error) {
        console.error('Error loading streaming chart data:', error);
        document.getElementById('price-chart').innerHTML = '<p style="text-align: center; color: #e53e3e;">Error loading streaming chart data</p>';
    }
}

function createEnhancedCandlestickChart(candles, pair, isStreaming = false) {
    const ctx = document.getElementById('price-chart').getContext('2d');
    
    // Destroy existing chart
    if (window.priceChart) {
        window.priceChart.destroy();
    }
    
    // Prepare data for financial chart
    const chartData = candles.map(candle => ({
        x: new Date(candle.x),
        o: parseFloat(candle.o),
        h: parseFloat(candle.h),
        l: parseFloat(candle.l),
        c: parseFloat(candle.c)
    }));
    
    // Create enhanced candlestick chart
    window.priceChart = new Chart(ctx, {
        type: 'candlestick',
        data: {
            datasets: [{
                label: `${pair} ${isStreaming ? '(Live)' : '(Historical)'}`,
                data: chartData,
                borderColor: isStreaming ? '#10B981' : '#3B82F6',
                backgroundColor: isStreaming ? 'rgba(16, 185, 129, 0.1)' : 'rgba(59, 130, 246, 0.1)',
                borderWidth: 1,
                upColor: '#10B981',
                downColor: '#EF4444',
                upBorderColor: '#10B981',
                downBorderColor: '#EF4444'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            const data = context.raw;
                            return [
                                `Open: ${data.o.toFixed(5)}`,
                                `High: ${data.h.toFixed(5)}`,
                                `Low: ${data.l.toFixed(5)}`,
                                `Close: ${data.c.toFixed(5)}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Price'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(5);
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

function startChartStreaming() {
    if (chartStreamingInterval) return;
    
    const pair = document.getElementById('chart-pair').value;
    const timeframe = document.getElementById('chart-timeframe').value;
    
    // Start periodic chart updates
    chartStreamingInterval = setInterval(() => {
        loadStreamingChartData();
    }, 5000); // Update every 5 seconds
    
    // Update button states
    document.querySelector('button[onclick="startChartStreaming()"]').disabled = true;
    document.querySelector('button[onclick="stopChartStreaming()"]').disabled = false;
    
    showNotification('Chart streaming started', 'success');
}

function stopChartStreaming() {
    if (!chartStreamingInterval) return;
    
    // Stop periodic updates
    clearInterval(chartStreamingInterval);
    chartStreamingInterval = null;
    
    // Update button states
    document.querySelector('button[onclick="startChartStreaming()"]').disabled = false;
    document.querySelector('button[onclick="stopChartStreaming()"]').disabled = true;
    
    showNotification('Chart streaming stopped', 'info');
}

// ============================================================================
// NAVIGATION FUNCTIONS
// ============================================================================

function showSection(sectionName) {
    // Hide all content sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));
    
    // Remove active class from all nav buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected section
    document.getElementById(sectionName + '-section').classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load specific data based on section
    switch(sectionName) {
        case 'chart-info':
            loadStreamingChartData();
            break;
        case 'ai-analysis':
            loadEnhancedAIAnalysis();
            break;
        case 'technical-analysis':
            loadTechnicalData();
            break;
        case 'account-data':
            loadAccountData();
            break;
        case 'trade-execution':
            loadTradeData();
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
            
            await loadSystemStatus();
            stopDataUpdates();
            
            showNotification('All systems stopped successfully!', 'success');
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
    refreshBtn.disabled = true;
    
    Promise.all([
        loadSystemStatus(),
        loadAccountData(),
        loadChartData()
    ]).finally(() => {
        refreshText.style.display = 'inline';
        refreshLoading.style.display = 'none';
        refreshBtn.disabled = false;
        showNotification('Data refreshed successfully!', 'success');
    });
}

function startDataUpdates() {
    if (updateInterval) clearInterval(updateInterval);
    updateInterval = setInterval(() => {
        loadSystemStatus();
        if (systemRunning) {
            loadAccountData();
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
        
        document.getElementById('last-update').textContent = 'Last Update: ' + new Date().toLocaleTimeString();
    } catch (error) {
        console.error('Error loading system status:', error);
    }
}

function updateSystemStatus(running) {
    systemRunning = running;
    const statusIndicator = document.getElementById('system-status');
    const statusText = document.getElementById('system-status-text');
    
    if (running) {
        statusIndicator.className = 'status-indicator running';
        statusText.textContent = 'System Running';
    } else {
        statusIndicator.className = 'status-indicator stopped';
        statusText.textContent = 'System Stopped';
    }
}

function updateStatusIndicators(status) {
    // Stream Bot Status
    const streamBotIndicator = document.getElementById('stream-bot-status');
    const streamBotText = document.getElementById('stream-bot-status-text');
    if (status.stream_bot) {
        streamBotIndicator.className = 'status-indicator running';
        streamBotText.textContent = 'Stream Bot Running';
    } else {
        streamBotIndicator.className = 'status-indicator stopped';
        streamBotText.textContent = 'Stream Bot Stopped';
    }
    
    // AI Analysis Status
    const analysisIndicator = document.getElementById('analysis-status');
    const analysisText = document.getElementById('analysis-status-text');
    if (status.ai_analysis) {
        analysisIndicator.className = 'status-indicator running';
        analysisText.textContent = 'AI Analysis Running';
    } else {
        analysisIndicator.className = 'status-indicator stopped';
        analysisText.textContent = 'AI Analysis Stopped';
    }
    
    // Data Streaming Status
    const dataStreamingIndicator = document.getElementById('data-streaming-status');
    const dataStreamingText = document.getElementById('data-streaming-status-text');
    if (status.data_streaming) {
        dataStreamingIndicator.className = 'status-indicator running';
        dataStreamingText.textContent = 'Data Streaming Running';
    } else {
        dataStreamingIndicator.className = 'status-indicator stopped';
        dataStreamingText.textContent = 'Data Streaming Stopped';
    }
}

// ============================================================================
// CHART INFO FUNCTIONS
// ============================================================================

async function loadChartData() {
    const pair = document.getElementById('chart-pair').value;
    const timeframe = document.getElementById('chart-timeframe').value;
    
    console.log(`Loading chart data for ${pair} ${timeframe}`);
    
    try {
        // Use the hybrid streaming endpoint (tries streaming first, falls back to historical)
        console.log('Loading hybrid streaming data...');
        const response = await fetch(`/api/streaming-candles/${pair}/${timeframe}`);
        const data = await response.json();
        
        if (data && data.candles && data.candles.length > 0) {
            console.log(`✅ Chart data loaded: ${data.candles.length} candles`);
            console.log(`Data source: ${data.data_source} (${data.status})`);
            
            // Update data source indicator
            updateDataSourceIndicator(data.data_source, data.status, data.streaming);
            
            // Create chart with the data
            createCandlestickChart(data.candles, pair, timeframe);
            
            // Update chart info
            updateChartInfo(data.candles);
            
        } else {
            console.error('❌ No chart data available');
            showNotification('No chart data available', 'error');
        }
        
    } catch (error) {
        console.error('Error loading chart data:', error);
        showNotification('Failed to load chart data', 'error');
    }
}

// Function to update data source indicator
function updateDataSourceIndicator(dataSource, status, isStreaming) {
    const indicator = document.getElementById('data-source-indicator');
    if (!indicator) return;
    
    let statusText = '';
    let statusClass = '';
    
    if (isStreaming) {
        statusText = '🟢 LIVE STREAMING';
        statusClass = 'status-live';
    } else if (dataSource === 'oanda_api') {
        statusText = '🟡 HISTORICAL DATA';
        statusClass = 'status-historical';
    } else if (dataSource === 'none') {
        statusText = '🔴 NO DATA';
        statusClass = 'status-error';
    } else {
        statusText = '⚪ UNKNOWN';
        statusClass = 'status-unknown';
    }
    
    indicator.textContent = statusText;
    indicator.className = `data-source-indicator ${statusClass}`;
    
    // Update tooltip with detailed info
    indicator.title = `Source: ${dataSource}\nStatus: ${status}\nStreaming: ${isStreaming}`;
}

function createCandlestickChart(candles) {
    console.log('Creating chart with candles:', candles);
    
    const canvas = document.getElementById('price-chart');
    if (!canvas) {
        console.error('Canvas element not found!');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('Could not get canvas context!');
        return;
    }
    
    // Destroy existing chart
    if (window.priceChart) {
        window.priceChart.destroy();
    }
    
    // Transform data for Chart.js
    const chartData = candles.map(candle => ({
        x: new Date(candle.x),
        o: parseFloat(candle.o),
        h: parseFloat(candle.h),
        l: parseFloat(candle.l),
        c: parseFloat(candle.c)
    }));
    
    console.log('Transformed chart data:', chartData);
    
    try {
        // Try candlestick chart first
        if (typeof Chart !== 'undefined' && Chart.controllers && Chart.controllers.Candlestick) {
            console.log('Creating candlestick chart...');
            window.priceChart = new Chart(ctx, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: 'Price',
                        data: chartData,
                        borderColor: '#1f77b4',
                        backgroundColor: function(context) {
                            const point = context.raw;
                            return point.c >= point.o ? '#4CAF50' : '#f44336';
                        }
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: { unit: 'hour' }
                        },
                        y: { beginAtZero: false }
                    }
                }
            });
            console.log('✅ Candlestick chart created successfully');
        } else {
            throw new Error('Candlestick chart type not available');
        }
    } catch (error) {
        console.log('Candlestick chart failed, using line chart:', error);
        
        // Fallback to line chart
        window.priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Close Price',
                    data: chartData.map(d => ({ x: d.x, y: d.c })),
                    borderColor: '#1f77b4',
                    backgroundColor: 'rgba(31, 119, 180, 0.1)',
                    tension: 0.1,
                    pointRadius: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Price: ${context.parsed.y.toFixed(5)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: { 
                            unit: 'hour',
                            displayFormats: {
                                hour: 'HH:mm'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price'
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(5);
                            }
                        }
                    }
                }
            }
        });
        console.log('✅ Line chart fallback created successfully');
    }
}

function updateChartInfo(candles) {
    if (!candles || candles.length === 0) return;
    
    const latest = candles[candles.length - 1];
    const previous = candles[candles.length - 2];
    
    // Handle both old format (mid.c) and new format (c)
    const currentPrice = parseFloat(latest.c || latest.mid?.c || 0);
    const previousPrice = parseFloat(previous.c || previous.mid?.c || 0);
    const change = currentPrice - previousPrice;
    const changePercent = previousPrice !== 0 ? (change / previousPrice) * 100 : 0;
    
    // Update DOM elements if they exist
    const currentPriceElement = document.getElementById('current-price');
    const priceChangeElement = document.getElementById('price-change');
    const priceHighElement = document.getElementById('price-high');
    const priceLowElement = document.getElementById('price-low');
    
    if (currentPriceElement) currentPriceElement.textContent = currentPrice.toFixed(5);
    if (priceChangeElement) {
        priceChangeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(5)} (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)`;
        
        // Color coding for change
        if (change > 0) {
            priceChangeElement.className = 'info-value text-success';
        } else if (change < 0) {
            priceChangeElement.className = 'info-value text-danger';
        } else {
            priceChangeElement.className = 'info-value';
        }
    }
    
    // Handle both formats for high/low
    const highPrice = parseFloat(latest.h || latest.mid?.h || 0);
    const lowPrice = parseFloat(latest.l || latest.mid?.l || 0);
    
    if (priceHighElement) priceHighElement.textContent = highPrice.toFixed(5);
    if (priceLowElement) priceLowElement.textContent = lowPrice.toFixed(5);
}

// ============================================================================
// AI ANALYSIS FUNCTIONS
// ============================================================================

async function loadAIAnalysis() {
    const pair = document.getElementById('ai-pair').value;
    try {
        const response = await fetch(`/api/ai-analysis/${pair}`);
        const data = await response.json();
        if (data && !data.error) {
            document.getElementById('ai-market-analysis').innerHTML = `<pre>${data.ai_report}</pre>`;
            document.getElementById('ai-full-analysis').innerHTML = `<pre>${data.ai_report}</pre>`;
        } else {
            document.getElementById('ai-market-analysis').innerHTML = '<p style="color: #e53e3e;">Error loading AI analysis</p>';
            document.getElementById('ai-full-analysis').innerHTML = '<p style="color: #e53e3e;">Error loading AI analysis</p>';
        }
    } catch (error) {
        document.getElementById('ai-market-analysis').innerHTML = '<p style="color: #e53e3e;">Error loading AI analysis</p>';
        document.getElementById('ai-full-analysis').innerHTML = '<p style="color: #e53e3e;">Error loading AI analysis</p>';
    }
}

function displayFullAIAnalysis(data) {
    const fullAnalysisContainer = document.getElementById('ai-full-analysis');
    
    const analysisText = `
=== COMPREHENSIVE AI ANALYSIS REPORT ===
Generated: ${new Date().toLocaleString()}
Currency Pair: ${data.pair}
Trading Horizon: ${document.getElementById('trade-horizon').value.toUpperCase()}

=== MARKET OVERVIEW ===
${data.market_overview || 'Market overview not available'}

=== TECHNICAL ANALYSIS ===
Trend Direction: ${data.technical.trend.toUpperCase()}
RSI (14): ${data.technical.rsi} - ${data.technical.rsi_signal}
MACD Signal: ${data.technical.macd_signal.toUpperCase()}
Support Level: ${data.technical.support}
Resistance Level: ${data.technical.resistance}
Volatility (ATR): ${data.technical.volatility}

=== PRICE ACTION ANALYSIS ===
Direction: ${data.price_action.direction.toUpperCase()}
Change: ${data.price_action.change_percent}%
Momentum: ${data.price_action.momentum || 'Not available'}

=== PATTERN ANALYSIS ===
Detected Patterns: ${data.patterns.join(', ') || 'None detected'}
Pattern Reliability: ${data.pattern_reliability || 'Not available'}

=== FUNDAMENTAL FACTORS ===
${data.fundamental_analysis || 'Fundamental analysis not available'}

=== RISK ASSESSMENT ===
Risk Level: ${data.risk_assessment.level || 'Not available'}
Risk Factors: ${data.risk_assessment.factors || 'Not available'}
Market Conditions: ${data.risk_assessment.market_conditions || 'Not available'}

=== TRADING RECOMMENDATION ===
Action: ${data.recommendation}
Confidence: ${data.confidence || 'N/A'}%
Reasoning: ${data.reasoning || 'Not available'}

=== POSITION SIZING SUGGESTIONS ===
${data.position_sizing || 'Position sizing not available'}

=== KEY LEVELS TO WATCH ===
${data.key_levels || 'Key levels not available'}

=== AI INSIGHTS ===
${data.ai_insights || 'AI insights not available'}

=== DISCLAIMER ===
This analysis is for informational purposes only. Always conduct your own research and consider your risk tolerance before trading. Past performance does not guarantee future results.
    `;
    
    fullAnalysisContainer.textContent = analysisText;
}

function displayAIAnalysis(data) {
    // Market Analysis
    const marketAnalysis = document.getElementById('ai-market-analysis');
    marketAnalysis.innerHTML = `
        <div class="analysis-item">
            <strong>Trend:</strong> <span class="text-${data.technical.trend === 'bullish' ? 'success' : 'danger'}">${data.technical.trend.toUpperCase()}</span>
        </div>
        <div class="analysis-item">
            <strong>RSI:</strong> ${data.technical.rsi} (${data.technical.rsi_signal})
        </div>
        <div class="analysis-item">
            <strong>MACD Signal:</strong> <span class="text-${data.technical.macd_signal === 'bullish' ? 'success' : 'danger'}">${data.technical.macd_signal.toUpperCase()}</span>
        </div>
        <div class="analysis-item">
            <strong>Support:</strong> ${data.technical.support}
        </div>
        <div class="analysis-item">
            <strong>Resistance:</strong> ${data.technical.resistance}
        </div>
        <div class="analysis-item">
            <strong>Volatility:</strong> ${data.technical.volatility}
        </div>
    `;
    
    // Trading Recommendation
    const recommendation = document.getElementById('ai-recommendation');
    recommendation.innerHTML = `
        <div class="analysis-item">
            <strong>Recommendation:</strong> <span class="text-${data.recommendation === 'BUY' ? 'success' : data.recommendation === 'SELL' ? 'danger' : 'warning'}">${data.recommendation}</span>
        </div>
        <div class="analysis-item">
            <strong>Confidence:</strong> ${data.confidence || 'N/A'}%
        </div>
        <div class="analysis-item">
            <strong>Patterns Detected:</strong> ${data.patterns.join(', ') || 'None'}
        </div>
        <div class="analysis-item">
            <strong>Price Action:</strong> ${data.price_action.direction.toUpperCase()} (${data.price_action.change_percent}%)
        </div>
    `;
    
    // Risk Assessment
    const riskAssessment = document.getElementById('ai-risk-assessment');
    const riskLevel = data.technical.volatility > 0.005 ? 'High' : data.technical.volatility > 0.002 ? 'Medium' : 'Low';
    riskAssessment.innerHTML = `
        <div class="analysis-item">
            <strong>Risk Level:</strong> <span class="text-${riskLevel === 'High' ? 'danger' : riskLevel === 'Medium' ? 'warning' : 'success'}">${riskLevel}</span>
        </div>
        <div class="analysis-item">
            <strong>Volatility:</strong> ${data.technical.volatility}
        </div>
        <div class="analysis-item">
            <strong>Market Condition:</strong> ${data.technical.trend} market
        </div>
        <div class="analysis-item">
            <strong>Horizon:</strong> ${document.getElementById('trade-horizon').value}
        </div>
    `;
}

// ============================================================================
// TECHNICAL ANALYSIS FUNCTIONS
// ============================================================================

async function loadTechnicalData() {
    const pair = document.getElementById('tech-pair').value;
    const timeframe = document.getElementById('tech-timeframe').value;
    
    try {
        const [technicalsResponse, patternsResponse] = await Promise.all([
            fetch(`/api/technicals/${pair}/${timeframe}`),
            fetch(`/api/patterns/${pair}/${timeframe}`)
        ]);
        
        const technicals = await technicalsResponse.json();
        const patterns = await patternsResponse.json();
        
        if (technicals && !technicals.error) {
            displayTechnicalIndicators(technicals);
        }
        
        if (patterns && !patterns.error) {
            displayCandlestickPatterns(patterns);
        }
    } catch (error) {
        console.error('Error loading technical data:', error);
    }
}

function displayTechnicalIndicators(data) {
    // Momentum Indicators
    const momentumContainer = document.getElementById('momentum-indicators');
    momentumContainer.innerHTML = `
        <div class="indicator-item">
            <strong>RSI:</strong> ${data.rsi}
        </div>
        <div class="indicator-item">
            <strong>Stochastic K:</strong> ${data.stoch_k}
        </div>
        <div class="indicator-item">
            <strong>Stochastic D:</strong> ${data.stoch_d}
        </div>
        <div class="indicator-item">
            <strong>MACD:</strong> ${data.macd}
        </div>
        <div class="indicator-item">
            <strong>MACD Signal:</strong> ${data.macd_signal}
        </div>
        <div class="indicator-item">
            <strong>MACD Histogram:</strong> ${data.macd_histogram}
        </div>
    `;
    
    // Trend Indicators
    const trendContainer = document.getElementById('trend-indicators');
    trendContainer.innerHTML = `
        <div class="indicator-item">
            <strong>EMA 20:</strong> ${data.ema_20}
        </div>
        <div class="indicator-item">
            <strong>EMA 50:</strong> ${data.ema_50}
        </div>
        <div class="indicator-item">
            <strong>EMA 200:</strong> ${data.ema_200}
        </div>
        <div class="indicator-item">
            <strong>SMA 20:</strong> ${data.sma_20}
        </div>
        <div class="indicator-item">
            <strong>SMA 50:</strong> ${data.sma_50}
        </div>
        <div class="indicator-item">
            <strong>ADX:</strong> ${data.adx}
        </div>
    `;
    
    // Volatility Indicators
    const volatilityContainer = document.getElementById('volatility-indicators');
    volatilityContainer.innerHTML = `
        <div class="indicator-item">
            <strong>ATR:</strong> ${data.atr}
        </div>
        <div class="indicator-item">
            <strong>Bollinger Upper:</strong> ${data.bollinger_upper}
        </div>
        <div class="indicator-item">
            <strong>Bollinger Middle:</strong> ${data.bollinger_middle}
        </div>
        <div class="indicator-item">
            <strong>Bollinger Lower:</strong> ${data.bollinger_lower}
        </div>
    `;
}

function displayCandlestickPatterns(patterns) {
    const patternsContainer = document.getElementById('candlestick-patterns');
    const detectedPatterns = [];
    
    for (const [pattern, detected] of Object.entries(patterns)) {
        if (detected) {
            detectedPatterns.push(pattern.replace('_', ' ').toUpperCase());
        }
    }
    
    if (detectedPatterns.length > 0) {
        patternsContainer.innerHTML = `
            <div class="pattern-item">
                <strong>Detected Patterns:</strong>
            </div>
            ${detectedPatterns.map(pattern => `
                <div class="pattern-item text-success">
                    ✓ ${pattern}
                </div>
            `).join('')}
        `;
    } else {
        patternsContainer.innerHTML = `
            <div class="pattern-item">
                <strong>No significant patterns detected</strong>
            </div>
        `;
    }
}

// ============================================================================
// ACCOUNT DATA FUNCTIONS
// ============================================================================

async function loadAccountData() {
    try {
        const response = await fetch('/api/account');
        const data = await response.json();
        
        if (data.success && data.account) {
            updateAccountSummary(data.account);
        }
        
        // Load positions and trades
        await Promise.all([
            loadPositions(),
            loadOpenTrades()
        ]);
    } catch (error) {
        console.error('Error loading account data:', error);
    }
}

function updateAccountSummary(account) {
    document.getElementById('account-balance').textContent = `$${parseFloat(account.balance).toFixed(2)}`;
    document.getElementById('account-equity').textContent = `$${parseFloat(account.NAV).toFixed(2)}`;
    document.getElementById('account-pnl').textContent = `$${parseFloat(account.pl).toFixed(2)}`;
    document.getElementById('account-margin').textContent = `$${parseFloat(account.marginUsed).toFixed(2)}`;
    document.getElementById('open-positions').textContent = account.openPositionCount;
    document.getElementById('open-trades').textContent = account.openTradeCount;
    
    // Color coding for P&L
    const pnlElement = document.getElementById('account-pnl');
    const pnl = parseFloat(account.pl);
    if (pnl > 0) {
        pnlElement.className = 'account-value text-success';
    } else if (pnl < 0) {
        pnlElement.className = 'account-value text-danger';
    } else {
        pnlElement.className = 'account-value';
    }
}

async function loadPositions() {
    try {
        const response = await fetch('/api/positions');
        const positions = await response.json();
        
        // Handle different response formats - positions might be an object with a positions array
        let positionsArray = [];
        if (Array.isArray(positions)) {
            positionsArray = positions;
        } else if (positions && Array.isArray(positions.positions)) {
            positionsArray = positions.positions;
        } else if (positions && positions.success && Array.isArray(positions.positions)) {
            positionsArray = positions.positions;
        }
        
        // Defensive: filter out undefined/null and missing units
        const safePositions = positionsArray.filter(pos => pos && typeof pos.units !== 'undefined');
        const positionsContainer = document.getElementById('positions-list');
        if (safePositions.length > 0) {
            positionsContainer.innerHTML = safePositions.map(position => `
                <div class="position-item">
                    <div class="position-header">
                        <strong>${position.instrument}</strong>
                        <span class="position-side ${position.long && position.long.units > 0 ? 'long' : 'short'}">
                            ${position.long && position.long.units > 0 ? 'LONG' : 'SHORT'}
                        </span>
                    </div>
                    <div class="position-details">
                        <span>Units: ${Math.abs((position.long && position.long.units) || (position.short && position.short.units) || 0)}</span>
                        <span>P&L: $${parseFloat(position.unrealizedPL || 0).toFixed(2)}</span>
                    </div>
                </div>
            `).join('');
        } else {
            positionsContainer.innerHTML = '<p style="opacity: 0.7;">No open positions</p>';
        }
    } catch (error) {
        console.error('Error loading positions:', error);
        const positionsContainer = document.getElementById('positions-list');
        if (positionsContainer) {
            positionsContainer.innerHTML = '<p style="opacity: 0.7;">Error loading positions</p>';
        }
    }
}

async function loadOpenTrades() {
    try {
        const response = await fetch('/api/trade/open');
        const data = await response.json();
        
        const tradesContainer = document.getElementById('trades-list');
        if (data.success && data.trades && data.trades.length > 0) {
            tradesContainer.innerHTML = data.trades.map(trade => `
                <div class="trade-item">
                    <div class="trade-header">
                        <strong>${trade.instrument}</strong>
                        <span class="trade-side ${trade.currentUnits > 0 ? 'long' : 'short'}">
                            ${trade.currentUnits > 0 ? 'LONG' : 'SHORT'}
                        </span>
                    </div>
                    <div class="trade-details">
                        <span>Units: ${Math.abs(trade.currentUnits)}</span>
                        <span>P&L: $${parseFloat(trade.unrealizedPL).toFixed(2)}</span>
                        <button class="btn btn-stop" onclick="closeTrade('${trade.id}')">Close</button>
                    </div>
                </div>
            `).join('');
        } else {
            tradesContainer.innerHTML = '<p style="opacity: 0.7;">No open trades</p>';
        }
    } catch (error) {
        console.error('Error loading trades:', error);
    }
}

// ============================================================================
// TRADE EXECUTION FUNCTIONS
// ============================================================================

function initializeTradeForm() {
    const form = document.getElementById('place-trade-form');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await placeTrade();
    });
    
    // Initialize form with default values
    updateTradePrices();
    
    // Add event listeners for real-time calculations
    document.getElementById('trade-units').addEventListener('input', updateOrderInfo);
    document.getElementById('trade-stop-loss').addEventListener('input', updateOrderInfo);
    document.getElementById('trade-take-profit').addEventListener('input', updateOrderInfo);
}

async function updateTradePrices() {
    const pair = document.getElementById('trade-pair').value;
    const direction = document.getElementById('trade-direction').value;
    
    if (!pair || !direction) {
        clearPriceDisplay();
        return;
    }
    
    try {
        const response = await fetch(`/api/prices/${pair}/M1/1`);
        const data = await response.json();
        
        if (data && data.candles && data.candles.length > 0) {
            const latest = data.candles[0];
            const bid = parseFloat(latest.mid.c) - 0.0001; // Approximate bid
            const ask = parseFloat(latest.mid.c) + 0.0001; // Approximate ask
            const spread = ask - bid;
            
            document.getElementById('current-bid').textContent = bid.toFixed(5);
            document.getElementById('current-ask').textContent = ask.toFixed(5);
            document.getElementById('current-spread').textContent = spread.toFixed(5);
            
            // Auto-populate stop loss and take profit based on direction
            if (direction === 'buy') {
                const stopLoss = (bid - 0.0050).toFixed(5); // 50 pips below bid
                const takeProfit = (ask + 0.0050).toFixed(5); // 50 pips above ask
                document.getElementById('trade-stop-loss').value = stopLoss;
                document.getElementById('trade-take-profit').value = takeProfit;
            } else {
                const stopLoss = (ask + 0.0050).toFixed(5); // 50 pips above ask
                const takeProfit = (bid - 0.0050).toFixed(5); // 50 pips below bid
                document.getElementById('trade-stop-loss').value = stopLoss;
                document.getElementById('trade-take-profit').value = takeProfit;
            }
            
            updateOrderInfo();
        }
    } catch (error) {
        console.error('Error updating trade prices:', error);
        clearPriceDisplay();
    }
}

function clearPriceDisplay() {
    document.getElementById('current-bid').textContent = '--';
    document.getElementById('current-ask').textContent = '--';
    document.getElementById('current-spread').textContent = '--';
}

function updateOrderInfo() {
    const units = parseFloat(document.getElementById('trade-units').value) || 0;
    const stopLoss = document.getElementById('trade-stop-loss').value;
    const takeProfit = document.getElementById('trade-take-profit').value;
    const direction = document.getElementById('trade-direction').value;
    const pair = document.getElementById('trade-pair').value;
    
    if (!units || !stopLoss || !takeProfit || !direction || !pair) {
        clearOrderInfo();
        return;
    }
    
    // Calculate pip value (simplified - would need actual pip values per pair)
    const pipValue = calculatePipValue(pair, units);
    
    // Calculate margin (assuming 20:1 leverage)
    const marginUsed = (units * 0.0001) / 20; // Simplified calculation
    
    // Calculate stop loss and take profit in pips
    const currentPrice = direction === 'buy' ? 
        parseFloat(document.getElementById('current-ask').textContent) :
        parseFloat(document.getElementById('current-bid').textContent);
    
    const stopLossPips = Math.abs(currentPrice - parseFloat(stopLoss)) * 10000;
    const takeProfitPips = Math.abs(currentPrice - parseFloat(takeProfit)) * 10000;
    
    // Calculate USD values
    const stopLossUSD = stopLossPips * pipValue;
    const takeProfitUSD = takeProfitPips * pipValue;
    
    // Update display
    document.getElementById('margin-amount').value = marginUsed.toFixed(2);
    document.getElementById('margin-used').textContent = `$${marginUsed.toFixed(2)}`;
    document.getElementById('pip-value').textContent = `$${pipValue.toFixed(2)} USD`;
    document.getElementById('trade-value').textContent = `$${(units * 0.0001).toFixed(2)} USD`;
    
    // Update stop loss and take profit details
    document.getElementById('stop-loss-pips').textContent = `${stopLossPips.toFixed(1)} pips`;
    document.getElementById('stop-loss-usd').textContent = `$${stopLossUSD.toFixed(2)}`;
    document.getElementById('take-profit-pips').textContent = `${takeProfitPips.toFixed(1)} pips`;
    document.getElementById('take-profit-usd').textContent = `$${takeProfitUSD.toFixed(2)}`;
    
    // Calculate risk/reward ratio
    const riskRewardRatio = takeProfitUSD / stopLossUSD;
    document.getElementById('risk-reward').textContent = `${riskRewardRatio.toFixed(2)}:1`;
    
    // Update button text
    const btnText = direction.toUpperCase();
    const btnDetails = `${units} ${pair} MKT`;
    document.getElementById('trade-btn-text').textContent = btnText;
    document.getElementById('trade-btn-details').textContent = btnDetails;
}

function clearOrderInfo() {
    document.getElementById('margin-amount').value = '';
    document.getElementById('margin-used').textContent = '--';
    document.getElementById('pip-value').textContent = '-- USD';
    document.getElementById('trade-value').textContent = '-- USD';
    document.getElementById('stop-loss-pips').textContent = '-- pips';
    document.getElementById('stop-loss-usd').textContent = '-- USD';
    document.getElementById('take-profit-pips').textContent = '-- pips';
    document.getElementById('take-profit-usd').textContent = '-- USD';
    document.getElementById('risk-reward').textContent = '--';
    document.getElementById('trade-btn-text').textContent = 'Place Trade';
    document.getElementById('trade-btn-details').textContent = '--';
}

function calculatePipValue(pair, units) {
    // Simplified pip value calculation
    // In reality, this would depend on the specific pair and account currency
    const basePipValue = 0.0001; // 1 pip = 0.0001 for most pairs
    return units * basePipValue * 10; // Simplified calculation
}

// Units Calculator Functions
function openUnitsCalculator() {
    const modal = document.getElementById('units-calculator-modal');
    modal.style.display = 'block';
    
    // Pre-populate with account balance if available
    const accountBalance = document.getElementById('account-balance').textContent;
    if (accountBalance && accountBalance !== '--') {
        document.getElementById('calc-account-balance').value = parseFloat(accountBalance.replace('$', ''));
    }
    
    // Pre-populate pip value based on current trade
    const pair = document.getElementById('trade-pair').value;
    const units = parseFloat(document.getElementById('trade-units').value) || 1000;
    const pipValue = calculatePipValue(pair, units);
    document.getElementById('calc-pip-value').value = pipValue.toFixed(2);
    
    // Add event listeners for real-time calculation
    document.getElementById('calc-account-balance').addEventListener('input', calculateUnits);
    document.getElementById('calc-risk-percentage').addEventListener('input', calculateUnits);
    document.getElementById('calc-stop-loss-pips').addEventListener('input', calculateUnits);
    document.getElementById('calc-pip-value').addEventListener('input', calculateUnits);
    
    calculateUnits();
}

function closeUnitsCalculator() {
    const modal = document.getElementById('units-calculator-modal');
    modal.style.display = 'none';
}

function calculateUnits() {
    const accountBalance = parseFloat(document.getElementById('calc-account-balance').value) || 0;
    const riskPercentage = parseFloat(document.getElementById('calc-risk-percentage').value) || 0;
    const stopLossPips = parseFloat(document.getElementById('calc-stop-loss-pips').value) || 0;
    const pipValue = parseFloat(document.getElementById('calc-pip-value').value) || 0;
    
    if (accountBalance > 0 && riskPercentage > 0 && stopLossPips > 0 && pipValue > 0) {
        const riskAmount = accountBalance * (riskPercentage / 100);
        const units = riskAmount / (stopLossPips * pipValue);
        document.getElementById('calculated-units').textContent = Math.round(units);
    } else {
        document.getElementById('calculated-units').textContent = '--';
    }
}

function applyCalculatedUnits() {
    const calculatedUnits = document.getElementById('calculated-units').textContent;
    if (calculatedUnits !== '--') {
        document.getElementById('trade-units').value = calculatedUnits;
        updateOrderInfo();
        closeUnitsCalculator();
        showNotification('Units applied to trade form!', 'success');
    }
}

async function placeTrade() {
    const pair = document.getElementById('trade-pair').value;
    const direction = document.getElementById('trade-direction').value;
    const units = parseFloat(document.getElementById('trade-units').value);
    const stopLoss = document.getElementById('trade-stop-loss').value;
    const takeProfit = document.getElementById('trade-take-profit').value;
    
    if (!pair || !direction || !units) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/trade/place', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pair: pair,
                direction: direction,
                units: units,
                stop_loss: stopLoss || null,
                take_profit: takeProfit || null
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Trade placed successfully!', 'success');
            document.getElementById('place-trade-form').reset();
            clearPriceDisplay();
            clearOrderInfo();
            loadAccountData();
        } else {
            showNotification('Failed to place trade: ' + result.error, 'error');
        }
    } catch (error) {
        showNotification('Error placing trade: ' + error.message, 'error');
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
            loadAccountData();
        } else {
            showNotification('Failed to close trade: ' + result.error, 'error');
        }
    } catch (error) {
        showNotification('Error closing trade: ' + error.message, 'error');
    }
}

async function loadTradeData() {
    await Promise.all([
        loadTradeAlerts()
    ]);
}

async function loadTradeAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const data = await response.json();
        
        const alertsContainer = document.getElementById('trade-alerts');
        if (data.success && data.alerts && data.alerts.length > 0) {
            alertsContainer.innerHTML = data.alerts.map(alert => `
                <div class="alert-item">
                    <div class="alert-header">
                        <strong>${alert.pair}</strong>
                        <span class="alert-signal ${alert.signal.toLowerCase()}">${alert.signal.toUpperCase()}</span>
                    </div>
                    <div class="alert-details">
                        <span>Confidence: ${alert.confidence}%</span>
                        <span>Price: ${alert.price}</span>
                    </div>
                    <div class="alert-reasoning">${alert.reasoning}</div>
                    <button class="btn" onclick="executeAlert('${alert.id}')">Execute</button>
                </div>
            `).join('');
        } else {
            alertsContainer.innerHTML = '<p style="opacity: 0.7;">No trade alerts available</p>';
        }
    } catch (error) {
        console.error('Error loading trade alerts:', error);
    }
}

async function executeAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/${alertId}/execute`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Alert executed successfully!', 'success');
            loadTradeAlerts();
            loadAccountData();
        } else {
            showNotification('Failed to execute alert: ' + result.error, 'error');
        }
    } catch (error) {
        showNotification('Error executing alert: ' + error.message, 'error');
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function setDefaultDates() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    // Set default dates for any date inputs that might exist
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach((input, index) => {
        if (index === 0) {
            input.value = today.toISOString().split('T')[0];
        } else {
            input.value = tomorrow.toISOString().split('T')[0];
        }
    });
    
    // Set default month for month inputs
    const monthInputs = document.querySelectorAll('input[type="month"]');
    monthInputs.forEach(input => {
        input.value = today.toISOString().slice(0, 7);
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 5000);
}

// Add notification styles
const notificationStyles = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 1001;
    transform: translateX(400px);
    transition: transform 0.3s ease;
    max-width: 350px;
}

.notification.show {
    transform: translateX(0);
}

.notification.success {
    background: #38a169;
}

.notification.error {
    background: #e53e3e;
}

.notification.info {
    background: #3182ce;
}

.analysis-item, .indicator-item, .pattern-item {
    margin-bottom: 8px;
    padding: 5px 0;
}

.position-item, .trade-item, .alert-item {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.position-header, .trade-header, .alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.position-side, .trade-side, .alert-signal {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.position-side.long, .trade-side.long, .alert-signal.buy {
    background: rgba(56, 161, 105, 0.2);
    color: #38a169;
}

.position-side.short, .trade-side.short, .alert-signal.sell {
    background: rgba(229, 62, 62, 0.2);
    color: #e53e3e;
}

.position-details, .trade-details, .alert-details {
    display: flex;
    gap: 15px;
    margin-bottom: 8px;
    font-size: 0.9rem;
    color: #a0aec0;
}

.alert-reasoning {
    font-size: 0.85rem;
    color: #718096;
    margin-bottom: 10px;
    line-height: 1.4;
}
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet); 

async function testChartWithMockData() {
    console.log('Testing chart with mock data...');
    
    try {
        const response = await fetch('/api/test-candles/EUR_USD/M15');
        const data = await response.json();
        
        console.log('Mock data response:', data);
        
        if (data && data.candles && data.candles.length > 0) {
            createSimpleLineChart(data.candles);
            console.log('✅ Mock chart created successfully');
        } else {
            console.log('❌ No mock data received');
        }
    } catch (error) {
        console.error('Error testing mock chart:', error);
    }
}

function createSimpleLineChart(candles) {
    const ctx = document.getElementById('price-chart');
    if (window.priceChart) {
        window.priceChart.destroy();
    }
    
    // Transform data for line chart
    const chartData = candles.map(candle => ({
        x: new Date(candle.x),
        y: parseFloat(candle.c)
    }));
    
    window.priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Close Price',
                data: chartData,
                borderColor: '#1f77b4',
                backgroundColor: 'rgba(31, 119, 180, 0.1)',
                tension: 0.1,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Price: ${context.parsed.y.toFixed(5)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: { 
                        unit: 'hour',
                        displayFormats: {
                            hour: 'HH:mm'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Price'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(5);
                        }
                    }
                }
            }
        }
    });
} 

// Defensive testChart function to avoid ReferenceError
function testChart() {
    if (typeof testChartWithMockData === 'function') {
        testChartWithMockData();
    } else {
        alert('Test chart function called!');
    }
} 