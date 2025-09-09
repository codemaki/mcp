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

1. Docker 이미지 빌드:
```bash
docker build -t base64-to-image .
```

2. 컨테이너 실행:
```bash
docker run -p 7001:7001 base64-to-image
```

3. 웹 브라우저에서 접속:
```
http://localhost:7001
```

## 로컬 개발 환경

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 애플리케이션 실행:
```bash
python app.py
```

3. 웹 브라우저에서 접속:
```
http://localhost:7001
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
