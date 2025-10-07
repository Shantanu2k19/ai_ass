#!/usr/bin/env python3
"""
Server runner for the Voice Assistant Platform.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
reload_enabled = True #os.environ.get("RELOAD", "false").lower() == "true"

def run_server():
    """Run the server."""
    try:
        from app.main import app
        import uvicorn
        import asyncio
        
        print("Starting Server -> http://localhost:8000")
        
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8080,
            log_level="info",
            access_log=True,
            reload=reload_enabled
        )
        server = uvicorn.Server(config)
        
        #asyncio
        asyncio.run(server.serve())
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()

