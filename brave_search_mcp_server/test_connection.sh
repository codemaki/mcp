#!/bin/bash

# MCP 서버 연결 테스트 스크립트

SERVER_IP=${1:-"localhost"}
PORT=${2:-"11001"}

echo "🔍 MCP 서버 연결을 테스트합니다..."
echo "   서버: $SERVER_IP:$PORT"

# 기본 헬스체크
echo ""
echo "1️⃣ 기본 헬스체크 테스트..."
curl -v http://$SERVER_IP:$PORT/ 2>&1 | head -20

echo ""
echo "2️⃣ 상세 상태 확인..."
curl -s http://$SERVER_IP:$PORT/health | jq . 2>/dev/null || curl -s http://$SERVER_IP:$PORT/health

echo ""
echo "3️⃣ MCP 엔드포인트 확인..."
curl -v http://$SERVER_IP:$PORT/mcp 2>&1 | head -10

echo ""
echo "4️⃣ 포트 연결 테스트..."
if command -v nc >/dev/null 2>&1; then
    if nc -z $SERVER_IP $PORT 2>/dev/null; then
        echo "✅ 포트 $PORT가 열려있습니다."
    else
        echo "❌ 포트 $PORT에 연결할 수 없습니다."
    fi
else
    echo "ℹ️  nc 명령어가 없어 포트 테스트를 건너뜁니다."
fi

echo ""
echo "📋 테스트 완료!"
echo "   - 서버가 정상적으로 응답하면 MCP 연결이 가능합니다."
echo "   - Postman에서 MCP 서버로 연결할 때는 http://$SERVER_IP:$PORT/mcp 를 사용하세요."
