# 📜 TESLA TPC Scripts 가이드

## 🗂️ Scripts 폴더 구조

```
scripts/
├── deploy.sh              # 🚀 메인 배포 자동화 스크립트
├── quick_commands.sh       # ⚡ 빠른 명령어 모음
├── setup_aliases.sh        # 🔗 쉘 Alias 설정
├── blue_green_deploy.sh    # 🔄 Blue-Green 배포 전용
├── deploy_cloud.sh         # ☁️ 클라우드 배포
├── run_ab_test.sh         # 🧪 A/B 테스트 실행
├── run_prod_blue_green.sh  # 🏭 운영 Blue-Green 실행
├── update_prod.sh         # 🔄 운영 서버 업데이트
├── run_dev.sh             # 🔧 개발 서버 간단 실행
├── run_prod_background.sh  # 🏃 운영 서버 백그라운드 실행
└── monitor.sh             # 📊 모니터링 스크립트
```

---

## 🚀 **메인 스크립트들**

### **1. deploy.sh** - 메인 배포 자동화 도구

```bash
./scripts/deploy.sh
# 또는
tpc-deploy
```

**🎯 역할:**

- 대화형 메뉴로 모든 배포 옵션 제공
- 포트 상태 확인 및 관리
- Blue-Green 배포 자동화
- 로그 모니터링
- 헬스체크 수행

**📋 메뉴 옵션:**

1. 🔧 개발 서버 실행 (8501)
2. 🧪 테스트 서버 실행 (8502)
3. 🚀 운영 배포 (Blue-Green)
4. 📊 포트 상태 확인
5. 🛑 모든 서버 종료
6. 📋 로그 확인

**✨ 특징:**

- 안전한 Blue-Green 배포
- 자동 헬스체크
- 에러 처리 및 롤백
- 로그 자동 생성

---

### **2. quick_commands.sh** - 빠른 명령어 모음

```bash
./scripts/quick_commands.sh <command>
# 또는 alias 사용
tpc-<command>
```

**🎯 역할:**

- 단일 명령어로 서버 실행/관리
- 터미널에서 빠른 작업 수행
- 개발자 친화적 인터페이스

**📋 사용 가능한 명령어:**

```bash
# 서버 실행
dev          # 개발 서버 (8501)
test         # 테스트 서버 (8502)
blue         # Blue 서버 (8503)
green        # Green 서버 (8504)

# 모니터링
status       # 포트 상태 확인
logs <포트>  # 로그 확인

# 서버 제어
stop         # 모든 서버 종료
kill_port <포트>  # 특정 포트 종료

# 도움말
help         # 사용법 표시
```

**📖 예시:**

```bash
./scripts/quick_commands.sh dev     # 개발 서버 실행
./scripts/quick_commands.sh status  # 상태 확인
./scripts/quick_commands.sh logs 8501  # 8501 로그 확인
```

---

### **3. setup_aliases.sh** - 쉘 Alias 설정

```bash
./scripts/setup_aliases.sh
source ~/.zshrc  # 설정 적용
```

**🎯 역할:**

- 편리한 alias 명령어 생성
- 쉘 환경 자동 감지 (zsh/bash)
- 프로젝트 디렉토리 자동 인식

**📋 생성되는 Alias:**

```bash
tpc-deploy   # 배포 도구 실행
tpc-dev      # 개발 서버 실행
tpc-test     # 테스트 서버 실행
tpc-blue     # Blue 서버 실행
tpc-green    # Green 서버 실행
tpc-status   # 포트 상태 확인
tpc-stop     # 모든 서버 종료
tpc-logs     # 로그 확인
tpc-kill     # 특정 포트 종료
tpc-help     # 도움말
tpc-cd       # 프로젝트 디렉토리로 이동
```

---

## 🔄 **배포 전용 스크립트들**

### **4. blue_green_deploy.sh** - Blue-Green 배포 전용

```bash
./scripts/blue_green_deploy.sh
```

**🎯 역할:**

- Blue-Green 배포에만 특화
- 안전한 무중단 배포
- 자동 롤백 기능

### **5. deploy_cloud.sh** - 클라우드 배포

```bash
./scripts/deploy_cloud.sh
```

**🎯 역할:**

- 클라우드 환경 배포
- 환경 변수 관리
- 외부 서비스 연동

### **6. run_ab_test.sh** - A/B 테스트

```bash
./scripts/run_ab_test.sh
```

**🎯 역할:**

- A/B 테스트 환경 구성
- 트래픽 분산 설정
- 성능 비교 테스트

---

## 🏭 **운영 관리 스크립트들**

### **7. run_prod_blue_green.sh** - 운영 Blue-Green

```bash
./scripts/run_prod_blue_green.sh
```

**🎯 역할:**

- 운영 환경 Blue-Green 실행
- 프로덕션 설정 적용

### **8. update_prod.sh** - 운영 서버 업데이트

```bash
./scripts/update_prod.sh
```

**🎯 역할:**

- 운영 서버 코드 업데이트
- 의존성 패키지 업데이트

### **9. run_prod_background.sh** - 운영 백그라운드 실행

```bash
./scripts/run_prod_background.sh
```

**🎯 역할:**

- 운영 서버 백그라운드 실행
- 시스템 재시작 시 자동 실행

---

## 🔧 **개발 및 모니터링 스크립트들**

### **10. run_dev.sh** - 개발 서버 간단 실행

```bash
./scripts/run_dev.sh
```

**🎯 역할:**

- 개발 서버 빠른 실행
- 최소한의 설정으로 실행

### **11. monitor.sh** - 모니터링

```bash
./scripts/monitor.sh
```

**🎯 역할:**

- 서버 상태 모니터링
- 리소스 사용량 확인
- 알림 및 로깅

---

## 🌐 **포트별 운영 방법**

### **📊 포트 구성 요약**

| 포트     | 역할      | 실행 방법   | 접속 URL              | 용도         |
| -------- | --------- | ----------- | --------------------- | ------------ |
| **8501** | 🔧 개발   | `tpc-dev`   | http://localhost:8501 | 개발/디버깅  |
| **8502** | 🧪 테스트 | `tpc-test`  | http://localhost:8502 | QA/스테이징  |
| **8503** | 🔵 Blue   | `tpc-blue`  | http://localhost:8503 | 운영 (Blue)  |
| **8504** | 🟢 Green  | `tpc-green` | http://localhost:8504 | 운영 (Green) |

### **🚀 기본 Streamlit 실행 vs 스크립트 실행**

#### **1. 기본 Streamlit 실행**

```bash
# 포그라운드 실행 (터미널 점유)
streamlit run app.py --server.port 8501

# 백그라운드 실행 (터미널에서 분리)
nohup streamlit run app.py --server.port 8501 > logs/streamlit_8501.log 2>&1 &
```

**특징:**

- ✅ 직접적인 제어
- ❌ 매번 긴 명령어 입력
- ❌ 포트 중복 체크 안 함
- ❌ 로그 관리 수동

#### **2. 스크립트 실행**

```bash
# 개발 서버
tpc-dev

# 테스트 서버 (백그라운드)
tpc-test

# 상태 확인
tpc-status
```

**특징:**

- ✅ 간단한 명령어
- ✅ 자동 포트 중복 체크
- ✅ 자동 로그 관리
- ✅ 에러 처리
- ✅ 헬스체크 포함

### **🔍 curl 헬스체크 사용법**

```bash
# 기본 헬스체크
curl http://localhost:8501/_stcore/health

# 응답 예시
# "ok" - 정상
# curl: (7) Failed to connect - 서버 중지

# 조건부 헬스체크 (스크립트에서 사용)
if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
    echo "서버 정상"
else
    echo "서버 중지"
fi
```

### **💡 실제 사용 시나리오**

#### **개발 작업 시**

```bash
# 1. 개발 서버 실행
tpc-dev

# 2. 브라우저에서 http://localhost:8501 접속
# 3. 코드 수정 후 자동 리로드 확인
# 4. Ctrl+C로 종료
```

#### **테스트 배포 시**

```bash
# 1. 테스트 서버 실행 (백그라운드)
tpc-test

# 2. QA팀에게 http://localhost:8502 공유
# 3. 로그 확인
tpc-logs 8502

# 4. 테스트 완료 후 종료
tpc-kill 8502
```

#### **운영 배포 시**

```bash
# 1. 현재 상태 확인
tpc-status

# 2. Blue-Green 배포 실행
tpc-deploy
# 메뉴에서 "3. 운영 배포" 선택

# 3. 배포 완료 후 확인
curl http://localhost:8503/_stcore/health
curl http://localhost:8504/_stcore/health
```

---

## 🎯 **권장 사용 패턴**

### **개발자용**

```bash
# 일상적인 개발
tpc-dev

# 기능 테스트
tpc-test
tpc-logs 8502
```

### **운영자용**

```bash
# 상태 모니터링
tpc-status

# 배포 작업
tpc-deploy

# 긴급 중지
tpc-stop
```

### **관리자용**

```bash
# 전체 시스템 모니터링
./scripts/monitor.sh

# Blue-Green 배포
./scripts/blue_green_deploy.sh

# 클라우드 배포
./scripts/deploy_cloud.sh
```

---

## 📋 **빠른 참조**

```bash
# 🚀 가장 많이 사용하는 명령어들
tpc-dev      # 개발 시작
tpc-test     # 테스트 배포
tpc-status   # 상태 확인
tpc-deploy   # 운영 배포
tpc-stop     # 전체 중지

# 🔍 문제 해결
tpc-logs 8501    # 로그 확인
tpc-kill 8501    # 특정 포트 종료
tpc-help         # 도움말
```

이 가이드를 참고하여 효율적으로 TESLA TPC Streamlit 애플리케이션을 관리하세요! 🚀
