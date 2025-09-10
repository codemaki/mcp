# Brave Search MCP Server

Brave Search API를 통한 웹 검색 기능을 제공하는 MCP (Model Context Protocol) 서버입니다.

## 기능

- `hello`: 인사말 생성 도구
- `get_prompt`: 프롬프트 템플릿 제공 도구
- `brave_search`: Brave Search API를 통한 웹 검색 도구
- `simple://info`: 서버 정보 리소스

## 환경 설정

### Brave Search API 키 설정

Brave Search 기능을 사용하려면 API 키가 필요합니다.

1. [Brave Search API](https://brave.com/search/api/)에서 API 키를 발급받으세요.
2. `.env` 파일을 편집하여 API 키를 설정하세요:

```bash
# .env 파일 편집
nano .env
```

`.env` 파일 내용:
```env
# Brave Search API 키
BRAVE_API_KEY=your_actual_api_key_here

# 서버 설정
HOST=0.0.0.0
PORT=11001
```

또는 환경변수로 직접 설정할 수도 있습니다:

```bash
export BRAVE_API_KEY="your_api_key_here"
```

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
python brave_search_mcp_server.py
```

## Docker 실행

### 빠른 배포 (권장)
```bash
# 1. 환경변수 설정
export BRAVE_API_KEY="your_api_key_here"

# 2. 배포 스크립트 실행
./deploy.sh
```

### 수동 Docker Compose 실행
```bash
# 1. 환경변수 설정
export BRAVE_API_KEY="your_api_key_here"

# 2. 서비스 시작
docker-compose up --build -d

# 3. 상태 확인
docker-compose ps

# 4. 로그 확인
docker-compose logs -f mcp-server
```

### 서버 상태 확인
```bash
# 로컬 테스트
./test_connection.sh

# 원격 서버 테스트
./test_connection.sh 10.10.10.201 11001
```

## 원격 서버 배포

### 1. 서버 준비
```bash
# 우분투 서버에 접속
ssh user@10.10.10.201

# Docker 및 Docker Compose 설치 (필요한 경우)
sudo apt update
sudo apt install docker.io docker-compose-plugin

# 프로젝트 클론 또는 파일 업로드
git clone <your-repo-url>
# 또는
scp -r . user@10.10.10.201:/path/to/project/
```

### 2. 서버에서 배포
```bash
# 프로젝트 디렉토리로 이동
cd /path/to/brave_search_mcp_server

# 환경변수 설정
export BRAVE_API_KEY="your_api_key_here"

# 배포 실행
./deploy.sh
```

### 3. 방화벽 설정 (필요한 경우)
```bash
# UFW 사용 시
sudo ufw allow 11001

# 또는 iptables 사용 시
sudo iptables -A INPUT -p tcp --dport 11001 -j ACCEPT
```

### 4. 연결 테스트
```bash
# 다른 서버에서 테스트
curl http://10.10.10.201:11001/
curl http://10.10.10.201:11001/health
```

## 문제 해결

### 1. 404 Not Found 오류
- **원인**: MCP 서버는 `/` 경로에서 404를 반환하는 것이 정상입니다.
- **해결**: `/` 또는 `/health` 엔드포인트를 사용하여 서버 상태를 확인하세요.

### 2. 연결 거부 오류
- **원인**: 포트가 열려있지 않거나 서버가 실행되지 않음
- **해결**: 
  ```bash
  # 서버 상태 확인
  docker-compose ps
  
  # 포트 확인
  netstat -tlnp | grep 11001
  
  # 방화벽 확인
  sudo ufw status
  ```

### 3. MCP 연결 실패
- **원인**: Postman에서 잘못된 엔드포인트 사용
- **해결**: MCP 연결 시 `http://10.10.10.201:11001/mcp` 엔드포인트를 사용하세요.

## 사용법

서버가 실행되면 `http://localhost:11001`에서 MCP 서버에 접근할 수 있습니다.

### 도구 사용 예제

#### 1. 인사말 도구
```python
# hello 도구 호출
result = hello("김철수")
# 결과: "안녕하세요, 김철수님!"
```

#### 2. 프롬프트 템플릿 도구
```python
# get_prompt 도구 호출
prompt = get_prompt("code_review")
# 결과: 코드 리뷰용 프롬프트 템플릿
```

#### 3. Brave Search 도구
```python
# brave_search 도구 호출
search_results = brave_search(
    query="Python MCP 서버 개발",
    count=5,
    country="KR",
    language="ko"
)
# 결과: 검색 결과 딕셔너리 (제목, URL, 설명 등 포함)
```

## 파일 구조

- `brave_search_mcp_server.py`: MCP 서버 소스 코드
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