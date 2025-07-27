#!/usr/bin/env python3
"""
Unified Trading System - Integrates Stream Bot with Analysis Classes

This system combines your stream_bot with analysis classes
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
from queue import Queue

# Add project root to path
sys.path.append("./")

# Import stream_bot components
from stream_bot.stream_bot import run_bot
from stream_bot.trade_settings_collection import tradeSettingsCollection
from stream_bot.candle_worker import CandleWorker
from stream_bot.trade_worker import TradeWorker
from stream_bot.price_processor import PriceProcessor
from stream_example.stream_prices import PriceStreamer

# Import analysis classes
try:
    from analysis.unified_trading_analyzer import UnifiedTradingAnalyzer, AnalysisMode, TradingSignal
    from analysis.realtime_trading_analyzer import RealtimeTradingAnalyzer
    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False
    print("⚠️  Analysis classes not available - running in stream_bot-only mode")

from api.oanda_api import OandaApi
from models.trade_decision import TradeDecision
from models.trade_settings import TradeSettings
import constants.defs as defs
from infrastructure.log_wrapper import LogWrapper

class TradingMode(Enum):
    """Trading modes for the unified system."""
    STREAM_BOT_ONLY = "stream_bot_only"
    ANALYSIS_ONLY = "analysis_only"
    HYBRID = "hybrid"
    AI_ENHANCED = "ai_enhanced"

@dataclass
class UnifiedTradeDecision:
    """Unified trade decision combining stream_bot and analysis signals."""
    timestamp: str
    pair: str
    signal: str  # BUY, SELL, NONE
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    reasoning: str
    
    # Source information
    stream_bot_signal: Optional[str] = None
    analysis_signal: Optional[str] = None
    ai_confidence: Optional[float] = None
    
    # Risk management
    position_size: float = 1.0
    risk_level: str = "MEDIUM"

class UnifiedTradingSystem:
    """
    Unified trading system that combines:
    - Your stream_bot (real-time price streaming + technical analysis)
    - Analysis classes (AI-powered analysis)
    - Risk management and position sizing
    """
    
    def __init__(self, mode: TradingMode = TradingMode.HYBRID, 
                 analysis_mode: AnalysisMode = AnalysisMode.ADAPTIVE):
        """
        Initialize the unified trading system.
        
        Args:
            mode: Trading mode (stream_bot_only, analysis_only, hybrid, ai_enhanced)
            analysis_mode: Analysis mode for AI analysis
        """
        self.mode = mode
        self.analysis_mode = analysis_mode
        
        # Initialize stream_bot components
        self.load_stream_bot_settings()
        self.api = OandaApi()
        self.logger = LogWrapper("UnifiedTradingSystem")
        
        # Stream bot components
        self.shared_prices = {}
        self.shared_prices_events = {}
        self.shared_prices_lock = threading.Lock()
        self.candle_queue = Queue()
        self.trade_work_queue = Queue()
        self.threads = []
        
        # Analysis components (if available)
        self.analysis_available = ANALYSIS_AVAILABLE
        if self.analysis_available:
            self.unified_analyzer = UnifiedTradingAnalyzer(
                update_interval=300,  # 5 minutes
                mode=analysis_mode
            )
            self.realtime_analyzer = RealtimeTradingAnalyzer(update_interval=60)
        
        # Trading parameters
        self.currency_pairs = tradeSettingsCollection.pair_list()
        self.trade_history = []
        self.is_running = False
        
        # Risk management
        self.max_concurrent_trades = 3
        self.max_daily_trades = 10
        self.daily_trade_count = {}
        self.open_trades = {}
        
        # Signal thresholds
        self.min_confidence_threshold = 0.7
        self.stream_bot_signal_weight = 0.6
        self.analysis_signal_weight = 0.4
        
        print(f"🤖 Unified Trading System initialized")
        print(f"📊 Mode: {mode.value.upper()}")
        print(f"🎯 Pairs: {', '.join(self.currency_pairs)}")
        print(f"🤖 Analysis Available: {self.analysis_available}")
        print(f"📈 Stream Bot Granularity: {tradeSettingsCollection.granularity}")
        print(f"💰 Trade Risk: {tradeSettingsCollection.trade_risk}")
    
    def load_stream_bot_settings(self):
        """Load stream_bot settings."""
        tradeSettingsCollection.load_trade_settings()
        tradeSettingsCollection.print_collection()
    
    def start_trading(self):
        """Start the unified trading system."""
        self.is_running = True
        
        print(f"🚀 Starting Unified Trading System")
        print(f"📈 Mode: {self.mode.value.upper()}")
        print("=" * 60)
        
        # Initialize stream bot components
        self._initialize_stream_bot()
        
        # Start analysis threads if available
        if self.analysis_available and self.mode != TradingMode.STREAM_BOT_ONLY:
            self._start_analysis_threads()
        
        # Start main trading loop
        trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        trading_thread.start()
        
        return trading_thread
    
    def stop_trading(self):
        """Stop the unified trading system."""
        self.is_running = False
        
        # Stop all threads
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1)
        
        if self.analysis_available:
            self.unified_analyzer.stop_analysis()
            self.realtime_analyzer.stop_realtime_analysis()
        
        print("🛑 Unified Trading System stopped")
    
    def _initialize_stream_bot(self):
        """Initialize stream_bot components."""
        # Initialize shared prices and events
        for pair in self.currency_pairs:
            self.shared_prices_events[pair] = threading.Event()
            self.shared_prices[pair] = {}
        
        # Start price streamer
        price_stream_t = PriceStreamer(self.shared_prices, self.shared_prices_lock, self.shared_prices_events)
        price_stream_t.daemon = True
        self.threads.append(price_stream_t)
        price_stream_t.start()
        
        # Start price processors
        for pair in self.currency_pairs:
            processing_t = PriceProcessor(
                self.shared_prices, 
                self.shared_prices_lock, 
                self.shared_prices_events, 
                self.candle_queue,
                f"PriceProcessor_{pair}", 
                pair,
                tradeSettingsCollection.granularity
            )
            processing_t.daemon = True
            self.threads.append(processing_t)
            processing_t.start()
        
        # Start candle workers if not analysis-only mode
        if self.mode != TradingMode.ANALYSIS_ONLY:
            for pair in self.currency_pairs:
                candle_t = CandleWorker(
                    tradeSettingsCollection.get_trade_settings(pair),
                    self.candle_queue,
                    self.trade_work_queue,
                    tradeSettingsCollection.granularity
                )
                candle_t.daemon = True
                self.threads.append(candle_t)
                candle_t.start()
        
        # Start trade worker
        trade_worker_t = TradeWorker(self.trade_work_queue, tradeSettingsCollection.trade_risk)
        trade_worker_t.daemon = True
        self.threads.append(trade_worker_t)
        trade_worker_t.start()
    
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
                
                # Process signals from stream_bot and analysis
                self._process_signals()
                
                # Sleep to maintain interval
                elapsed_time = time.time() - start_time
                sleep_time = max(0, 30 - elapsed_time)  # 30-second intervals
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                self.logger.logger.error(f"Error in trading loop: {e}")
                time.sleep(5)
    
    def _process_signals(self):
        """Process signals from both stream_bot and analysis."""
        try:
            # Get stream_bot signals (from trade work queue)
            stream_bot_signals = []
            while not self.trade_work_queue.empty():
                try:
                    signal = self.trade_work_queue.get_nowait()
                    if isinstance(signal, TradeDecision):
                        stream_bot_signals.append(signal)
                except:
                    break
            
            # Get analysis signals (if available)
            analysis_signals = []
            if self.analysis_available:
                analysis_signals = self._get_analysis_signals()
            
            # Combine and process signals
            for pair in self.currency_pairs:
                stream_signal = next((s for s in stream_bot_signals if s.pair == pair), None)
                analysis_signal = next((s for s in analysis_signals if s.currency_pair == pair), None)
                
                unified_decision = self._combine_signals(pair, stream_signal, analysis_signal)
                
                if unified_decision and self._validate_trade_decision(unified_decision):
                    self._execute_trade(unified_decision)
                    
        except Exception as e:
            self.logger.logger.error(f"Error processing signals: {e}")
    
    def _get_analysis_signals(self) -> List[TradingSignal]:
        """Get trading signals from AI analysis."""
        try:
            signals = []
            
            if self.mode == TradingMode.AI_ENHANCED:
                # Use unified analyzer for enhanced analysis
                if hasattr(self.unified_analyzer, 'signals_history') and self.unified_analyzer.signals_history:
                    signals.extend(self.unified_analyzer.signals_history[-10:])  # Last 10 signals
            else:
                # Use realtime analyzer for basic analysis
                if hasattr(self.realtime_analyzer, 'signals_history') and self.realtime_analyzer.signals_history:
                    signals.extend(self.realtime_analyzer.signals_history[-10:])  # Last 10 signals
            
            return signals
        except Exception as e:
            self.logger.logger.error(f"Error getting analysis signals: {e}")
            return []
    
    def _combine_signals(self, pair: str, stream_signal: Optional[TradeDecision], 
                        analysis_signal: Optional[TradingSignal]) -> Optional[UnifiedTradeDecision]:
        """Combine stream_bot and analysis signals based on trading mode."""
        try:
            if self.mode == TradingMode.STREAM_BOT_ONLY:
                return self._stream_bot_only_decision(pair, stream_signal)
            
            elif self.mode == TradingMode.ANALYSIS_ONLY:
                return self._analysis_only_decision(pair, analysis_signal)
            
            elif self.mode == TradingMode.HYBRID:
                return self._hybrid_decision(pair, stream_signal, analysis_signal)
            
            elif self.mode == TradingMode.AI_ENHANCED:
                return self._ai_enhanced_decision(pair, stream_signal, analysis_signal)
            
            return None
            
        except Exception as e:
            self.logger.logger.error(f"Error combining signals for {pair}: {e}")
            return None
    
    def _stream_bot_only_decision(self, pair: str, stream_signal: Optional[TradeDecision]) -> Optional[UnifiedTradeDecision]:
        """Create decision based only on stream_bot signal."""
        if stream_signal and stream_signal.signal != defs.NONE:
            return UnifiedTradeDecision(
                timestamp=datetime.now().isoformat(),
                pair=pair,
                signal=stream_signal.signal,
                confidence=0.8,  # High confidence for stream_bot signals
                entry_price=stream_signal.price,
                stop_loss=stream_signal.sl,
                take_profit=stream_signal.tp,
                reasoning="Stream bot technical analysis signal",
                stream_bot_signal=stream_signal.signal
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
    
    def _hybrid_decision(self, pair: str, stream_signal: Optional[TradeDecision], 
                        analysis_signal: Optional[TradingSignal]) -> Optional[UnifiedTradeDecision]:
        """Create decision combining both stream_bot and analysis signals."""
        stream_confidence = 0.0
        analysis_confidence = 0.0
        
        if stream_signal and stream_signal.signal != defs.NONE:
            stream_confidence = 0.8
        
        if analysis_signal and analysis_signal.signal_type != 'HOLD':
            analysis_confidence = analysis_signal.confidence
        
        # Weighted combination
        total_confidence = (stream_confidence * self.stream_bot_signal_weight + 
                          analysis_confidence * self.analysis_signal_weight)
        
        if total_confidence >= self.min_confidence_threshold:
            # Use stream_bot signal as primary, enhance with analysis
            if stream_signal and stream_signal.signal != defs.NONE:
                reasoning = f"Stream Bot: {stream_signal.signal}"
                if analysis_signal:
                    reasoning += f" | AI: {analysis_signal.signal_type} ({analysis_signal.confidence:.2f})"
                
                return UnifiedTradeDecision(
                    timestamp=datetime.now().isoformat(),
                    pair=pair,
                    signal=stream_signal.signal,
                    confidence=total_confidence,
                    entry_price=stream_signal.price,
                    stop_loss=stream_signal.sl,
                    take_profit=stream_signal.tp,
                    reasoning=reasoning,
                    stream_bot_signal=stream_signal.signal,
                    analysis_signal=analysis_signal.signal_type if analysis_signal else None,
                    ai_confidence=analysis_signal.confidence if analysis_signal else None
                )
        
        return None
    
    def _ai_enhanced_decision(self, pair: str, stream_signal: Optional[TradeDecision], 
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
        elif stream_signal and stream_signal.signal != defs.NONE:
            # Fall back to stream_bot signal
            return self._stream_bot_only_decision(pair, stream_signal)
        
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
        """Execute the trade decision using stream_bot's trade worker."""
        try:
            # Create TradeDecision object for the stream_bot's trade worker
            trade_decision = TradeDecision({
                'PAIR': decision.pair,
                'SIGNAL': decision.signal,
                'mid_c': decision.entry_price,
                'SL': decision.stop_loss,
                'TP': decision.take_profit,
                'LOSS': abs(decision.entry_price - decision.stop_loss)
            })
            
            # Add to trade work queue for stream_bot's trade worker to process
            self.trade_work_queue.put(trade_decision)
            
            # Update tracking
            today = datetime.now().strftime('%Y-%m-%d')
            self.daily_trade_count[today] = self.daily_trade_count.get(today, 0) + 1
            
            # Log success
            self.logger.logger.info(f"✅ Trade queued: {decision.pair} {decision.signal} "
                                  f"(Confidence: {decision.confidence:.2f})")
            self.logger.logger.info(f"   Entry: {decision.entry_price}, "
                                  f"SL: {decision.stop_loss}, TP: {decision.take_profit}")
            self.logger.logger.info(f"   Reasoning: {decision.reasoning}")
            
            # Store in history
            self.trade_history.append(decision)
            
        except Exception as e:
            self.logger.logger.error(f"Error executing trade: {e}")
    
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
            'analysis_available': self.analysis_available,
            'stream_bot_granularity': tradeSettingsCollection.granularity,
            'trade_risk': tradeSettingsCollection.trade_risk
        }

def main():
    """Main function to run the unified trading system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Trading System with Stream Bot")
    parser.add_argument('--mode', choices=['stream_bot_only', 'analysis_only', 'hybrid', 'ai_enhanced'],
                       default='hybrid', help='Trading mode')
    parser.add_argument('--analysis-mode', choices=['basic', 'adaptive', 'comprehensive'],
                       default='adaptive', help='Analysis mode')
    
    args = parser.parse_args()
    
    # Convert string to enum
    mode_map = {
        'stream_bot_only': TradingMode.STREAM_BOT_ONLY,
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