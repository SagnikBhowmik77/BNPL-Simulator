#!/usr/bin/env python3
"""
BNPL Simulator Application Launcher

This script helps start both the FastAPI backend and Streamlit frontend
for the BNPL Simulator application.
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        print("Backend dependencies (FastAPI, Uvicorn) are installed")
    except ImportError:
        print("Backend dependencies missing. Please install:")
        print("   pip install fastapi uvicorn")
        return False
    
    try:
        import streamlit
        import requests
        import pandas
        import plotly
        print("Frontend dependencies (Streamlit, Requests, Pandas, Plotly) are installed")
    except ImportError:
        print("Frontend dependencies missing. Please install:")
        print("   pip install streamlit requests pandas plotly")
        return False
    
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("Starting FastAPI Backend Server...")
    print("   Backend URL: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/docs")
    
    # Change to the project directory
    os.chdir(Path(__file__).parent)
    
    # Start the backend server with PYTHONPATH set
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path(__file__).parent)
    
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "bnpl_simulator.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000",
        "--reload"
    ], env=env)
    
    return backend_process

def start_frontend():
    """Start the Streamlit frontend."""
    print("Starting Streamlit Frontend...")
    print("   Frontend URL: http://localhost:8501")
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    # Start the frontend
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py"
    ])
    
    return frontend_process

def open_browser():
    """Open the frontend in the default web browser."""
    print("Opening application in browser...")
    time.sleep(3)  # Wait for servers to start
    webbrowser.open("http://localhost:8501")

def main():
    """Main application launcher."""
    print("BNPL Simulator Application Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        sys.exit(1)
    
    print("All dependencies are installed!")
    
    # Ask user what to start
    print("\nWhat would you like to start?")
    print("1. Backend only (FastAPI)")
    print("2. Frontend only (Streamlit)")
    print("3. Both backend and frontend")
    print("4. Exit")
    
    # Default to starting both backend and frontend if no choice is provided
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("Starting Backend Only...")
        backend_process = start_backend()
        print("\nBackend is running. Press Ctrl+C to stop.")
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\nStopping backend...")
            backend_process.terminate()
    
    elif choice == "2":
        print("Starting Frontend Only...")
        print("Note: Backend must be running separately on http://localhost:8000")
        frontend_process = start_frontend()
        print("\nFrontend is running. Press Ctrl+C to stop.")
        try:
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\nStopping frontend...")
            frontend_process.terminate()
    
    elif choice == "3":
        print("Starting Both Backend and Frontend...")
        
        # Start backend
        backend_process = start_backend()
        time.sleep(2)  # Give backend time to start
        
        # Start frontend
        frontend_process = start_frontend()
        
        # Open browser
        open_browser()
        
        print("Application is running!")
        print("   Backend: http://localhost:8000")
        print("   Frontend: http://localhost:8501")
        print("   API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop all services.")
        
        try:
            # Wait for user to stop
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping all services...")
            backend_process.terminate()
            frontend_process.terminate()
            print("All services stopped.")
    
    elif choice == "4":
        print("Goodbye!")
        sys.exit(0)
    
    else:
        print("Invalid choice. Please run the script again.")
        sys.exit(1)

if __name__ == "__main__":
    main()