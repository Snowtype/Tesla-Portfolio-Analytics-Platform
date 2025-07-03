# Snowflake 연결 설정
# Streamlit secrets와 config.toml 파일에서 연결 정보를 읽어옵니다.

from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Session
import os
import toml
from pathlib import Path

def load_config():
    """
    설정을 로드합니다. 우선순위:
    1. Streamlit secrets (권장)
    2. config.toml 파일
    3. 환경 변수
    """
    
    # 1. Streamlit secrets 확인 (가장 권장)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and st.secrets:
            snowflake_config = st.secrets.get("snowflake", {})
            if snowflake_config:
                print("Streamlit secrets에서 설정을 로드했습니다.")
                return snowflake_config
    except:
        pass
    
    # 2. config.toml 파일 확인
    config_paths = [
        Path(".streamlit/config.toml"),
        Path("config.toml"),
        Path(".streamlit/secrets.toml")
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                config = toml.load(config_path)
                snowflake_config = config.get("snowflake", {})
                if snowflake_config:
                    print(f"{config_path}에서 설정을 로드했습니다.")
                    return snowflake_config
            except Exception as e:
                print(f"{config_path} 파일 읽기 실패: {e}")
    
    print("설정 파일을 찾을 수 없습니다.")
    return None

def create_snowflake_session():
    """
    Snowflake 세션을 생성하는 함수
    """
    
    # 설정 로드
    config = load_config()
    if not config:
        return None
    
    # 필수 연결 파라미터
    connection_parameters = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT") or config.get("account"),
        "user": os.getenv("SNOWFLAKE_USER") or config.get("user"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE") or config.get("warehouse"),
        "database": os.getenv("SNOWFLAKE_DATABASE") or config.get("database"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA") or config.get("schema")
    }
    
    # 선택적 role 설정 (필요한 경우에만)
    role = os.getenv("SNOWFLAKE_ROLE") or config.get("role")
    if role:
        connection_parameters["role"] = role
    
    # 인증 방식 결정 (password 또는 private_key)
    if os.getenv("SNOWFLAKE_PASSWORD"):
        # 환경 변수에서 password 사용
        connection_parameters["password"] = os.getenv("SNOWFLAKE_PASSWORD")
    elif config.get("password"):
        # 설정에서 password 사용
        connection_parameters["password"] = config.get("password")
    elif config.get("private_key_path"):
        # private key 파일 경로 사용
        private_key_path = config.get("private_key_path")
        if os.path.exists(private_key_path):
            with open(private_key_path, "r") as f:
                connection_parameters["private_key"] = f.read()
        else:
            print(f"Private key 파일을 찾을 수 없습니다: {private_key_path}")
            return None
    elif config.get("private_key"):
        # 설정에서 직접 private key 사용
        connection_parameters["private_key"] = config.get("private_key")
    else:
        print("인증 정보가 없습니다. password 또는 private_key를 설정해주세요.")
        return None
    
    # None 값 제거
    connection_parameters = {k: v for k, v in connection_parameters.items() if v is not None}
    
    try:
        session = Session.builder.configs(connection_parameters).create()
        print("Snowflake 연결 성공!")
        return session
    except Exception as e:
        print(f"Snowflake 연결 실패: {e}")
        return None

def get_active_session():
    """
    Streamlit에서 사용할 수 있는 활성 세션을 반환합니다.
    """
    return create_snowflake_session()

# 테스트용
if __name__ == "__main__":
    session = create_snowflake_session()
    if session:
        # 간단한 테스트 쿼리
        try:
            result = session.sql("SELECT CURRENT_VERSION()").collect()
            print(f"Snowflake 버전: {result[0][0]}")
        except Exception as e:
            print(f"테스트 쿼리 실패: {e}")
        finally:
            session.close()
    else:
        print("Snowflake 연결 실패!") 