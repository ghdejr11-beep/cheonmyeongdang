"""B2B daily auto-batch sender — schtask wrapper.

매일 11:00 schtask가 이 스크립트 호출 → sent_log 읽고 다음 batch 자동 발송.
- BATCH_SIZE = 5/일 (send_b2b_emails.py 상수)
- 30 verified emails → 6일 분산 (5/6 batch1 완료 → 5/7~5/11 batch2~6)
- sent_log 기준 진행 (재실행 안전)
"""
import os, sys, json, subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
SENT_LOG = ROOT / "sent_log.json"
SEND_SCRIPT = ROOT / "send_b2b_emails.py"


def main():
    sent = []
    if SENT_LOG.exists():
        try:
            sent = json.loads(SENT_LOG.read_text(encoding="utf-8"))
        except Exception:
            sent = []

    # 다음 batch 결정 — 5/일 기준
    sent_count = len(sent)
    next_batch = (sent_count // 5) + 1

    if next_batch > 10:
        print(f"[STOP] All batches sent (sent_count={sent_count}). Nothing to do.")
        return

    print(f"[INFO] sent_count={sent_count}, next batch={next_batch}")
    result = subprocess.run(
        [sys.executable, str(SEND_SCRIPT), "--confirm", "--batch", str(next_batch)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[:500])


if __name__ == "__main__":
    main()
