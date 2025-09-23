# MCP Finance Tool Server

FastMCP를 사용한 금융 데이터 조회를 위한 MCP Tool Server입니다. yfinance 라이브러리를 통해 실시간 주식 데이터, 시장 정보, 포트폴리오 분석 등의 기능을 HTTP API로 제공합니다.

## 기능

### 📊 제공되는 도구들

1. **get_market_summary**: 전세계 주요 증시 요약 정보
   - S&P 500, NASDAQ, Dow Jones, Russell 2000
   - VIX, 10년 국채 수익률
   - FTSE 100, DAX, Nikkei 225, 상해종합지수, 항셍지수

2. **get_stock_details**: 개별 주식 상세 정보
   - 현재 가격, 시가총액, PER, EPS
   - 52주 최고/최저가, 베타
   - 기술적 지표 (SMA 20/50, RSI)
   - 회사 정보 및 사업 요약

3. **search_stocks**: 주식 검색
   - 회사명 또는 심볼로 검색
   - 섹터 및 시가총액 정보 포함

4. **analyze_portfolio**: 포트폴리오 분석
   - 여러 주식의 가중 분석
   - 기대수익률, 변동성, 샤프비율 계산

5. **get_sector_performance**: 섹터별 성과 분석
   - 주요 10개 섹터 ETF 성과
   - 5일간 변화율 포함

## 설치 및 실행

### uv를 사용한 로컬 설치

```bash
# 프로젝트 클론
git clone <repository-url>
cd mcp_finance_search

# uv로 의존성 설치
uv sync

# HTTP 서버 실행 (포트 8000)
uv run python src/finance_server.py
```

서버가 실행되면 `http://localhost:8000`에서 접근할 수 있습니다.

### Docker를 사용한 배포

```bash
# Docker 이미지 빌드
docker build -t mcp-finance-server .

# 컨테이너 실행
docker run -d --name mcp-finance-server mcp-finance-server

# 또는 docker-compose 사용
docker-compose up -d
```

Docker로 실행하면 `http://localhost:8000`에서 접근할 수 있습니다.

## 사용 예시

### MCP 클라이언트와 연동

이 서버를 Claude Desktop이나 다른 MCP 클라이언트와 HTTP 방식으로 연동할 수 있습니다.

**HTTP 연결 설정:**
- URL: `http://localhost:8000`
- Transport: HTTP
- Content-Type: `application/json`

**Claude Desktop 설정 (HTTP 모드):**
```json
{
  "mcpServers": {
    "finance": {
      "url": "http://localhost:8000",
      "transport": "http"
    }
  }
}
```

### HTTP API 사용 예시

HTTP POST 요청으로 도구들을 직접 호출할 수 있습니다:

```bash
# 시장 요약 정보 조회
curl -X POST http://localhost:8000/tools/get_market_summary \
  -H "Content-Type: application/json" \
  -d '{}'

# 애플 주식 상세 정보 조회
curl -X POST http://localhost:8000/tools/get_stock_details \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "period": "1y"}'

# 테슬라 검색
curl -X POST http://localhost:8000/tools/search_stocks \
  -H "Content-Type: application/json" \
  -d '{"query": "Tesla", "limit": 5}'

# 포트폴리오 분석
curl -X POST http://localhost:8000/tools/analyze_portfolio \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL"], "weights": [0.5, 0.3, 0.2]}'

# 섹터 성과 분석
curl -X POST http://localhost:8000/tools/get_sector_performance \
  -H "Content-Type: application/json" \
  -d '{}'
```

### MCP 클라이언트에서 사용

```python
# MCP 클라이언트 코드 예시
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # HTTP 연결은 MCP 클라이언트 라이브러리에 따라 다름
    async with ClientSession() as session:
        # 시장 요약 정보 조회
        result = await session.call_tool("get_market_summary", {})
        print(result)
```

## API 참조

### get_market_summary()

전 세계 주요 증시의 실시간 요약 정보를 반환합니다.

**반환값:**
```json
{
  "^GSPC": {
    "name": "S&P 500",
    "price": 4500.25,
    "change": 15.30,
    "change_percent": 0.34,
    "volume": 3500000000,
    "market_cap": "N/A",
    "currency": "USD"
  }
}
```

### get_stock_details(symbol, period="1mo")

개별 주식의 상세 정보를 반환합니다.

**매개변수:**
- `symbol` (str): 주식 심볼 (예: "AAPL")
- `period` (str): 기간 ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")

**반환값:**
```json
{
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "sector": "Technology",
  "current_price": 175.43,
  "market_cap": 2800000000000,
  "pe_ratio": 28.5,
  "technical_indicators": {
    "sma_20": 170.25,
    "sma_50": 165.80,
    "rsi": 55.2
  }
}
```

### search_stocks(query, limit=10)

회사명 또는 심볼로 주식을 검색합니다.

**매개변수:**
- `query` (str): 검색어
- `limit` (int): 최대 결과 수

### analyze_portfolio(symbols, weights=None)

포트폴리오를 분석하고 위험 지표를 계산합니다.

**매개변수:**
- `symbols` (List[str]): 주식 심볼 리스트
- `weights` (List[float], optional): 가중치 리스트

### get_sector_performance()

주요 섹터별 성과를 반환합니다.

## 개발

### 테스트 실행

```bash
uv run pytest
```

### 코드 포맷팅

```bash
uv run black src/
uv run ruff check src/
```

## 요구사항

- Python 3.10+
- uv (패키지 관리)
- 인터넷 연결 (yfinance API 접근)

## 라이선스

MIT License

## 기여

이슈 및 풀 리퀘스트를 환영합니다.