#!/usr/bin/env python3
"""
Startup script for the Comprehensive Forex Trading Dashboard
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def main():
    print("🚀 Starting Comprehensive Forex Trading Dashboard...")
    print("=" * 60)
    
    # Change to the comprehensive dashboard directory
    dashboard_dir = Path(__file__).parent / "comprehensive_dashboard"
    os.chdir(dashboard_dir)
    
    # Check if app.py exists
    if not Path("app.py").exists():
        print("❌ Error: app.py not found in comprehensive_dashboard directory")
        sys.exit(1)
    
    # Start the Flask application
    try:
        print("📊 Starting Flask application on port 5001...")
        print("🌐 Dashboard will be available at: http://localhost:5001")
        print("=" * 60)
        
        # Run the Flask app
        subprocess.run([sys.executable, "app.py"])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 