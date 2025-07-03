#!/bin/bash

# 배포용 앱 업데이트 스크립트 (끊김 없는 재시작)

echo "배포용 앱 업데이트 시작..."

# 1. 새 버전을 다른 포트에서 먼저 실행
echo "새 버전을 8504 포트에서 시작..."
nohup streamlit run app.py --server.port 8504 --server.address 0.0.0.0 --server.fileWatcherType none > streamlit_new.log 2>&1 &

# 2. 새 버전이 완전히 시작될 때까지 대기
echo "새 버전 시작 대기 중..."
sleep 10

# 3. 새 버전이 정상 작동하는지 확인
if curl -f -s http://localhost:8504/_stcore/health > /dev/null; then
    echo "새 버전 정상 작동 확인"
    
    # 4. 기존 버전 종료
    echo "기존 버전(8503) 종료 중..."
    pkill -f "streamlit.*8503"
    
    # 5. 잠시 대기
    sleep 5
    
    # 6. 새 버전을 8503 포트로 이동
    echo "새 버전을 8503 포트로 이동..."
    pkill -f "streamlit.*8504"
    nohup streamlit run app.py --server.port 8503 --server.address 0.0.0.0 --server.fileWatcherType none > streamlit.log 2>&1 &
    
    echo "업데이트 완료! 새 버전이 8503 포트에서 실행 중입니다."
else
    echo "새 버전 시작 실패. 기존 버전 유지"
    pkill -f "streamlit.*8504"
fi 