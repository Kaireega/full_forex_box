#!/usr/bin/env python3
"""
Shared Data Store - Enables inter-system communication for trading systems

This module provides a centralized data store that allows different trading systems
to share data, signals, alerts, and status information with each other.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from queue import Queue
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/shared_data_store.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SharedDataStore')

@dataclass
class TradeAlert:
    """Trade alert data structure."""
    id: str
    timestamp: str
    pair: str
    signal_type: str  # 'BUY', 'SELL'
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    confidence: float
    risk_reward_ratio: float
    reasoning: str
    status: str  # 'pending', 'executed', 'failed', 'expired'
    source_system: str

@dataclass
class MarketData:
    """Market data structure."""
    pair: str
    timeframe: str
    timestamp: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    source_system: str

@dataclass
class SystemStatus:
    """System status structure."""
    system_name: str
    status: str  # 'running', 'stopped', 'error'
    last_update: str
    active_positions: int
    total_signals: int
    performance_metrics: Dict[str, Any]

class SharedDataStore:
    """Centralized data store for inter-system communication."""
    
    def __init__(self, data_file: str = "shared_data.json"):
        self.data_file = data_file
        self.lock = threading.RLock()
        
        # Data storage
        self.trade_alerts: List[TradeAlert] = []
        self.market_data: Dict[str, List[MarketData]] = {}
        self.system_statuses: Dict[str, SystemStatus] = {}
        self.signals: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
        
        # Communication queue
        self.message_queue = Queue()
        
        # Load existing data
        self._load_data()
        
        # Start background tasks
        self.is_running = False
        self._start_background_tasks()
        
        logger.info("Shared Data Store initialized")
    
    def _start_background_tasks(self):
        """Start background tasks for data management."""
        self.is_running = True
        
        # Start data persistence thread
        threading.Thread(target=self._persist_data_worker, daemon=True).start()
        
        # Start cleanup thread
        threading.Thread(target=self._cleanup_worker, daemon=True).start()
        
        # Start message processing thread
        threading.Thread(target=self._message_processor, daemon=True).start()
        
        logger.info("Background tasks started")
    
    def _load_data(self):
        """Load data from file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Load trade alerts
                self.trade_alerts = [TradeAlert(**alert) for alert in data.get('trade_alerts', [])]
                
                # Load market data
                self.market_data = {}
                for pair, data_list in data.get('market_data', {}).items():
                    self.market_data[pair] = [MarketData(**md) for md in data_list]
                
                # Load system statuses
                self.system_statuses = {}
                for system_name, status_data in data.get('system_statuses', {}).items():
                    self.system_statuses[system_name] = SystemStatus(**status_data)
                
                # Load other data
                self.signals = data.get('signals', [])
                self.performance_metrics = data.get('performance_metrics', {})
                
                logger.info(f"Loaded {len(self.trade_alerts)} trade alerts, {len(self.market_data)} market data pairs")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def _persist_data_worker(self):
        """Background worker to persist data to file."""
        while self.is_running:
            try:
                time.sleep(30)  # Save every 30 seconds
                self._save_data()
            except Exception as e:
                logger.error(f"Error in persist worker: {e}")
    
    def _save_data(self):
        """Save data to file."""
        try:
            with self.lock:
                data = {
                    'trade_alerts': [asdict(alert) for alert in self.trade_alerts],
                    'market_data': {
                        pair: [asdict(md) for md in data_list] 
                        for pair, data_list in self.market_data.items()
                    },
                    'system_statuses': {
                        name: asdict(status) for name, status in self.system_statuses.items()
                    },
                    'signals': self.signals,
                    'performance_metrics': self.performance_metrics,
                    'last_updated': datetime.now().isoformat()
                }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def _cleanup_worker(self):
        """Background worker to cleanup old data."""
        while self.is_running:
            try:
                time.sleep(300)  # Cleanup every 5 minutes
                self._cleanup_old_data()
            except Exception as e:
                logger.error(f"Error in cleanup worker: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data."""
        try:
            with self.lock:
                # Remove expired trade alerts (older than 1 hour)
                current_time = datetime.now()
                expired_alerts = []
                for alert in self.trade_alerts:
                    alert_time = datetime.fromisoformat(alert.timestamp)
                    if (current_time - alert_time).total_seconds() > 3600:
                        expired_alerts.append(alert)
                
                for alert in expired_alerts:
                    self.trade_alerts.remove(alert)
                    alert.status = 'expired'
                
                if expired_alerts:
                    logger.info(f"Cleaned up {len(expired_alerts)} expired alerts")
                
                # Remove old market data (keep last 1000 entries per pair)
                for pair in self.market_data:
                    if len(self.market_data[pair]) > 1000:
                        self.market_data[pair] = self.market_data[pair][-1000:]
                
                # Remove old signals (keep last 1000)
                if len(self.signals) > 1000:
                    self.signals = self.signals[-1000:]
                    
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def _message_processor(self):
        """Process messages from the queue."""
        while self.is_running:
            try:
                # Process messages
                while not self.message_queue.empty():
                    message = self.message_queue.get_nowait()
                    self._handle_message(message)
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in message processor: {e}")
    
    def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages."""
        try:
            msg_type = message.get('type')
            
            if msg_type == 'trade_alert':
                self.add_trade_alert(message['alert'])
            elif msg_type == 'market_data':
                self.add_market_data(message['data'])
            elif msg_type == 'system_status':
                self.update_system_status(message['status'])
            elif msg_type == 'signal':
                self.add_signal(message['signal'])
            elif msg_type == 'performance_update':
                self.update_performance_metrics(message['metrics'])
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    # Public API methods
    
    def add_trade_alert(self, alert: TradeAlert):
        """Add a new trade alert."""
        with self.lock:
            # Remove any existing alert with the same ID
            self.trade_alerts = [a for a in self.trade_alerts if a.id != alert.id]
            self.trade_alerts.append(alert)
            
            logger.info(f"Added trade alert: {alert.signal_type} {alert.pair} @ {alert.entry_price}")
    
    def get_trade_alerts(self, status: Optional[str] = None) -> List[TradeAlert]:
        """Get trade alerts, optionally filtered by status."""
        with self.lock:
            if status:
                return [alert for alert in self.trade_alerts if alert.status == status]
            return self.trade_alerts.copy()
    
    def update_trade_alert_status(self, alert_id: str, new_status: str):
        """Update the status of a trade alert."""
        with self.lock:
            for alert in self.trade_alerts:
                if alert.id == alert_id:
                    alert.status = new_status
                    logger.info(f"Updated alert {alert_id} status to {new_status}")
                    break
    
    def add_market_data(self, data: MarketData):
        """Add new market data."""
        with self.lock:
            if data.pair not in self.market_data:
                self.market_data[data.pair] = []
            self.market_data[data.pair].append(data)
    
    def get_market_data(self, pair: str, limit: int = 100) -> List[MarketData]:
        """Get market data for a specific pair."""
        with self.lock:
            if pair in self.market_data:
                return self.market_data[pair][-limit:]
            return []
    
    def update_system_status(self, status: SystemStatus):
        """Update system status."""
        with self.lock:
            self.system_statuses[status.system_name] = status
    
    def get_system_status(self, system_name: str) -> Optional[SystemStatus]:
        """Get status of a specific system."""
        with self.lock:
            return self.system_statuses.get(system_name)
    
    def get_all_system_statuses(self) -> Dict[str, SystemStatus]:
        """Get all system statuses."""
        with self.lock:
            return self.system_statuses.copy()
    
    def add_signal(self, signal: Dict[str, Any]):
        """Add a new trading signal."""
        with self.lock:
            signal['timestamp'] = datetime.now().isoformat()
            self.signals.append(signal)
    
    def get_signals(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trading signals."""
        with self.lock:
            return self.signals[-limit:]
    
    def update_performance_metrics(self, metrics: Dict[str, Any]):
        """Update performance metrics."""
        with self.lock:
            self.performance_metrics.update(metrics)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        with self.lock:
            return self.performance_metrics.copy()
    
    def send_message(self, message: Dict[str, Any]):
        """Send a message to be processed."""
        self.message_queue.put(message)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all data."""
        with self.lock:
            return {
                'trade_alerts_count': len(self.trade_alerts),
                'pending_alerts_count': len([a for a in self.trade_alerts if a.status == 'pending']),
                'market_data_pairs': list(self.market_data.keys()),
                'active_systems': len([s for s in self.system_statuses.values() if s.status == 'running']),
                'total_signals': len(self.signals),
                'last_updated': datetime.now().isoformat()
            }
    
    def stop(self):
        """Stop the shared data store."""
        self.is_running = False
        self._save_data()
        logger.info("Shared Data Store stopped")

# Global instance
_shared_store = None

def get_shared_store() -> SharedDataStore:
    """Get the global shared data store instance."""
    global _shared_store
    if _shared_store is None:
        _shared_store = SharedDataStore()
    return _shared_store

if __name__ == "__main__":
    # Test the shared data store
    store = get_shared_store()
    
    try:
        # Add some test data
        test_alert = TradeAlert(
            id="test_1",
            timestamp=datetime.now().isoformat(),
            pair="EUR_USD",
            signal_type="BUY",
            entry_price=1.0850,
            stop_loss=1.0820,
            take_profit=1.0900,
            position_size=1000,
            confidence=0.85,
            risk_reward_ratio=1.67,
            reasoning="Strong bullish momentum with RSI oversold bounce",
            status="pending",
            source_system="comprehensive_strategy"
        )
        
        store.add_trade_alert(test_alert)
        
        # Print summary
        summary = store.get_summary()
        print("Shared Data Store Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Keep running
        while True:
            time.sleep(10)
            summary = store.get_summary()
            print(f"Active alerts: {summary['pending_alerts_count']}")
            
    except KeyboardInterrupt:
        print("\nStopping Shared Data Store...")
        store.stop()
        print("Stopped.") 