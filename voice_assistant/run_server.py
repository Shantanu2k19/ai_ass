#!/usr/bin/env python3
"""
Server runner for the Voice Assistant Platform.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_server():
    """Run the server."""
    try:
        from app.main import app
        import uvicorn
        import asyncio
        
        print("Starting Voice Assistant Platform...")
        print("Server will be available at: http://localhost:8000")
        print("API documentation: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        
        # Python 3.6 compatible uvicorn run
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        
        # Use the old asyncio.get_event_loop() for Python 3.6
        loop = asyncio.get_event_loop()
        loop.run_until_complete(server.serve())
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()

