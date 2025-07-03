#!/bin/bash

# 블루-그린 배포 관리 스크립트

echo "🔄 블루-그린 배포 관리"

# 현재 활성 버전 확인
check_current_version() {
    if [ -f /tmp/current_color.txt ]; then
        echo "🟢 현재 활성 버전: GREEN (포트 8504)"
        return 1
    else
        echo "🔵 현재 활성 버전: BLUE (포트 8503)"
        return 0
    fi
}

# 블루로 전환
switch_to_blue() {
    echo "🔵 BLUE 버전으로 전환 중..."
    sudo rm -f /tmp/current_color.txt
    echo "✅ BLUE 버전이 활성화되었습니다."
    echo "🌐 접속 URL: http://$(hostname -I | awk '{print $1}')/blue/"
}

# 그린으로 전환
switch_to_green() {
    echo "🟢 GREEN 버전으로 전환 중..."
    echo "green" | sudo tee /tmp/current_color.txt > /dev/null
    echo "✅ GREEN 버전이 활성화되었습니다."
    echo "🌐 접속 URL: http://$(hostname -I | awk '{print $1}')/green/"
}

# 상태 확인
check_status() {
    echo ""
    echo "📊 블루-그린 배포 상태:"
    echo "========================"
    
    # 서비스 상태 확인
    if sudo systemctl is-active --quiet streamlit-blue; then
        echo "✅ BLUE 서비스 (포트 8503): 실행 중"
    else
        echo "❌ BLUE 서비스 (포트 8503): 중지됨"
    fi
    
    if sudo systemctl is-active --quiet streamlit-green; then
        echo "✅ GREEN 서비스 (포트 8504): 실행 중"
    else
        echo "❌ GREEN 서비스 (포트 8504): 중지됨"
    fi
    
    # 현재 활성 버전 확인
    check_current_version
    
    echo ""
    echo "🌐 접속 URL:"
    echo "BLUE 버전: http://$(hostname -I | awk '{print $1}')/blue/"
    echo "GREEN 버전: http://$(hostname -I | awk '{print $1}')/green/"
    echo "메인 페이지: http://$(hostname -I | awk '{print $1}')/"
    echo "배포 관리: http://$(hostname -I | awk '{print $1}')/deploy/"
}

# 서비스 재시작
restart_services() {
    echo "🔄 서비스 재시작 중..."
    sudo systemctl restart streamlit-blue
    sudo systemctl restart streamlit-green
    echo "✅ 서비스 재시작 완료"
}

# 메인 로직
case "${1:-status}" in
    "blue")
        switch_to_blue
        ;;
    "green")
        switch_to_green
        ;;
    "status")
        check_status
        ;;
    "restart")
        restart_services
        ;;
    "switch")
        if check_current_version; then
            switch_to_green
        else
            switch_to_blue
        fi
        ;;
    *)
        echo "사용법: $0 {blue|green|status|restart|switch}"
        echo "  blue    - BLUE 버전으로 전환"
        echo "  green   - GREEN 버전으로 전환"
        echo "  status  - 현재 상태 확인"
        echo "  restart - 서비스 재시작"
        echo "  switch  - 현재 버전과 반대 버전으로 전환"
        exit 1
        ;;
esac 