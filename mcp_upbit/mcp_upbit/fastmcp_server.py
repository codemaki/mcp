"""FastMCP server for Upbit market data."""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP, Context
import httpx

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP app
mcp = FastMCP("Upbit Market Data")


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


# Global client instance
upbit_client = UpbitClient()

# 다국어 지원을 위한 설명 딕셔너리
TOOL_DESCRIPTIONS = {
    "get_markets": {
        "en": "Get all available markets on Upbit",
        "ko": "업비트의 모든 사용 가능한 마켓 조회"
    },
    "get_ticker": {
        "en": "Get ticker information for specified markets",
        "ko": "지정된 마켓의 현재가 정보 조회"
    },
    "get_orderbook": {
        "en": "Get orderbook for specified markets",
        "ko": "지정된 마켓의 호가 정보 조회"
    },
    "get_trades": {
        "en": "Get recent trades for a market",
        "ko": "마켓의 최근 체결 내역 조회"
    },
    "get_candles_minutes": {
        "en": "Get minute candles for a market",
        "ko": "마켓의 분봉 데이터 조회"
    },
    "get_candles_days": {
        "en": "Get daily candles for a market",
        "ko": "마켓의 일봉 데이터 조회"
    }
}

# 다국어 에러 메시지
ERROR_MESSAGES = {
    "markets_required": {
        "en": "markets parameter is required",
        "ko": "markets 파라미터가 필요합니다"
    },
    "market_required": {
        "en": "market parameter is required",
        "ko": "market 파라미터가 필요합니다"
    },
    "unit_market_required": {
        "en": "unit and market parameters are required",
        "ko": "unit과 market 파라미터가 필요합니다"
    },
    "count_range_500": {
        "en": "count must be between 1 and 500",
        "ko": "count는 1~500 사이의 값이어야 합니다"
    },
    "count_range_200": {
        "en": "count must be between 1 and 200",
        "ko": "count는 1~200 사이의 값이어야 합니다"
    },
    "unit_invalid": {
        "en": "unit must be one of [1, 3, 5, 10, 15, 30, 60, 240]",
        "ko": "unit은 [1, 3, 5, 10, 15, 30, 60, 240] 중 하나여야 합니다"
    }
}

def get_tool_description(tool_name: str, lang: str = "en") -> str:
    """언어에 따른 도구 설명 반환"""
    descriptions = TOOL_DESCRIPTIONS.get(tool_name, {})
    return descriptions.get(lang, descriptions.get("en", tool_name))

def get_error_message(error_key: str, lang: str = "en") -> str:
    """언어에 따른 에러 메시지 반환"""
    messages = ERROR_MESSAGES.get(error_key, {})
    return f"Error: {messages.get(lang, messages.get('en', error_key))}"

def detect_language(ctx: Context = None) -> str:
    """요청 컨텍스트에서 언어 감지"""
    if ctx and hasattr(ctx, 'request_headers'):
        # Accept-Language 헤더에서 언어 감지
        accept_lang = ctx.request_headers.get('accept-language', '')
        if 'ko' in accept_lang.lower() or 'kr' in accept_lang.lower():
            return "ko"
    return "en"


@mcp.tool()
async def get_markets(ctx: Context) -> str:
    """업비트의 모든 사용 가능한 마켓 조회 / Get all available markets on Upbit"""
    lang = detect_language(ctx)
    try:
        data = await upbit_client.get_markets()
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error getting markets: {e}")
        if lang == "ko":
            return f"오류: {str(e)}"
        return f"Error: {str(e)}"


@mcp.tool()
async def get_ticker(markets: str, ctx: Context) -> str:
    """지정된 마켓의 현재가 정보 조회 / Get ticker information for specified markets.

    Args:
        markets: 쉼표로 구분된 마켓 코드 (예: 'KRW-BTC,KRW-ETH') / Comma-separated market codes (e.g., 'KRW-BTC,KRW-ETH')
    """
    lang = detect_language(ctx)
    try:
        data = await upbit_client.get_ticker(markets)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error getting ticker: {e}")
        if lang == "ko":
            return f"오류: {str(e)}"
        return f"Error: {str(e)}"


@mcp.tool()
async def get_orderbook(markets: str, ctx: Context) -> str:
    """지정된 마켓의 호가 정보 조회 / Get orderbook for specified markets.

    Args:
        markets: 쉼표로 구분된 마켓 코드 (예: 'KRW-BTC,KRW-ETH') / Comma-separated market codes (e.g., 'KRW-BTC,KRW-ETH')
    """
    lang = detect_language(ctx)
    try:
        data = await upbit_client.get_orderbook(markets)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error getting orderbook: {e}")
        if lang == "ko":
            return f"오류: {str(e)}"
        return f"Error: {str(e)}"


@mcp.tool()
async def get_trades(market: str, count: Optional[int] = None, ctx: Context = None) -> str:
    """마켓의 최근 체결 내역 조회 / Get recent trades for a market.

    Args:
        market: 마켓 코드 (예: 'KRW-BTC') / Market code (e.g., 'KRW-BTC')
        count: 조회할 체결 건수 (최대 500) / Number of trades to retrieve (max 500)
    """
    lang = detect_language(ctx)
    try:
        if count is not None and (count < 1 or count > 500):
            return get_error_message("count_range_500", lang)
        data = await upbit_client.get_trades(market, count)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        if lang == "ko":
            return f"오류: {str(e)}"
        return f"Error: {str(e)}"


@mcp.tool()
async def get_candles_minutes(unit: int, market: str, count: Optional[int] = None, ctx: Context = None) -> str:
    """마켓의 분봉 데이터 조회 / Get minute candles for a market.

    Args:
        unit: 분 단위 (1, 3, 5, 10, 15, 30, 60, 240) / Minute unit (1, 3, 5, 10, 15, 30, 60, 240)
        market: 마켓 코드 (예: 'KRW-BTC') / Market code (e.g., 'KRW-BTC')
        count: 조회할 캔들 개수 (최대 200) / Number of candles to retrieve (max 200)
    """
    lang = detect_language(ctx)
    try:
        if unit not in [1, 3, 5, 10, 15, 30, 60, 240]:
            return get_error_message("unit_invalid", lang)
        if count is not None and (count < 1 or count > 200):
            return get_error_message("count_range_200", lang)
        data = await upbit_client.get_candles_minutes(unit, market, count)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error getting minute candles: {e}")
        if lang == "ko":
            return f"오류: {str(e)}"
        return f"Error: {str(e)}"


@mcp.tool()
async def get_candles_days(market: str, count: Optional[int] = None, ctx: Context = None) -> str:
    """마켓의 일봉 데이터 조회 / Get daily candles for a market.

    Args:
        market: 마켓 코드 (예: 'KRW-BTC') / Market code (e.g., 'KRW-BTC')
        count: 조회할 캔들 개수 (최대 200) / Number of candles to retrieve (max 200)
    """
    lang = detect_language(ctx)
    try:
        if count is not None and (count < 1 or count > 200):
            return get_error_message("count_range_200", lang)
        data = await upbit_client.get_candles_days(market, count)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error getting daily candles: {e}")
        if lang == "ko":
            return f"오류: {str(e)}"
        return f"Error: {str(e)}"


def main():
    """Main entry point for the FastMCP server."""
    port = int(os.getenv("PORT", 10000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting FastMCP Upbit server with StreamableHTTP on {host}:{port}")

    # FastMCP에서 HTTP 서버 실행 (StreamableHTTP transport)
    mcp.run(transport="http", host=host, port=port)


if __name__ == "__main__":
    main()