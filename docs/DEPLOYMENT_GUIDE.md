# 🚀 TESLA TPC Streamlit 배포 가이드

## 📋 포트 구성

| 포트     | 역할              | 설명                     | 접속 URL              |
| -------- | ----------------- | ------------------------ | --------------------- |
| **8501** | 🔧 **개발**       | 개발 중인 기능 테스트    | http://localhost:8501 |
| **8502** | 🧪 **테스트**     | 스테이징 환경, QA 테스트 | http://localhost:8502 |
| **8503** | 🔵 **Blue 운영**  | 운영 서버 (Blue)         | http://localhost:8503 |
| **8504** | 🟢 **Green 운영** | 운영 서버 (Green)        | http://localhost:8504 |

---

## 🔄 개발 → 운영 플로우

### 1️⃣ **개발 단계 (8501)**

```bash
# 개발 서버 실행
streamlit run app.py --server.port 8501

# 또는 alias 사용 (설정 후)
tpc-dev
```

**특징:**

- 포그라운드 실행 (터미널에서 직접 확인)
- 코드 변경 시 자동 리로드
- 디버깅 용이

### 2️⃣ **테스트 단계 (8502)**

```bash
# 테스트 서버 실행 (백그라운드)
nohup streamlit run app.py --server.port 8502 > logs/streamlit_8502.log 2>&1 &

# 또는 alias 사용
tpc-test
```

**특징:**

- 백그라운드 실행
- QA 팀 테스트 환경
- 로그 파일로 모니터링

### 3️⃣ **운영 배포 (Blue-Green)**

#### **현재 상태 확인**

```bash
# 포트 상태 확인
lsof -i :8503 -i :8504

# 또는 alias 사용
tpc-status
```

#### **Blue-Green 배포 시나리오**

**시나리오 A: Blue(8503) → Green(8504) 배포**

```bash
# 1. Green 서버에 새 버전 배포
nohup streamlit run app.py --server.port 8504 > logs/streamlit_8504.log 2>&1 &

# 2. Green 서버 헬스체크
curl -f http://localhost:8504/_stcore/health

# 3. nginx 설정 변경 (upstream을 8504로)
# nginx.conf에서 upstream 설정 변경 후:
sudo nginx -s reload

# 4. Blue 서버 종료
lsof -ti:8503 | xargs kill -9
```

**시나리오 B: Green(8504) → Blue(8503) 배포**

```bash
# 1. Blue 서버에 새 버전 배포
nohup streamlit run app.py --server.port 8503 > logs/streamlit_8503.log 2>&1 &

# 2. Blue 서버 헬스체크
curl -f http://localhost:8503/_stcore/health

# 3. nginx 설정 변경 (upstream을 8503으로)
sudo nginx -s reload

# 4. Green 서버 종료
lsof -ti:8504 | xargs kill -9
```

---

## 🛠️ 자동화 도구 사용법

### **1. 배포 자동화 스크립트**

```bash
# 대화형 배포 도구 실행
./scripts/deploy.sh

# 또는 alias 사용
tpc-deploy
```

**메뉴 옵션:**

- `1` - 개발 서버 실행 (8501)
- `2` - 테스트 서버 실행 (8502)
- `3` - 운영 배포 (Blue-Green)
- `4` - 포트 상태 확인
- `5` - 모든 서버 종료
- `6` - 로그 확인

### **2. 빠른 명령어**

```bash
# 개발 서버
./scripts/quick_commands.sh dev
tpc-dev

# 테스트 서버
./scripts/quick_commands.sh test
tpc-test

# Blue/Green 서버
./scripts/quick_commands.sh blue
./scripts/quick_commands.sh green
tpc-blue
tpc-green

# 상태 확인
./scripts/quick_commands.sh status
tpc-status

# 모든 서버 종료
./scripts/quick_commands.sh stop
tpc-stop

# 로그 확인
./scripts/quick_commands.sh logs 8501
tpc-logs 8501

# 특정 포트 종료
./scripts/quick_commands.sh kill_port 8501
tpc-kill 8501
```

### **3. Alias 설정**

```bash
# alias 설정 (최초 1회)
./scripts/setup_aliases.sh
source ~/.zshrc  # 또는 ~/.bashrc
```

---

## 📊 모니터링

### **포트 상태 확인**

```bash
# 간단한 확인
lsof -i :8501 -i :8502 -i :8503 -i :8504

# 상세 확인
tpc-status
```

### **로그 모니터링**

```bash
# 실시간 로그 확인
tail -f logs/streamlit_8501.log
tail -f logs/streamlit_8502.log
tail -f logs/streamlit_8503.log
tail -f logs/streamlit_8504.log

# 또는 alias 사용
tpc-logs 8501
```

### **헬스체크**

```bash
# Streamlit 헬스체크 엔드포인트
curl http://localhost:8501/_stcore/health
curl http://localhost:8502/_stcore/health
curl http://localhost:8503/_stcore/health
curl http://localhost:8504/_stcore/health
```

---

## 🚨 트러블슈팅

### **포트 충돌 해결**

```bash
# 특정 포트 사용 프로세스 확인
lsof -i :8501

# 강제 종료
lsof -ti:8501 | xargs kill -9

# 모든 Streamlit 프로세스 종료
pkill -f streamlit
```

### **로그 확인**

```bash
# 에러 로그 확인
grep -i error logs/streamlit_*.log

# 최근 100줄 확인
tail -n 100 logs/streamlit_8501.log
```

### **권한 문제**

```bash
# 스크립트 실행 권한 부여
chmod +x scripts/*.sh

# 로그 디렉토리 권한 확인
ls -la logs/
```

---

## 🔧 nginx 설정 예시

### **Blue-Green 설정**

```nginx
upstream backend {
    # Blue 또는 Green 중 하나만 활성화
    server localhost:8503;  # Blue
    # server localhost:8504;  # Green
}

server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **A/B 테스트 설정**

```nginx
upstream blue_backend {
    server localhost:8503;
}

upstream green_backend {
    server localhost:8504;
}

server {
    listen 80;
    server_name localhost;

    # A/B 테스트 분기
    location /blue/ {
        rewrite ^/blue/(.*)$ /$1 break;
        proxy_pass http://blue_backend;
        # ... 기타 proxy 설정
    }

    location /green/ {
        rewrite ^/green/(.*)$ /$1 break;
        proxy_pass http://green_backend;
        # ... 기타 proxy 설정
    }
}
```

---

## 📝 배포 체크리스트

### **개발 완료 후**

- [ ] 코드 테스트 완료
- [ ] 8501에서 기능 검증
- [ ] Git 커밋 & 푸시

### **테스트 배포**

- [ ] 8502 테스트 서버 배포
- [ ] QA 테스트 수행
- [ ] 성능 테스트 완료

### **운영 배포**

- [ ] 현재 운영 포트 확인
- [ ] 반대 포트에 새 버전 배포
- [ ] 헬스체크 통과
- [ ] nginx 설정 변경
- [ ] 기존 서버 종료
- [ ] 운영 모니터링

### **배포 후**

- [ ] 서비스 정상 동작 확인
- [ ] 로그 모니터링
- [ ] 성능 지표 확인
- [ ] 사용자 피드백 수집

---

## 🎯 베스트 프랙티스

### **개발 환경**

- 개발은 항상 8501 포트 사용
- 코드 변경 시 즉시 테스트
- 디버깅 정보 충분히 활용

### **테스트 환경**

- 운영과 동일한 환경 구성
- 자동화된 테스트 스크립트 활용
- 성능 테스트 포함

### **운영 환경**

- Blue-Green 배포로 무중단 서비스
- 롤백 계획 항상 준비
- 모니터링 및 알림 설정

### **보안**

- 운영 서버는 방화벽 설정
- 로그 파일 정기적 백업
- 접근 권한 최소화

---

## 📞 지원

문제 발생 시:

1. 로그 파일 확인 (`tpc-logs <포트>`)
2. 포트 상태 확인 (`tpc-status`)
3. 트러블슈팅 가이드 참조
4. 필요시 전체 재시작 (`tpc-stop` → 재배포)
