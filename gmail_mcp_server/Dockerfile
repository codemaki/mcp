# Python 3.13 slim 이미지 사용
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY gmail_mcp_server.py ./

# Install dependencies with uv
RUN uv sync

# 포트 노출 (MCP 서버가 사용할 포트)
EXPOSE 11011

# 환경변수 설정
ENV HOST=0.0.0.0
ENV PORT=11011

# 서버 실행
CMD ["uv", "run", "gmail_mcp_server.py"]
