// ============================================================================
// FOREX TRADING DASHBOARD - MODULAR STRUCTURE
// ============================================================================

// Global chart instance management
let currentChart = null;

// Function to destroy existing chart
function destroyCurrentChart() {
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
}

// Function to parse and validate date
function parseChartDate(dateString) {
    try {
        if (typeof dateString === 'string') {
            // Handle OANDA date format
            const cleanDate = dateString.replace(/\.\d+Z$/, 'Z');
            const date = new Date(cleanDate);
            
            if (isNaN(date.getTime())) {
                console.warn('Invalid date:', dateString);
                return new Date();
            }
            return date;
        }
        return new Date(dateString);
    } catch (error) {
        console.error('Date parsing error:', error, 'for date:', dateString);
        return new Date();
    }
}

let systemRunning = false;
let updateInterval = null;
let priceChart = null;
let chartStreamingInterval = null;
let aiAnalysisInterval = null;
let realTimeUpdatesActive = false;
