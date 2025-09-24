# MCP SKB Search Server

FastMCP를 사용한 SKB 콘텐츠 검색 MCP 서버입니다.

## 기능

1. **검색어 자동완성** (`search_content_autocomplete`)
   - 검색어로 관련 콘텐츠 제목 리스트 출력
   - 사용자가 정확한 콘텐츠 제목을 찾을 수 있도록 도움

2. **콘텐츠 에피소드 검색** (`search_content_episodes`)
   - 검색어로 관련된 모든 에피소드 ID들을 반환
   - CE로 시작하는 에피소드 ID와 시리즈 정보, 썸네일 포함

3. **에피소드 상세 정보** (`get_episode_details`)
   - 개별 에피소드 ID로 상세 정보 조회
   - 제목, 시놉시스, 감독, 배우, 평점 등 포함

4. **정확한 콘텐츠 찾기** (`find_exact_content`) ✨
   - 정확한 제목 매칭으로 콘텐츠 검색
   - 2단계와 3단계를 조합하여 자동으로 정확한 매치 찾기
   - 정확한 매치가 없을 경우 첫 번째 결과를 fallback으로 제공

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

## 사용 워크플로우

### 일반적인 검색 플로우
1. **자동완성으로 콘텐츠 찾기**:
   ```
   search_content_autocomplete("다이 하드")
   ```

2. **정확한 제목으로 바로 검색** (권장):
   ```
   find_exact_content("다이 하드")
   ```

### 개별 툴 사용
1. **에피소드 ID들 가져오기**:
   ```
   search_content_episodes("다이 하드")
   ```

2. **특정 에피소드 상세 정보**:
   ```
   get_episode_details("CE1000386027")
   ```

## 새로운 검색 방식

기존 3단계 프로세스:
- `search_content_autocomplete` → 사용자가 제목 선택 → `search_content_episodes` → `get_episode_details`

**새로운 통합 방식** 🎯:
- `search_content_autocomplete` → 사용자가 제목 선택 → `find_exact_content` (자동으로 정확한 매치 찾기)