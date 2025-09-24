# MCP SKB Search Server

FastMCP를 사용한 SKB 콘텐츠 검색 MCP 서버입니다.

## 기능

1. **검색어 자동완성** (`search_content_autocomplete`)
   - 검색어로 관련 콘텐츠 리스트 출력
   - 사용자가 정확한 콘텐츠 제목을 찾을 수 있도록 도움

2. **콘텐츠 검색** (`search_content_episodes`)
   - 정확한 콘텐츠 제목으로 에피소드 ID 검색
   - CE로 시작하는 에피소드 ID와 시리즈 정보 반환

3. **에피소드 상세 정보** (`get_episode_details`)
   - 에피소드 ID로 상세 정보 조회
   - 제목, 시놉시스, 감독, 배우, 평점 등 포함

## 설치 및 실행

### uv 사용 (권장)

```bash
# 의존성 설치
uv sync

# 서버 실행
uv run python main.py
```

### Docker 사용

```bash
# Docker 이미지 빌드
docker build -t mcp-skb-search .

# 컨테이너 실행
docker run -p 8005:8005 mcp-skb-search
```

## 서버 정보

- **포트**: 8005
- **프로토콜**: Streamable HTTP (MCP)
- **엔드포인트**: `http://localhost:8005/mcp`

## 사용 예시

1. 먼저 검색어로 콘텐츠 찾기:
   ```
   search_content_autocomplete("백설공주")
   ```

2. 정확한 제목으로 에피소드 ID 찾기:
   ```
   search_content_episodes("백설공주")
   ```

3. 에피소드 상세 정보 조회:
   ```
   get_episode_details("CE1000386027")
   ```