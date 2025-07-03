"""
보안 설정 관리
- IP 화이트리스트
- 세션 타임아웃
- 비밀번호 정책
- 접근 제어
"""

import os
from typing import List, Dict, Any

class SecurityConfig:
    """보안 설정 클래스"""
    
    # 기본 설정값
    DEFAULT_CONFIG = {
        # 세션 관리
        "session_timeout": 86400,  # 24시간 (초)
        "max_login_attempts": 5,
        "lockout_duration": 1800,  # 30분 (초)
        
        # 비밀번호 정책
        "password_min_length": 8,
        "password_require_uppercase": True,
        "password_require_lowercase": True,
        "password_require_numbers": True,
        "password_require_special": True,
        
        # IP 제한
        "enable_ip_whitelist": False,
        "allowed_ips": [],
        
        # 로깅
        "log_level": "INFO",
        "log_retention_days": 30,
        
        # 데이터 보안
        "enable_data_masking": True,
        "mask_sensitive_fields": ["email", "phone", "name", "ssn"],
        
        # 접근 제어
        "require_https": True,
        "enable_cors": False,
        "enable_xsrf_protection": True
    }
    
    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_from_env()
    
    def load_from_env(self):
        """환경변수에서 설정 로드"""
        # 세션 관리
        if os.getenv("SESSION_TIMEOUT"):
            self.config["session_timeout"] = int(os.getenv("SESSION_TIMEOUT"))
        
        if os.getenv("MAX_LOGIN_ATTEMPTS"):
            self.config["max_login_attempts"] = int(os.getenv("MAX_LOGIN_ATTEMPTS"))
        
        # 비밀번호 정책
        if os.getenv("PASSWORD_MIN_LENGTH"):
            self.config["password_min_length"] = int(os.getenv("PASSWORD_MIN_LENGTH"))
        
        # IP 화이트리스트
        if os.getenv("ALLOWED_IPS"):
            self.config["allowed_ips"] = os.getenv("ALLOWED_IPS").split(",")
            self.config["enable_ip_whitelist"] = True
        
        # 로깅
        if os.getenv("LOG_LEVEL"):
            self.config["log_level"] = os.getenv("LOG_LEVEL")
    
    def get(self, key: str, default=None):
        """설정값 조회"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """설정값 변경"""
        self.config[key] = value
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """IP 주소 허용 여부 확인"""
        if not self.config["enable_ip_whitelist"]:
            return True
        
        return ip_address in self.config["allowed_ips"]
    
    def get_session_timeout(self) -> int:
        """세션 타임아웃 반환 (초)"""
        return self.config["session_timeout"]
    
    def get_password_policy(self) -> Dict[str, Any]:
        """비밀번호 정책 반환"""
        return {
            "min_length": self.config["password_min_length"],
            "require_uppercase": self.config["password_require_uppercase"],
            "require_lowercase": self.config["password_require_lowercase"],
            "require_numbers": self.config["password_require_numbers"],
            "require_special": self.config["password_require_special"]
        }
    
    def should_mask_field(self, field_name: str) -> bool:
        """필드 마스킹 여부 확인"""
        return field_name in self.config["mask_sensitive_fields"]

# 전역 설정 인스턴스
security_config = SecurityConfig()

# 편의 함수들
def get_security_config() -> SecurityConfig:
    """보안 설정 인스턴스 반환"""
    return security_config

def is_ip_allowed(ip_address: str) -> bool:
    """IP 주소 허용 여부 확인"""
    return security_config.is_ip_allowed(ip_address)

def get_session_timeout() -> int:
    """세션 타임아웃 반환"""
    return security_config.get_session_timeout()

def should_mask_field(field_name: str) -> bool:
    """필드 마스킹 여부 확인"""
    return security_config.should_mask_field(field_name) 