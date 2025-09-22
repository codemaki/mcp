# Simple MCP Server

간단한 MCP (Model Context Protocol) 서버 예제입니다.

## 기능

- `hello`: 인사말 생성 도구
- `get_prompt`: 프롬프트 템플릿 제공 도구
- `simple://info`: 서버 정보 리소스

## 로컬 실행 (Python 가상환경)

### 1. 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 서버 실행
```bash
python simple_mcp_server.py
```

## Docker 실행

### 1. Docker 이미지 빌드
```bash
docker build -t mcp-server .
```

### 2. Docker 컨테이너 실행
```bash
docker run -p 8000:8000 mcp-server
```

### 3. Docker Compose 사용 (권장)
```bash
docker-compose up --build
```

## 사용법

서버가 실행되면 `http://localhost:8000`에서 MCP 서버에 접근할 수 있습니다.

## 파일 구조

- `simple_mcp_server.py`: MCP 서버 소스 코드
- `requirements.txt`: Python 의존성
- `Dockerfile`: Docker 이미지 설정
- `docker-compose.yml`: Docker Compose 설정
- `.dockerignore`: Docker 빌드 시 제외할 파일들

# TODO

## 서비스 중지 + 컨테이너 제거 + 볼륨 제거
docker-compose down -v

# 백그라운드에서 시작 (권장)
docker-compose up -d

# 로그와 함께 시작 (실시간 모니터링)
docker-compose up

# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f mcp-server