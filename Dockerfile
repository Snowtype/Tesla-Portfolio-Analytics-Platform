# ==================================
# 1. Builder Stage
# ==================================
FROM python:3.10-slim as builder

WORKDIR /app

# 시스템 패키지 업데이트 및 빌드에 필요한 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential

# Python 가상환경 생성
RUN python -m venv /opt/venv

# 환경변수에 가상환경 경로 추가
ENV PATH="/opt/venv/bin:$PATH"

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==================================
# 2. Final Stage
# ==================================
FROM python:3.10-slim

WORKDIR /app

# Builder 스테이지에서 생성한 가상환경 복사
COPY --from=builder /opt/venv /opt/venv

# 애플리케이션 코드 복사
COPY . .

# 환경변수에 가상환경 경로 추가
ENV PATH="/opt/venv/bin:$PATH"

# 보안을 위해 non-root 사용자 생성 및 전환 (Host OS와 UID/GID 동기화)
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID -o appgroup || true
RUN useradd --uid $UID --gid $GID --create-home appuser

USER appuser

# 기본 실행 포트 설정 (docker-compose에서 오버라이드 가능)
EXPOSE 8501

# 컨테이너 실행 명령어
CMD ["streamlit", "run", "app.py"] 