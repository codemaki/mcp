# Gmail MCP Server 설정 가이드

## 1. 사전 준비

### Google Cloud Console 설정
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Gmail API 활성화:
   - 좌측 메뉴에서 "API 및 서비스" > "라이브러리" 선택
   - "Gmail API" 검색 후 활성화

### OAuth2 자격 증명 설정
1. "API 및 서비스" > "사용자 인증 정보" 이동
2. "+ 사용자 인증 정보 만들기" > "OAuth 클라이언트 ID" 선택
3. 애플리케이션 유형: "데스크톱 애플리케이션" 선택
4. 이름 입력 후 생성
5. JSON 파일 다운로드하여 `credentials.json`으로 저장

## 2. 설치 및 실행

### 의존성 설치
```bash
# uv를 사용하여 의존성 설치
uv sync

# 또는 개발 환경 설정
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
uv pip install -e .
```

### 서버 실행
```bash
# uv를 사용하여 실행
uv run gmail_mcp_server.py

# 또는 가상환경 활성화 후 실행
python gmail_mcp_server.py
```

## 3. 사용법

### 인증
먼저 Gmail API 인증을 수행합니다:
```python
gmail_authenticate()
```

### 이메일 조회
```python
# 최근 10개 이메일 조회
read_emails()

# 읽지 않은 이메일만 조회
read_emails(query="is:unread", max_results=5)

# 특정 발신자의 이메일 조회
read_emails(query="from:example@gmail.com")
```

### 이메일 발송
```python
send_email(
    to="recipient@example.com",
    subject="테스트 이메일",
    body="안녕하세요! 이것은 테스트 이메일입니다."
)
```

### 고급 검색
```python
search_emails(
    sender="example@gmail.com",
    subject_contains="urgent",
    is_unread=True,
    after_date="2024/01/01"
)
```

## 4. 주요 기능

- **gmail_authenticate**: Gmail API 인증
- **read_emails**: 이메일 조회 (Gmail 검색 쿼리 지원)
- **send_email**: 이메일 발송 (텍스트/HTML 지원)
- **get_email_by_id**: 특정 ID로 이메일 상세 조회
- **search_emails**: 다양한 조건으로 이메일 검색

## 5. 지원하는 Gmail 검색 쿼리

- `from:email@example.com` - 특정 발신자
- `to:email@example.com` - 특정 수신자
- `subject:keyword` - 제목에 키워드 포함
- `is:unread` - 읽지 않은 이메일
- `is:read` - 읽은 이메일
- `has:attachment` - 첨부파일 포함
- `after:2024/01/01` - 특정 날짜 이후
- `before:2024/12/31` - 특정 날짜 이전

## 6. 보안 고려사항

- `credentials.json`과 `token.json` 파일은 버전 관리에서 제외
- 토큰은 자동으로 갱신되며 만료 시 재인증 필요
- Gmail API 할당량 제한 주의 (일일 10억 요청)