# 🚀 클라우드 배포 가이드

이 가이드는 Streamlit A/B 테스트 환경을 클라우드 서버에 배포하는 방법을 설명합니다.

## 📋 사전 요구사항

- Ubuntu/Debian 기반 서버
- sudo 권한이 있는 사용자 계정
- 도메인 (선택사항, SSL 인증서용)

## 🎯 배포 옵션

### 1. 직접 배포 (권장)

```bash
# 1. 프로젝트 클론
git clone <your-repository>
cd TESLA_TPC_STREAMLIT

# 2. 배포 스크립트 실행
chmod +x deploy_cloud.sh
./deploy_cloud.sh
```

### 2. Docker 배포

```bash
# 1. Docker 및 Docker Compose 설치
sudo apt update
sudo apt install -y docker.io docker-compose

# 2. SSL 인증서 생성
mkdir -p ssl_certs
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl_certs/nginx-selfsigned.key \
    -out ssl_certs/nginx-selfsigned.crt \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Company/CN=localhost"

# 3. Docker Compose로 배포
docker-compose -f docker-compose.cloud.yml up -d
```

## 🌐 접속 방법

배포 완료 후 다음 URL로 접속할 수 있습니다:

### HTTP 접속

- **A 버전 (기존)**: `http://your-server-ip/a/`
- **B 버전 (새로운 기능)**: `http://your-server-ip/b/`
- **A/B 테스트 선택 페이지**: `http://your-server-ip/ab-test/`

### HTTPS 접속 (SSL 설정 후)

- **A 버전 (기존)**: `https://your-server-ip/a/`
- **B 버전 (새로운 기능)**: `https://your-server-ip/b/`
- **A/B 테스트 선택 페이지**: `https://your-server-ip/ab-test/`

## 🔧 관리 명령어

### 직접 배포 환경

```bash
# 상태 확인
./monitor_cloud.sh

# 서비스 재시작
sudo systemctl restart streamlit-a
sudo systemctl restart streamlit-b
sudo systemctl restart nginx

# 로그 확인
sudo journalctl -u streamlit-a -f
sudo journalctl -u streamlit-b -f
sudo tail -f /var/log/nginx/access.log
```

### Docker 환경

```bash
# 상태 확인
docker-compose -f docker-compose.cloud.yml ps

# 서비스 재시작
docker-compose -f docker-compose.cloud.yml restart

# 로그 확인
docker-compose -f docker-compose.cloud.yml logs -f streamlit-a
docker-compose -f docker-compose.cloud.yml logs -f streamlit-b
docker-compose -f docker-compose.cloud.yml logs -f nginx
```

## 🧪 A/B 테스트 환경

### A 버전 (기존)

- **포트**: 8501
- **특징**: 현재 운영 중인 버전
- **기능**: 기본적인 대시보드 및 분석 기능

### B 버전 (새로운 기능)

- **포트**: 8502
- **특징**: 새로운 기능이 추가된 테스트 버전
- **새로운 기능**:
  - 🔔 실시간 알림 시스템
  - 🌙 다크모드 토글
  - ⚡ 성능 개선된 데이터 캐싱
  - 🎨 개선된 UI/UX

## 📊 모니터링

### 헬스체크

- nginx: `http://your-server-ip/health`
- Streamlit A: `http://your-server-ip:8501/_stcore/health`
- Streamlit B: `http://your-server-ip:8502/_stcore/health`

### 로그 위치

- nginx: `/var/log/nginx/`
- Streamlit A: `sudo journalctl -u streamlit-a`
- Streamlit B: `sudo journalctl -u streamlit-b`

## 🔒 보안 설정

### 방화벽

```bash
# 필요한 포트만 열기
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8501
sudo ufw allow 8502
sudo ufw --force enable
```

### SSL 인증서 (Let's Encrypt)

도메인이 있는 경우:

```bash
sudo certbot --nginx -d your-domain.com
```

## 🚨 문제 해결

### 포트 충돌

```bash
# 포트 사용 확인
sudo netstat -tlnp | grep -E ':(80|443|8501|8502)'

# 프로세스 종료
sudo kill -9 <PID>
```

### 서비스 시작 실패

```bash
# 서비스 상태 확인
sudo systemctl status streamlit-a
sudo systemctl status streamlit-b
sudo systemctl status nginx

# 로그 확인
sudo journalctl -u streamlit-a --no-pager -l
```

### nginx 설정 오류

```bash
# 설정 파일 문법 검사
sudo nginx -t

# nginx 재시작
sudo systemctl restart nginx
```

## 📈 성능 최적화

### nginx 설정

- Gzip 압축 활성화
- 정적 파일 캐싱
- 연결 타임아웃 설정

### Streamlit 설정

- `--server.headless true`: 헤드리스 모드
- `--server.fileWatcherType none`: 파일 감시 비활성화 (프로덕션)

## 🔄 업데이트 방법

### 코드 업데이트

```bash
# 1. 코드 업데이트
git pull origin main

# 2. 서비스 재시작
sudo systemctl restart streamlit-a
sudo systemctl restart streamlit-b
```

### Docker 환경 업데이트

```bash
# 1. 이미지 재빌드
docker-compose -f docker-compose.cloud.yml build

# 2. 서비스 재시작
docker-compose -f docker-compose.cloud.yml up -d
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. 로그 파일 확인
2. 서비스 상태 확인
3. 포트 및 방화벽 설정 확인
4. SSL 인증서 유효성 확인
