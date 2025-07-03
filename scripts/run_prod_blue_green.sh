#!/bin/bash

# Blue-Green 배포 스크립트

BLUE_PORT=8503
GREEN_PORT=8504
CURRENT_COLOR_FILE="current_color.txt"

# 현재 실행 중인 색상 확인
if [ -f "$CURRENT_COLOR_FILE" ]; then
    CURRENT_COLOR=$(cat $CURRENT_COLOR_FILE)
else
    CURRENT_COLOR="blue"
fi

# 새 색상 결정
if [ "$CURRENT_COLOR" = "blue" ]; then
    NEW_COLOR="green"
    NEW_PORT=$GREEN_PORT
    OLD_PORT=$BLUE_PORT
else
    NEW_COLOR="blue"
    NEW_PORT=$BLUE_PORT
    OLD_PORT=$GREEN_PORT
fi

echo "현재 실행 중: $CURRENT_COLOR (포트: $OLD_PORT)"
echo "새로 배포할 색상: $NEW_COLOR (포트: $NEW_PORT)"

# 1. 새 버전 시작
echo "새 버전($NEW_COLOR) 시작 중..."
nohup streamlit run app.py --server.port $NEW_PORT --server.address 0.0.0.0 --server.fileWatcherType none > streamlit_${NEW_COLOR}.log 2>&1 &

# 2. 새 버전 준비 대기
echo "새 버전 준비 대기 중..."
sleep 15

# 3. 새 버전 헬스체크
if curl -f -s http://localhost:$NEW_PORT/_stcore/health > /dev/null; then
    echo "새 버전 정상 작동 확인"
    
    # 4. 색상 전환 (현재 색상 업데이트)
    echo $NEW_COLOR > $CURRENT_COLOR_FILE
    
    # 5. 기존 버전 종료
    echo "기존 버전($CURRENT_COLOR) 종료 중..."
    pkill -f "streamlit.*$OLD_PORT"
    
    echo "Blue-Green 배포 완료!"
    echo "현재 활성: $NEW_COLOR (포트: $NEW_PORT)"
    echo "접속 URL: http://localhost:$NEW_PORT"
else
    echo "새 버전 시작 실패. 기존 버전 유지"
    pkill -f "streamlit.*$NEW_PORT"
fi 