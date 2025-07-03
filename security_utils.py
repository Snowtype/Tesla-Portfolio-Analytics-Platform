"""
Security utilities for Tesla Portfolio Analytics Platform
Enterprise-grade security logging and audit trail functionality
"""

import re
import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# 포트별 로그 파일 경로 설정
def get_log_file_path():
    """포트별 로그 파일 경로 반환"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)  # 로그 디렉토리 생성
    
    try:
        import streamlit as st
        # Streamlit 서버 포트 확인
        port = st.get_option('server.port')
        if port:
            return os.path.join(log_dir, f"security_events_port_{port}.log")
    except Exception:
        pass
    
    # 기본값
    return "security_events.log"

# 로깅 설정
def setup_logging():
    """컨테이너 환경에 맞는 표준 출력 로깅 설정"""
    # 파일 핸들러를 제거하고 스트림 핸들러만 사용합니다.
    # 이렇게 하면 모든 로그가 컨테이너의 stdout으로 출력되어
    # 'docker-compose logs'로 중앙에서 관리할 수 있습니다.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class SecurityUtils:
    """Enterprise security utilities for audit logging and access control"""
    
    @staticmethod
    def get_log_filename():
        """
        Get appropriate log filename based on current environment
        For portfolio demonstration, uses simple file logging
        """
        # Try to detect if running on specific port for multi-instance deployment
        try:
            port = os.environ.get('STREAMLIT_SERVER_PORT', 'default')
            return f"security_events_port_{port}.log"
        except:
            return "security_events.log"
    
    @staticmethod
    def log_security_event(event_type, user, details, ip_address=None):
        """
        Log security events for audit trail
        
        Args:
            event_type (str): Type of security event
            user (str): Username associated with event
            details (dict): Additional event details
            ip_address (str): Client IP address
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user": user,
            "ip_address": ip_address or "unknown",
            "details": details,
            "session_id": SecurityUtils._get_session_id(user, ip_address)
        }
        
        try:
            log_file = SecurityUtils.get_log_filename()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            # In production, this would use proper error handling
            print(f"Security logging error: {e}")
    
    @staticmethod
    def log_login_attempt(username, success, ip_address=None, additional_info=None):
        """
        Log user login attempts for security monitoring
        
        Args:
            username (str): Username attempting login
            success (bool): Whether login was successful
            ip_address (str): Client IP address
            additional_info (dict): Additional login context
        """
        event_type = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
        details = {
            "username": username,
            "success": success,
            "login_method": "streamlit_form",
            "additional_info": additional_info or {}
        }
        
        SecurityUtils.log_security_event(
            event_type=event_type,
            user=username,
            details=details,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_data_access(user, data_type, record_count, ip_address=None, query_info=None):
        """
        Log data access events for compliance and audit
        
        Args:
            user (str): Username accessing data
            data_type (str): Type of data being accessed
            record_count (int): Number of records accessed
            ip_address (str): Client IP address
            query_info (dict): Query execution details
        """
        details = {
            "data_type": data_type,
            "record_count": record_count,
            "access_time": datetime.now().isoformat(),
            "query_info": query_info or {},
            "portfolio_mode": True  # Flag for portfolio demonstration
        }
        
        SecurityUtils.log_security_event(
            event_type="DATA_ACCESS",
            user=user,
            details=details,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_permission_change(admin_user, target_user, old_role, new_role, ip_address=None):
        """
        Log permission and role changes for security audit
        
        Args:
            admin_user (str): Administrator making the change
            target_user (str): User whose permissions are being changed
            old_role (str): Previous role
            new_role (str): New role assigned
            ip_address (str): Client IP address
        """
        details = {
            "target_user": target_user,
            "old_role": old_role,
            "new_role": new_role,
            "changed_by": admin_user,
            "change_reason": "admin_action"
        }
        
        SecurityUtils.log_security_event(
            event_type="PERMISSION_CHANGE",
            user=admin_user,
            details=details,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_system_event(event_type, details, user="system"):
        """
        Log system-level events for operational monitoring
        
        Args:
            event_type (str): Type of system event
            details (dict): Event details
            user (str): User context (defaults to system)
        """
        SecurityUtils.log_security_event(
            event_type=event_type,
            user=user,
            details=details,
            ip_address="localhost"
        )
    
    @staticmethod
    def _get_session_id(user, ip_address):
        """
        Generate session identifier for tracking
        
        Args:
            user (str): Username
            ip_address (str): Client IP
            
        Returns:
            str: Session identifier hash
        """
        try:
            session_data = f"{user}_{ip_address}_{datetime.now().strftime('%Y%m%d')}"
            return hashlib.md5(session_data.encode()).hexdigest()[:8]
        except:
            return "unknown"
    
    @staticmethod
    def get_security_summary():
        """
        Get summary of recent security events for monitoring dashboard
        
        Returns:
            dict: Security event summary
        """
        try:
            log_file = SecurityUtils.get_log_filename()
            if not Path(log_file).exists():
                return {"total_events": 0, "recent_logins": 0, "data_accesses": 0}
            
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            recent_events = []
            for line in lines[-100:]:  # Last 100 events
                try:
                    event = json.loads(line.strip())
                    recent_events.append(event)
                except:
                    continue
            
            summary = {
                "total_events": len(recent_events),
                "recent_logins": len([e for e in recent_events if e.get("event_type", "").startswith("LOGIN")]),
                "data_accesses": len([e for e in recent_events if e.get("event_type") == "DATA_ACCESS"]),
                "failed_logins": len([e for e in recent_events if e.get("event_type") == "LOGIN_FAILED"]),
                "unique_users": len(set([e.get("user") for e in recent_events if e.get("user")]))
            }
            
            return summary
            
        except Exception as e:
            return {"error": f"Unable to generate security summary: {e}"}

# Convenience function for backward compatibility
def log_security_event(event_type, user, details, ip_address=None):
    """Convenience wrapper for SecurityUtils.log_security_event"""
    SecurityUtils.log_security_event(event_type, user, details, ip_address)

logger.info("Security utilities initialized") 