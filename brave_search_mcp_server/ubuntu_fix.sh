#!/bin/bash

# 우분투 서버 MCP 서버 문제 해결 스크립트

echo "🔧 우분투 서버 MCP 서버 문제를 해결합니다..."
echo "================================================"

# 1. Docker 서비스 시작
echo ""
echo "1️⃣ Docker 서비스 시작"
if ! systemctl is-active --quiet docker; then
    echo "   Docker 서비스를 시작합니다..."
    sudo systemctl start docker
    sudo systemctl enable docker
    echo "   ✅ Docker 서비스가 시작되었습니다."
else
    echo "   ✅ Docker 서비스가 이미 실행 중입니다."
fi

# 2. 방화벽 설정
echo ""
echo "2️⃣ 방화벽 설정"
if command -v ufw >/dev/null 2>&1; then
    echo "   UFW에서 포트 11001을 열고 있습니다..."
    sudo ufw allow 11001
    echo "   ✅ 포트 11001이 UFW에서 허용되었습니다."
else
    echo "   ℹ️  UFW가 설치되지 않았습니다. iptables를 사용하세요."
    echo "   iptables 명령어: sudo iptables -A INPUT -p tcp --dport 11001 -j ACCEPT"
fi

# 3. Docker 권한 설정
echo ""
echo "3️⃣ Docker 권한 설정"
if ! groups $USER | grep -q docker; then
    echo "   현재 사용자를 docker 그룹에 추가합니다..."
    sudo usermod -aG docker $USER
    echo "   ✅ 사용자가 docker 그룹에 추가되었습니다."
    echo "   ⚠️  변경사항을 적용하려면 로그아웃 후 다시 로그인하거나 'newgrp docker'를 실행하세요."
else
    echo "   ✅ 사용자가 이미 docker 그룹에 속해 있습니다."
fi

# 4. 포트 충돌 해결
echo ""
echo "4️⃣ 포트 충돌 확인"
if netstat -tlnp 2>/dev/null | grep -q ":11001 "; then
    echo "   포트 11001을 사용하는 프로세스를 확인합니다..."
    PID=$(netstat -tlnp | grep ":11001 " | awk '{print $7}' | cut -d'/' -f1)
    if [ ! -z "$PID" ] && [ "$PID" != "-" ]; then
        echo "   프로세스 $PID가 포트 11001을 사용하고 있습니다."
        echo "   프로세스를 종료하시겠습니까? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            sudo kill -9 $PID
            echo "   ✅ 프로세스가 종료되었습니다."
        else
            echo "   ⚠️  포트 충돌이 있을 수 있습니다."
        fi
    fi
else
    echo "   ✅ 포트 11001이 사용되지 않고 있습니다."
fi

# 5. Docker Compose 설치 확인
echo ""
echo "5️⃣ Docker Compose 설치 확인"
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "   Docker Compose를 설치합니다..."
    sudo apt update
    sudo apt install -y docker-compose-plugin
    echo "   ✅ Docker Compose가 설치되었습니다."
else
    echo "   ✅ Docker Compose가 이미 설치되어 있습니다."
fi

# 6. 환경변수 확인
echo ""
echo "6️⃣ 환경변수 확인"
if [ -z "$BRAVE_API_KEY" ]; then
    echo "   ❌ BRAVE_API_KEY 환경변수가 설정되지 않았습니다."
    echo "   다음 명령어로 설정하세요:"
    echo "   export BRAVE_API_KEY='your_api_key_here'"
    echo ""
    echo "   API 키를 입력하세요 (또는 Enter를 눌러 건너뛰기):"
    read -r api_key
    if [ ! -z "$api_key" ]; then
        export BRAVE_API_KEY="$api_key"
        echo "   ✅ BRAVE_API_KEY가 설정되었습니다."
    fi
else
    echo "   ✅ BRAVE_API_KEY가 설정되어 있습니다."
fi

# 7. 서비스 재시작
echo ""
echo "7️⃣ MCP 서비스 재시작"
if [ -f "docker-compose.yml" ]; then
    echo "   기존 서비스를 중지합니다..."
    docker-compose down 2>/dev/null || true
    
    echo "   서비스를 시작합니다..."
    docker-compose up -d
    
    echo "   서비스 상태를 확인합니다..."
    sleep 3
    docker-compose ps
    
    echo "   서비스 로그를 확인합니다..."
    docker-compose logs --tail=10 mcp-server
else
    echo "   ❌ docker-compose.yml 파일을 찾을 수 없습니다."
    echo "   프로젝트 디렉토리에서 실행하세요."
fi

# 8. 연결 테스트
echo ""
echo "8️⃣ 연결 테스트"
echo "   로컬 연결 테스트..."
if curl -s --connect-timeout 5 http://localhost:11001/ >/dev/null 2>&1; then
    echo "   ✅ 로컬에서 서버에 연결할 수 있습니다."
else
    echo "   ❌ 로컬에서 서버에 연결할 수 없습니다."
    echo "   서비스 로그를 확인하세요: docker-compose logs mcp-server"
fi

echo ""
echo "================================================"
echo "🎉 문제 해결 완료!"
echo ""
echo "📋 다음 단계:"
echo "   1. 서비스 상태 확인: docker-compose ps"
echo "   2. 로그 확인: docker-compose logs -f mcp-server"
echo "   3. 외부 연결 테스트: curl http://YOUR_SERVER_IP:11001/"
echo ""
echo "🔧 여전히 문제가 있다면 ubuntu_diagnose.sh를 실행하세요."
