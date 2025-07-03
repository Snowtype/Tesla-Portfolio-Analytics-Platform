# 📁 TESLA TPC Streamlit 프로젝트 구조

## 🌳 전체 디렉토리 구조

```
TESLA_TPC_STREAMLIT/
│
├── 📄 README.md                     # 🚀 프로젝트 메인 문서
├── 📄 requirements.txt              # 📦 Python 패키지 의존성
├── 📄 app.py                        # 🎯 메인 Streamlit 애플리케이션
├── 📄 snowflake_connection.py       # ❄️ Snowflake 연결 관리
├── 📄 security_utils.py             # 🔐 보안 유틸리티
│
├── 📂 page_modules/                 # 📊 분석 페이지 모듈들
│   ├── 📄 __init__.py
│   ├── 📄 user_segment_mau.py       # 👥 유저 세그먼트 및 MAU
│   ├── 📄 new_subscribers.py        # 📈 일자별 신규 가입자
│   ├── 📄 region_age_data.py        # 🗺️ 지역/연령 데이터
│   ├── 📄 heavy_users_by_menu.py    # 🍽️ 메뉴별 헤비유저
│   ├── 📄 heavy_users_simple.py     # 💪 헤비유저 분석
│   ├── 📄 sales_by_category.py      # 💰 카테고리별 매출
│   ├── 📄 repurchase_rate.py        # 🔄 재구매 고객비율
│   ├── 📄 non_new_sig_customers.py  # 📌 신규/시그니처 미구매 고객
│   └── 📄 regional_purchase_analysis.py  # 🗺️ 지역별 구매 주기 및 주력 상품
│
├── 📂 scripts/                      # 🛠️ 배포 자동화 스크립트들
│   ├── 📄 deploy.sh                 # 🚀 메인 배포 자동화 도구
│   ├── 📄 quick_commands.sh         # ⚡ 빠른 명령어 모음
│   ├── 📄 setup_aliases.sh          # 🔗 쉘 Alias 설정
│   ├── 📄 blue_green_deploy.sh      # 🔄 Blue-Green 배포 전용
│   ├── 📄 deploy_cloud.sh           # ☁️ 클라우드 배포
│   ├── 📄 run_ab_test.sh            # 🧪 A/B 테스트 실행
│   ├── 📄 run_prod_blue_green.sh    # 🏭 운영 Blue-Green 실행
│   ├── 📄 update_prod.sh            # 🔄 운영 서버 업데이트
│   ├── 📄 run_dev.sh                # 🔧 개발 서버 간단 실행
│   ├── 📄 run_prod_background.sh    # 🏃 운영 서버 백그라운드 실행
│   └── 📄 monitor.sh                # 📊 모니터링 스크립트
│
├── 📂 docs/                         # 📚 문서화
│   ├── 📄 DEPLOYMENT_GUIDE.md       # 🚀 배포 가이드
│   ├── 📄 SCRIPTS_GUIDE.md          # 📜 스크립트 상세 가이드
│   ├── 📄 QUICK_START.md            # ⚡ 빠른 시작 가이드
│   └── 📄 PROJECT_STRUCTURE.md      # 📁 프로젝트 구조 (현재 파일)
│
├── 📂 logs/                         # 📋 로그 파일들
│   ├── 📄 streamlit_8501.log        # 🔧 개발 서버 로그
│   ├── 📄 streamlit_8502.log        # 🧪 테스트 서버 로그
│   ├── 📄 streamlit_8503.log        # 🔵 Blue 운영 서버 로그
│   ├── 📄 streamlit_8504.log        # 🟢 Green 운영 서버 로그
│   ├── 📄 security_events.log       # 🔐 보안 이벤트 로그
│   └── 📄 security_events_port_*.log # 🔐 포트별 보안 로그
│
├── 📂 .streamlit/                   # ⚙️ Streamlit 설정
│   ├── 📄 config.toml               # 🔧 Streamlit 기본 설정
│   ├── 📄 secrets.toml              # 🔐 Snowflake 연결 정보 (비공개)
│   ├── 📄 secrets.toml.example      # 📝 설정 파일 템플릿
│   └── 📄 session.json              # 💾 세션 저장 파일
│
└── 📂 __pycache__/                  # 🐍 Python 캐시 (자동 생성)
    └── *.pyc
```

---

## 📋 **파일별 상세 설명**

### 🎯 **메인 애플리케이션**

| 파일명                    | 역할    | 설명                                             |
| ------------------------- | ------- | ------------------------------------------------ |
| `app.py`                  | 메인 앱 | Streamlit 메인 애플리케이션, 페이지 라우팅, 인증 |
| `snowflake_connection.py` | DB 연결 | Snowflake 연결 관리 및 세션 생성                 |
| `security_utils.py`       | 보안    | 로깅, 인증, IP 추적 등 보안 기능                 |

### 📊 **분석 페이지 모듈**

| 모듈명                          | 기능                  | 주요 데이터                   |
| ------------------------------- | --------------------- | ----------------------------- |
| `user_segment_mau.py`           | 사용자 세그먼트 분석  | MAU, 활성/비활성 사용자       |
| `new_subscribers.py`            | 신규 가입자 추이      | 일별 신규 가입자 수           |
| `region_age_data.py`            | 인구통계 분석         | 지역별, 연령별 사용자 분포    |
| `heavy_users_by_menu.py`        | 메뉴별 헤비유저       | 상품별 고빈도 사용자 분석     |
| `heavy_users_simple.py`         | 헤비유저 간단 분석    | 기본 헤비유저 통계            |
| `sales_by_category.py`          | 카테고리별 매출       | 상품 카테고리 성과            |
| `repurchase_rate.py`            | 재구매율 분석         | 고객 재방문 패턴              |
| `non_new_sig_customers.py`      | 특정 상품 미구매 고객 | 신규/시그니처 미구매 분석     |
| `regional_purchase_analysis.py` | 지역별 구매 분석      | 지역별 구매 주기 및 인기 상품 |

### 🛠️ **배포 스크립트**

| 스크립트명             | 용도            | 실행 방법                               |
| ---------------------- | --------------- | --------------------------------------- |
| `deploy.sh`            | 메인 배포 도구  | `./scripts/deploy.sh` 또는 `tpc-deploy` |
| `quick_commands.sh`    | 빠른 명령어     | `./scripts/quick_commands.sh <command>` |
| `setup_aliases.sh`     | Alias 설정      | `./scripts/setup_aliases.sh`            |
| `blue_green_deploy.sh` | Blue-Green 배포 | `./scripts/blue_green_deploy.sh`        |
| `deploy_cloud.sh`      | 클라우드 배포   | `./scripts/deploy_cloud.sh`             |

### 📚 **문서화**

| 문서명                 | 내용               | 대상          |
| ---------------------- | ------------------ | ------------- |
| `README.md`            | 프로젝트 전체 개요 | 모든 사용자   |
| `DEPLOYMENT_GUIDE.md`  | 배포 가이드        | 개발자/운영자 |
| `SCRIPTS_GUIDE.md`     | 스크립트 설명서    | 개발자/운영자 |
| `QUICK_START.md`       | 빠른 시작 가이드   | 신규 개발자   |
| `PROJECT_STRUCTURE.md` | 프로젝트 구조      | 개발자        |

---

## 🔄 **데이터 흐름**

```
📱 [커피숍 앱]
     ↓
❄️ [Snowflake DW]
     ↓
🔄 [Dynamic Tables]
     ↓
🐍 [Python/Streamlit]
     ↓
📊 [Plotly Visualizations]
     ↓
👤 [사용자 브라우저]
```

---

## 🌐 **포트별 환경 구성**

```
🔧 개발 환경 (8501)
   ├── 포그라운드 실행
   ├── 실시간 코드 리로드
   └── 디버깅 모드

🧪 테스트 환경 (8502)
   ├── 백그라운드 실행
   ├── QA 테스트용
   └── 로그 파일 저장

🔵 Blue 운영 (8503)
   ├── 백그라운드 실행
   ├── 운영 서버 A
   └── nginx 업스트림

🟢 Green 운영 (8504)
   ├── 백그라운드 실행
   ├── 운영 서버 B
   └── Blue-Green 배포용
```

---

## 🔐 **보안 구조**

```
👤 [사용자 로그인]
     ↓
🔑 [계정 인증]
     ├── tpc_user → TPC 브랜드 데이터
     ├── mmc_user → MMC 브랜드 데이터
     └── admin → 전체 브랜드 + 관리 기능
     ↓
💾 [세션 관리]
     ├── 파일 기반 저장
     ├── 24시간 자동 만료
     └── IP 추적 및 로깅
     ↓
📊 [데이터 접근]
     └── 브랜드별 스키마 분리
```

---

## 📦 **의존성 관리**

### **핵심 패키지**

- `streamlit` - 웹 애플리케이션 프레임워크
- `snowflake-connector-python` - Snowflake 연결
- `plotly` - 인터랙티브 시각화
- `pandas` - 데이터 처리

### **개발 도구**

- `black` - 코드 포매팅
- `flake8` - 코드 품질 검사
- `pytest` - 단위 테스트

### **성능 최적화**

- `watchdog` - 파일 변경 감지
- `@st.cache_data` - 데이터 캐싱

---

## 🚀 **확장 가능한 구조**

### **새 페이지 추가 시**

1. `page_modules/new_analysis.py` 생성
2. `app.py`에서 import 및 라우팅 추가
3. 페이지 딕셔너리에 메타데이터 등록

### **새 브랜드 추가 시**

1. `BRAND_SCHEMA`에 스키마 추가
2. `USER_CREDENTIALS`에 계정 추가
3. `brand_texts`에 브랜드 텍스트 추가

### **새 환경 추가 시**

1. 새 포트 번호 할당
2. 스크립트에 포트 정보 추가
3. nginx 설정 업데이트

이 구조는 확장성과 유지보수성을 고려하여 설계되었으며, 모듈형 아키텍처로 새로운 기능을 쉽게 추가할 수 있습니다. 🎯
