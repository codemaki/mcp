#!/usr/bin/env python3
"""Test script to verify the MCP Upbit server setup."""

import asyncio
import json
import httpx
import time
from mcp_upbit.upbit_client import UpbitClient


async def test_upbit_client():
    """Test the Upbit client directly."""
    print("Testing Upbit client...")
    client = UpbitClient()

    try:
        # Test getting markets
        print("1. Testing get_markets...")
        markets = await client.get_markets()
        print(f"   Found {len(markets)} markets")

        # Test getting ticker for BTC
        print("2. Testing get_ticker for KRW-BTC...")
        ticker = await client.get_ticker("KRW-BTC")
        if ticker:
            print(f"   BTC price: {ticker[0].get('trade_price')} KRW")

        # Test getting orderbook
        print("3. Testing get_orderbook for KRW-BTC...")
        orderbook = await client.get_orderbook("KRW-BTC")
        if orderbook:
            print(f"   Orderbook has {len(orderbook[0].get('orderbook_units', []))} levels")

        print("✅ Upbit client tests passed!")

    except Exception as e:
        print(f"❌ Upbit client test failed: {e}")
        return False
    finally:
        await client.close()

    return True


async def test_http_server():
    """Test the HTTP server if it's running."""
    print("\nTesting HTTP server...")

    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            print("1. Testing health endpoint...")
            response = await client.get("http://localhost:10000/health", timeout=5.0)
            if response.status_code == 200:
                print("   ✅ Health check passed")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False

            # Test tools endpoint
            print("2. Testing tools endpoint...")
            response = await client.get("http://localhost:10000/tools", timeout=5.0)
            if response.status_code == 200:
                tools = response.json()
                print(f"   ✅ Found {len(tools.get('tools', []))} tools")
            else:
                print(f"   ❌ Tools endpoint failed: {response.status_code}")
                return False

            # Test MCP endpoint
            print("3. Testing MCP endpoint...")
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_markets",
                    "arguments": {}
                }
            }
            response = await client.post(
                "http://localhost:10000/mcp",
                json=mcp_request,
                timeout=10.0
            )
            if response.status_code == 200:
                print("   ✅ MCP endpoint test passed")
            else:
                print(f"   ❌ MCP endpoint failed: {response.status_code}")
                return False

            print("✅ HTTP server tests passed!")
            return True

        except httpx.ConnectError:
            print("   ℹ️  HTTP server not running (use 'docker-compose up -d' to start)")
            return False
        except Exception as e:
            print(f"   ❌ HTTP server test failed: {e}")
            return False


def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "="*60)
    print("🚀 MCP Upbit Server Setup Complete!")
    print("="*60)
    print("\n📋 Usage Instructions:")
    print("\n1. Start with Docker Compose (recommended):")
    print("   docker-compose up -d")
    print("\n2. Or start with UV:")
    print("   uv run python -m mcp_upbit.http_server")
    print("\n3. Test the server:")
    print("   curl http://localhost:10000/health")
    print("\n4. Change port (optional):")
    print("   PORT=8080 docker-compose up -d")
    print("\n5. View logs:")
    print("   docker-compose logs -f")
    print("\n📚 Check README.md for detailed API documentation")
    print("\n✨ Available endpoints:")
    print("   - GET  /health     - Health check")
    print("   - GET  /tools      - List available tools")
    print("   - POST /mcp        - MCP JSON-RPC endpoint")


async def main():
    """Main test function."""
    print("🧪 Testing MCP Upbit Server Setup")
    print("=" * 40)

    # Test Upbit client
    client_success = await test_upbit_client()

    # Test HTTP server (if running)
    server_success = await test_http_server()

    # Print results
    print("\n" + "="*40)
    print("📊 Test Results:")
    print(f"   Upbit Client: {'✅ PASS' if client_success else '❌ FAIL'}")
    print(f"   HTTP Server:  {'✅ PASS' if server_success else 'ℹ️  NOT RUNNING'}")

    # Print usage instructions
    print_usage_instructions()


if __name__ == "__main__":
    asyncio.run(main())