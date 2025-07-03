#!/bin/bash

# A/B 테스트 실행 스크립트
# A 버전: 8501 포트 (현재 버전)
# B 버전: 8502 포트 (새로운 기능 버전)

echo "🚀 A/B 테스트 환경 시작..."

# 포트 확인
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ 포트 $port가 이미 사용 중입니다."
        return 1
    else
        echo "✅ 포트 $port 사용 가능"
        return 0
    fi
}

# A 버전 시작 (8501)
start_version_a() {
    echo "📊 A 버전 시작 (포트 8501)..."
    if check_port 8501; then
        nohup streamlit run app.py --server.port 8501 --server.headless true > streamlit_a.log 2>&1 &
        echo $! > streamlit_a.pid
        echo "✅ A 버전이 포트 8501에서 시작되었습니다."
        echo "📝 로그: streamlit_a.log"
    else
        echo "❌ A 버전 시작 실패"
        return 1
    fi
}

# B 버전 시작 (8502)
start_version_b() {
    echo "🧪 B 버전 시작 (포트 8502)..."
    if check_port 8502; then
        nohup streamlit run app_b.py --server.port 8502 --server.headless true > streamlit_b.log 2>&1 &
        echo $! > streamlit_b.pid
        echo "✅ B 버전이 포트 8502에서 시작되었습니다."
        echo "📝 로그: streamlit_b.log"
    else
        echo "❌ B 버전 시작 실패"
        return 1
    fi
}

# 상태 확인
check_status() {
    echo ""
    echo "📈 A/B 테스트 상태:"
    echo "=================="
    
    if [ -f streamlit_a.pid ]; then
        PID_A=$(cat streamlit_a.pid)
        if ps -p $PID_A > /dev/null; then
            echo "✅ A 버전 (포트 8501): 실행 중 (PID: $PID_A)"
        else
            echo "❌ A 버전 (포트 8501): 중지됨"
        fi
    else
        echo "❌ A 버전 (포트 8501): 시작되지 않음"
    fi
    
    if [ -f streamlit_b.pid ]; then
        PID_B=$(cat streamlit_b.pid)
        if ps -p $PID_B > /dev/null; then
            echo "✅ B 버전 (포트 8502): 실행 중 (PID: $PID_B)"
        else
            echo "❌ B 버전 (포트 8502): 중지됨"
        fi
    else
        echo "❌ B 버전 (포트 8502): 시작되지 않음"
    fi
    
    echo ""
    echo "🌐 접속 URL:"
    echo "A 버전: http://localhost:8501"
    echo "B 버전: http://localhost:8502"
}

# 중지
stop_all() {
    echo "🛑 A/B 테스트 환경 중지..."
    
    if [ -f streamlit_a.pid ]; then
        PID_A=$(cat streamlit_a.pid)
        if ps -p $PID_A > /dev/null; then
            kill $PID_A
            echo "✅ A 버전 중지됨"
        fi
        rm -f streamlit_a.pid
    fi
    
    if [ -f streamlit_b.pid ]; then
        PID_B=$(cat streamlit_b.pid)
        if ps -p $PID_B > /dev/null; then
            kill $PID_B
            echo "✅ B 버전 중지됨"
        fi
        rm -f streamlit_b.pid
    fi
}

# 메인 로직
case "${1:-start}" in
    "start")
        start_version_a
        start_version_b
        check_status
        ;;
    "stop")
        stop_all
        ;;
    "status")
        check_status
        ;;
    "restart")
        stop_all
        sleep 2
        start_version_a
        start_version_b
        check_status
        ;;
    *)
        echo "사용법: $0 {start|stop|status|restart}"
        echo "  start   - A/B 테스트 환경 시작"
        echo "  stop    - A/B 테스트 환경 중지"
        echo "  status  - 현재 상태 확인"
        echo "  restart - A/B 테스트 환경 재시작"
        exit 1
        ;;
esac 