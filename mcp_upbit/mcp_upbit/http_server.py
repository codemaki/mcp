"""HTTP server wrapper for MCP Upbit server with streamable HTTP transport."""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json as json_lib

from .upbit_client import UpbitClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Upbit HTTP Server", description="HTTP server for Upbit market data")

# Upbit client instance
upbit_client = UpbitClient()


# Pydantic models for requests
class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


async def handle_list_tools() -> List[Dict[str, Any]]:
    """List available tools."""
    return [
        {
            "name": "get_markets",
            "description": "Get all available markets on Upbit",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_ticker",
            "description": "Get ticker information for specified markets",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "markets": {
                        "type": "string",
                        "description": "Comma-separated market codes (e.g., 'KRW-BTC,KRW-ETH')"
                    }
                },
                "required": ["markets"]
            }
        },
        {
            "name": "get_orderbook",
            "description": "Get orderbook for specified markets",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "markets": {
                        "type": "string",
                        "description": "Comma-separated market codes (e.g., 'KRW-BTC,KRW-ETH')"
                    }
                },
                "required": ["markets"]
            }
        },
        {
            "name": "get_trades",
            "description": "Get recent trades for a market",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "market": {
                        "type": "string",
                        "description": "Market code (e.g., 'KRW-BTC')"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of trades to retrieve (max 500)",
                        "minimum": 1,
                        "maximum": 500
                    }
                },
                "required": ["market"]
            }
        },
        {
            "name": "get_candles_minutes",
            "description": "Get minute candles for a market",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "unit": {
                        "type": "integer",
                        "description": "Minute unit (1, 3, 5, 10, 15, 30, 60, 240)",
                        "enum": [1, 3, 5, 10, 15, 30, 60, 240]
                    },
                    "market": {
                        "type": "string",
                        "description": "Market code (e.g., 'KRW-BTC')"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of candles to retrieve (max 200)",
                        "minimum": 1,
                        "maximum": 200
                    }
                },
                "required": ["unit", "market"]
            }
        },
        {
            "name": "get_candles_days",
            "description": "Get daily candles for a market",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "market": {
                        "type": "string",
                        "description": "Market code (e.g., 'KRW-BTC')"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of candles to retrieve (max 200)",
                        "minimum": 1,
                        "maximum": 200
                    }
                },
                "required": ["market"]
            }
        }
    ]


async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Handle tool calls."""
    try:
        if name == "get_markets":
            data = await upbit_client.get_markets()
            return json_lib.dumps(data, ensure_ascii=False, indent=2)

        elif name == "get_ticker":
            markets = arguments.get("markets")
            if not markets:
                raise ValueError("markets parameter is required")
            data = await upbit_client.get_ticker(markets)
            return json_lib.dumps(data, ensure_ascii=False, indent=2)

        elif name == "get_orderbook":
            markets = arguments.get("markets")
            if not markets:
                raise ValueError("markets parameter is required")
            data = await upbit_client.get_orderbook(markets)
            return json_lib.dumps(data, ensure_ascii=False, indent=2)

        elif name == "get_trades":
            market = arguments.get("market")
            if not market:
                raise ValueError("market parameter is required")
            count = arguments.get("count")
            data = await upbit_client.get_trades(market, count)
            return json_lib.dumps(data, ensure_ascii=False, indent=2)

        elif name == "get_candles_minutes":
            unit = arguments.get("unit")
            market = arguments.get("market")
            if not unit or not market:
                raise ValueError("unit and market parameters are required")
            count = arguments.get("count")
            data = await upbit_client.get_candles_minutes(unit, market, count)
            return json_lib.dumps(data, ensure_ascii=False, indent=2)

        elif name == "get_candles_days":
            market = arguments.get("market")
            if not market:
                raise ValueError("market parameter is required")
            count = arguments.get("count")
            data = await upbit_client.get_candles_days(market, count)
            return json_lib.dumps(data, ensure_ascii=False, indent=2)

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return f"Error: {str(e)}"


@app.post("/mcp")
async def mcp_endpoint(request: JSONRPCRequest):
    """Handle MCP JSON-RPC requests."""
    try:
        # Handle the request directly with the server
        if request.method == "initialize":
            # MCP 초기화 응답
            response = JSONRPCResponse(
                jsonrpc="2.0",
                id=request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "upbit-mcp-server",
                        "version": "0.1.0"
                    }
                }
            )
            return response
        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})

            result = await handle_call_tool(tool_name, arguments)

            response = JSONRPCResponse(
                jsonrpc="2.0",
                id=request.id,
                result={"content": [{"type": "text", "text": result}]}
            )
            return response
        elif request.method == "tools/list":
            tools = await handle_list_tools()
            response = JSONRPCResponse(
                jsonrpc="2.0",
                id=request.id,
                result={"tools": tools}
            )
            return response
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported method: {request.method}")

    except Exception as e:
        logger.error(f"Error handling MCP request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-upbit-server"}


@app.get("/tools")
async def list_tools():
    """List available tools."""
    tools = await handle_list_tools()
    return {"tools": tools}




def run_server(host: str = "0.0.0.0", port: int = 10000):
    """Run the HTTP server."""
    logger.info(f"Starting MCP Upbit server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


def main():
    """Main entry point."""
    port = int(os.getenv("PORT", 10000))
    host = os.getenv("HOST", "0.0.0.0")
    run_server(host, port)


if __name__ == "__main__":
    main()