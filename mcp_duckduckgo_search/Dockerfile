# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# pyproject.toml과 uv.lock 복사 (있는 경우)
COPY pyproject.toml .
COPY uv.lock* .

# uv를 사용하여 의존성 설치
RUN uv sync --frozen --no-dev

# 애플리케이션 코드 복사
COPY duckduckgo_mcp_server.py .

# 포트 11005 노출
EXPOSE 11005

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import httpx; httpx.get('http://localhost:11005/mcp', timeout=5)" || exit 1

# 애플리케이션 실행
CMD ["uv", "run", "python", "duckduckgo_mcp_server.py"]
