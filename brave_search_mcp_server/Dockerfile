# Python 3.13 slim 이미지 사용
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY brave_search_mcp_server.py .

# 포트 노출 (MCP 서버가 사용할 포트)
EXPOSE 11001

# 환경변수 설정
ENV HOST=0.0.0.0
ENV PORT=11001

# 서버 실행
CMD ["python", "brave_search_mcp_server.py"]
