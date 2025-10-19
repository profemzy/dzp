#!/usr/bin/env python3
"""
Simple server to serve the web app alongside the API
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import the API app
from src.api.app import app as api_app

# Create main app
app = FastAPI(
    title="DZP IAC Agent - Web Interface",
    description="Web interface for DZP Infrastructure as Code Agent"
)

# Mount the API
app.mount("/api", api_app)

# Get the directory of this file
current_dir = Path(__file__).parent

# Serve static files and the main HTML file
@app.get("/")
async def read_index():
    """Serve the main HTML file"""
    return FileResponse(current_dir / "index.html")

# Mount static files (if we add any CSS, JS, images later)
if (current_dir / "static").exists():
    app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")

# Add CORS for the web app
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DZP IAC Agent Web Server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind the server to (default: 8080)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)"
    )
    
    args = parser.parse_args()
    
    print(f"🚀 Starting DZP IAC Agent Web Server")
    print(f"📍 Web Interface: http://{args.host}:{args.port}")
    print(f"🔗 API Endpoint: http://{args.host}:{args.port}/api")
    print(f"📚 API Docs: http://{args.host}:{args.port}/api/docs")
    print()
    
    uvicorn.run(
        "web_interface.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        access_log=True
    )

if __name__ == "__main__":
    main()
