#!/bin/bash
# 로컬 Docker 개발 환경을 중지하고 모든 관련 리소스를 삭제합니다.

echo "🛑 로컬 개발 환경(Docker)을 중지합니다..."

# -v: 볼륨 삭제
# --remove-orphans: 더 이상 사용되지 않는 컨테이너 삭제
docker-compose down -v --remove-orphans

echo "✅ 모든 서비스가 중지되었고 관련 리소스가 삭제되었습니다." 