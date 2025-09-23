#!/usr/bin/env python3
"""
MCP Finance Server 도구 테스트 스크립트
"""

import asyncio
import sys
sys.path.append('src')

from finance_server import finance_provider

async def test_tools():
    """모든 도구들을 테스트"""
    print("🧪 Testing MCP Finance Tools...\n")

    # 1. Market Summary 테스트
    print("📊 Testing market summary...")
    try:
        market_data = await finance_provider.get_market_summary()
        print(f"✅ Market summary: Found {len(market_data)} indices")
        for symbol, data in list(market_data.items())[:3]:  # 처음 3개만 출력
            if 'error' not in data:
                print(f"   {data['name']}: ${data['price']} ({data['change_percent']:+.2f}%)")
            else:
                print(f"   {symbol}: Error - {data['error']}")
    except Exception as e:
        print(f"❌ Market summary failed: {e}")

    print()

    # 2. Stock Details 테스트
    print("📈 Testing stock details for AAPL...")
    try:
        stock_data = await finance_provider.get_stock_details("AAPL")
        if 'error' not in stock_data:
            print(f"✅ {stock_data['company_name']}: ${stock_data['current_price']}")
            print(f"   Sector: {stock_data['sector']}")
            print(f"   P/E Ratio: {stock_data['pe_ratio']}")
            print(f"   Market Cap: {stock_data['market_cap']}")
        else:
            print(f"❌ Error: {stock_data['error']}")
    except Exception as e:
        print(f"❌ Stock details failed: {e}")

    print()

    # 3. Stock Search 테스트
    print("🔍 Testing stock search for 'Apple'...")
    try:
        search_results = await finance_provider.search_stocks("Apple", limit=3)
        print(f"✅ Found {len(search_results)} results")
        for result in search_results:
            if 'error' not in result:
                print(f"   {result['symbol']}: {result['name']}")
            else:
                print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"❌ Stock search failed: {e}")

    print()

    # 4. Portfolio Analysis 테스트
    print("💼 Testing portfolio analysis...")
    try:
        portfolio_data = await finance_provider.get_portfolio_analysis(
            ["AAPL", "MSFT"],
            [0.6, 0.4]
        )
        if 'error' not in portfolio_data:
            print(f"✅ Portfolio total value: ${portfolio_data['total_value']}")
            print(f"   Number of stocks: {len(portfolio_data['portfolio'])}")
            if 'metrics' in portfolio_data:
                metrics = portfolio_data['metrics']
                print(f"   Expected return: {metrics.get('expected_return', 'N/A')}")
                print(f"   Volatility: {metrics.get('volatility', 'N/A')}")
                print(f"   Sharpe ratio: {metrics.get('sharpe_ratio', 'N/A')}")
        else:
            print(f"❌ Error: {portfolio_data['error']}")
    except Exception as e:
        print(f"❌ Portfolio analysis failed: {e}")

    print()
    print("🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_tools())