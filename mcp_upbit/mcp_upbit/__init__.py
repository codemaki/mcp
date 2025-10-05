"""MCP Upbit server for market data."""

__version__ = "0.1.0"

from .fastmcp_server import main as run_fastmcp_server

__all__ = ["run_fastmcp_server"]