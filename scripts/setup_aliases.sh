#!/bin/bash

# ==============================================
# TESLA TPC Streamlit Alias 설정 스크립트
# ==============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔧 TESLA TPC Streamlit Alias 설정"
echo "프로젝트 경로: $PROJECT_DIR"

# alias 내용 생성
ALIAS_CONTENT="
# ================================
# TESLA TPC Streamlit Aliases
# ================================
alias tpc-deploy='$PROJECT_DIR/scripts/deploy.sh'
alias tpc-dev='cd $PROJECT_DIR && ./scripts/quick_commands.sh dev'
alias tpc-test='cd $PROJECT_DIR && ./scripts/quick_commands.sh test'
alias tpc-blue='cd $PROJECT_DIR && ./scripts/quick_commands.sh blue'
alias tpc-green='cd $PROJECT_DIR && ./scripts/quick_commands.sh green'
alias tpc-status='cd $PROJECT_DIR && ./scripts/quick_commands.sh status'
alias tpc-stop='cd $PROJECT_DIR && ./scripts/quick_commands.sh stop'
alias tpc-logs='cd $PROJECT_DIR && ./scripts/quick_commands.sh logs'
alias tpc-kill='cd $PROJECT_DIR && ./scripts/quick_commands.sh kill_port'
alias tpc-help='cd $PROJECT_DIR && ./scripts/quick_commands.sh help'
alias tpc-cd='cd $PROJECT_DIR'
"

# 쉘 타입 확인
if [[ "$SHELL" == *"zsh"* ]]; then
    RC_FILE="$HOME/.zshrc"
    echo "🐚 Zsh 쉘 감지됨"
elif [[ "$SHELL" == *"bash"* ]]; then
    RC_FILE="$HOME/.bashrc"
    echo "🐚 Bash 쉘 감지됨"
else
    echo "⚠️ 지원되지 않는 쉘입니다. 수동으로 alias를 설정해주세요."
    echo "다음 내용을 쉘 설정 파일에 추가하세요:"
    echo "$ALIAS_CONTENT"
    exit 1
fi

# 기존 alias 제거
echo "🧹 기존 TPC alias 제거 중..."
sed -i.bak '/# TESLA TPC Streamlit Aliases/,/^$/d' "$RC_FILE" 2>/dev/null || true

# 새 alias 추가
echo "➕ 새 alias 추가 중..."
echo "$ALIAS_CONTENT" >> "$RC_FILE"

echo "✅ Alias 설정 완료!"
echo ""
echo "🔄 다음 명령어로 설정을 적용하세요:"
echo "   source $RC_FILE"
echo ""
echo "📋 사용 가능한 명령어:"
echo "   tpc-deploy   - 배포 도구 실행"
echo "   tpc-dev      - 개발 서버 실행 (8501)"
echo "   tpc-test     - 테스트 서버 실행 (8502)"
echo "   tpc-blue     - Blue 서버 실행 (8503)"
echo "   tpc-green    - Green 서버 실행 (8504)"
echo "   tpc-status   - 포트 상태 확인"
echo "   tpc-stop     - 모든 서버 종료"
echo "   tpc-logs <포트> - 로그 확인"
echo "   tpc-kill <포트> - 특정 포트 종료"
echo "   tpc-help     - 도움말"
echo "   tpc-cd       - 프로젝트 디렉토리로 이동"
echo "" 