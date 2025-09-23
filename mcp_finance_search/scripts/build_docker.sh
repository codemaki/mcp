#!/bin/bash

# Docker 빌드 및 실행 스크립트

set -e

echo "🐳 Building MCP Finance Server Docker image..."

# 프로젝트 디렉토리로 이동
cd "$(dirname "$0")/.."

# Docker 이미지 빌드
echo "🏗️ Building Docker image..."
docker build -t mcp-finance-server:latest .

echo "✅ Docker image built successfully!"

# 실행 옵션 제공
read -p "🚀 Do you want to run the container now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🏃 Starting container..."
    docker run -d --name mcp-finance-server --restart unless-stopped mcp-finance-server:latest
    echo "✅ Container started! Name: mcp-finance-server"
    echo "📊 Check logs with: docker logs mcp-finance-server"
    echo "🛑 Stop with: docker stop mcp-finance-server"
fi