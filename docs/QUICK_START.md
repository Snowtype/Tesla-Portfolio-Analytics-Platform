# ⚡ TESLA TPC 빠른 시작 가이드

## 🚀 **1분만에 시작하기**

### **1. Alias 설정 (최초 1회만)**

```bash
./scripts/setup_aliases.sh
source ~/.zshrc  # 또는 ~/.bashrc
```

### **2. 개발 시작**

```bash
tpc-dev      # 개발 서버 실행 (8501)
```

브라우저에서 http://localhost:8501 접속

---

## 📊 **포트별 역할**

| 포트     | 역할          | 명령어      | URL                   |
| -------- | ------------- | ----------- | --------------------- |
| **8501** | 🔧 개발       | `tpc-dev`   | http://localhost:8501 |
| **8502** | 🧪 테스트     | `tpc-test`  | http://localhost:8502 |
| **8503** | 🔵 Blue 운영  | `tpc-blue`  | http://localhost:8503 |
| **8504** | 🟢 Green 운영 | `tpc-green` | http://localhost:8504 |

---

## ⚡ **자주 사용하는 명령어**

```bash
# 🚀 서버 실행
tpc-dev      # 개발 서버 (포그라운드)
tpc-test     # 테스트 서버 (백그라운드)
tpc-blue     # Blue 운영 서버 (백그라운드)
tpc-green    # Green 운영 서버 (백그라운드)

# 📊 모니터링
tpc-status   # 모든 포트 상태 확인
tpc-logs 8501  # 특정 포트 로그 확인

# 🛑 서버 제어
tpc-stop     # 모든 서버 종료
tpc-kill 8501  # 특정 포트만 종료

# 🚀 배포
tpc-deploy   # 대화형 배포 도구
```

---

## 🔄 **기본 vs 스크립트 실행**

### **기본 Streamlit 실행**

```bash
# 포그라운드 (터미널 점유)
streamlit run app.py --server.port 8501

# 백그라운드 (복잡한 명령어)
nohup streamlit run app.py --server.port 8501 > logs/streamlit_8501.log 2>&1 &
```

### **스크립트 실행 (권장)**

```bash
# 간단하고 안전
tpc-dev      # 개발
tpc-test     # 테스트 (자동 백그라운드)
```

**스크립트 사용 시 장점:**

- ✅ 간단한 명령어
- ✅ 자동 포트 중복 체크
- ✅ 자동 로그 관리
- ✅ 에러 처리

---

## 🔍 **헬스체크 (서버 상태 확인)**

```bash
# 기본 헬스체크
curl http://localhost:8501/_stcore/health

# 응답:
# "ok" → 서버 정상
# 에러 → 서버 중지
```

---

## 💡 **실제 사용 예시**

### **개발 작업**

```bash
tpc-dev                    # 개발 서버 실행
# 브라우저에서 http://localhost:8501 접속
# 코드 수정 → 자동 리로드
# Ctrl+C로 종료
```

### **테스트 배포**

```bash
tpc-test                   # 테스트 서버 실행 (백그라운드)
tpc-logs 8502             # 로그 확인
# QA팀에게 http://localhost:8502 공유
tpc-kill 8502             # 테스트 완료 후 종료
```

### **운영 배포**

```bash
tpc-status                # 현재 상태 확인
tpc-deploy                # 배포 도구 실행
# 메뉴에서 "3. 운영 배포" 선택
```

---

## 🚨 **문제 해결**

### **포트 충돌 시**

```bash
tpc-status               # 어떤 포트가 사용 중인지 확인
tpc-kill 8501           # 특정 포트 종료
tpc-stop                # 모든 포트 종료
```

### **서버가 안 켜질 때**

```bash
tpc-logs 8501           # 로그 확인으로 에러 원인 파악
```

### **헬스체크 실패 시**

```bash
curl http://localhost:8501/_stcore/health
# 응답이 없으면 서버가 완전히 시작되지 않은 상태
# 몇 초 기다린 후 재시도
```

---

## 📋 **치트시트**

```bash
# 🚀 필수 명령어 5개
tpc-dev      # 개발 시작
tpc-test     # 테스트 배포
tpc-status   # 상태 확인
tpc-deploy   # 운영 배포
tpc-stop     # 전체 중지

# 🔍 디버깅 명령어
tpc-logs <포트>   # 로그 확인
tpc-kill <포트>   # 특정 포트 종료
tpc-help          # 도움말
```

이 가이드로 TESLA TPC Streamlit을 쉽고 안전하게 운영하세요! 🎯
