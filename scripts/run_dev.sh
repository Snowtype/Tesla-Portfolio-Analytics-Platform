#!/bin/bash

# 개발 환경 실행 스크립트 (파일 감시 활성화)
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true

echo "개발 환경으로 Streamlit 실행 중... (포트: 8501, 파일 감시 활성화)"
# 파일 감시를 활성화하여 개발 모드로 실행
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 