#!/usr/bin/env python3
"""
briefing.py — v2로 교체된 shim (2026-04-20)
기존 Task Scheduler 6개가 이 파일을 호출하므로 entry point 유지.
실제 로직은 briefing_v2.py.

원본 백업: briefing_v1_backup.py
"""
import sys
from pathlib import Path

# briefing_v2 모듈 실행
sys.path.insert(0, str(Path(__file__).parent))
import briefing_v2

if __name__ == "__main__":
    hour = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "preview":
            print(briefing_v2.build_message())
            sys.exit(0)
        try:
            hour = int(sys.argv[1])
        except ValueError:
            pass
    msg = briefing_v2.build_message(hour)
    result = briefing_v2.send_telegram(msg)
    import datetime
    if result.get("ok"):
        print(f"✅ 브리핑 v2 전송 완료 ({datetime.datetime.now().strftime('%H:%M')})")
    else:
        print(f"❌ 실패: {result}")
