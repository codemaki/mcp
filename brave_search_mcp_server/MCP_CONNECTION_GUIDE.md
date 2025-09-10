# MCP 서버 연결 가이드

## Postman에서 MCP 서버 연결하기

### 1. MCP 서버 정보
- **서버 주소**: `http://10.10.10.201:11001`
- **전송 방식**: Streamable HTTP (SSE 아님)
- **MCP 엔드포인트**: `http://10.10.10.201:11001/mcp`

### 2. Postman 설정

#### 방법 1: MCP 클라이언트 사용 (권장)
Postman에서 MCP 서버에 연결하려면 MCP 클라이언트를 사용해야 합니다.

1. **새 요청 생성**
   - Method: `POST`
   - URL: `http://10.10.10.201:11001/mcp`

2. **Headers 설정**
   ```
   Content-Type: application/json
   Accept: application/json, text/event-stream
   ```

3. **Body 설정 (JSON)**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "initialize",
     "params": {
       "protocolVersion": "2024-11-05",
       "capabilities": {
         "roots": {
           "listChanged": true
         },
         "sampling": {}
       },
       "clientInfo": {
         "name": "postman-client",
         "version": "1.0.0"
       }
     }
   }
   ```

#### 방법 2: 세션 시작
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "notifications/initialized",
  "params": {}
}
```

#### 방법 3: 도구 목록 조회 (세션 시작 후)
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/list",
  "params": {}
}
```

#### 방법 4: 리소스 목록 조회
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/list",
  "params": {}
}
```

### 3. 사용 가능한 도구들

#### hello 도구 호출
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "hello",
    "arguments": {
      "name": "김철수"
    }
  }
}
```

#### health_check 도구 호출
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "health_check",
    "arguments": {}
  }
}
```

#### brave_search 도구 호출
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "brave_search",
    "arguments": {
      "query": "Python MCP 서버",
      "count": 5,
      "country": "KR",
      "language": "ko"
    }
  }
}
```

### 4. 네트워크 연결 문제 해결

#### 연결 테스트
```bash
# 1. 서버 연결 확인
curl -v http://10.10.10.201:11001/

# 2. 포트 연결 확인
telnet 10.10.10.201 11001

# 3. 방화벽 확인 (서버에서)
sudo ufw status
sudo netstat -tlnp | grep 11001
```

#### 방화벽 설정 (서버에서)
```bash
# UFW 사용 시
sudo ufw allow 11001

# iptables 사용 시
sudo iptables -A INPUT -p tcp --dport 11001 -j ACCEPT
```

### 5. 서버 상태 확인

#### 헬스체크
```bash
curl http://10.10.10.201:11001/health
```

#### 서비스 상태 확인 (서버에서)
```bash
docker-compose ps
docker-compose logs mcp-server
```

### 6. 일반적인 오류 해결

#### EHOSTUNREACH 오류
- 네트워크 연결 확인
- 방화벽 설정 확인
- 서버가 실행 중인지 확인

#### 404 Not Found 오류
- MCP 엔드포인트(`/mcp`) 사용 확인
- 일반 HTTP 엔드포인트(`/`)는 404가 정상

#### 연결 거부 오류
- 포트가 열려있는지 확인
- 서비스가 실행 중인지 확인
