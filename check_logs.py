#!/usr/bin/env python3
"""
포트별 보안 로그 확인 스크립트
"""

import json
from pathlib import Path
from datetime import datetime

def check_logs():
    """포트별 로그 파일 확인"""
    print("🔍 포트별 보안 로그 확인")
    print("=" * 50)
    
    # 포트별 로그 파일 확인
    for port in [8501, 8502, 8503, 8504]:
        log_file = f"security_events_port_{port}.log"
        if Path(log_file).exists():
            print(f"\n📁 포트 {port} 로그 파일: {log_file}")
            print("-" * 30)
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if lines:
                    print(f"총 {len(lines)}개의 로그 항목")
                    
                    # 최근 5개 로그 표시
                    recent_logs = lines[-5:]
                    for i, line in enumerate(recent_logs, 1):
                        try:
                            log_data = json.loads(line.strip())
                            timestamp = log_data.get('timestamp', 'N/A')
                            event_type = log_data.get('event_type', 'N/A')
                            user = log_data.get('user', 'N/A')
                            ip = log_data.get('ip_address', 'N/A')
                            
                            print(f"{i}. {timestamp} | {event_type} | {user} | IP: {ip}")
                        except:
                            print(f"{i}. {line.strip()}")
                else:
                    print("로그가 없습니다.")
                    
            except Exception as e:
                print(f"로그 파일 읽기 오류: {e}")
        else:
            print(f"\n❌ 포트 {port} 로그 파일 없음: {log_file}")
    
    # 기본 로그 파일도 확인
    default_log = "security_events.log"
    if Path(default_log).exists():
        print(f"\n📁 기본 로그 파일: {default_log}")
        print("-" * 30)
        
        try:
            with open(default_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if lines:
                print(f"총 {len(lines)}개의 로그 항목")
                
                # 최근 5개 로그 표시
                recent_logs = lines[-5:]
                for i, line in enumerate(recent_logs, 1):
                    try:
                        log_data = json.loads(line.strip())
                        timestamp = log_data.get('timestamp', 'N/A')
                        event_type = log_data.get('event_type', 'N/A')
                        user = log_data.get('user', 'N/A')
                        ip = log_data.get('ip_address', 'N/A')
                        
                        print(f"{i}. {timestamp} | {event_type} | {user} | IP: {ip}")
                    except:
                        print(f"{i}. {line.strip()}")
            else:
                print("로그가 없습니다.")
                
        except Exception as e:
            print(f"로그 파일 읽기 오류: {e}")
    else:
        print(f"\n❌ 기본 로그 파일 없음: {default_log}")
    
    print("\n" + "=" * 50)
    print("✅ 로그 확인 완료")

if __name__ == "__main__":
    check_logs() 