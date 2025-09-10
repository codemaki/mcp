#!/bin/bash

# Brave Search MCP Server 배포 스크립트

echo "🚀 Brave Search MCP Server 배포를 시작합니다..."

# 환경변수 확인
if [ -z "$BRAVE_API_KEY" ]; then
    echo "❌ BRAVE_API_KEY 환경변수가 설정되지 않았습니다."
    echo "다음 명령어로 설정하세요:"
    echo "export BRAVE_API_KEY=your_api_key_here"
    exit 1
fi

echo "✅ BRAVE_API_KEY가 설정되어 있습니다."

# Docker 이미지 빌드
echo "🔨 Docker 이미지를 빌드합니다..."
docker-compose build

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너를 정리합니다..."
docker-compose down

# 서비스 시작
echo "🚀 서비스를 시작합니다..."
docker-compose up -d

# 서비스 상태 확인
echo "⏳ 서비스가 시작될 때까지 잠시 기다립니다..."
sleep 5

# 헬스체크
echo "🔍 서버 상태를 확인합니다..."
curl -s http://localhost:11001/ | jq . || echo "서버가 아직 시작되지 않았습니다. 잠시 후 다시 시도하세요."

echo "✅ 배포가 완료되었습니다!"
echo "📋 서버 정보:"
echo "   - URL: http://localhost:11001"
echo "   - 헬스체크: http://localhost:11001/"
echo "   - 상세 상태: http://localhost:11001/health"
echo "   - MCP 엔드포인트: http://localhost:11001/mcp"

echo ""
echo "🔧 외부에서 접근하려면:"
echo "   - 서버 IP:11001 포트로 접근"
echo "   - 방화벽에서 11001 포트가 열려있는지 확인"
