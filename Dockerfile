# 베이스 이미지로 Python 3.12 slim 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치
# 시스템 패키지 설치 (필수 라이브러리 추가)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치를 위한 requirements.txt 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 및 PDF 데이터 복사
COPY . .

# Flask 환경 변수 설정
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001

# 5001 포트를 컨테이너 외부에 노출
EXPOSE 5001

# 애플리케이션 실행
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
