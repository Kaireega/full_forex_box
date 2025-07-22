# OpenAI Analysis Integration

This module adds powerful AI-driven analysis capabilities to your forex trading system using OpenAI's GPT models.

## Features

### 🤖 AI-Powered Analysis
- **Market Condition Analysis**: Real-time analysis of currency pair movements
- **News Sentiment Analysis**: Interpretation of forex factory news impact
- **Trading Strategy Generation**: AI-generated trading recommendations
- **Technical Analysis**: Pattern recognition and technical indicator insights
- **Fundamental Analysis**: Economic factor assessment and impact analysis

### 📊 Analysis Types
1. **General Analysis**: Comprehensive market overview
2. **Technical Analysis**: Price action, trends, and indicators
3. **Fundamental Analysis**: Economic indicators and policy impacts
4. **Sentiment Analysis**: Market psychology and sentiment drivers

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Test Installation
```bash
python test_openai_analysis.py
```

## Usage

### Basic Analysis
```python
from api.openai_api import OpenAIAnalyzer
import pandas as pd

# Initialize analyzer
analyzer = OpenAIAnalyzer()

# Analyze forex data
data = pd.DataFrame({...})  # Your forex data
result = analyzer.analyze_forex_data(data, "technical")
print(result['analysis'])
```

### Comprehensive Analysis
```python
from analysis.openai_analysis import ForexOpenAIAnalysis

# Initialize comprehensive analyzer
analyzer = ForexOpenAIAnalysis()

# Generate full market report
report = analyzer.comprehensive_market_report(
    currency_pairs=['EUR_USD', 'GBP_USD'],
    include_news=True,
    analysis_types=['general', 'technical']
)
```

### News Sentiment Analysis
```python
# Analyze news impact
news_analysis = analyzer.analyze_news_impact(['jan.2025'])
print(news_analysis['openai_sentiment_analysis']['sentiment_analysis'])
```

### Trading Strategy Generation
```python
market_data = {
    'EUR_USD': {'current_price': 1.0350, 'volatility': 0.008},
    'GBP_USD': {'current_price': 1.2450, 'volatility': 0.012}
}

strategy = analyzer.generate_trading_strategy(market_data, "medium")
print(strategy['strategy'])
```

## File Structure

```
analysis/
├── openai_analysis.py          # Main analysis integration
├── openai_analysis_demo.ipynb  # Jupyter notebook demo
└── README_OpenAI.md            # This documentation

api/
└── openai_api.py               # Core OpenAI API wrapper

test_openai_analysis.py         # Test suite
```

## API Reference

### OpenAIAnalyzer Class

#### Methods

##### `analyze_forex_data(data, analysis_type="general")`
Analyze forex data using OpenAI.

**Parameters:**
- `data` (DataFrame): Forex price data
- `analysis_type` (str): "general", "technical", "fundamental", or "sentiment"

**Returns:**
- Dictionary with analysis results

##### `analyze_news_sentiment(news_data)`
Analyze news sentiment and market impact.

**Parameters:**
- `news_data` (List[Dict]): List of news events

**Returns:**
- Dictionary with sentiment analysis

##### `generate_trading_strategy(market_data, risk_tolerance="medium")`
Generate AI-powered trading strategies.

**Parameters:**
- `market_data` (Dict): Current market conditions
- `risk_tolerance` (str): "low", "medium", or "high"

**Returns:**
- Dictionary with trading strategy

### ForexOpenAIAnalysis Class

#### Methods

##### `analyze_current_market_conditions(currency_pairs=None)`
Analyze real-time market conditions using OANDA data.

##### `analyze_news_impact(months=None)`
Analyze forex factory news for specified months.

##### `comprehensive_market_report(currency_pairs, include_news, analysis_types)`
Generate comprehensive multi-type analysis report.

## Configuration

### Model Selection
The system uses `gpt-4o-mini` by default for cost efficiency. You can modify this in `api/openai_api.py`:

```python
self.model = "gpt-4o"  # For more advanced analysis
```

### Cost Management
- Monitor token usage returned in analysis results
- Use appropriate analysis types for your needs
- Consider caching results for repeated queries

## Integration with Existing System

### With OANDA API
The OpenAI analysis automatically integrates with your existing OANDA API setup to fetch real-time market data.

### With Forex Factory Data
News sentiment analysis works with the existing forex factory scraping functionality.

### With Trading Bots
Integrate AI insights into your trading decision process:

```python
# In your trading bot
def make_trading_decision(self, pair):
    # Get AI analysis
    analyzer = ForexOpenAIAnalysis()
    market_analysis = analyzer.analyze_current_market_conditions([pair])
    
    # Extract AI recommendations
    ai_strategy = market_analysis['openai_analysis']['strategy']
    
    # Combine with your existing logic
    return self.combine_ai_and_technical_signals(ai_strategy, pair)
```

## Example Workflows

### Daily Market Analysis
```python
# Run this daily for market insights
analyzer = ForexOpenAIAnalysis()
daily_report = analyzer.comprehensive_market_report()

# Save or email the report
with open(f"market_report_{datetime.now().date()}.json", 'w') as f:
    json.dump(daily_report, f, indent=2)
```

### Pre-Trade Analysis
```python
# Before making a trade
def pre_trade_analysis(currency_pair):
    analyzer = ForexOpenAIAnalysis()
    
    # Get current conditions
    conditions = analyzer.analyze_current_market_conditions([currency_pair])
    
    # Get news sentiment
    news = analyzer.analyze_news_impact()
    
    return {
        'market_conditions': conditions,
        'news_sentiment': news,
        'recommendation': 'proceed' if conditions_favorable else 'wait'
    }
```

## Best Practices

### 1. Token Usage Optimization
- Use specific analysis types rather than always running comprehensive reports
- Cache results for repeated analysis of the same data
- Monitor daily token usage

### 2. Error Handling
```python
try:
    analysis = analyzer.analyze_forex_data(data)
    if 'error' in analysis:
        print(f"Analysis error: {analysis['error']}")
    else:
        # Process successful analysis
        process_analysis(analysis)
except Exception as e:
    print(f"System error: {e}")
```

### 3. Data Quality
- Ensure your input data is clean and properly formatted
- Handle missing or invalid data before sending to OpenAI
- Validate analysis results for reasonableness

### 4. Security
- Never commit API keys to version control
- Use environment variables for API key storage
- Consider using OpenAI API usage limits

## Troubleshooting

### Common Issues

#### "OpenAI API key not found"
- Set the environment variable: `export OPENAI_API_KEY="your-key"`
- Or pass it directly: `OpenAIAnalyzer(api_key="your-key")`

#### "OANDA API errors"
- Check your OANDA API configuration in `constants/defs.py`
- Ensure OANDA credentials are properly set

#### "No news data available"
- Check forex factory scraping functionality
- Verify the month format (e.g., 'jan.2025')

#### High token usage
- Use more specific analysis types
- Reduce the amount of data sent to OpenAI
- Consider using shorter time periods

### Performance Tips

1. **Batch Processing**: Analyze multiple currency pairs together
2. **Caching**: Store results for repeated queries
3. **Selective Analysis**: Use specific analysis types rather than comprehensive reports
4. **Data Filtering**: Send only relevant data to OpenAI

## Contributing

To extend the OpenAI analysis functionality:

1. Add new analysis types in `_get_analysis_prompt()`
2. Create specialized analyzers for specific markets
3. Implement result caching mechanisms
4. Add new integration points with existing systems

## Support

For issues related to:
- **OpenAI API**: Check OpenAI documentation and status
- **Integration**: Review the test suite and examples
- **Performance**: Monitor token usage and optimize queries

## Version History

- **v1.0**: Initial OpenAI integration
  - Basic analysis capabilities
  - News sentiment analysis
  - Trading strategy generation
  - Comprehensive reporting system