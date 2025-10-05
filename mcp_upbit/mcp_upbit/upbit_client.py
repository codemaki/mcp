"""Upbit API client for market data."""

import httpx
from typing import Dict, List, Optional, Any
import asyncio


class UpbitClient:
    """Client for Upbit public API."""

    def __init__(self):
        self.base_url = "https://api.upbit.com/v1"
        self.client = httpx.AsyncClient()

    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get all available markets."""
        response = await self.client.get(f"{self.base_url}/market/all")
        response.raise_for_status()
        return response.json()

    async def get_ticker(self, markets: str) -> List[Dict[str, Any]]:
        """Get ticker information for specified markets."""
        params = {"markets": markets}
        response = await self.client.get(f"{self.base_url}/ticker", params=params)
        response.raise_for_status()
        return response.json()

    async def get_orderbook(self, markets: str) -> List[Dict[str, Any]]:
        """Get orderbook for specified markets."""
        params = {"markets": markets}
        response = await self.client.get(f"{self.base_url}/orderbook", params=params)
        response.raise_for_status()
        return response.json()

    async def get_trades(self, market: str, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent trades for a market."""
        params = {"market": market}
        if count:
            params["count"] = count
        response = await self.client.get(f"{self.base_url}/trades/ticks", params=params)
        response.raise_for_status()
        return response.json()

    async def get_candles_minutes(
        self,
        unit: int,
        market: str,
        count: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get minute candles for a market."""
        params = {"market": market}
        if count:
            params["count"] = count
        response = await self.client.get(f"{self.base_url}/candles/minutes/{unit}", params=params)
        response.raise_for_status()
        return response.json()

    async def get_candles_days(
        self,
        market: str,
        count: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get daily candles for a market."""
        params = {"market": market}
        if count:
            params["count"] = count
        response = await self.client.get(f"{self.base_url}/candles/days", params=params)
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()