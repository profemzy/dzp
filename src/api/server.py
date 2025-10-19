#!/usr/bin/env python3
"""
FastAPI server entry point for DZP IAC Agent
"""

import uvicorn
from src.api.app import app
from src.core.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main entry point for the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DZP IAC Agent API Server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
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
    
    logger.info(f"Starting DZP IAC Agent API server on {args.host}:{args.port}")
    
    uvicorn.run(
        "src.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        access_log=True
    )


if __name__ == "__main__":
    main()
