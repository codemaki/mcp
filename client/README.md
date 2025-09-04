# MCP Client Docker 배포

이 프로젝트는 MCP (Model Context Protocol) 클라이언트를 Docker와 Docker Compose를 사용하여 배포할 수 있도록 구성되어 있습니다.

## 프로젝트 구조

```
.
├── simple_mcp_client.py    # MCP 클라이언트 메인 애플리케이션
├── requirements.txt        # Python 의존성 목록
├── Dockerfile             # Docker 이미지 빌드 설정
├── docker-compose.yml     # Docker Compose 서비스 설정
├── .dockerignore          # Docker 빌드 시 제외할 파일 목록
└── README.md              # 프로젝트 문서
```

## 사전 요구사항

- Docker (20.10 이상)
- Docker Compose (2.0 이상)

## 사용법

### 1. Docker Compose를 사용한 실행 (권장)

```bash
# 모든 서비스 빌드 및 실행
docker-compose up --build

# 백그라운드에서 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f mcp-client

# 서비스 중지
docker-compose down
```

### 2. Docker만을 사용한 실행

```bash
# 이미지 빌드
docker build -t mcp-client .

# 컨테이너 실행
docker run --rm -p 8001:8000 mcp-client
```

### 3. 개발 모드 실행

개발 중에 코드 변경사항을 실시간으로 반영하려면:

```bash
# 볼륨 마운트를 사용한 개발 모드
docker-compose -f docker-compose.yml up --build
```

## 서비스 구성

### MCP Client
- **포트**: 8001 (호스트) → 8000 (컨테이너)
- **이미지**: 로컬 빌드
- **재시작 정책**: unless-stopped

### MCP Server (예시)
- **포트**: 8000 (호스트) → 8000 (컨테이너)
- **이미지**: python:3.11-slim
- **재시작 정책**: unless-stopped

## 환경 변수

다음 환경 변수들을 설정할 수 있습니다:

- `PYTHONUNBUFFERED=1`: Python 출력 버퍼링 비활성화

## 네트워크

서비스들은 `mcp-network`라는 브리지 네트워크를 통해 통신합니다.

## 헬스체크

각 서비스는 헬스체크가 설정되어 있어 서비스 상태를 모니터링할 수 있습니다.

## 문제 해결

### 포트 충돌
만약 8000 또는 8001 포트가 이미 사용 중이라면, `docker-compose.yml`에서 포트 매핑을 변경하세요:

```yaml
ports:
  - "8002:8000"  # 다른 포트로 변경
```

### MCP 서버 연결 문제
MCP 서버가 다른 주소에서 실행 중이라면, `simple_mcp_client.py`에서 URL을 수정하세요:

```python
client = Client("http://your-server-address:port/mcp")
```

### 로그 확인
```bash
# 특정 서비스 로그 확인
docker-compose logs mcp-client

# 실시간 로그 확인
docker-compose logs -f mcp-client

# 모든 서비스 로그 확인
docker-compose logs
```

## 개발 팁

1. **코드 변경사항 반영**: 개발 중에는 볼륨 마운트를 사용하여 코드 변경사항을 실시간으로 반영할 수 있습니다.

2. **의존성 추가**: 새로운 Python 패키지가 필요하면 `requirements.txt`에 추가하고 이미지를 다시 빌드하세요.

3. **환경별 설정**: 프로덕션과 개발 환경을 분리하려면 `docker-compose.override.yml` 파일을 생성하세요.

## 정리

모든 컨테이너와 네트워크를 정리하려면:

```bash
docker-compose down -v
docker system prune -f
```
