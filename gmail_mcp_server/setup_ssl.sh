#!/bin/bash

# Let's Encrypt를 사용한 무료 SSL 인증서 설정

# 1. Certbot 설치
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# 2. Nginx 설치 (아직 설치되지 않은 경우)
sudo apt install nginx -y

# 3. 기본 Nginx 설정
sudo tee /etc/nginx/sites-available/skax.app > /dev/null <<EOF
server {
    listen 80;
    server_name skax.app www.skax.app;

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
sudo nginx -t
sudo systemctl reload nginx

# 5. SSL 인증서 발급
sudo certbot --nginx -d skax.app -d www.skax.app

# 6. 자동 갱신 설정
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo "SSL 설정 완료! https://skax.app 으로 접속 가능합니다."