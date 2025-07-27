#!/usr/bin/env python3
"""
Unified Trading System - Integrates Bot with Analysis Classes

This system combines your existing trading bot with analysis classes
to place trades based on both technical signals and AI analysis.
"""

import sys
import os
import time
import threading
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add project root to path
sys.path.append("./")

from bot.bot import Bot
from bot.technicals_manager import get_trade_decision
from bot.trade_manager import place_trade
from api.oanda_api import OandaApi
from models.trade_settings import TradeSettings
from models.trade_decision import TradeDecision
import constants.defs as defs
from infrastructure.log_wrapper import LogWrapper

# Import analysis classes
try:
    from analysis.unified_trading_analyzer import UnifiedTradingAnalyzer, AnalysisMode, TradingSignal
    from analysis.realtime_trading_analyzer import RealtimeTradingAnalyzer
    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False
    print("⚠️  Analysis classes not available - running in bot-only mode")

class TradingMode(Enum):
    """Trading modes for the unified system."""
    BOT_ONLY = "bot_only"
    ANALYSIS_ONLY = "analysis_only"
    HYBRID = "hybrid"
    AI_ENHANCED = "ai_enhanced"

@dataclass
class UnifiedTradeDecision:
    """Unified trade decision combining bot and analysis signals."""
    timestamp: str
    pair: str
    signal: str  # BUY, SELL, NONE
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    reasoning: str
    
    # Source information
    bot_signal: Optional[str] = None
    analysis_signal: Optional[str] = None
    ai_confidence: Optional[float] = None
    
    # Risk management
    position_size: float = 1.0
    risk_level: str = "MEDIUM"

class UnifiedTradingSystem:
    """
    Unified trading system that combines:
    - Your existing trading bot (technical analysis)
    - Analysis classes (AI-powered analysis)
    - Risk management and position sizing
    """
    
    def __init__(self, mode: TradingMode = TradingMode.HYBRID, 
                 analysis_mode: AnalysisMode = AnalysisMode.ADAPTIVE):
        """
        Initialize the unified trading system.
        
        Args:
            mode: Trading mode (bot_only, analysis_only, hybrid, ai_enhanced)
            analysis_mode: Analysis mode for AI analysis
        """
        self.mode = mode
        self.analysis_mode = analysis_mode
        
        # Initialize components
        self.bot = Bot()
        self.api = OandaApi()
        self.logger = LogWrapper("UnifiedTradingSystem")
        
        # Analysis components (if available)
        self.analysis_available = ANALYSIS_AVAILABLE
        if self.analysis_available:
            self.unified_analyzer = UnifiedTradingAnalyzer(
                update_interval=300,  # 5 minutes
                mode=analysis_mode
            )
            self.realtime_analyzer = RealtimeTradingAnalyzer(update_interval=60)
        
        # Trading parameters
        self.currency_pairs = list(self.bot.trade_settings.keys())
        self.trade_history = []
        self.is_running = False
        
        # Risk management
        self.max_concurrent_trades = 3
        self.max_daily_trades = 10
        self.daily_trade_count = {}
        self.open_trades = {}
        
        # Signal thresholds
        self.min_confidence_threshold = 0.7
        self.bot_signal_weight = 0.6
        self.analysis_signal_weight = 0.4
        
        print(f"🤖 Unified Trading System initialized")
        print(f"📊 Mode: {mode.value.upper()}")
        print(f"🎯 Pairs: {', '.join(self.currency_pairs)}")
        print(f"🤖 Analysis Available: {self.analysis_available}")
    
    def start_trading(self):
        """Start the unified trading system."""
        self.is_running = True
        
        print(f"🚀 Starting Unified Trading System")
        print(f"📈 Mode: {self.mode.value.upper()}")
        print("=" * 60)
        
        # Start analysis threads if available
        if self.analysis_available and self.mode != TradingMode.BOT_ONLY:
            self._start_analysis_threads()
        
        # Start main trading loop
        trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        trading_thread.start()
        
        return trading_thread
    
    def stop_trading(self):
        """Stop the unified trading system."""
        self.is_running = False
        
        if self.analysis_available:
            self.unified_analyzer.stop_analysis()
            self.realtime_analyzer.stop_realtime_analysis()
        
        print("🛑 Unified Trading System stopped")
    
    def _start_analysis_threads(self):
        """Start analysis threads for AI-powered analysis."""
        if self.mode in [TradingMode.ANALYSIS_ONLY, TradingMode.HYBRID, TradingMode.AI_ENHANCED]:
            print("🤖 Starting AI analysis threads...")
            
            # Start unified analyzer
            self.unified_analyzer.start_analysis(self.currency_pairs)
            
            # Start realtime analyzer for minute-level signals
            self.realtime_analyzer.start_realtime_analysis(self.currency_pairs)
    
    def _trading_loop(self):
        """Main trading loop that processes signals and places trades."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Reset daily counters if needed
                self._reset_daily_counters_if_needed()
                
                # Process new candles from bot
                triggered_pairs = self.bot.candle_manager.update_timings()
                
                if triggered_pairs:
                    for pair in triggered_pairs:
                        if self._should_analyze_pair(pair):
                            self._process_pair_signals(pair)
                
                # Sleep to maintain interval
                elapsed_time = time.time() - start_time
                sleep_time = max(0, 30 - elapsed_time)  # 30-second intervals
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                self.logger.logger.error(f"Error in trading loop: {e}")
                time.sleep(5)
    
    def _process_pair_signals(self, pair: str):
        """Process signals for a specific currency pair."""
        try:
            # Get bot signal (existing technical analysis)
            bot_signal = self._get_bot_signal(pair)
            
            # Get analysis signal (AI-powered analysis)
            analysis_signal = None
            if self.analysis_available and self.mode != TradingMode.BOT_ONLY:
                analysis_signal = self._get_analysis_signal(pair)
            
            # Combine signals based on mode
            unified_decision = self._combine_signals(pair, bot_signal, analysis_signal)
            
            if unified_decision and self._validate_trade_decision(unified_decision):
                self._execute_trade(unified_decision)
                
        except Exception as e:
            self.logger.logger.error(f"Error processing signals for {pair}: {e}")
    
    def _get_bot_signal(self, pair: str) -> Optional[TradeDecision]:
        """Get trading signal from the existing bot."""
        try:
            last_time = self.bot.candle_manager.timings[pair].last_time
            trade_decision = get_trade_decision(
                last_time, 
                pair, 
                self.bot.GRANULARITY, 
                self.api,
                self.bot.trade_settings[pair], 
                self.bot.log_message
            )
            return trade_decision
        except Exception as e:
            self.logger.logger.error(f"Error getting bot signal for {pair}: {e}")
            return None
    
    def _get_analysis_signal(self, pair: str) -> Optional[TradingSignal]:
        """Get trading signal from AI analysis."""
        try:
            if self.mode == TradingMode.AI_ENHANCED:
                # Use unified analyzer for enhanced analysis
                if hasattr(self.unified_analyzer, 'signals_history') and self.unified_analyzer.signals_history:
                    # Get the latest signal for this pair
                    for signal in reversed(self.unified_analyzer.signals_history):
                        if signal.currency_pair == pair:
                            return signal
            else:
                # Use realtime analyzer for basic analysis
                if hasattr(self.realtime_analyzer, 'signals_history') and self.realtime_analyzer.signals_history:
                    for signal in reversed(self.realtime_analyzer.signals_history):
                        if signal.currency_pair == pair:
                            return signal
            
            return None
        except Exception as e:
            self.logger.logger.error(f"Error getting analysis signal for {pair}: {e}")
            return None
    
    def _combine_signals(self, pair: str, bot_signal: Optional[TradeDecision], 
                        analysis_signal: Optional[TradingSignal]) -> Optional[UnifiedTradeDecision]:
        """Combine bot and analysis signals based on trading mode."""
        try:
            if self.mode == TradingMode.BOT_ONLY:
                return self._bot_only_decision(pair, bot_signal)
            
            elif self.mode == TradingMode.ANALYSIS_ONLY:
                return self._analysis_only_decision(pair, analysis_signal)
            
            elif self.mode == TradingMode.HYBRID:
                return self._hybrid_decision(pair, bot_signal, analysis_signal)
            
            elif self.mode == TradingMode.AI_ENHANCED:
                return self._ai_enhanced_decision(pair, bot_signal, analysis_signal)
            
            return None
            
        except Exception as e:
            self.logger.logger.error(f"Error combining signals for {pair}: {e}")
            return None
    
    def _bot_only_decision(self, pair: str, bot_signal: Optional[TradeDecision]) -> Optional[UnifiedTradeDecision]:
        """Create decision based only on bot signal."""
        if bot_signal and bot_signal.signal != defs.NONE:
            return UnifiedTradeDecision(
                timestamp=datetime.now().isoformat(),
                pair=pair,
                signal=bot_signal.signal,
                confidence=0.8,  # High confidence for bot signals
                entry_price=bot_signal.price,
                stop_loss=bot_signal.sl,
                take_profit=bot_signal.tp,
                reasoning="Bot technical analysis signal",
                bot_signal=bot_signal.signal
            )
        return None
    
    def _analysis_only_decision(self, pair: str, analysis_signal: Optional[TradingSignal]) -> Optional[UnifiedTradeDecision]:
        """Create decision based only on analysis signal."""
        if analysis_signal and analysis_signal.signal_type != 'HOLD':
            return UnifiedTradeDecision(
                timestamp=datetime.now().isoformat(),
                pair=pair,
                signal=analysis_signal.signal_type,
                confidence=analysis_signal.confidence,
                entry_price=analysis_signal.entry_price,
                stop_loss=analysis_signal.stop_loss,
                take_profit=analysis_signal.take_profit,
                reasoning=analysis_signal.reasoning,
                analysis_signal=analysis_signal.signal_type,
                ai_confidence=analysis_signal.confidence
            )
        return None
    
    def _hybrid_decision(self, pair: str, bot_signal: Optional[TradeDecision], 
                        analysis_signal: Optional[TradingSignal]) -> Optional[UnifiedTradeDecision]:
        """Create decision combining both bot and analysis signals."""
        bot_confidence = 0.0
        analysis_confidence = 0.0
        
        if bot_signal and bot_signal.signal != defs.NONE:
            bot_confidence = 0.8
        
        if analysis_signal and analysis_signal.signal_type != 'HOLD':
            analysis_confidence = analysis_signal.confidence
        
        # Weighted combination
        total_confidence = (bot_confidence * self.bot_signal_weight + 
                          analysis_confidence * self.analysis_signal_weight)
        
        if total_confidence >= self.min_confidence_threshold:
            # Use bot signal as primary, enhance with analysis
            if bot_signal and bot_signal.signal != defs.NONE:
                reasoning = f"Bot: {bot_signal.signal}"
                if analysis_signal:
                    reasoning += f" | AI: {analysis_signal.signal_type} ({analysis_signal.confidence:.2f})"
                
                return UnifiedTradeDecision(
                    timestamp=datetime.now().isoformat(),
                    pair=pair,
                    signal=bot_signal.signal,
                    confidence=total_confidence,
                    entry_price=bot_signal.price,
                    stop_loss=bot_signal.sl,
                    take_profit=bot_signal.tp,
                    reasoning=reasoning,
                    bot_signal=bot_signal.signal,
                    analysis_signal=analysis_signal.signal_type if analysis_signal else None,
                    ai_confidence=analysis_signal.confidence if analysis_signal else None
                )
        
        return None
    
    def _ai_enhanced_decision(self, pair: str, bot_signal: Optional[TradeDecision], 
                            analysis_signal: Optional[TradingSignal]) -> Optional[UnifiedTradeDecision]:
        """Create AI-enhanced decision with higher weight on analysis."""
        if analysis_signal and analysis_signal.confidence >= 0.75:
            # High-confidence AI signal takes precedence
            return UnifiedTradeDecision(
                timestamp=datetime.now().isoformat(),
                pair=pair,
                signal=analysis_signal.signal_type,
                confidence=analysis_signal.confidence,
                entry_price=analysis_signal.entry_price,
                stop_loss=analysis_signal.stop_loss,
                take_profit=analysis_signal.take_profit,
                reasoning=f"AI Enhanced: {analysis_signal.reasoning}",
                analysis_signal=analysis_signal.signal_type,
                ai_confidence=analysis_signal.confidence
            )
        elif bot_signal and bot_signal.signal != defs.NONE:
            # Fall back to bot signal
            return self._bot_only_decision(pair, bot_signal)
        
        return None
    
    def _validate_trade_decision(self, decision: UnifiedTradeDecision) -> bool:
        """Validate trade decision before execution."""
        try:
            # Check daily trade limit
            today = datetime.now().strftime('%Y-%m-%d')
            if self.daily_trade_count.get(today, 0) >= self.max_daily_trades:
                self.logger.logger.info(f"Daily trade limit reached for {today}")
                return False
            
            # Check if trade already open for this pair
            if decision.pair in self.open_trades:
                self.logger.logger.info(f"Trade already open for {decision.pair}")
                return False
            
            # Check confidence threshold
            if decision.confidence < self.min_confidence_threshold:
                return False
            
            # Check concurrent trade limit
            if len(self.open_trades) >= self.max_concurrent_trades:
                self.logger.logger.info("Maximum concurrent trades reached")
                return False
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Error validating trade decision: {e}")
            return False
    
    def _execute_trade(self, decision: UnifiedTradeDecision):
        """Execute the trade decision."""
        try:
            # Create TradeDecision object for the bot's trade manager
            trade_decision = TradeDecision({
                'PAIR': decision.pair,
                'SIGNAL': decision.signal,
                'mid_c': decision.entry_price,
                'SL': decision.stop_loss,
                'TP': decision.take_profit,
                'LOSS': abs(decision.entry_price - decision.stop_loss)
            })
            
            # Place trade using existing bot infrastructure
            trade_id = place_trade(
                trade_decision,
                self.api,
                self.bot.log_message,
                self.bot.log_to_error,
                self.bot.trade_risk
            )
            
            if trade_id:
                # Update tracking
                self.open_trades[decision.pair] = trade_id
                today = datetime.now().strftime('%Y-%m-%d')
                self.daily_trade_count[today] = self.daily_trade_count.get(today, 0) + 1
                
                # Log success
                self.logger.logger.info(f"✅ Trade executed: {decision.pair} {decision.signal} "
                                      f"(Confidence: {decision.confidence:.2f})")
                self.logger.logger.info(f"   Entry: {decision.entry_price}, "
                                      f"SL: {decision.stop_loss}, TP: {decision.take_profit}")
                self.logger.logger.info(f"   Reasoning: {decision.reasoning}")
                
                # Store in history
                self.trade_history.append(decision)
                
            else:
                self.logger.logger.error(f"❌ Failed to execute trade for {decision.pair}")
                
        except Exception as e:
            self.logger.logger.error(f"Error executing trade: {e}")
    
    def _should_analyze_pair(self, pair: str) -> bool:
        """Check if pair should be analyzed."""
        return pair in self.currency_pairs
    
    def _reset_daily_counters_if_needed(self):
        """Reset daily counters if it's a new day."""
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.daily_trade_count:
            self.daily_trade_count = {today: 0}
    
    def get_status(self) -> Dict:
        """Get current system status."""
        return {
            'mode': self.mode.value,
            'is_running': self.is_running,
            'pairs': self.currency_pairs,
            'open_trades': len(self.open_trades),
            'daily_trades': self.daily_trade_count.get(datetime.now().strftime('%Y-%m-%d'), 0),
            'total_trades': len(self.trade_history),
            'analysis_available': self.analysis_available
        }

def main():
    """Main function to run the unified trading system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Trading System")
    parser.add_argument('--mode', choices=['bot_only', 'analysis_only', 'hybrid', 'ai_enhanced'],
                       default='hybrid', help='Trading mode')
    parser.add_argument('--analysis-mode', choices=['basic', 'adaptive', 'comprehensive'],
                       default='adaptive', help='Analysis mode')
    
    args = parser.parse_args()
    
    # Convert string to enum
    mode_map = {
        'bot_only': TradingMode.BOT_ONLY,
        'analysis_only': TradingMode.ANALYSIS_ONLY,
        'hybrid': TradingMode.HYBRID,
        'ai_enhanced': TradingMode.AI_ENHANCED
    }
    
    analysis_mode_map = {
        'basic': AnalysisMode.BASIC,
        'adaptive': AnalysisMode.ADAPTIVE,
        'comprehensive': AnalysisMode.COMPREHENSIVE
    }
    
    # Initialize and start system
    system = UnifiedTradingSystem(
        mode=mode_map[args.mode],
        analysis_mode=analysis_mode_map[args.analysis_mode]
    )
    
    try:
        system.start_trading()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Unified Trading System...")
        system.stop_trading()

if __name__ == "__main__":
    main()