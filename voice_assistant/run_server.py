#!/usr/bin/env python3
"""
Alternative server runner for Python 3.6 compatibility.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_server():
    """Run the server with Python 3.6 compatibility."""
    try:
        from app.main import app
        import uvicorn
        
        print("Starting Voice Assistant Platform...")
        print("Server will be available at: http://localhost:8000")
        print("API documentation: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        
        # Use uvicorn directly with Python 3.6 compatible settings
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()

