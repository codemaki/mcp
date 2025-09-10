#!/bin/bash

# MCP 서버 연결 테스트 스크립트

SERVER_IP=${1:-"localhost"}
PORT=${2:-"11001"}

echo "🔍 MCP 서버 연결을 테스트합니다..."
echo "   서버: $SERVER_IP:$PORT"

# 네트워크 연결 확인
echo ""
echo "1️⃣ 네트워크 연결 확인..."
if ping -c 1 -W 3 $SERVER_IP >/dev/null 2>&1; then
    echo "✅ 서버 $SERVER_IP에 ping이 성공했습니다."
else
    echo "❌ 서버 $SERVER_IP에 ping이 실패했습니다. 네트워크 연결을 확인하세요."
    echo "   - 방화벽 설정 확인"
    echo "   - 서버가 실행 중인지 확인"
    echo "   - IP 주소가 올바른지 확인"
fi

# 포트 연결 테스트
echo ""
echo "2️⃣ 포트 연결 테스트..."
if command -v nc >/dev/null 2>&1; then
    if timeout 5 nc -z $SERVER_IP $PORT 2>/dev/null; then
        echo "✅ 포트 $PORT가 열려있습니다."
    else
        echo "❌ 포트 $PORT에 연결할 수 없습니다."
        echo "   - 서버에서 방화벽 설정 확인: sudo ufw allow $PORT"
        echo "   - 서비스가 실행 중인지 확인: docker-compose ps"
    fi
else
    echo "ℹ️  nc 명령어가 없어 포트 테스트를 건너뜁니다."
fi

# HTTP 응답 테스트
echo ""
echo "3️⃣ HTTP 응답 테스트..."
echo "   - MCP 서버는 일반 HTTP 엔드포인트가 아닙니다."
echo "   - 404 응답은 정상입니다 (MCP 프로토콜 사용)."

# MCP 엔드포인트 테스트
echo ""
echo "4️⃣ MCP 엔드포인트 테스트..."
echo "   MCP 초기화 요청 테스트:"
echo "   curl -X POST http://$SERVER_IP:$PORT/mcp \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -H 'Accept: application/json, text/event-stream' \\"
echo "     -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{},\"clientInfo\":{\"name\":\"test-client\",\"version\":\"1.0.0\"}}}'"

echo ""
echo "📋 테스트 완료!"
echo ""
echo "🔧 Postman에서 MCP 서버 연결 방법:"
echo "   1. Method: POST"
echo "   2. URL: http://$SERVER_IP:$PORT/mcp"
echo "   3. Headers:"
echo "      - Content-Type: application/json"
echo "      - Accept: application/json, text/event-stream"
echo "   4. Body: JSON-RPC 2.0 형식의 MCP 요청"
echo ""
echo "📖 자세한 연결 가이드는 MCP_CONNECTION_GUIDE.md 파일을 참조하세요."
