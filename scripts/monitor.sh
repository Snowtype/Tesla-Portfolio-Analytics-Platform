#!/bin/bash

# Streamlit 앱 모니터링 스크립트

APP_URL="http://localhost:3001/_stcore/health"
LOG_FILE="/home/mask/TESLA_CRM/TESLA_TPC_STREAMLIT/monitor.log"

# 헬스체크 함수
check_health() {
    if curl -f -s $APP_URL > /dev/null; then
        echo "$(date): Streamlit 앱이 정상 실행 중입니다." >> $LOG_FILE
        return 0
    else
        echo "$(date): Streamlit 앱이 응답하지 않습니다. 재시작을 시도합니다." >> $LOG_FILE
        return 1
    fi
}

# 재시작 함수
restart_app() {
    echo "$(date): 앱 재시작 중..." >> $LOG_FILE
    
    # 현재 프로세스 종료
    pkill -f streamlit
    
    # 잠시 대기
    sleep 5
    
    # 앱 재시작
    cd /home/mask/TESLA_CRM/TESLA_TPC_STREAMLIT
    source venv/bin/activate
    nohup streamlit run app.py --server.port 3001 --server.address 0.0.0.0 > streamlit.log 2>&1 &
    
    echo "$(date): 앱 재시작 완료" >> $LOG_FILE
}

# 메인 로직
if ! check_health; then
    restart_app
fi 