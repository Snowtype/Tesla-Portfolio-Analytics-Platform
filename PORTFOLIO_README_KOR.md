# 🚀 Portfolio: Multi-Brand Analytics Platform

## 👋 테슬라 리쿠르터님께

안녕하세요! 이 프로젝트는 제가 실제 업무에서 개발한 **다중 브랜드 커피체인 분석 플랫폼**을 포트폴리오용으로 각색한 것입니다.

> **⚠️ 개인정보보호**: 실제 브랜드명, DB 연결정보, API 키 등은 모두 마스킹 처리하였습니다.

---

## 🎯 프로젝트 하이라이트

### **1. 실제 프로덕션 환경에서 운영된 프로젝트**

- 일일 수백만 건의 거래 데이터 처리
- 실시간 대시보드로 비즈니스 의사결정 지원
- 다중 브랜드 환경에서 안정적 운영

### **2. 확장 가능한 아키텍처**

```python
# 모듈화된 페이지 구조
page_modules/
├── user_segment_mau.py      # 사용자 세그먼트 분석
├── sales_by_category.py     # 매출 분석
├── regional_analysis.py     # 지역별 분석
└── repurchase_rate.py       # 재구매율 분석
```

### **3. 데이터 보안 및 접근 제어**

- 브랜드별 스키마 분리
- 역할 기반 접근 제어 (RBAC)
- 세션 관리 및 로깅

---

## 🛠️ 기술 스택 및 역량 증명

| 영역                 | 기술                            | 적용 사례                          |
| -------------------- | ------------------------------- | ---------------------------------- |
| **Backend**          | Python, Snowflake               | 대용량 데이터 처리, 동적 쿼리 생성 |
| **Frontend**         | Streamlit                       | 직관적 대시보드 UI/UX              |
| **Data Engineering** | Snowpark, Dynamic Tables        | 실시간 데이터 파이프라인           |
| **Security**         | Custom Auth, Session Management | 엔터프라이즈급 보안                |
| **DevOps**           | Docker, Blue-Green Deployment   | 무중단 배포 시스템                 |

---

## 📊 비즈니스 임팩트

### **데이터 민주화**

- 비개발자도 쉽게 사용할 수 있는 셀프서비스 분석 도구
- 데이터 분석 시간 90% 단축

### **실시간 의사결정**

- MAU, 매출, 고객 세그먼트 실시간 모니터링
- 마케팅 캠페인 효과 즉시 측정 가능

### **운영 효율성**

- 브랜드별 독립적 분석 환경
- 자동화된 보고서 생성

---

## 🔧 주요 구현 사항

### **1. 동적 스키마 관리**

```python
# 브랜드별 동적 스키마 매핑
BRAND_SCHEMA = {
    "BRAND_A": "ANALYSIS_BRAND_A",
    "BRAND_B": "ANALYSIS_BRAND_B",
}

def get_table_name(brand, table_type):
    return f"DT_{brand}_{table_type}"
```

### **2. 보안 세션 관리**

```python
# 역할 기반 접근 제어
def check_permission(user_role, required_role):
    permissions = {"user": 1, "admin": 2}
    return permissions.get(user_role, 0) >= permissions.get(required_role, 0)
```

### **3. 최적화된 쿼리**

```python
# Snowpark를 활용한 효율적 데이터 처리
@st.cache_data(ttl=300)
def get_mau_data(session, brand, schema):
    return session.table(f"{schema}.DT_{brand}_MAU_USERS").collect()
```

---

## 🚀 스케일링 고려사항

### **성능 최적화**

- Streamlit 캐싱으로 응답속도 개선
- Snowflake Dynamic Tables로 실시간 데이터 갱신
- 페이지별 독립적 로딩으로 UX 향상

### **확장성**

- 새로운 브랜드 추가 시 설정만으로 확장 가능
- 모듈형 구조로 새로운 분석 페이지 쉽게 추가
- Multi-tenant 아키텍처

### **모니터링**

- 사용자 행동 로깅
- 시스템 성능 모니터링
- 에러 추적 및 알림

---

## 💡 테슬라와의 연관성

### **데이터 중심 사고**

- 대용량 데이터에서 인사이트 도출
- 실시간 모니터링과 의사결정 자동화

### **사용자 경험 최적화**

- 직관적인 인터페이스 설계
- 빠른 응답속도와 안정성

### **확장 가능한 시스템 설계**

- 글로벌 멀티 브랜드 환경 경험
- 엔터프라이즈급 보안 고려

---

## 📁 프로젝트 구조

```
Multi-Brand-Analytics-Platform/
├── 📄 app.py                    # 메인 대시보드
├── 📄 brand_config.py           # 브랜드 설정 관리
├── 📄 snowflake_connection.py   # DB 연결 추상화
├── 📄 security_utils.py         # 보안 유틸리티
├── 📁 page_modules/             # 분석 모듈들
│   ├── user_segment_mau.py      # 사용자 분석
│   ├── sales_by_category.py     # 매출 분석
│   └── regional_analysis.py     # 지역별 분석
├── 📁 config/                   # 설정 파일들
├── 📁 docs/                     # 문서화
└── 📁 scripts/                  # 배포 스크립트
```

---

## 🎬 실행 방법

### **로컬 실행**

```bash
# 의존성 설치
pip install -r requirements.txt

# 설정 파일 준비 (예제 파일 참고)
cp config/config.toml.example config/config.toml

# 앱 실행
streamlit run app.py
```

### **Docker 실행**

```bash
docker-compose up -d
```

---

## 🎯 향후 개선 방향

1. **AI/ML 통합**: 고객 행동 예측 모델 추가
2. **실시간 알림**: 이상치 탐지 및 자동 알림
3. **모바일 최적화**: 반응형 디자인 개선
4. **API 개발**: 외부 시스템 연동을 위한 REST API

---

## 📞 연락처

- **Email**: [본인 이메일]
- **LinkedIn**: [본인 링크드인]
- **GitHub**: [본인 깃허브]

---

**감사합니다! 테슬라에서 함께 일할 수 있는 기회를 기대하고 있습니다.** 🚗⚡

---

_이 프로젝트는 실제 업무 경험을 바탕으로 포트폴리오용으로 재구성되었습니다._
