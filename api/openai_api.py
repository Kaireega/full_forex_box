import openai
import os
import json
import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime
import constants.defs as defs

class OpenAIAnalyzer:
    """
    OpenAI-powered analysis for forex trading data and market insights.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to get from environment variable.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either as parameter or OPENAI_API_KEY environment variable")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Using GPT-4o-mini for cost efficiency
    
    def analyze_forex_data(self, data: pd.DataFrame, analysis_type: str = "general") -> Dict:
        """
        Analyze forex data using OpenAI.
        
        Args:
            data: DataFrame containing forex data
            analysis_type: Type of analysis ("general", "technical", "fundamental", "sentiment")
        
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Prepare data summary for OpenAI
            data_summary = self._prepare_data_summary(data)
            
            # Get appropriate prompt based on analysis type
            prompt = self._get_analysis_prompt(data_summary, analysis_type)
            
            # Make OpenAI API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert forex trading analyst with deep knowledge of market patterns, technical analysis, and economic indicators."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis_result = response.choices[0].message.content
            
            return {
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "data_summary": data_summary,
                "analysis": analysis_result,
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_news_sentiment(self, news_data: List[Dict]) -> Dict:
        """
        Analyze forex factory news sentiment using OpenAI.
        
        Args:
            news_data: List of news events with titles and descriptions
        
        Returns:
            Sentiment analysis results
        """
        try:
            # Prepare news summary
            news_summary = self._prepare_news_summary(news_data)
            
            prompt = f"""
            Analyze the sentiment and potential forex market impact of the following economic news events:
            
            {news_summary}
            
            Please provide:
            1. Overall market sentiment (bullish/bearish/neutral)
            2. Currency-specific impacts
            3. Risk assessment (high/medium/low)
            4. Trading recommendations
            5. Key events to watch
            
            Format your response as structured analysis with clear sections.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert forex news analyst specializing in interpreting economic events and their market impact."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            return {
                "analysis_type": "news_sentiment",
                "timestamp": datetime.now().isoformat(),
                "news_count": len(news_data),
                "sentiment_analysis": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": "news_sentiment",
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_trading_strategy(self, market_data: Dict, risk_tolerance: str = "medium") -> Dict:
        """
        Generate trading strategy recommendations using OpenAI.
        
        Args:
            market_data: Dictionary containing current market conditions
            risk_tolerance: Risk tolerance level ("low", "medium", "high")
        
        Returns:
            Trading strategy recommendations
        """
        try:
            prompt = f"""
            Based on the following market data and risk tolerance, generate a comprehensive forex trading strategy:
            
            Market Data:
            {json.dumps(market_data, indent=2, default=str)}
            
            Risk Tolerance: {risk_tolerance}
            
            Please provide:
            1. Recommended currency pairs to trade
            2. Entry and exit strategies
            3. Risk management guidelines
            4. Position sizing recommendations
            5. Market outlook and key levels to watch
            6. Stop loss and take profit suggestions
            
            Format your response as a structured trading plan.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional forex trading strategist with expertise in risk management and market analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            return {
                "analysis_type": "trading_strategy",
                "timestamp": datetime.now().isoformat(),
                "risk_tolerance": risk_tolerance,
                "strategy": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": "trading_strategy",
                "timestamp": datetime.now().isoformat()
            }
    
    def _prepare_data_summary(self, data: pd.DataFrame) -> str:
        """Prepare a concise summary of DataFrame for OpenAI analysis."""
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Dataset: {len(data)} rows, {len(data.columns)} columns")
        summary_parts.append(f"Columns: {list(data.columns)}")
        
        # Data types and basic stats
        if not data.empty:
            summary_parts.append("\nData Overview:")
            summary_parts.append(data.describe().to_string())
            
            # Recent data sample
            summary_parts.append("\nRecent Data Sample:")
            summary_parts.append(data.tail(10).to_string())
        
        return "\n".join(summary_parts)
    
    def _prepare_news_summary(self, news_data: List[Dict]) -> str:
        """Prepare news data summary for analysis."""
        if not news_data:
            return "No news data provided"
        
        summary_parts = []
        for i, news in enumerate(news_data[:20]):  # Limit to 20 most recent
            event_str = f"{i+1}. "
            if 'Date' in news:
                event_str += f"[{news['Date']}] "
            if 'Currency' in news:
                event_str += f"{news['Currency']}: "
            if 'Event' in news:
                event_str += f"{news['Event']}"
            if 'Actual' in news:
                event_str += f" (Actual: {news['Actual']})"
            if 'Forecast' in news:
                event_str += f" (Forecast: {news['Forecast']})"
            if 'Previous' in news:
                event_str += f" (Previous: {news['Previous']})"
            
            summary_parts.append(event_str)
        
        return "\n".join(summary_parts)
    
    def _get_analysis_prompt(self, data_summary: str, analysis_type: str) -> str:
        """Generate appropriate prompt based on analysis type."""
        base_prompt = f"Analyze the following forex market data:\n\n{data_summary}\n\n"
        
        if analysis_type == "technical":
            return base_prompt + """
            Provide a technical analysis focusing on:
            1. Price action patterns
            2. Support and resistance levels
            3. Trend analysis
            4. Volume indicators
            5. Technical indicators insights
            6. Entry/exit recommendations
            """
        
        elif analysis_type == "fundamental":
            return base_prompt + """
            Provide a fundamental analysis focusing on:
            1. Economic indicators impact
            2. Central bank policies
            3. Geopolitical factors
            4. Market sentiment drivers
            5. Long-term outlook
            6. Currency strength assessment
            """
        
        elif analysis_type == "sentiment":
            return base_prompt + """
            Provide a sentiment analysis focusing on:
            1. Market mood and psychology
            2. Risk-on vs risk-off sentiment
            3. Investor confidence levels
            4. News impact assessment
            5. Social sentiment indicators
            6. Contrarian opportunities
            """
        
        else:  # general
            return base_prompt + """
            Provide a comprehensive market analysis including:
            1. Overall market condition assessment
            2. Key trends and patterns
            3. Notable price movements
            4. Risk factors and opportunities
            5. Trading recommendations
            6. Market outlook
            """