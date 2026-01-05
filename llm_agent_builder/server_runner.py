"""
Server runner module for LLM Agent Builder.

This module handles launching and managing the web server interface.
"""
import sys
import signal
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _handle_shutdown(signum, frame):
    """Signal handler for graceful shutdown."""
    logger.info("Shutting down server gracefully...")
    sys.exit(0)


def run_web_server(host: str = "0.0.0.0", port: int = 7860, reload: bool = False) -> None:
    """
    Launch the web interface server.
    
    Args:
        host: Host address to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 7860)
        reload: Enable auto-reload for development (default: False)
    
    Raises:
        ImportError: If uvicorn is not installed
        Exception: If server fails to start
    """
    try:
        import uvicorn
        
        logger.info(f"Starting LLM Agent Builder web interface at http://{host}:{port}")
        logger.info("Press CTRL+C to stop the server")
        
        # Register graceful shutdown handlers
        signal.signal(signal.SIGINT, _handle_shutdown)
        signal.signal(signal.SIGTERM, _handle_shutdown)
        
        # Run the server
        uvicorn.run(
            "server.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except ImportError:
        logger.error("uvicorn is not installed. Please install it with 'pip install uvicorn'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting web server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Allow running this module directly for testing
    run_web_server()
