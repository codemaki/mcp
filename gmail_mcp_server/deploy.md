# Gmail MCP Server 배포 가이드

## Docker로 배포

### 1. Docker 빌드 및 실행
```bash
# 이미지 빌드
docker build -t gmail-mcp-server .

# 컨테이너 실행
docker run -d -p 11011:11011 --name gmail-mcp-server gmail-mcp-server

# 또는 docker-compose 사용
docker-compose up -d
```

### 2. 배포 주소
- **서버 URL**: `http://skax.app:11011`
- **MCP 엔드포인트**: `http://skax.app:11011/mcp`

### 3. Google Cloud Console 설정

OAuth 2.0 클라이언트 ID 설정에서 "승인된 리디렉션 URI"에 추가:
```
http://skax.app:11011/oauth/callback
```

### 4. 사용법

#### 4.1 OAuth URL 생성
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_oauth_url_for_refresh_token",
    "arguments": {
      "client_id": "YOUR_CLIENT_ID"
    }
  }
}
```

#### 4.2 Refresh Token 발급
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_refresh_token_from_auth_code",
    "arguments": {
      "auth_code": "AUTH_CODE_FROM_OAUTH",
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET"
    }
  }
}
```

#### 4.3 Gmail 인증
```json
{
  "method": "tools/call",
  "params": {
    "name": "gmail_authenticate_with_refresh_token",
    "arguments": {
      "refresh_token": "YOUR_REFRESH_TOKEN",
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET"
    }
  }
}
```

### 5. 환경변수
- `HOST`: 바인드 호스트 (기본값: 0.0.0.0)
- `PORT`: 포트 번호 (기본값: 11011)

### 6. 도메인 요구사항
- HTTP 지원
- 포트 11011 오픈
- 도메인: skax.app

### 7. 배포 확인
```bash
curl http://skax.app:11011/mcp
```

정상 배포시 MCP 서버 응답을 받을 수 있습니다.