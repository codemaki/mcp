# Python 3.13 slim 이미지 사용
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# uv 설치 (Python 패키지 관리자)
RUN pip install uv

# 프로젝트 파일들 복사
COPY pyproject.toml ./
COPY example_server.py ./

# 의존성 설치
RUN uv pip install --system langchain-mcp-adapters paramiko

# SSH 키 디렉토리 생성
RUN mkdir -p /app/keys

# 포트 노출
EXPOSE 11010

# 서버 실행
CMD ["python", "example_server.py"]
