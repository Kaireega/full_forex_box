import sys
import os

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.openai_api import OpenAIAnalyzer
from api.oanda_api import OandaApi
import scraping.forexfactory_calendar as ff

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import json
from api.oanda_api import OandaApi
import scraping.forexfactory_calendar as ff
from typing import List, Dict
from datetime import datetime
import traceback

class ForexOpenAIAnalysis:
    """
    Comprehensive forex analysis using OpenAI integration with existing data sources.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the analysis system.
        
        Args:
            openai_api_key: OpenAI API key. If not provided, will use environment variable.
        """
        self.openai_analyzer = OpenAIAnalyzer(openai_api_key)
        self.oanda_api = OandaApi()
        


    def analyze_current_market_conditions(self, currency_pairs: List[str] = None) -> Dict:
        """
        Analyze current market conditions using OpenAI across multiple timeframes.

        Args:
            currency_pairs: List of currency pairs to analyze (e.g., ['EUR_USD', 'GBP_USD'])

        Returns:
            Comprehensive market analysis dictionary
        """
        if currency_pairs is None:
            currency_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD']

        timeframes = ["M15", "H1", "D"]
        max_candles = 5000
        market_data = {}

        try:
            for pair in currency_pairs:
                market_data[pair] = {}
                for tf in timeframes:
                    try:
                        df = self.oanda_api.get_candles_df(pair, count=max_candles, granularity=tf)
                        if df is None or df.empty:
                            continue

                        # Basic metrics
                        mid_c = df['mid_c'].astype(float)
                        current_price = float(mid_c.iloc[-1])
                        volatility = float(mid_c.pct_change().std())
                        price_change_24 = (current_price - float(mid_c.iloc[-24])) if len(df) >= 24 else 0
                        avg_volume = float(df['volume'].mean()) if 'volume' in df.columns else None

                        market_data[pair][tf] = {
                            "recent_prices": df.tail(100).to_dict('records'),
                            "current_price": current_price,
                            "price_change_24": price_change_24,
                            "volatility": volatility,
                            "volume": avg_volume,
                            "total_candles": len(df)
                        }

                    except Exception as e:
                        print(f"[ERROR] Failed to fetch {tf} data for {pair}: {e}")
                        traceback.print_exc()
                        continue

            # Pass the structured market data to your OpenAI strategy generator
            analysis = self.openai_analyzer.generate_trading_strategy(
                market_data=market_data,
                risk_tolerance="high"
            )

            return {
                "timestamp": datetime.now().isoformat(),
                "currency_pairs_analyzed": currency_pairs,
                "market_data": market_data,
                "openai_analysis": analysis
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "currency_pairs": currency_pairs
            }

    def analyze_news_impact(self, months: List[str] = None) -> Dict:
        """
        Analyze forex factory news and their potential market impact using OpenAI.
        
        Args:
            months: List of months to analyze (e.g., ['jan.2025', 'feb.2025'])
        
        Returns:
            News sentiment analysis and market impact assessment
        """
        if months is None:
            months = [ 'jun.2025', 'jul.2025']  # Current month by default

        try:
            all_news_data = []
            
            # Gather news data from forex factory
            for month in months:
                try:
                    news_data = ff.get_monthly_data(month)
                    if news_data is not None and not news_data.empty:
                        # Convert DataFrame to list of dictionaries
                        news_dict = news_data.to_dict('records')
                        all_news_data.extend(news_dict)
                except Exception as e:
                    print(f"Error fetching news for {month}: {e}")
                    continue
            
            if not all_news_data:
                return {
                    "error": "No news data available",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Filter and prepare high-impact news
            high_impact_news = self._filter_high_impact_news(all_news_data)
            
            # Use OpenAI to analyze news sentiment
            sentiment_analysis = self.openai_analyzer.analyze_news_sentiment(high_impact_news)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "months_analyzed": months,
                "total_news_events": len(all_news_data),
                "high_impact_events": len(high_impact_news),
                "openai_sentiment_analysis": sentiment_analysis
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "months": months
            }
    
    def comprehensive_market_report(self, currency_pairs: List[str] = None, 
                                  include_news: bool = True,
                                  analysis_types: List[str] = None) -> Dict:
        """
        Generate a comprehensive market report combining multiple analysis types.
        
        Args:
            currency_pairs: Currency pairs to analyze
            include_news: Whether to include news sentiment analysis
            analysis_types: Types of analysis to perform ("technical", "fundamental", "sentiment", "general")
        
        Returns:
            Comprehensive market report
        """
        if analysis_types is None:
            analysis_types = ["general", "technical", "sentiment"]
        
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "report_type": "comprehensive_market_analysis",
                "analyses": {}
            }
            
            # Market conditions analysis
            market_analysis = self.analyze_current_market_conditions(currency_pairs)
            report["analyses"]["market_conditions"] = market_analysis
            
            # News sentiment analysis
            if include_news:
                news_analysis = self.analyze_news_impact()
                report["analyses"]["news_sentiment"] = news_analysis
            
            # Detailed analysis for each type requested
            if "market_data" in market_analysis and not market_analysis.get("error"):
                for analysis_type in analysis_types:
                    try:
                        # Create sample DataFrame for analysis
                        sample_data = self._create_analysis_dataframe(market_analysis["market_data"])
                        
                        detailed_analysis = self.openai_analyzer.analyze_forex_data(
                            data=sample_data,
                            analysis_type=analysis_type
                        )
                        
                        report["analyses"][f"{analysis_type}_analysis"] = detailed_analysis
                        
                    except Exception as e:
                        report["analyses"][f"{analysis_type}_analysis"] = {
                            "error": str(e),
                            "analysis_type": analysis_type
                        }
            
            return report
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "report_type": "comprehensive_market_analysis"
            }
    
    def _filter_high_impact_news(self, news_data: List[Dict]) -> List[Dict]:
        """Filter news data to focus on high-impact events."""
        high_impact_keywords = [
            'GDP', 'inflation', 'CPI', 'PPI', 'unemployment', 'interest rate', 
            'central bank', 'federal reserve', 'ECB', 'BOJ', 'NFP', 'payroll',
            'PMI', 'manufacturing', 'retail sales', 'trade balance'
        ]
        
        high_impact_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD']
        
        filtered_news = []
        
        for news in news_data:
            if not isinstance(news, dict):
                continue
                
            # Check if currency is major
            currency = news.get('Currency', '')
            if currency not in high_impact_currencies:
                continue
            
            # Check if event contains high-impact keywords
            event = str(news.get('Event', '')).lower()
            if any(keyword.lower() in event for keyword in high_impact_keywords):
                filtered_news.append(news)
            
            # Include events with actual vs forecast data
            elif (news.get('Actual') and news.get('Forecast') and 
                  news.get('Actual') != '' and news.get('Forecast') != ''):
                filtered_news.append(news)
            
        return filtered_news
    
    def _create_analysis_dataframe(self, market_data: Dict) -> pd.DataFrame:
        """Create a DataFrame from market data for OpenAI analysis."""
        rows = []
        
        for pair, data in market_data.items():
            if 'recent_prices' in data:
                for price_record in data['recent_prices']:
                    row = {
                        'currency_pair': pair,
                        'timestamp': price_record.get('time', ''),
                        'open': price_record.get('mid_o', 0),
                        'high': price_record.get('mid_h', 0),
                        'low': price_record.get('mid_l', 0),
                        'close': price_record.get('mid_c', 0),
                        'volume': price_record.get('volume', 0)
                    }
                    rows.append(row)
        
        if not rows:
            # Create minimal DataFrame if no data available
            return pd.DataFrame({
                'currency_pair': list(market_data.keys()),
                'current_price': [data.get('current_price', 0) for data in market_data.values()],
                'price_change_24h': [data.get('price_change_24h', 0) for data in market_data.values()],
                'volatility': [data.get('volatility', 0) for data in market_data.values()]
            })
        
        return pd.DataFrame(rows)

def main():
    """Example usage of the ForexOpenAIAnalysis class."""
    try:
        # Initialize the analysis system
        analyzer = ForexOpenAIAnalysis()
        
        print("=== Forex OpenAI Analysis Demo ===\n")
        
        # Generate comprehensive market report
        print("Generating comprehensive market report...")
        report = analyzer.comprehensive_market_report(
            currency_pairs=['EUR_USD', 'GBP_USD', 'USD_JPY'],
            include_news=True,
            analysis_types=['general', 'technical']
        )
        
        # Print results
        if 'error' not in report:
            print(f"Report generated at: {report['timestamp']}")
            
            for analysis_name, analysis_data in report['analyses'].items():
                print(f"\n--- {analysis_name.upper()} ---")
                if 'error' in analysis_data:
                    print(f"Error: {analysis_data['error']}")
                else:
                    if 'analysis' in analysis_data:
                        print(analysis_data['analysis'])
                    elif 'openai_analysis' in analysis_data:
                        print(analysis_data['openai_analysis'].get('strategy', 'No strategy found'))
                    elif 'openai_sentiment_analysis' in analysis_data:
                        print(analysis_data['openai_sentiment_analysis'].get('sentiment_analysis', 'No sentiment analysis found'))
        else:
            print(f"Error generating report: {report['error']}")
            
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()