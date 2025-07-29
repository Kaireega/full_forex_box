#!/usr/bin/env python3
"""
System Coordinator - Manages communication between different trading systems
"""

import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Any
import requests
from queue import Queue
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_coordinator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SystemCoordinator')

class SystemCoordinator:
    def __init__(self):
        self.systems = {
            'comprehensive_dashboard': {'status': 'unknown', 'last_check': None, 'port': 5001},
            'stream_bot': {'status': 'unknown', 'last_check': None},
            'data_streaming': {'status': 'unknown', 'last_check': None},
            'comprehensive_strategy': {'status': 'unknown', 'last_check': None, 'alerts': []}
        }
        self.communication_queue = Queue()
        self.is_running = False
        
    def start(self):
        """Start the system coordinator."""
        self.is_running = True
        logger.info("🚀 System Coordinator starting...")
        
        # Start monitoring threads
        threading.Thread(target=self._monitor_systems, daemon=True).start()
        threading.Thread(target=self._process_communications, daemon=True).start()
        threading.Thread(target=self._sync_alerts, daemon=True).start()
        
        logger.info("✅ System Coordinator started")
        
        try:
            status_counter = 0
            while self.is_running:
                time.sleep(10)
                status_counter += 1
                # Only print status every 6 minutes (36 iterations * 10 seconds)
                if status_counter % 36 == 0:
                    self._print_status()
        except KeyboardInterrupt:
            logger.info("🛑 Stopping System Coordinator...")
            self.stop()
    
    def stop(self):
        """Stop the system coordinator."""
        self.is_running = False
        logger.info("✅ System Coordinator stopped")
    
    def _monitor_systems(self):
        """Monitor all trading systems."""
        while self.is_running:
            try:
                # Check comprehensive dashboard
                try:
                    response = requests.get('http://localhost:5001/api/system/status', timeout=5)
                    if response.status_code == 200:
                        self.systems['comprehensive_dashboard']['status'] = 'running'
                        self.systems['comprehensive_dashboard']['last_check'] = datetime.now()
                    else:
                        self.systems['comprehensive_dashboard']['status'] = 'error'
                except:
                    self.systems['comprehensive_dashboard']['status'] = 'stopped'
                
                # Check comprehensive strategy (via PID file)
                try:
                    with open('.comprehensive_strategy.pid', 'r') as f:
                        pid = int(f.read().strip())
                    # Use ps command for macOS compatibility
                    import subprocess
                    result = subprocess.run(['ps', '-p', str(pid)], capture_output=True, text=True)
                    if result.returncode == 0:
                        self.systems['comprehensive_strategy']['status'] = 'running'
                        self.systems['comprehensive_strategy']['last_check'] = datetime.now()
                    else:
                        self.systems['comprehensive_strategy']['status'] = 'stopped'
                except:
                    self.systems['comprehensive_strategy']['status'] = 'stopped'
                
                # Check stream bot (via PID file)
                try:
                    with open('.stream_bot.pid', 'r') as f:
                        pid = int(f.read().strip())
                    # Use ps command for macOS compatibility
                    import subprocess
                    result = subprocess.run(['ps', '-p', str(pid)], capture_output=True, text=True)
                    if result.returncode == 0:
                        self.systems['stream_bot']['status'] = 'running'
                        self.systems['stream_bot']['last_check'] = datetime.now()
                    else:
                        self.systems['stream_bot']['status'] = 'stopped'
                except:
                    self.systems['stream_bot']['status'] = 'stopped'
                
                # Check data streaming (via PID file)
                try:
                    with open('.data_streaming.pid', 'r') as f:
                        pid = int(f.read().strip())
                    # Use ps command for macOS compatibility
                    import subprocess
                    result = subprocess.run(['ps', '-p', str(pid)], capture_output=True, text=True)
                    if result.returncode == 0:
                        self.systems['data_streaming']['status'] = 'running'
                        self.systems['data_streaming']['last_check'] = datetime.now()
                    else:
                        self.systems['data_streaming']['status'] = 'stopped'
                except:
                    self.systems['data_streaming']['status'] = 'stopped'
                
            except Exception as e:
                logger.error(f"Error monitoring systems: {e}")
            
            time.sleep(30)  # Check every 30 seconds
    
    def _process_communications(self):
        """Process inter-system communications."""
        while self.is_running:
            try:
                # Process any queued communications
                while not self.communication_queue.empty():
                    message = self.communication_queue.get_nowait()
                    self._handle_message(message)
                
                # Sync data between systems
                self._sync_data()
                
            except Exception as e:
                logger.error(f"Error processing communications: {e}")
            
            time.sleep(5)
    
    def _sync_alerts(self):
        """Sync trade alerts between systems."""
        while self.is_running:
            try:
                # Get alerts from comprehensive dashboard
                if self.systems['comprehensive_dashboard']['status'] == 'running':
                    try:
                        response = requests.get('http://localhost:5001/api/alerts', timeout=5)
                        if response.status_code == 200:
                            alerts = response.json().get('alerts', [])
                            self.systems['comprehensive_strategy']['alerts'] = alerts
                            
                            # Log new alerts
                            for alert in alerts:
                                if alert.get('status') == 'pending':
                                    logger.info(f"🚨 New Trade Alert: {alert['signal_type']} {alert['pair']} @ {alert['entry_price']}")
                    except Exception as e:
                        logger.debug(f"Could not fetch alerts: {e}")
                
            except Exception as e:
                logger.error(f"Error syncing alerts: {e}")
            
            time.sleep(10)  # Sync every 10 seconds
    
    def _handle_message(self, message: Dict[str, Any]):
        """Handle inter-system messages."""
        try:
            msg_type = message.get('type')
            if msg_type == 'trade_alert':
                logger.info(f"📢 Broadcasting trade alert: {message.get('pair')}")
                # Could broadcast to other systems here
            elif msg_type == 'system_status':
                logger.info(f"📊 System status update: {message.get('system')}")
            elif msg_type == 'error':
                logger.error(f"❌ System error: {message.get('error')}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def _sync_data(self):
        """Sync data between different systems."""
        try:
            # Sync account data
            if self.systems['comprehensive_dashboard']['status'] == 'running':
                try:
                    response = requests.get('http://localhost:5001/api/account', timeout=5)
                    if response.status_code == 200:
                        account_data = response.json()
                        # Could store this for other systems to access
                except:
                    pass
            
            # Sync market data
            if self.systems['comprehensive_dashboard']['status'] == 'running':
                try:
                    response = requests.get('http://localhost:5001/api/prices/EUR_USD/M15/100', timeout=5)
                    if response.status_code == 200:
                        market_data = response.json()
                        # Could share this with other systems
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error syncing data: {e}")
    
    def _print_status(self):
        """Print current system status."""
        logger.info("📊 System Status (every 6 minutes):")
        for system, info in self.systems.items():
            status_emoji = "✅" if info['status'] == 'running' else "❌" if info['status'] == 'stopped' else "⚠️"
            logger.info(f"  {status_emoji} {system}: {info['status']}")
        
        # Show active alerts
        alerts = self.systems['comprehensive_strategy']['alerts']
        if alerts:
            pending_alerts = [a for a in alerts if a.get('status') == 'pending']
            if pending_alerts:
                logger.info(f"🚨 Active Trade Alerts: {len(pending_alerts)}")
                for alert in pending_alerts[:3]:
                    logger.info(f"  - {alert['signal_type']} {alert['pair']} @ {alert['entry_price']}")

if __name__ == "__main__":
    coordinator = SystemCoordinator()
    coordinator.start()
