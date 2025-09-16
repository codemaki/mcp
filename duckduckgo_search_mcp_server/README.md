# DuckDuckGo Search MCP Server

AI Agent에서 DuckDuckGo 검색 기능을 사용할 수 있도록 하는 MCP (Model Context Protocol) 서버입니다.

## 주요 기능

- **웹 검색**: DuckDuckGo를 통한 일반 웹 검색
- **즉석 답변**: 계산, 정의, 간단한 질문에 대한 직접적인 답변
- **통합 검색**: 즉석 답변과 웹 검색을 동시에 수행
- **한국어 지원**: 한국어 검색 및 결과 지원
- **Docker 지원**: 컨테이너화된 실행 환경

## 파일 구조

```
duckduckgo/
├── duckduckgo_mcp_server.py  # 메인 MCP 서버 코드
├── requirements.txt          # Python 의존성
├── Dockerfile               # Docker 이미지 빌드 파일
├── docker-compose.yml       # Docker Compose 설정
├── README.md               # 이 파일
└── simple_mcp_server.py    # 참고용 예시 파일
```

## Docker를 사용한 실행

### 1. Docker Compose 사용 (권장)

```bash
# 서버 빌드 및 실행
docker-compose up --build -d

# 로그 확인
docker-compose logs -f

# 서버 중지
docker-compose down
```

### 2. Docker 직접 사용

```bash
# 이미지 빌드
docker build -t duckduckgo-mcp-server .

# 컨테이너 실행
docker run -d -p 11005:11005 --name duckduckgo-mcp-server duckduckgo-mcp-server

# 로그 확인
docker logs -f duckduckgo-mcp-server

# 컨테이너 중지 및 제거
docker stop duckduckgo-mcp-server
docker rm duckduckgo-mcp-server
```

## 로컬 실행

Docker를 사용하지 않고 로컬에서 직접 실행하려면:

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python duckduckgo_mcp_server.py
```

## 사용 가능한 도구 (Tools)

### 1. search_web
일반적인 웹 검색을 수행합니다.

**매개변수:**
- `query` (str): 검색할 키워드
- `max_results` (int, 선택사항): 반환할 최대 결과 수 (기본값: 10)

**사용 예시:**
```python
search_web("파이썬 튜토리얼", max_results=5)
```

### 2. search_instant_answer
즉석 답변을 검색합니다. 계산, 정의, 간단한 질문 등에 유용합니다.

**매개변수:**
- `query` (str): 검색할 질문이나 키워드

**사용 예시:**
```python
search_instant_answer("2+2는 무엇인가요?")
search_instant_answer("서울의 인구는?")
```

### 3. search_combined
즉석 답변과 웹 검색을 동시에 수행하여 통합된 결과를 제공합니다.

**매개변수:**
- `query` (str): 검색할 키워드나 질문
- `max_results` (int, 선택사항): 웹 검색 결과의 최대 개수 (기본값: 5)

**사용 예시:**
```python
search_combined("인공지능이란 무엇인가", max_results=3)
```


## 사용 가능한 리소스 (Resources)

### 1. duckduckgo://info
서버 정보를 제공합니다.

### 2. duckduckgo://usage
사용 예시를 제공합니다.

## 응답 형식

모든 검색 결과는 JSON 형태로 반환됩니다:

```json
{
  "status": "success",
  "query": "검색어",
  "results_count": 5,
  "results": [
    {
      "title": "검색 결과 제목",
      "url": "https://example.com",
      "description": "검색 결과 설명"
    }
  ]
}
```

## 서버 정보

- **포트**: 11005
- **프로토콜**: MCP (Model Context Protocol)
- **전송 방식**: streamable-http
- **호스트**: 0.0.0.0 (모든 인터페이스에서 접근 가능)

## 주의사항

1. **네트워크 연결**: 인터넷 연결이 필요합니다.
2. **속도 제한**: DuckDuckGo의 속도 제한을 고려하여 과도한 요청을 피해주세요.
3. **에러 처리**: 네트워크 오류나 파싱 오류 시 적절한 에러 메시지를 반환합니다.

## 문제 해결

### 컨테이너가 시작되지 않는 경우
```bash
# 로그 확인
docker-compose logs

# 컨테이너 상태 확인
docker-compose ps
```

### 검색 결과가 나오지 않는 경우
1. 인터넷 연결 확인
2. DuckDuckGo 접속 가능 여부 확인
3. 서버 로그 확인: `docker logs duckduckgo-mcp-server`
4. 다른 검색어로 테스트
5. 컨테이너 재시작: `docker-compose restart`

### 포트 충돌 시
docker-compose.yml에서 포트를 변경하세요:
```yaml
ports:
  - "다른포트:11005"
```

## 개발 정보

- **언어**: Python 3.11+
- **주요 라이브러리**: 
  - mcp (Model Context Protocol)
  - httpx (HTTP 클라이언트)
  - beautifulsoup4 (HTML 파싱)
- **개발자**: AI Assistant
- **라이선스**: MIT
