#!/bin/bash

# Ngrok을 사용한 Gmail MCP 서버 배포 스크립트

echo "=== Gmail MCP Server with Ngrok 배포 ==="

# 1. Docker 컨테이너 실행
echo "1. Docker 컨테이너 시작..."
docker run -d -p 11011:11011 --name gmail-mcp-server gmail-mcp-server

# 2. Ngrok 설치 확인
if ! command -v ngrok &> /dev/null; then
    echo "Ngrok이 설치되지 않았습니다. 설치 중..."
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
    sudo apt update && sudo apt install ngrok -y
fi

# 3. Ngrok 터널링 시작 (백그라운드)
echo "2. Ngrok 터널링 시작..."
ngrok http 11011 --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!

# 4. Ngrok URL 확인
echo "3. Ngrok URL 확인 중..."
sleep 5

# Ngrok API로 터널 정보 가져오기
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [ "$NGROK_URL" != "null" ] && [ "$NGROK_URL" != "" ]; then
    echo "=== 배포 완료! ==="
    echo "Gmail MCP 서버 URL: ${NGROK_URL}/mcp"
    echo "OAuth 리다이렉트 URI: ${NGROK_URL}/oauth/callback"
    echo ""
    echo "Google Cloud Console에서 다음 URI를 등록하세요:"
    echo "${NGROK_URL}/oauth/callback"
    echo ""
    echo "환경변수로 리다이렉트 URI 설정:"
    echo "export OAUTH_REDIRECT_URI=\"${NGROK_URL}/oauth/callback\""
    echo ""
    echo "서버 재시작 (환경변수 적용):"
    echo "docker stop gmail-mcp-server && docker rm gmail-mcp-server"
    echo "docker run -d -p 11011:11011 -e OAUTH_REDIRECT_URI=\"${NGROK_URL}/oauth/callback\" --name gmail-mcp-server gmail-mcp-server"
else
    echo "❌ Ngrok URL을 가져올 수 없습니다. 수동으로 확인해주세요:"
    echo "http://localhost:4040"
fi

echo ""
echo "Ngrok 프로세스 ID: $NGROK_PID"
echo "종료하려면: kill $NGROK_PID"