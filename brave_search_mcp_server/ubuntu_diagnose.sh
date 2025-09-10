#!/bin/bash

# 우분투 서버 MCP 서버 진단 스크립트

echo "🔍 우분투 서버 MCP 서버 진단을 시작합니다..."
echo "================================================"

# 1. 시스템 정보
echo ""
echo "1️⃣ 시스템 정보"
echo "   OS: $(lsb_release -d | cut -f2)"
echo "   Kernel: $(uname -r)"
echo "   Architecture: $(uname -m)"

# 2. Docker 상태 확인
echo ""
echo "2️⃣ Docker 상태 확인"
if systemctl is-active --quiet docker; then
    echo "   ✅ Docker 서비스가 실행 중입니다."
else
    echo "   ❌ Docker 서비스가 중지되었습니다."
    echo "   해결방법: sudo systemctl start docker"
fi

# 3. Docker Compose 확인
echo ""
echo "3️⃣ Docker Compose 확인"
if command -v docker-compose >/dev/null 2>&1; then
    echo "   ✅ Docker Compose가 설치되어 있습니다."
    echo "   버전: $(docker-compose --version)"
else
    echo "   ❌ Docker Compose가 설치되지 않았습니다."
    echo "   해결방법: sudo apt install docker-compose-plugin"
fi

# 4. 포트 사용 확인
echo ""
echo "4️⃣ 포트 11001 사용 확인"
if netstat -tlnp 2>/dev/null | grep -q ":11001 "; then
    echo "   ✅ 포트 11001이 사용 중입니다."
    echo "   사용 중인 프로세스:"
    netstat -tlnp | grep ":11001 " | head -3
else
    echo "   ❌ 포트 11001이 사용되지 않고 있습니다."
    echo "   MCP 서버가 실행되지 않았을 수 있습니다."
fi

# 5. 방화벽 상태 확인
echo ""
echo "5️⃣ 방화벽 상태 확인"
if command -v ufw >/dev/null 2>&1; then
    echo "   UFW 상태:"
    sudo ufw status | head -5
    if sudo ufw status | grep -q "11001"; then
        echo "   ✅ 포트 11001이 UFW에서 허용되어 있습니다."
    else
        echo "   ❌ 포트 11001이 UFW에서 허용되지 않았습니다."
        echo "   해결방법: sudo ufw allow 11001"
    fi
else
    echo "   ℹ️  UFW가 설치되지 않았습니다. iptables를 확인하세요."
fi

# 6. Docker 컨테이너 상태 확인
echo ""
echo "6️⃣ Docker 컨테이너 상태 확인"
if docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "mcp-server"; then
    echo "   ✅ MCP 서버 컨테이너가 실행 중입니다."
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "mcp-server"
else
    echo "   ❌ MCP 서버 컨테이너가 실행되지 않았습니다."
    echo "   해결방법: docker-compose up -d"
fi

# 7. 네트워크 인터페이스 확인
echo ""
echo "7️⃣ 네트워크 인터페이스 확인"
echo "   활성 네트워크 인터페이스:"
ip addr show | grep -E "inet [0-9]" | grep -v "127.0.0.1" | head -3

# 8. 서비스 로그 확인
echo ""
echo "8️⃣ 서비스 로그 확인 (최근 10줄)"
if docker-compose ps | grep -q "mcp-server"; then
    echo "   MCP 서버 로그:"
    docker-compose logs --tail=10 mcp-server 2>/dev/null || echo "   로그를 가져올 수 없습니다."
else
    echo "   MCP 서버가 실행되지 않아 로그를 확인할 수 없습니다."
fi

# 9. 연결 테스트
echo ""
echo "9️⃣ 로컬 연결 테스트"
if curl -s --connect-timeout 5 http://localhost:11001/ >/dev/null 2>&1; then
    echo "   ✅ 로컬에서 서버에 연결할 수 있습니다."
else
    echo "   ❌ 로컬에서 서버에 연결할 수 없습니다."
fi

# 10. 권한 확인
echo ""
echo "🔟 Docker 권한 확인"
if groups $USER | grep -q docker; then
    echo "   ✅ 현재 사용자가 docker 그룹에 속해 있습니다."
else
    echo "   ❌ 현재 사용자가 docker 그룹에 속해 있지 않습니다."
    echo "   해결방법: sudo usermod -aG docker $USER && newgrp docker"
fi

echo ""
echo "================================================"
echo "📋 진단 완료!"
echo ""
echo "🔧 일반적인 해결 방법:"
echo "   1. 방화벽 열기: sudo ufw allow 11001"
echo "   2. Docker 권한: sudo usermod -aG docker $USER"
echo "   3. 서비스 시작: docker-compose up -d"
echo "   4. 로그 확인: docker-compose logs -f mcp-server"
echo ""
echo "📖 자세한 설정 가이드는 UBUNTU_SERVER_SETUP.md를 참조하세요."
