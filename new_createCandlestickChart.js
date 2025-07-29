function createCandlestickChart(candles) {
    console.log('Creating chart with candles:', candles);
    
    // Destroy existing chart first
    destroyCurrentChart();
    
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
    
    // Transform data for Chart.js with proper date parsing
    const chartData = candles.map(candle => {
        // Handle different candle formats
        let o, h, l, c, t;
        
        if (candle.mid) {
            // OANDA format with mid prices
            o = parseFloat(candle.mid.o);
            h = parseFloat(candle.mid.h);
            l = parseFloat(candle.mid.l);
            c = parseFloat(candle.mid.c);
            t = parseChartDate(candle.time);
        } else if (candle.o !== undefined) {
            // Direct OHLC format
            o = parseFloat(candle.o);
            h = parseFloat(candle.h);
            l = parseFloat(candle.l);
            c = parseFloat(candle.c);
            t = parseChartDate(candle.x || candle.time);
        } else {
            console.warn('Unknown candle format:', candle);
            return null;
        }
        
        // Validate the data
        if (isNaN(o) || isNaN(h) || isNaN(l) || isNaN(c)) {
            console.warn('Invalid OHLC values:', { o, h, l, c });
            return null;
        }
        
        return {
            x: t,
            o: o,
            h: h,
            l: l,
            c: c
        };
    }).filter(candle => candle !== null);
    
    console.log('Transformed chart data:', chartData);
    
    if (chartData.length === 0) {
        console.error('No valid chart data after transformation');
        return;
    }
    
    try {
        // Always use line chart for now (more reliable)
        currentChart = new Chart(ctx, {
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
                                hour: 'MMM dd HH:mm'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: { 
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Price'
                        }
                    }
                }
            }
        });
        console.log('✅ Line chart created successfully');
        
    } catch (error) {
        console.error('Chart creation failed:', error);
        showNotification('Failed to create chart', 'error');
    }
}
