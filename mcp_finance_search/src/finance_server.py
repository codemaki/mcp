#!/usr/bin/env python3
"""
MCP Finance Tool Server using FastMCP
Provides finance data tools for market analysis and stock information
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

import yfinance as yf
import pandas as pd
import numpy as np
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("Finance Data Server")


class FinanceDataProvider:
    """Finance data provider using yfinance"""

    def __init__(self):
        self.major_indices = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ",
            "^RUT": "Russell 2000",
            "^VIX": "VIX",
            "^TNX": "10-Year Treasury",
            "^FTSE": "FTSE 100",
            "^GDAXI": "DAX",
            "^N225": "Nikkei 225",
            "000001.SS": "Shanghai Composite",
            "^HSI": "Hang Seng"
        }

        self.popular_stocks = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"
        ]

    async def get_market_summary(self) -> Dict[str, Any]:
        """Get overall market summary with major indices"""
        try:
            summary = {}
            tickers = yf.Tickers(list(self.major_indices.keys()))

            for symbol, name in self.major_indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d")
                    info = ticker.info

                    if not hist.empty and len(hist) >= 2:
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-2]
                        change = current_price - prev_price
                        change_pct = (change / prev_price) * 100

                        summary[symbol] = {
                            "name": name,
                            "price": round(current_price, 2),
                            "change": round(change, 2),
                            "change_percent": round(change_pct, 2),
                            "volume": int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0,
                            "market_cap": info.get("marketCap", "N/A"),
                            "currency": info.get("currency", "USD")
                        }
                except Exception as e:
                    logger.warning(f"Failed to get data for {symbol}: {e}")
                    summary[symbol] = {
                        "name": name,
                        "error": str(e)
                    }

            return summary
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {"error": str(e)}

    async def get_stock_details(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """Get detailed information for a specific stock"""
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            hist = ticker.history(period=period)

            if hist.empty:
                return {"error": f"No data found for symbol {symbol}"}

            current_price = hist['Close'].iloc[-1]

            # Calculate technical indicators
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['RSI'] = self._calculate_rsi(hist['Close'])

            # Price statistics
            high_52w = hist['High'].max()
            low_52w = hist['Low'].min()
            volume_avg = hist['Volume'].mean()

            result = {
                "symbol": symbol.upper(),
                "company_name": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "current_price": round(current_price, 2),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "eps": info.get("trailingEps", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "52_week_high": round(high_52w, 2),
                "52_week_low": round(low_52w, 2),
                "average_volume": int(volume_avg),
                "beta": info.get("beta", "N/A"),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange", "N/A"),
                "website": info.get("website", "N/A"),
                "business_summary": info.get("longBusinessSummary", "N/A")[:500] + "..." if info.get("longBusinessSummary") and len(info.get("longBusinessSummary", "")) > 500 else info.get("longBusinessSummary", "N/A"),
                "technical_indicators": {
                    "sma_20": round(hist['SMA_20'].iloc[-1], 2) if not pd.isna(hist['SMA_20'].iloc[-1]) else "N/A",
                    "sma_50": round(hist['SMA_50'].iloc[-1], 2) if not pd.isna(hist['SMA_50'].iloc[-1]) else "N/A",
                    "rsi": round(hist['RSI'].iloc[-1], 2) if not pd.isna(hist['RSI'].iloc[-1]) else "N/A"
                }
            }

            return result
        except Exception as e:
            logger.error(f"Error getting stock details for {symbol}: {e}")
            return {"error": str(e)}

    async def search_stocks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for stocks by company name or symbol"""
        try:
            # This is a simplified search - in production, you might want to use a proper search API
            results = []

            # First, try exact symbol match
            try:
                ticker = yf.Ticker(query.upper())
                info = ticker.info
                if info.get("symbol"):
                    results.append({
                        "symbol": info.get("symbol", query.upper()),
                        "name": info.get("longName", "N/A"),
                        "sector": info.get("sector", "N/A"),
                        "market_cap": info.get("marketCap", "N/A")
                    })
            except:
                pass

            # Add popular stocks that match the query
            for stock in self.popular_stocks:
                if query.upper() in stock or len(results) >= limit:
                    break
                try:
                    ticker = yf.Ticker(stock)
                    info = ticker.info
                    name = info.get("longName", "")
                    if query.lower() in name.lower() or query.upper() in stock:
                        results.append({
                            "symbol": stock,
                            "name": name,
                            "sector": info.get("sector", "N/A"),
                            "market_cap": info.get("marketCap", "N/A")
                        })
                except:
                    continue

            return results[:limit]
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return [{"error": str(e)}]

    async def get_portfolio_analysis(self, symbols: List[str], weights: Optional[List[float]] = None) -> Dict[str, Any]:
        """Analyze a portfolio of stocks"""
        try:
            if not symbols:
                return {"error": "No symbols provided"}

            if weights and len(weights) != len(symbols):
                return {"error": "Number of weights must match number of symbols"}

            if not weights:
                weights = [1.0 / len(symbols)] * len(symbols)

            portfolio_data = {}
            total_value = 0

            for i, symbol in enumerate(symbols):
                try:
                    ticker = yf.Ticker(symbol.upper())
                    hist = ticker.history(period="1mo")
                    info = ticker.info

                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        portfolio_data[symbol.upper()] = {
                            "price": round(current_price, 2),
                            "weight": weights[i],
                            "value": round(current_price * weights[i], 2),
                            "name": info.get("longName", "N/A"),
                            "sector": info.get("sector", "N/A")
                        }
                        total_value += current_price * weights[i]
                except Exception as e:
                    portfolio_data[symbol.upper()] = {"error": str(e)}

            # Calculate portfolio metrics
            returns_data = []
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol.upper())
                    hist = ticker.history(period="1y")
                    if not hist.empty:
                        returns = hist['Close'].pct_change().dropna()
                        returns_data.append(returns)
                except:
                    continue

            portfolio_metrics = {}
            if returns_data:
                portfolio_returns = pd.concat(returns_data, axis=1)
                portfolio_returns.columns = [f"{s}_returns" for s in symbols[:len(returns_data)]]

                # Calculate weighted portfolio returns
                weighted_returns = portfolio_returns.multiply(weights[:len(returns_data)], axis=1).sum(axis=1)

                portfolio_metrics = {
                    "expected_return": round(weighted_returns.mean() * 252, 4),  # Annualized
                    "volatility": round(weighted_returns.std() * np.sqrt(252), 4),  # Annualized
                    "sharpe_ratio": round((weighted_returns.mean() * 252) / (weighted_returns.std() * np.sqrt(252)), 4) if weighted_returns.std() > 0 else 0
                }

            return {
                "portfolio": portfolio_data,
                "total_value": round(total_value, 2),
                "metrics": portfolio_metrics,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return {"error": str(e)}

    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


# Initialize the finance data provider
finance_provider = FinanceDataProvider()


@mcp.tool()
async def get_market_summary() -> Dict[str, Any]:
    """S&P 500, NASDAQ, 다우존스 등 전세계 주요 증시 지수의 실시간 요약 정보를 조회합니다"""
    return await finance_provider.get_market_summary()


@mcp.tool()
async def get_stock_details(symbol: str, period: str = "1mo") -> Dict[str, Any]:
    """
    특정 주식의 상세 정보를 조회합니다 (가격, 재무정보, 기술적 지표 포함)

    Args:
        symbol: 주식 심볼 (예: 'AAPL', 'TSLA')
        period: 히스토리 데이터 기간 ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
    """
    return await finance_provider.get_stock_details(symbol, period)


@mcp.tool()
async def search_stocks(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    회사명 또는 심볼로 주식을 검색합니다

    Args:
        query: 검색어 (회사명 또는 주식 심볼)
        limit: 반환할 최대 결과 수 (기본값: 10)
    """
    return await finance_provider.search_stocks(query, limit)


@mcp.tool()
async def analyze_portfolio(symbols: List[str], weights: Optional[List[float]] = None) -> Dict[str, Any]:
    """
    여러 주식으로 구성된 포트폴리오를 분석합니다 (위험지표, 수익률 계산)

    Args:
        symbols: 주식 심볼 리스트
        weights: 각 주식의 가중치 (합계 1.0, 미제공시 동일 가중치 적용)
    """
    return await finance_provider.get_portfolio_analysis(symbols, weights)


@mcp.tool()
async def get_sector_performance() -> Dict[str, Any]:
    """주요 시장 섹터별 성과 데이터를 조회합니다 (기술, 금융, 헬스케어 등)"""
    sector_etfs = {
        "XLK": "Technology",
        "XLF": "Financial",
        "XLV": "Healthcare",
        "XLE": "Energy",
        "XLI": "Industrial",
        "XLY": "Consumer Discretionary",
        "XLP": "Consumer Staples",
        "XLB": "Materials",
        "XLU": "Utilities",
        "XLRE": "Real Estate"
    }

    try:
        sector_data = {}
        for symbol, sector_name in sector_etfs.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")

                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[0]
                    change_pct = ((current_price - prev_price) / prev_price) * 100

                    sector_data[sector_name] = {
                        "symbol": symbol,
                        "price": round(current_price, 2),
                        "change_percent_5d": round(change_pct, 2),
                        "volume": int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0
                    }
            except Exception as e:
                logger.warning(f"Failed to get data for sector {sector_name}: {e}")
                sector_data[sector_name] = {"error": str(e)}

        return sector_data
    except Exception as e:
        logger.error(f"Error getting sector performance: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # StreamableHTTP 모드로 서버 실행
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")