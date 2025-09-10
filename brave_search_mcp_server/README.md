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
# .env 파일에 API 키 설정 후 실행
docker-compose up --build
```

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