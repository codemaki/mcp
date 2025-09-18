# Base64 to Image Converter

Base64로 인코딩된 이미지 데이터를 실제 이미지로 변환하여 사용자 친화적인 인터페이스로 표시하는 웹 애플리케이션입니다.

## 주요 기능

- Base64 이미지 데이터를 실제 이미지로 변환
- 깔끔하고 반응형 웹 인터페이스
- Base64 데이터 입력을 위한 왼쪽 패널
- 변환된 이미지 표시를 위한 오른쪽 패널
- 에러 처리 및 사용자 피드백
- 쉬운 배포를 위한 Docker 컨테이너화

## Docker로 빠른 시작

### 1. Docker 이미지 빌드
```bash
docker build -t base64-to-image .
```

### 2. 컨테이너 실행

#### 포그라운드 실행 (터미널이 차단됨)
```bash
docker run -p 7001:7001 base64-to-image
```

#### 백그라운드 실행 (추천)
```bash
# 백그라운드에서 실행
docker run -d -p 7001:7001 --name base64-app base64-to-image

# 실행 상태 확인
docker ps

# 로그 확인
docker logs base64-app

# 실시간 로그 보기
docker logs -f base64-app
```

#### 포트 변경하여 실행
```bash
# 다른 포트로 실행 (예: 8080)
docker run -d -p 8080:7001 --name base64-app base64-to-image
```

#### 볼륨 마운트하여 데이터 영속화
```bash
# 업로드된 이미지가 컨테이너 삭제 후에도 보존됨
docker run -d -p 7001:7001 -v $(pwd)/uploads:/app/uploads --name base64-app base64-to-image
```

### 3. 컨테이너 관리

#### 컨테이너 중지
```bash
docker stop base64-app
```

#### 컨테이너 재시작
```bash
docker restart base64-app
```

#### 컨테이너 제거
```bash
# 컨테이너 중지 후 제거
docker stop base64-app
docker rm base64-app

# 또는 강제 제거
docker rm -f base64-app
```

#### 컨테이너 내부 접속
```bash
docker exec -it base64-app /bin/bash
```

### 4. Docker Compose 사용 (더 편리함)

#### docker-compose.yml 파일 사용
```bash
# 백그라운드에서 실행
docker-compose up -d

# 실행 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs

# 실시간 로그 보기
docker-compose logs -f

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart
```

### 5. 웹 브라우저에서 접속
```
http://localhost:7001
```

## 로컬 개발 환경

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 애플리케이션 실행:

### 일반 실행
```bash
python app.py
```

### 백그라운드 실행

#### 방법 1: nohup 사용 (Linux/macOS)
```bash
nohup python app.py > app.log 2>&1 &
```
- 애플리케이션이 백그라운드에서 실행됩니다
- 로그는 `app.log` 파일에 저장됩니다
- 프로세스 ID가 출력되며, 이를 사용해 프로세스를 종료할 수 있습니다

#### 방법 2: screen 사용 (Linux/macOS)
```bash
# screen 세션 시작
screen -S base64-app

# 애플리케이션 실행
python app.py

# Ctrl+A, D로 세션에서 분리
# screen -r base64-app으로 다시 연결
```

#### 방법 3: tmux 사용 (Linux/macOS)
```bash
# tmux 세션 시작
tmux new-session -d -s base64-app

# 애플리케이션 실행
tmux send-keys -t base64-app "python app.py" Enter

# 세션에 연결: tmux attach -t base64-app
# 세션에서 분리: Ctrl+B, D
```

#### 방법 4: systemd 서비스 (Linux)
1. 서비스 파일 생성:
```bash
sudo nano /etc/systemd/system/base64-to-image.service
```

2. 서비스 파일 내용:
```ini
[Unit]
Description=Base64 to Image Converter
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/your/project
ExecStart=/usr/bin/python3 /path/to/your/project/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. 서비스 활성화 및 시작:
```bash
sudo systemctl daemon-reload
sudo systemctl enable base64-to-image
sudo systemctl start base64-to-image
```

#### 방법 5: Docker 백그라운드 실행
```bash
# 백그라운드에서 Docker 컨테이너 실행
docker run -d -p 7001:7001 --name base64-app base64-to-image

# 컨테이너 상태 확인
docker ps

# 컨테이너 중지
docker stop base64-app

# 컨테이너 제거
docker rm base64-app
```

3. 웹 브라우저에서 접속:
```
http://localhost:7001
```

## 프로세스 관리

### 백그라운드 프로세스 확인 및 종료

#### nohup으로 실행한 경우
```bash
# 실행 중인 프로세스 확인
ps aux | grep python

# 프로세스 종료 (PID는 ps 명령어 결과에서 확인)
kill [PID]

# 또는 강제 종료
kill -9 [PID]
```

#### screen으로 실행한 경우
```bash
# 실행 중인 screen 세션 확인
screen -ls

# 세션에 다시 연결
screen -r base64-app

# 세션 종료 (세션 내에서)
exit
```

#### tmux로 실행한 경우
```bash
# 실행 중인 tmux 세션 확인
tmux list-sessions

# 세션에 다시 연결
tmux attach -t base64-app

# 세션 종료
tmux kill-session -t base64-app
```

#### systemd 서비스로 실행한 경우
```bash
# 서비스 상태 확인
sudo systemctl status base64-to-image

# 서비스 중지
sudo systemctl stop base64-to-image

# 서비스 시작
sudo systemctl start base64-to-image

# 서비스 재시작
sudo systemctl restart base64-to-image

# 서비스 비활성화
sudo systemctl disable base64-to-image
```

#### Docker로 실행한 경우
```bash
# 실행 중인 컨테이너 확인
docker ps

# 컨테이너 중지
docker stop base64-app

# 컨테이너 재시작
docker restart base64-app

# 컨테이너 로그 확인
docker logs base64-app

# 컨테이너 제거
docker rm base64-app
```

## 사용 방법

1. 왼쪽 패널에 Base64 이미지 데이터를 붙여넣기
2. "Convert to Image" 버튼 클릭
3. 오른쪽 패널에서 변환된 이미지 확인
4. "Clear All" 버튼으로 인터페이스 초기화

## API 엔드포인트

- `GET /` - 메인 애플리케이션 인터페이스
- `POST /convert` - Base64 데이터를 이미지로 변환
- `GET /image/<filename>` - 변환된 이미지 제공
- `POST /clear` - 모든 업로드된 이미지 삭제

## 시스템 요구사항

- Python 3.11 이상
- Flask 2.3.3
- Pillow 10.0.1
- Docker (컨테이너화된 배포용)
