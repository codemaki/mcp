# MCP Upbit Server

A Python MCP (Model Context Protocol) server for accessing Upbit cryptocurrency market data.

## Features

- **MCP Protocol Support**: Full MCP server implementation with streamable HTTP transport
- **Upbit Market Data**: Access to real-time market data from Upbit exchange
- **Docker Support**: Containerized deployment with Docker Compose
- **UV Package Manager**: Uses UV for fast Python package management
- **Configurable Port**: Default port 10000, configurable via environment variables

## Available Tools

- `get_markets`: Get all available markets on Upbit
- `get_ticker`: Get ticker information for specified markets
- `get_orderbook`: Get orderbook for specified markets
- `get_trades`: Get recent trades for a market
- `get_candles_minutes`: Get minute candles for a market
- `get_candles_days`: Get daily candles for a market

## Quick Start

### Using Docker Compose (Recommended)

1. Clone this repository
2. Copy environment file: `cp .env.example .env`
3. (Optional) Edit `.env` to change the port
4. Start the server:
```bash
docker-compose up -d
```

The server will be available at `http://localhost:10000`

### Using UV

1. Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Install dependencies: `uv sync`
3. Run the server: `uv run python -m mcp_upbit.http_server`

## Configuration

### Environment Variables

- `PORT`: Server port (default: 10000)
- `HOST`: Server host (default: 0.0.0.0)

### Custom Port

To use a custom port, set the `PORT` environment variable:

```bash
# Using Docker Compose
PORT=8080 docker-compose up -d

# Using UV
PORT=8080 uv run python -m mcp_upbit.http_server
```

## API Endpoints

### Health Check
```bash
GET /health
```

### List Tools
```bash
GET /tools
```

### MCP Endpoint
```bash
POST /mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_ticker",
    "arguments": {
      "markets": "KRW-BTC,KRW-ETH"
    }
  }
}
```

## Example Usage

### Get Bitcoin Ticker
```bash
curl -X POST http://localhost:10000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_ticker",
      "arguments": {
        "markets": "KRW-BTC"
      }
    }
  }'
```

### Get Market List
```bash
curl -X POST http://localhost:10000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_markets",
      "arguments": {}
    }
  }'
```

## Development

### Project Structure
```
mcp_upbit/
├── mcp_upbit/
│   ├── __init__.py
│   ├── server.py          # MCP server implementation
│   ├── http_server.py     # HTTP server wrapper
│   └── upbit_client.py    # Upbit API client
├── pyproject.toml         # UV configuration
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── README.md            # This file
```

### Running Tests

```bash
uv run pytest
```

## License

MIT License