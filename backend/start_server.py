#!/usr/bin/env python3
"""
Simple Flask server test to verify our universal playlist system works
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Change to the backend directory
os.chdir(r"C:\Users\kaz.roche\Desktop\music-intelligence\backend")

# Import and start the server
from simple_working import app

if __name__ == '__main__':
    print("🚀 Starting Server for Testing...")
    app.run(host='0.0.0.0', port=5001, debug=False)  # No debug to avoid restarts