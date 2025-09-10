# Postman에서 MCP 서버 연결 가이드

## 문제 해결: EHOSTUNREACH 오류

### 현재 상황
- ✅ 서버(10.10.10.201:11001)가 정상 작동 중
- ✅ 네트워크 연결 정상
- ❌ Postman에서 `EHOSTUNREACH` 오류 발생

### 해결 방법

#### 1. Postman 설정 확인

**Proxy 설정 확인:**
1. Postman → Settings → Proxy
2. "Use the system proxy" 체크 해제
3. "Add a custom proxy configuration" 체크 해제

**SSL 설정 확인:**
1. Postman → Settings → General
2. "SSL certificate verification" OFF로 설정 (테스트용)

#### 2. Postman 요청 설정

**Method:** `POST`
**URL:** `http://10.10.10.201:11001/mcp`

**Headers:**
```
Content-Type: application/json
Accept: application/json, text/event-stream
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "postman-client",
      "version": "1.0.0"
    }
  }
}
```

#### 3. 네트워크 진단

**Postman이 실행되는 환경에서 테스트:**
```bash
# 1. 네트워크 연결 확인
ping 10.10.10.201

# 2. 포트 연결 확인
telnet 10.10.10.201 11001

# 3. HTTP 요청 테스트
curl -v http://10.10.10.201:11001/

# 4. MCP 요청 테스트
curl -X POST http://10.10.10.201:11001/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}'
```

#### 4. 대안 방법

**Insomnia 사용:**
Insomnia는 Postman과 유사한 API 클라이언트로, 때로는 Postman보다 네트워크 문제가 적습니다.

**curl 명령어 사용:**
```bash
# MCP 초기화
curl -X POST http://10.10.10.201:11001/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl-client","version":"1.0.0"}}}'

# 도구 목록 조회 (초기화 후)
curl -X POST http://10.10.10.201:11001/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"notifications/initialized","params":{}}'

# 도구 목록 조회
curl -X POST http://10.10.10.201:11001/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/list","params":{}}'
```

#### 5. Postman 환경 변수 설정

**Environment 생성:**
1. Postman → Environments → Create Environment
2. Environment 이름: "MCP Server"
3. Variables 추가:
   - `mcp_url`: `http://10.10.10.201:11001/mcp`
   - `server_ip`: `10.10.10.201`
   - `server_port`: `11001`

**Collection 생성:**
1. Postman → Collections → Create Collection
2. Collection 이름: "MCP Server API"
3. Requests 추가:
   - Initialize
   - List Tools
   - Call Tool (hello)
   - Call Tool (health_check)
   - Call Tool (brave_search)

#### 6. 요청 예제

**1. Initialize Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "postman-client",
      "version": "1.0.0"
    }
  }
}
```

**2. List Tools Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "notifications/initialized",
  "params": {}
}
```

**3. Call Hello Tool:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "hello",
    "arguments": {
      "name": "김철수"
    }
  }
}
```

**4. Call Health Check Tool:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "health_check",
    "arguments": {}
  }
}
```

#### 7. 문제 해결 체크리스트

- [ ] Postman Proxy 설정 확인
- [ ] SSL 인증서 검증 비활성화
- [ ] 네트워크 연결 테스트 (ping, telnet)
- [ ] curl로 동일한 요청 테스트
- [ ] Postman 재시작
- [ ] 다른 API 클라이언트 시도 (Insomnia, Thunder Client)

#### 8. 로그 확인

**서버 로그 확인:**
```bash
# 우분투 서버에서
docker-compose logs -f mcp-server
```

**네트워크 로그 확인:**
```bash
# 서버에서
sudo netstat -tlnp | grep 11001
sudo ss -tlnp | grep 11001
```

### 성공적인 연결 확인

연결이 성공하면 다음과 같은 응답을 받을 수 있습니다:

**Initialize 응답:**
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
