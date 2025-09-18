# n8n에서 MCP 서버 연결 가이드

## 🚨 Postman vs n8n 연결 차이점

Postman에서는 연결이 잘 되지만 n8n에서 연결이 안 되는 경우, 다음과 같은 차이점들이 원인일 수 있습니다:

### 주요 차이점
1. **HTTP 클라이언트 구현**: n8n은 Node.js 기반, Postman은 Electron/Chrome 기반
2. **기본 헤더**: n8n과 Postman이 자동으로 추가하는 헤더가 다름
3. **Timeout 설정**: n8n의 기본 timeout이 더 짧을 수 있음
4. **네트워크 환경**: n8n이 Docker에서 실행되는 경우 네트워크 접근 방식이 다름

## 🛠️ n8n HTTP Request 노드 설정

### 1. 기본 설정

**HTTP Request 노드 추가:**
1. n8n 워크플로우에서 "HTTP Request" 노드 추가
2. 다음과 같이 설정:

**Method:** `POST`
**URL:** `http://10.10.10.201:11001/mcp`

### 2. Headers 설정

Headers 섹션에서 다음 헤더들을 **반드시** 추가:

```json
{
  "Content-Type": "application/json",
  "Accept": "application/json, text/event-stream",
  "User-Agent": "n8n-mcp-client/1.0.0"
}
```

### 3. Options 설정

**중요한 옵션들:**
- **Timeout**: `30000` (30초)
- **Follow Redirects**: `true`
- **Ignore SSL Issues**: `true` (HTTP 연결이므로)

### 4. Body 설정

**Body Type:** `JSON`

**MCP 초기화 요청:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "n8n-client",
      "version": "1.0.0"
    }
  }
}
```

## 📋 n8n 워크플로우 예제

### 1. MCP 초기화 워크플로우

```json
{
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://10.10.10.201:11001/mcp",
        "headers": {
          "Content-Type": "application/json",
          "Accept": "application/json, text/event-stream",
          "User-Agent": "n8n-mcp-client/1.0.0"
        },
        "body": {
          "jsonrpc": "2.0",
          "id": 1,
          "method": "initialize",
          "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
              "name": "n8n-client",
              "version": "1.0.0"
            }
          }
        },
        "options": {
          "timeout": 30000,
          "followRedirects": true
        }
      },
      "name": "MCP Initialize",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [380, 240]
    }
  ]
}
```

### 2. MCP 도구 호출 워크플로우

**Hello 도구 호출:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "hello",
    "arguments": {
      "name": "n8n 사용자"
    }
  }
}
```

**Health Check 도구 호출:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "health_check",
    "arguments": {}
  }
}
```

**Brave Search 도구 호출:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "brave_search",
    "arguments": {
      "query": "n8n workflow automation",
      "count": 5,
      "offset": 0,
      "country": "KR",
      "language": "ko"
    }
  }
}
```

**⚠️ 중요: 데이터 타입 주의사항**
- `query`: 문자열 (예: "검색어")
- `count`: 숫자 (예: 5, 문자열 "5" 아님)
- `offset`: 숫자 (예: 0)
- `country`: 문자열 (예: "KR")
- `language`: 문자열 (예: "ko")

## 🔧 문제 해결 방법

### 1. 스키마 오류 해결 ("Received tool input did not match expected schema")

**원인:** MCP 도구 호출 시 arguments의 데이터 타입이 맞지 않음

**해결 방법:**
1. **숫자 파라미터는 반드시 숫자로 전송:**
   - ❌ 잘못된 예: `"count": "5"` (문자열)
   - ✅ 올바른 예: `"count": 5` (숫자)

2. **필수 파라미터 확인:**
   - `brave_search`의 경우 `query`는 필수
   - 다른 파라미터들은 기본값이 있어서 생략 가능

3. **n8n Expression 사용 시:**
   ```javascript
   {
     "query": "{{ $json.search_term }}", // 문자열
     "count": {{ parseInt($json.count) || 5 }}, // 숫자로 변환
     "offset": {{ parseInt($json.offset) || 0 }}
   }
   ```

4. **테스트용 최소 요청:**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 4,
     "method": "tools/call",
     "params": {
       "name": "brave_search",
       "arguments": {
         "query": "test"
       }
     }
   }
   ```

### 2. n8n이 Docker에서 실행되는 경우

**네트워크 문제 해결:**
- n8n Docker 컨테이너에서 `host.docker.internal` 사용:
  ```
  URL: http://host.docker.internal:11001/mcp
  ```

**또는 Docker 네트워크 사용:**
```yaml
# docker-compose.yml에 추가
networks:
  shared-network:
    external: true
```

### 2. 연결 테스트 방법

**n8n에서 단계별 테스트:**

1. **기본 연결 테스트:**
   - Method: `GET`
   - URL: `http://10.10.10.201:11001/`
   - 응답: 기본 FastAPI 문서 페이지

2. **MCP 엔드포인트 테스트:**
   - Method: `POST`
   - URL: `http://10.10.10.201:11001/mcp`
   - Body: 위의 초기화 JSON

### 3. 일반적인 오류 및 해결

#### 오류: "ECONNREFUSED" 또는 "EHOSTUNREACH"

**해결 방법:**
1. n8n이 Docker에서 실행되는지 확인
2. Docker 네트워크 설정 확인
3. 방화벽 설정 확인
4. URL에서 `localhost` 대신 실제 IP 주소 사용

#### 오류: "Request timeout"

**해결 방법:**
1. Timeout 값을 30초로 증가
2. 서버 상태 확인: `docker-compose ps`
3. 서버 로그 확인: `docker-compose logs mcp-server`

#### 오류: "Invalid JSON response"

**해결 방법:**
1. Content-Type 헤더가 올바른지 확인
2. Accept 헤더에 `text/event-stream` 포함 확인
3. JSON Body 형식이 올바른지 확인

### 4. n8n 환경 변수 설정

**Environment Variables 노드 사용:**
```json
{
  "MCP_SERVER_URL": "http://10.10.10.201:11001/mcp",
  "MCP_SERVER_IP": "10.10.10.201",
  "MCP_SERVER_PORT": "11001"
}
```

### 5. 고급 설정

**Webhook을 통한 MCP 연결:**
```json
{
  "parameters": {
    "httpMethod": "POST",
    "path": "mcp-webhook",
    "responseMode": "responseNode",
    "options": {}
  },
  "name": "MCP Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 1,
  "position": [240, 300]
}
```

## 🎯 체크리스트

n8n에서 MCP 서버 연결이 안 될 때 다음 순서로 확인:

### 서버 측 확인
- [ ] Docker 컨테이너가 실행 중인지 확인
- [ ] 포트 11001이 바인딩되어 있는지 확인
- [ ] 서버 로그에서 오류 메시지 확인

### n8n 설정 확인
- [ ] HTTP Request 노드의 URL이 정확한지 확인
- [ ] Headers가 모두 설정되어 있는지 확인
- [ ] Body가 올바른 JSON 형식인지 확인
- [ ] Timeout이 충분히 길게 설정되어 있는지 확인

### 네트워크 확인
- [ ] n8n이 Docker에서 실행되는 경우 네트워크 설정 확인
- [ ] 방화벽이 11001 포트를 차단하지 않는지 확인
- [ ] ping과 telnet으로 기본 연결 확인

### 디버깅
- [ ] n8n의 실행 로그 확인
- [ ] 서버의 액세스 로그 확인
- [ ] curl로 동일한 요청이 작동하는지 확인

## 📞 지원

문제가 계속 발생하는 경우:
1. n8n 실행 로그 확인
2. MCP 서버 로그 확인
3. 네트워크 연결 상태 확인
4. 다른 HTTP 클라이언트(curl, Postman)로 동일한 요청 테스트

성공적인 연결 시 다음과 같은 응답을 받을 수 있습니다:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "experimental": {},
      "prompts": {"listChanged": false},
      "resources": {"subscribe": false, "listChanged": false},
      "tools": {"listChanged": false}
    },
    "serverInfo": {
      "name": "Brave Search MCP Server",
      "version": "1.13.1"
    }
  }
}
```
