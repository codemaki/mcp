# Image Converter MCP Server

이미지 변환 및 처리를 위한 MCP (Model Context Protocol) 서버입니다.

## 기능

### 이미지 변환 도구
- `convert_image_format`: 이미지 포맷 변환 (PNG, JPEG, WEBP, BMP, TIFF)
- `resize_image`: 이미지 크기 조정 (너비/높이/배율 지정 가능)
- `crop_image`: 이미지 자르기
- `rotate_image`: 이미지 회전
- `get_image_info`: 이미지 정보 조회
- `apply_filters`: 이미지 필터 적용 (블러, 샤프닝, 엣지 검출, 엠보싱)

### 리소스
- `image-converter://info`: 서버 정보 리소스

## 지원하는 이미지 포맷

- **입력**: PNG, JPEG, WEBP, BMP, TIFF, GIF 등
- **출력**: PNG, JPEG, WEBP, BMP, TIFF

## 로컬 실행 (Python 가상환경)

### 1. 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 서버 실행
```bash
python image_converter_mcp_server.py
```

## Docker 실행

### 1. Docker 이미지 빌드
```bash
docker build -t image-converter-mcp-server .
```

### 2. Docker 컨테이너 실행
```bash
docker run -p 8001:8000 image-converter-mcp-server
```

### 3. Docker Compose 사용 (권장)
```bash
docker-compose up --build
```

## 사용법

서버가 실행되면 `http://localhost:8001`에서 MCP 서버에 접근할 수 있습니다.

### 이미지 데이터 형식
모든 이미지 데이터는 Base64로 인코딩되어 전달되어야 합니다.

### 사용 예시
```python
import base64

# 이미지 파일을 Base64로 인코딩
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# MCP 서버의 도구 호출
# convert_image_format(image_data, "PNG", 95)
# resize_image(image_data, width=800, height=600)
# crop_image(image_data, x=100, y=100, width=400, height=300)
```

## 파일 구조

- `image_converter_mcp_server.py`: 이미지 변환 MCP 서버 소스 코드
- `requirements.txt`: Python 의존성 (Pillow, OpenCV 포함)
- `Dockerfile`: Docker 이미지 설정 (OpenCV 의존성 포함)
- `docker-compose.yml`: Docker Compose 설정
- `.dockerignore`: Docker 빌드 시 제외할 파일들

# TODO

## 서비스 중지 + 컨테이너 제거 + 볼륨 제거
docker-compose down -v

# 백그라운드에서 시작 (권장)
docker-compose up -d

# 로그와 함께 시작 (실시간 모니터링)
docker-compose up

# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f image-converter-mcp-server