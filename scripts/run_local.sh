#!/bin/bash
# 로컬 Docker 개발 환경을 시작합니다.

echo "🚀 로컬 개발 환경(Docker)을 시작합니다..."

# Docker 컨테이너 내부 사용자 권한을 호스트와 맞추기 위함
export UID=$(id -u)
export GID=$(id -g)

echo "📦 이미지를 빌드하고 컨테이너를 시작합니다. (UID: $UID, GID: $GID)"

# -d: 백그라운드 실행
# --build: 실행 전 이미지 다시 빌드
docker-compose up -d --build

echo ""
echo "✅ 모든 서비스가 백그라운드에서 실행 중입니다."
echo "👀 로그 확인: docker-compose logs -f"
echo "🛑 중지: ./scripts/stop_local.sh"
echo ""
echo "🌐 접속 URL:"
echo "  - 메인 (Blue): https://localhost"
echo "  - A/B (A):   https://localhost/ab/a/"
echo "  - A/B (B):   https://localhost/ab/b/"
echo "  - Blue:      https://localhost/blue/"
echo "  - Green:     https://localhost/green/" 