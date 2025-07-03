#!/bin/bash

# 프로덕션 환경 백그라운드 실행 스크립트 (파일 감시 비활성화)
export STREAMLIT_SERVER_PORT=8503
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true

echo "프로덕션 환경으로 Streamlit 백그라운드 실행 중... (포트: 8503, 파일 감시 비활성화)"
# 파일 감시를 비활성화하여 진짜 프로덕션 모드로 실행
nohup streamlit run app.py --server.port 8503 --server.address 0.0.0.0 --server.fileWatcherType none > streamlit.log 2>&1 &
echo "백그라운드에서 실행 중... PID: $!"
echo "로그 확인: tail -f streamlit.log" 