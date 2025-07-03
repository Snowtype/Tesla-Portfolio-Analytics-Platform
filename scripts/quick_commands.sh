#!/bin/bash

# ==============================================
# TESLA TPC Streamlit 빠른 명령어 모음
# ==============================================

# 개발 서버 실행
dev() {
    echo "🔧 개발 서버 실행 (포트 8501)"
    lsof -ti:8501 | xargs kill -9 2>/dev/null || true
    streamlit run app.py --server.port 8501
}

# 테스트 서버 실행 (백그라운드)
test() {
    echo "🧪 테스트 서버 실행 (포트 8502, 백그라운드)"
    lsof -ti:8502 | xargs kill -9 2>/dev/null || true
    nohup streamlit run app.py --server.port 8502 > logs/streamlit_8502.log 2>&1 &
    sleep 3
    echo "✅ 테스트 서버 실행 완료: http://localhost:8502"
}

# Blue 서버 실행 (백그라운드)
blue() {
    echo "🔵 Blue 운영 서버 실행 (포트 8503, 백그라운드)"
    lsof -ti:8503 | xargs kill -9 2>/dev/null || true
    nohup streamlit run app.py --server.port 8503 > logs/streamlit_8503.log 2>&1 &
    sleep 3
    echo "✅ Blue 서버 실행 완료: http://localhost:8503"
}

# Green 서버 실행 (백그라운드)
green() {
    echo "🟢 Green 운영 서버 실행 (포트 8504, 백그라운드)"
    lsof -ti:8504 | xargs kill -9 2>/dev/null || true
    nohup streamlit run app.py --server.port 8504 > logs/streamlit_8504.log 2>&1 &
    sleep 3
    echo "✅ Green 서버 실행 완료: http://localhost:8504"
}

# 포트 상태 확인
status() {
    echo "📊 포트 상태 확인"
    echo ""
    echo "포트 | 상태    | 역할"
    echo "-----|---------|-------------"
    
    for port in 8501 8502 8503 8504; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            status="🟢 실행중"
        else
            status="🔴 중지"
        fi
        
        case $port in
            8501) role="🔧 개발" ;;
            8502) role="🧪 테스트" ;;
            8503) role="🔵 Blue 운영" ;;
            8504) role="🟢 Green 운영" ;;
        esac
        
        printf "%-4s | %-7s | %s\n" "$port" "$status" "$role"
    done
    echo ""
}

# 모든 서버 종료
stop() {
    echo "🛑 모든 서버 종료"
    for port in 8501 8502 8503 8504; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "  포트 $port 종료 중..."
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done
    echo "✅ 모든 서버 종료 완료"
}

# 특정 포트 종료
kill_port() {
    local port=$1
    if [ -z "$port" ]; then
        echo "사용법: kill_port <포트번호>"
        echo "예시: kill_port 8501"
        return 1
    fi
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "🛑 포트 $port 종료 중..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        echo "✅ 포트 $port 종료 완료"
    else
        echo "ℹ️ 포트 $port는 이미 종료되어 있습니다"
    fi
}

# 로그 확인
logs() {
    local port=$1
    if [ -z "$port" ]; then
        echo "📋 사용 가능한 로그 파일:"
        ls -la logs/streamlit_*.log 2>/dev/null || echo "로그 파일이 없습니다"
        echo ""
        echo "사용법: logs <포트번호>"
        echo "예시: logs 8501"
        return 1
    fi
    
    local log_file="logs/streamlit_$port.log"
    if [ -f "$log_file" ]; then
        echo "📋 포트 $port 로그 확인 (Ctrl+C로 종료)"
        tail -f "$log_file"
    else
        echo "❌ 로그 파일이 없습니다: $log_file"
    fi
}

# 도움말
help() {
    echo ""
    echo "=================================="
    echo "  TESLA TPC Streamlit 빠른 명령어"
    echo "=================================="
    echo ""
    echo "🚀 서버 실행:"
    echo "  dev          - 개발 서버 실행 (8501, 포그라운드)"
    echo "  test         - 테스트 서버 실행 (8502, 백그라운드)"
    echo "  blue         - Blue 운영 서버 실행 (8503, 백그라운드)"
    echo "  green        - Green 운영 서버 실행 (8504, 백그라운드)"
    echo ""
    echo "📊 모니터링:"
    echo "  status       - 포트 상태 확인"
    echo "  logs <포트>  - 로그 확인 (예: logs 8501)"
    echo ""
    echo "🛑 서버 제어:"
    echo "  stop         - 모든 서버 종료"
    echo "  kill_port <포트> - 특정 포트 종료 (예: kill_port 8501)"
    echo ""
    echo "🔧 기타:"
    echo "  help         - 이 도움말 표시"
    echo ""
    echo "=================================="
    echo ""
}

# 명령어 실행
case "$1" in
    "dev")
        dev
        ;;
    "test")
        test
        ;;
    "blue")
        blue
        ;;
    "green")
        green
        ;;
    "status")
        status
        ;;
    "stop")
        stop
        ;;
    "kill_port")
        kill_port "$2"
        ;;
    "logs")
        logs "$2"
        ;;
    "help"|"")
        help
        ;;
    *)
        echo "❌ 알 수 없는 명령어: $1"
        help
        ;;
esac 