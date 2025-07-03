import streamlit as st
# 페이지 너비, 네비게이션 바 확장여부 수정
# [중요] set_page_config는 반드시 첫 Streamlit 명령어여야 하므로 최상단에 위치시킴
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

import pandas as pd
import calendar
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import json
import os
from pathlib import Path
import time

from page_modules import user_segment_mau, new_subscribers, region_age_data, repurchase_rate, heavy_users_by_menu, heavy_users_simple, sales_by_category, heavy_users_simple

# ------------------------
# [보안 유틸리티 import]
# ------------------------
try:
    from security_utils import SecurityUtils, log_security_event
except ImportError:
    # security_utils가 없으면 기본 함수들 정의
    class SecurityUtils:
        @staticmethod
        def log_login_attempt(username, success, ip_address=None):
            pass
    
    def log_security_event(event_type, user, details, ip_address=None):
        pass

# ------------------------
# [IP 주소 추적 함수]
# ------------------------
def get_client_ip():
    """클라이언트 IP 주소 추적"""
    try:
        # Streamlit의 내장 기능으로 IP 추적
        if hasattr(st, 'get_option') and st.get_option('server.address') != 'localhost':
            # 실제 서버 환경에서는 클라이언트 IP를 추적할 수 있음
            return "unknown"  # 실제 구현에서는 프록시 헤더에서 IP 추출
        else:
            # 로컬 개발 환경에서는 더 구체적인 정보 제공
            import socket
            try:
                # 로컬 IP 주소 가져오기
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                return f"local-{local_ip}"
            except:
                # 실패시 호스트명 사용
                try:
                    hostname = socket.gethostname()
                    return f"local-{hostname}"
                except:
                    return "localhost-dev"
    except:
        return "localhost-dev"

# ------------------------
# [A/B 테스트 B 버전 - 새로운 기능들]
# ------------------------

# 실시간 알림 기능
def show_realtime_notifications():
    """실시간 알림 표시 (B 버전 전용 기능)"""
    with st.sidebar:
        st.markdown("### 🔔 실시간 알림")
        if st.button("새로운 알림 확인"):
            st.success("새로운 데이터가 업데이트되었습니다!")
            st.info("매출 데이터가 5% 증가했습니다.")
            st.warning("일부 지역에서 재고 부족이 발생했습니다.")

# 다크모드 토글 (B 버전 전용)
def dark_mode_toggle():
    """다크모드 토글 기능 (B 버전 전용)"""
    with st.sidebar:
        st.markdown("### 🌙 테마 설정")
        dark_mode = st.toggle("다크모드", key="dark_mode_b")
        if dark_mode:
            st.markdown("""
            <style>
            .stApp {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            </style>
            """, unsafe_allow_html=True)
            st.info("다크모드가 활성화되었습니다.")
        else:
            st.info("라이트모드가 활성화되었습니다.")

# 성능 개선된 데이터 로딩 (B 버전 전용)
def enhanced_data_loading():
    """성능 개선된 데이터 로딩 (B 버전 전용)"""
    with st.sidebar:
        st.markdown("### ⚡ 성능 설정")
        cache_enabled = st.checkbox("데이터 캐싱 활성화", value=True, key="cache_b")
        if cache_enabled:
            st.success("데이터 캐싱이 활성화되어 로딩 속도가 향상됩니다.")
        else:
            st.warning("실시간 데이터를 사용합니다. 로딩 시간이 길어질 수 있습니다.")

# ------------------------
# [브랜드별 스키마명 관리] - 브랜드별로 스키마만 다르고 DB/테이블 구조는 동일
# ------------------------
BRAND_SCHEMA = {
    "BRAND_A": "ANALYSIS_BRAND_A",  # Coffee Brand A
    "BRAND_B": "ANALYSIS_BRAND_B",  # Coffee Brand B
}

# ------------------------
# [계정/브랜드/권한 정보 관리] - 계정별로 브랜드, 권한(role) 정보 포함
# ------------------------
USER_CREDENTIALS = {
    "brand_a_user": {"password": "[MASKED]", "brand": "BRAND_A", "role": "user"},
    "brand_b_user": {"password": "[MASKED]", "brand": "BRAND_B", "role": "user"},
    "admin": {"password": "[MASKED]", "brand": "BRAND_A", "role": "admin"},
}

# ------------------------
# [세션 저장/복원 기능] - 파일 기반 세션 관리
# ------------------------
def save_session_to_file(session_data):
    """세션 데이터를 파일에 저장"""
    session_file = Path(".streamlit/session.json")
    session_file.parent.mkdir(exist_ok=True)
    
    try:
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"세션 저장 실패: {e}")
        return False

def load_session_from_file():
    """파일에서 세션 데이터 로드"""
    session_file = Path(".streamlit/session.json")
    
    if not session_file.exists():
        return None
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # 세션 데이터 유효성 검사 (24시간 이내인지)
        if "login_timestamp" in session_data:
            login_time = pd.Timestamp(session_data["login_timestamp"])
            current_time = pd.Timestamp.now()
            if (current_time - login_time).total_seconds() > 24 * 3600:
                # 24시간 초과시 세션 파일 삭제
                session_file.unlink()
                return None
        
        return session_data
    except Exception as e:
        st.error(f"세션 로드 실패: {e}")
        return None

def clear_session_file():
    """세션 파일 삭제"""
    session_file = Path(".streamlit/session.json")
    if session_file.exists():
        try:
            session_file.unlink()
        except Exception as e:
            st.error(f"세션 파일 삭제 실패: {e}")

# ------------------------
# [로그인 기능] - 로그인 성공 시 세션에 브랜드/권한 정보 저장
# ------------------------
def login():
    st.title("로그인")
    
    # B 버전 전용 로그인 페이지 개선
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🚀 B 버전 - 개선된 로그인")
        st.info("새로운 기능이 포함된 B 버전입니다!")
        
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        login_btn = st.button("로그인", type="primary")
        
        if login_btn:
            # IP 주소 추적
            client_ip = get_client_ip()
            
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
                # 로그인 성공 로그
                SecurityUtils.log_login_attempt(username, True, client_ip)
                
                # 세션 상태 설정
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["brand"] = USER_CREDENTIALS[username]["brand"]
                st.session_state["role"] = USER_CREDENTIALS[username]["role"]
                st.session_state["login_timestamp"] = pd.Timestamp.now().isoformat()
                st.session_state["client_ip"] = client_ip
                
                # 파일에 세션 데이터 저장
                session_data = {
                    "logged_in": True,
                    "username": username,
                    "brand": USER_CREDENTIALS[username]["brand"],
                    "role": USER_CREDENTIALS[username]["role"],
                    "login_timestamp": st.session_state["login_timestamp"],
                    "client_ip": client_ip
                }
                save_session_to_file(session_data)
                
                st.success(f"{username}님, B 버전에 오신 것을 환영합니다! 🎉")
                time.sleep(1)
                st.rerun()
            else:
                # 로그인 실패 로그
                SecurityUtils.log_login_attempt(username, False, client_ip)
                st.error("아이디 또는 비밀번호가 틀렸습니다.")

# 로그인 상태 확인 및 복원
def check_login_status():
    # 먼저 세션 상태에서 로그인 정보 확인
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        # 로그인 시간 확인 (24시간 이내인지 체크)
        if "login_timestamp" in st.session_state:
            login_time = pd.Timestamp(st.session_state["login_timestamp"])
            current_time = pd.Timestamp.now()
            # 24시간 이내면 로그인 유지
            if (current_time - login_time).total_seconds() < 24 * 3600:
                return True
            else:
                # 24시간 초과시 로그아웃
                st.session_state["logged_in"] = False
                st.session_state["username"] = ""
                st.session_state["brand"] = ""
                st.session_state["role"] = ""
                if "login_timestamp" in st.session_state:
                    del st.session_state["login_timestamp"]
                clear_session_file()
                return False
        return True
    
    # 세션 상태에 없으면 파일에서 복원 시도
    session_data = load_session_from_file()
    if session_data and session_data.get("logged_in"):
        # 파일에서 세션 데이터를 세션 상태로 복원
        st.session_state["logged_in"] = True
        st.session_state["username"] = session_data["username"]
        st.session_state["brand"] = session_data["brand"]
        st.session_state["role"] = session_data["role"]
        st.session_state["login_timestamp"] = session_data["login_timestamp"]
        return True
    
    return False

# 로그인 상태가 없으면 로그인 페이지 표시
if not check_login_status():
    login()
    st.stop()
    
# 로그아웃 버튼
with st.sidebar:
    st.markdown(f"**로그인 계정:** {st.session_state['username']} (브랜드: {st.session_state['brand']}, 권한: {st.session_state['role']})")
    st.markdown("**🔬 A/B 테스트 B 버전**")
    
    if st.button("로그아웃"):
        # 로그아웃 로그 기록
        SecurityUtils.log_security_event(
            "LOGOUT",
            st.session_state.get("username", "unknown"),
            {"action": "사용자 로그아웃", "version": "B"},
            st.session_state.get("client_ip", "unknown")
        )
        
        # 세션 상태 초기화
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["brand"] = ""
        st.session_state["role"] = ""
        if "login_timestamp" in st.session_state:
            del st.session_state["login_timestamp"]
        
        # 세션 파일도 삭제
        clear_session_file()
        
        st.rerun()

# B 버전 전용 기능들 표시
show_realtime_notifications()
dark_mode_toggle()
enhanced_data_loading()

# ------------------------
# [관리자 페이지 분기] - admin 계정만 접근 가능
# ------------------------
def admin_page():
    st.title("관리자 페이지")
    st.write("여기서 계정 관리, 브랜드 관리, 로그 확인 등 가능")
    st.write("계정 목록:")
    for user, info in USER_CREDENTIALS.items():
        st.write(f"- {user} (브랜드: {info['brand']}, 권한: {info['role']})")
    st.info("실제 서비스라면 DB/파일로 계정 관리, 추가/삭제/수정 폼 구현 가능")
    
    # B 버전 전용 관리자 기능
    st.markdown("### 🧪 A/B 테스트 관리")
    st.info("B 버전에서만 사용 가능한 새로운 관리 기능들")
    if st.button("A/B 테스트 결과 확인"):
        st.success("A/B 테스트 결과를 확인합니다...")

# ------------------------
# [Snowflake 연결] - 로그인 성공 후에만 연결 시도 (session 미정의 에러 방지)
# ------------------------
try:
    from snowflake_connection import get_active_session
    session = get_active_session()
    if session is None:
        st.error("Snowflake 연결에 실패했습니다. config.toml 파일을 확인해주세요.")
        st.stop()
except Exception as e:
    st.error(f"Snowflake 연결 오류: {e}")
    st.stop()

# 헤더 이미지 (포트폴리오용 플레이스홀더)
def display_header_image(brand=None):
    header_images = {
        "BRAND_A": "https://via.placeholder.com/1200x200/FF6B6B/FFFFFF?text=Coffee+Brand+A+Analytics+B+Version",
        "BRAND_B": "https://via.placeholder.com/1200x200/4ECDC4/FFFFFF?text=Coffee+Brand+B+Analytics+B+Version",
    }
    
    if brand == "ALL" or not brand:
        st.image(header_images["BRAND_A"], use_column_width=True)
    else:
        brand_image = header_images.get(brand, header_images["BRAND_A"])
        try:
            st.image(brand_image, use_column_width=True)
        except:
            st.info(f"📊 Coffee {brand} Analytics Dashboard (B Version)")

# 푸터 이미지
def display_footer_image():
    st.markdown("---")
    st.markdown("### 🧪 A/B 테스트 B 버전 - 새로운 기능들")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔔 실시간 알림**")
        st.info("새로운 데이터 업데이트 알림")
    
    with col2:
        st.markdown("**🌙 다크모드**")
        st.info("사용자 선호 테마 설정")
    
    with col3:
        st.markdown("**⚡ 성능 개선**")
        st.info("캐싱을 통한 빠른 로딩")

# 페이지 설정 함수
def set_page(page):
    st.session_state["current_page"] = page

# 메인 앱 로직 (기존 app.py와 동일하지만 B 버전 표시)
if __name__ == "__main__":
    # B 버전 헤더 표시
    st.markdown("## 🧪 A/B 테스트 B 버전")
    st.info("이것은 새로운 기능이 포함된 B 버전입니다!")
    
    # 브랜드별 헤더 이미지 표시
    display_header_image(st.session_state.get("brand"))
    
    # 페이지 네비게이션
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "대시보드"
    
    # 사이드바에 페이지 선택 메뉴
    with st.sidebar:
        st.markdown("### 📊 페이지 선택")
        page = st.selectbox(
            "페이지를 선택하세요",
            ["대시보드", "사용자 세그먼트", "신규 가입자", "지역별 연령대", "재구매율", "헤비유저", "카테고리별 매출"],
            index=0 if st.session_state["current_page"] == "대시보드" else 1
        )
        
        if page != st.session_state["current_page"]:
            set_page(page)
    
    # 페이지별 내용 표시
    if st.session_state["current_page"] == "대시보드":
        st.title("📊 대시보드 (B 버전)")
        st.info("B 버전에서는 더 나은 성능과 새로운 기능을 제공합니다!")
        
        # 대시보드 내용 (기존과 동일)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 매출", "₩1,234,567,890", "12%")
        with col2:
            st.metric("신규 고객", "1,234", "8%")
    
    elif st.session_state["current_page"] == "사용자 세그먼트":
        user_segment_mau.show_page()
    
    elif st.session_state["current_page"] == "신규 가입자":
        new_subscribers.show_page()
    
    elif st.session_state["current_page"] == "지역별 연령대":
        region_age_data.show_page()
    
    elif st.session_state["current_page"] == "재구매율":
        repurchase_rate.show_page()
    
    elif st.session_state["current_page"] == "헤비유저":
        heavy_users_simple.show_page()
    
    elif st.session_state["current_page"] == "카테고리별 매출":
        sales_by_category.show_page()
    
    # B 버전 전용 푸터
    display_footer_image() 