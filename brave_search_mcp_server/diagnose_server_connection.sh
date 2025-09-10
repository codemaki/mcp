#!/bin/bash

# MCP 서버 연결 진단 스크립트
# 우분투 서버에서 실행하여 연결 문제를 진단합니다.

echo "========================================="
echo "MCP 서버 연결 진단 스크립트"
echo "========================================="

# 1. 기본 정보 확인
echo -e "\n1. 시스템 정보:"
echo "OS: $(lsb_release -d | cut -f2)"
echo "IP 주소:"
ip addr show | grep "inet " | grep -v 127.0.0.1

# 2. Docker 상태 확인
echo -e "\n2. Docker 컨테이너 상태:"
docker-compose ps

echo -e "\n3. Docker 컨테이너 로그 (최근 20줄):"
docker-compose logs --tail=20 mcp-server

# 4. 포트 바인딩 확인
echo -e "\n4. 포트 11001 바인딩 상태:"
sudo netstat -tlnp | grep 11001
echo "또는:"
sudo ss -tlnp | grep 11001

# 5. 방화벽 상태 확인
echo -e "\n5. 방화벽(ufw) 상태:"
sudo ufw status verbose

# 6. 로컬 연결 테스트
echo -e "\n6. 로컬 연결 테스트:"
echo "localhost 테스트:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:11001/ || echo "연결 실패"

echo -e "\n내부 IP 테스트:"
INTERNAL_IP=$(ip route get 8.8.8.8 | awk '{print $7; exit}')
echo "내부 IP: $INTERNAL_IP"
curl -s -o /dev/null -w "%{http_code}" http://$INTERNAL_IP:11001/ || echo "연결 실패"

# 7. MCP 엔드포인트 테스트
echo -e "\n7. MCP 엔드포인트 테스트:"
curl -X POST http://localhost:11001/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}' \
  -w "\nHTTP Status: %{http_code}\n" 2>/dev/null || echo "MCP 요청 실패"

# 8. 프로세스 확인
echo -e "\n8. Python 프로세스 확인:"
ps aux | grep python | grep -v grep

# 9. 네트워크 인터페이스 확인
echo -e "\n9. 네트워크 인터페이스:"
ip link show

echo -e "\n========================================="
echo "진단 완료"
echo "========================================="
