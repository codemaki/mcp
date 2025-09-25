# SSH MCP Tool Server

SSH를 통해 원격 서버에 명령을 실행하고 결과를 받아오는 MCP (Model Context Protocol) Tool 서버입니다.

## 기능

- **ssh_execute**: SSH를 통해 원격 서버에서 임의의 명령을 실행
- **get_server_processes**: 서버의 실행 중인 프로세스 목록 조회 (`ps aux`)
- **get_server_status**: 서버의 시스템 상태 정보 조회 (CPU, 메모리, 디스크 등)

## 특징

- PEM 키 파일을 통한 인증 지원
- 매 명령마다 새로운 SSH 연결 생성 (상태 비유지)
- 에러 처리 및 상세한 오류 메시지 제공
- Docker 컨테이너로 실행 가능

## 설치 및 실행

### 1. Docker를 사용한 실행

```bash
# 이미지 빌드
docker build -t ssh-mcp-server .

# PEM 키 파일을 준비하고 컨테이너 실행
docker run -d \
  -p 11010:11010 \
  -v /path/to/your/key.pem:/app/keys/key.pem:ro \
  --name ssh-mcp-server \
  ssh-mcp-server
```

### 2. 로컬 실행

```bash
# 의존성 설치
pip install -e .

# 서버 실행
python example_server.py
```

## 사용법

### MCP Tool 호출 예시

#### 1. 서버 프로세스 조회
```json
{
  "tool": "get_server_processes",
  "arguments": {
    "hostname": "10.10.10.101",
    "username": "ec2-user",
    "pem_key_path": "/app/keys/key.pem"
  }
}
```

#### 2. 서버 상태 조회
```json
{
  "tool": "get_server_status",
  "arguments": {
    "hostname": "10.10.10.101",
    "username": "ubuntu",
    "pem_key_path": "/app/keys/my-key.pem"
  }
}
```

#### 3. 임의의 SSH 명령 실행
```json
{
  "tool": "ssh_execute",
  "arguments": {
    "hostname": "10.10.10.101",
    "command": "systemctl status nginx",
    "username": "ec2-user",
    "pem_key_path": "/app/keys/key.pem"
  }
}
```

## 설정

### 기본값
- **사용자명**: `ec2-user`
- **PEM 키 경로**: `/app/keys/key.pem`
- **SSH 포트**: `22`
- **연결 타임아웃**: `10초`

### PEM 키 파일 준비

1. AWS EC2 인스턴스용 PEM 키 파일을 준비합니다
2. Docker 실행 시 볼륨 마운트로 키 파일을 컨테이너에 전달합니다:
   ```bash
   -v /local/path/to/key.pem:/app/keys/key.pem:ro
   ```

## 보안 주의사항

- PEM 키 파일은 읽기 전용으로 마운트하세요
- 키 파일 권한을 적절히 설정하세요 (600)
- 프로덕션 환경에서는 네트워크 보안을 고려하세요

## 에러 처리

다음과 같은 상황에서 적절한 오류 메시지를 반환합니다:

- PEM 키 파일을 찾을 수 없는 경우
- SSH 인증 실패
- SSH 연결 실패 (호스트 접근 불가, 포트 차단 등)
- 명령 실행 중 오류 발생

## 예제 응답

### 성공적인 프로세스 조회
```
명령 실행 완료:
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1  19356  1548 ?        Ss   Dec01   0:01 /sbin/init
root         2  0.0  0.0      0     0 ?        S    Dec01   0:00 [kthreadd]
...
```

### 인증 실패 시
```
오류: SSH 인증 실패 - 사용자명(ec2-user) 또는 PEM 키(/app/keys/key.pem)를 확인하세요
```
