#!/bin/bash

# MCP Finance Server 실행 스크립트

set -e

echo "🚀 Starting MCP Finance Server..."

# 프로젝트 디렉토리로 이동
cd "$(dirname "$0")/.."

# uv가 설치되어 있는지 확인
if ! command -v uv &> /dev/null; then
    echo "❌ uv가 설치되어 있지 않습니다. 설치 방법:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 의존성 설치
echo "📦 Installing dependencies..."
uv sync

# 서버 실행
echo "🏃 Running finance server..."
uv run python src/finance_server.py