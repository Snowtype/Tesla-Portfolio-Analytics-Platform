# 간단한 Snowflake 연결 방식 (snowflake-connector 사용)
import streamlit as st
import snowflake.connector
import pandas as pd

@st.cache_resource
def get_snowflake_connection():
    """
    간단한 Snowflake 연결 (snowflake-connector 사용)
    """
    try:
        # Streamlit secrets에서 설정 읽기
        conn = snowflake.connector.connect(
            account=st.secrets["snowflake"]["account"],
            user=st.secrets["snowflake"]["user"],
            private_key=st.secrets["snowflake"]["private_key"],
            warehouse=st.secrets["snowflake"]["warehouse"],
            database=st.secrets["snowflake"]["database"],
            schema=st.secrets["snowflake"]["schema"]
        )
        print("Snowflake 연결 성공! (connector 방식)")
        return conn
    except Exception as e:
        print(f"Snowflake 연결 실패: {e}")
        return None

def execute_query(query):
    """
    SQL 쿼리 실행하여 DataFrame 반환
    """
    conn = get_snowflake_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            print(f"쿼리 실행 실패: {e}")
            return None
        finally:
            conn.close()
    return None

# 사용 예시:
# df = execute_query("SELECT * FROM COMPANY_DW.ANALYSIS_BRAND_A.DT_BRAND_A_USER_COUNTS")
# st.dataframe(df) 