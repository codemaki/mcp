# 우분투 서버 MCP 서버 설정 가이드

## 1. 방화벽 설정

### UFW (Uncomplicated Firewall) 사용 시
```bash
# UFW 상태 확인
sudo ufw status

# 11001 포트 열기
sudo ufw allow 11001

# UFW 활성화 (비활성화된 경우)
sudo ufw enable

# 설정 확인
sudo ufw status numbered
```

### iptables 사용 시
```bash
# 포트 열기
sudo iptables -A INPUT -p tcp --dport 11001 -j ACCEPT

# 설정 저장 (Ubuntu 18.04+)
sudo netfilter-persistent save

# 현재 규칙 확인
sudo iptables -L -n | grep 11001
```

## 2. Docker 설정 확인

### Docker 서비스 상태 확인
```bash
# Docker 서비스 상태
sudo systemctl status docker

# Docker 서비스 시작 (중지된 경우)
sudo systemctl start docker
sudo systemctl enable docker
```

### Docker Compose 설치 확인
```bash
# Docker Compose 버전 확인
docker-compose --version

# 설치되지 않은 경우
sudo apt update
sudo apt install docker-compose-plugin
```

## 3. 포트 사용 확인

### 포트 사용 중인지 확인
```bash
# 11001 포트 사용 확인
sudo netstat -tlnp | grep 11001
sudo lsof -i :11001

# 다른 프로세스가 사용 중인 경우 종료
sudo kill -9 <PID>
```

### Docker 컨테이너 포트 확인
```bash
# 실행 중인 컨테이너 확인
docker ps

# 포트 매핑 확인
docker port <container_name>
```

## 4. 네트워크 인터페이스 확인

### 네트워크 인터페이스 확인
```bash
# 네트워크 인터페이스 확인
ip addr show

# 특정 IP에서만 접근 허용하는 경우
# 0.0.0.0:11001로 바인딩되어 있는지 확인
```

### Docker 네트워크 설정 확인
```bash
# Docker 네트워크 확인
docker network ls

# 컨테이너 네트워크 설정 확인
docker inspect <container_name> | grep -A 10 "NetworkSettings"
```

## 5. 서비스 배포 및 확인

### 1. 프로젝트 디렉토리로 이동
```bash
cd /path/to/brave_search_mcp_server
```

### 2. 환경변수 설정
```bash
export BRAVE_API_KEY="your_api_key_here"
```

### 3. 서비스 시작
```bash
# 기존 컨테이너 정리
docker-compose down

# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f mcp-server
```

### 4. 서비스 상태 확인
```bash
# 컨테이너 상태
docker-compose ps

# 포트 바인딩 확인
docker-compose port mcp-server 11001

# 서비스 로그
docker-compose logs mcp-server
```

## 6. 연결 테스트

### 로컬에서 테스트
```bash
# 서버에서 직접 테스트
curl -v http://localhost:11001/

# MCP 초기화 테스트
curl -X POST http://localhost:11001/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}'
```

### 외부에서 테스트
```bash
# 다른 서버에서 테스트
curl -v http://10.10.10.201:11001/

# 포트 연결 테스트
telnet 10.10.10.201 11001
```

## 7. 문제 해결

### 일반적인 문제들

#### 1. "Connection refused" 오류
```bash
# 서비스가 실행 중인지 확인
docker-compose ps

# 포트가 열려있는지 확인
sudo netstat -tlnp | grep 11001

# 방화벽 확인
sudo ufw status
```

#### 2. "No route to host" 오류
```bash
# 네트워크 연결 확인
ping 10.10.10.201

# 라우팅 테이블 확인
ip route show
```

#### 3. "Permission denied" 오류
```bash
# Docker 권한 확인
sudo usermod -aG docker $USER
newgrp docker

# 또는 sudo로 실행
sudo docker-compose up -d
```

#### 4. 포트 충돌 오류
```bash
# 포트 사용 중인 프로세스 확인
sudo lsof -i :11001

# 프로세스 종료
sudo kill -9 <PID>
```

## 8. 자동 시작 설정

### systemd 서비스 생성 (선택사항)
```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/mcp-server.service
```

서비스 파일 내용:
```ini
[Unit]
Description=MCP Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/brave_search_mcp_server
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

서비스 활성화:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
```

## 9. 모니터링

### 로그 모니터링
```bash
# 실시간 로그 확인
docker-compose logs -f mcp-server

# 최근 로그 확인
docker-compose logs --tail=100 mcp-server
```

### 리소스 모니터링
```bash
# 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
df -h
```

### 서비스 상태 모니터링
```bash
# 서비스 상태 확인
docker-compose ps

# 헬스체크
curl http://localhost:11001/health
```
