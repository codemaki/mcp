#!/bin/bash

# 자체 서명 SSL 인증서 생성 (개발/테스트용)

# 1. SSL 디렉토리 생성
sudo mkdir -p /etc/ssl/certs
sudo mkdir -p /etc/ssl/private

# 2. 자체 서명 인증서 생성
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/skax.app.key \
    -out /etc/ssl/certs/skax.app.crt \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Organization/OU=OrgUnit/CN=skax.app"

# 3. Nginx 설정
sudo tee /etc/nginx/sites-available/skax.app > /dev/null <<EOF
server {
    listen 80;
    server_name skax.app;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name skax.app;

    ssl_certificate /etc/ssl/certs/skax.app.crt;
    ssl_certificate_key /etc/ssl/private/skax.app.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:11011;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 4. 사이트 활성화
sudo ln -sf /etc/nginx/sites-available/skax.app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

echo "자체 서명 SSL 설정 완료!"
echo "브라우저에서 보안 경고가 나타나면 '고급' > '안전하지 않음' 클릭하여 계속 진행하세요."