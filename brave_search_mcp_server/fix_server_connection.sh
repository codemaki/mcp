#!/bin/bash

# MCP 서버 연결 문제 해결 스크립트
# 우분투 서버에서 실행하여 연결 문제를 해결합니다.

echo "========================================="
echo "MCP 서버 연결 문제 해결 스크립트"
echo "========================================="

# 1. 방화벽 포트 열기
echo -e "\n1. 방화벽 포트 11001 열기:"
sudo ufw allow 11001/tcp
sudo ufw reload
echo "포트 11001이 열렸습니다."

# 2. Docker 컨테이너 재시작
echo -e "\n2. Docker 컨테이너 재시작:"
docker-compose down
docker-compose up -d
echo "컨테이너가 재시작되었습니다."

# 3. 포트 바인딩 재확인
echo -e "\n3. 포트 바인딩 확인:"
sleep 5  # 컨테이너 시작 대기
sudo netstat -tlnp | grep 11001

# 4. 로컬 테스트
echo -e "\n4. 로컬 연결 테스트:"
curl -X POST http://localhost:11001/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}' \
  -w "\nHTTP Status: %{http_code}\n"

# 5. 외부 IP 확인
echo -e "\n5. 서버의 외부 접근 가능한 IP 주소:"
echo "내부 IP:"
ip route get 8.8.8.8 | awk '{print $7; exit}'

echo -e "\n공인 IP (있는 경우):"
curl -s ifconfig.me || echo "공인 IP 확인 실패"

# 6. Postman에서 사용할 정보 출력
echo -e "\n========================================="
echo "Postman 설정 정보:"
echo "========================================="
INTERNAL_IP=$(ip route get 8.8.8.8 | awk '{print $7; exit}')
echo "URL: http://$INTERNAL_IP:11001/mcp"
echo "또는: http://10.10.10.201:11001/mcp"
echo ""
echo "Headers:"
echo "Content-Type: application/json"
echo "Accept: application/json, text/event-stream"
echo ""
echo "Body (Initialize):"
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"postman-client","version":"1.0.0"}}}'

echo -e "\n========================================="
echo "추가 확인 사항:"
echo "========================================="
echo "1. 클라우드 서비스를 사용하는 경우 보안 그룹에서 11001 포트를 열어주세요."
echo "2. 라우터/방화벽에서 포트 포워딩이 필요할 수 있습니다."
echo "3. Postman의 Proxy 설정을 확인해주세요."
echo "4. SSL 인증서 검증을 비활성화해주세요."
