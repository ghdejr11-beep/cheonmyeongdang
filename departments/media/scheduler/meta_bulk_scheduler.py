"""
Meta (Facebook + Instagram) 대량 예약 업로드 스크립트
====================================================

사용법:
    # 1. .env 파일에 토큰 입력
    # 2. posts_queue.json 생성 (--build)
    # 3. Facebook 30개 한 번에 네이티브 예약
        python meta_bulk_scheduler.py --fb-schedule-all
    # 4. Instagram: Windows Task Scheduler가 매시간 실행
        python meta_bulk_scheduler.py --ig-run-due

재사용: 다른 부서 콘텐츠도 posts_queue.json 만들면 그대로 사용 가능.
"""

import os
import sys
import json
import time
import argparse
import datetime as dt
from pathlib import Path
import requests

# Windows CP949 콘솔에서 이모지 출력 에러 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ─── 설정 ────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent.parent.parent  # cheonmyeongdang
ENV_FILE = SCRIPT_DIR / ".env"
QUEUE_FILE = SCRIPT_DIR / "posts_queue.json"
LOG_FILE = SCRIPT_DIR / "post_log.txt"
GRAPH_VERSION = "v23.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"

# ─── 환경변수 로드 ────────────────────────────────────────
def load_env():
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def log(msg):
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ─── 콘텐츠 로더 (.txt 파일에서 캡션 추출) ─────────────────
def parse_post_txt(txt_path):
    """post_XX_*.txt에서 캡션 부분만 추출"""
    text = Path(txt_path).read_text(encoding="utf-8")
    marker = "붙여넣기:"
    if marker in text:
        after = text.split(marker, 1)[1]
        # 첫 번째 ──── 구분선 이후가 실제 캡션
        parts = after.split("─" * 10, 1)
        caption = parts[1] if len(parts) > 1 else after
    else:
        caption = text
    return caption.strip()

# ─── 큐 빌더 ──────────────────────────────────────────────
def build_queue(content_dir, image_url_base, start_date, posts_per_day=3, hours=(9, 13, 19)):
    """
    content_dir: post_XX_*.txt + images/ 폴더
    image_url_base: 이미지 공개 URL prefix (예: https://ghdejr11-beep.github.io/cheonmyeongdang/tax-images/)
    start_date: YYYY-MM-DD
    """
    content_dir = Path(content_dir)
    image_dir = content_dir / "images"
    txt_files = sorted(content_dir.glob("post_*.txt"))

    queue = []
    start = dt.datetime.strptime(start_date, "%Y-%m-%d")

    for i, txt_file in enumerate(txt_files):
        num = txt_file.stem.split("_")[1]  # "01"
        img_name = f"post_{num}.jpg"
        img_path = image_dir / img_name

        if not img_path.exists():
            log(f"⚠️  이미지 없음: {img_path}")
            continue

        # 예약 시간 계산
        day_offset = i // posts_per_day
        slot = i % posts_per_day
        hour = hours[slot] if slot < len(hours) else hours[-1]
        schedule_dt = start + dt.timedelta(days=day_offset)
        schedule_dt = schedule_dt.replace(hour=hour, minute=0, second=0, microsecond=0)

        caption = parse_post_txt(txt_file)

        queue.append({
            "index": i + 1,
            "txt_file": str(txt_file),
            "image_local": str(img_path),
            "image_url": f"{image_url_base.rstrip('/')}/{img_name}",
            "caption": caption,
            "scheduled_time": schedule_dt.isoformat(),
            "scheduled_ts": int(schedule_dt.timestamp()),
            "fb_status": "pending",
            "fb_post_id": None,
            "ig_status": "pending",
            "ig_post_id": None,
        })

    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"✅ 큐 생성: {len(queue)}개 → {QUEUE_FILE}")
    return queue

# ─── Facebook 네이티브 예약 ─────────────────────────────────
def fb_schedule_photo(page_id, page_token, image_path, caption, scheduled_ts):
    """FB 페이지에 이미지 + 캡션으로 예약 게시 (로컬 파일 업로드)"""
    url = f"{BASE_URL}/{page_id}/photos"
    with open(image_path, "rb") as img:
        files = {"source": img}
        data = {
            "caption": caption,
            "published": "false",
            "scheduled_publish_time": str(scheduled_ts),
            "access_token": page_token,
        }
        r = requests.post(url, files=files, data=data, timeout=120)
    return r.json()

def fb_schedule_all():
    env = load_env()
    page_id = env.get("FB_PAGE_ID")
    page_token = env.get("FB_PAGE_ACCESS_TOKEN")
    if not page_id or not page_token:
        log("❌ .env에 FB_PAGE_ID / FB_PAGE_ACCESS_TOKEN 필요")
        return

    queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    now_ts = int(time.time())
    min_future_ts = now_ts + 15 * 60  # 15분 버퍼

    updated = 0
    for post in queue:
        if post["fb_status"] != "pending":
            continue

        ts = post["scheduled_ts"]
        if ts < min_future_ts:
            ts = min_future_ts + (updated * 600)  # 10분씩 미룸

        log(f"📅 FB 예약 중 #{post['index']}: {dt.datetime.fromtimestamp(ts)}")
        result = fb_schedule_photo(page_id, page_token, post["image_local"], post["caption"], ts)

        if "id" in result or "post_id" in result:
            post["fb_status"] = "scheduled"
            post["fb_post_id"] = result.get("post_id") or result.get("id")
            post["fb_scheduled_ts_actual"] = ts
            updated += 1
            log(f"   ✅ 성공: {post['fb_post_id']}")
        else:
            post["fb_status"] = "error"
            post["fb_error"] = result
            log(f"   ❌ 실패: {result}")

        time.sleep(1)  # rate limit 회피

    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"✅ FB 완료: {updated}개 예약")

# ─── Instagram 즉시 발행 (cron으로 매시간 due 체크) ─────────
def ig_publish_now(ig_user_id, access_token, image_url, caption):
    """IG 2단계 발행: 컨테이너 생성 → publish"""
    # 1단계: 미디어 컨테이너
    r1 = requests.post(
        f"{BASE_URL}/{ig_user_id}/media",
        data={"image_url": image_url, "caption": caption, "access_token": access_token},
        timeout=60,
    ).json()
    if "id" not in r1:
        return {"error": "container_failed", "detail": r1}
    container_id = r1["id"]

    # IG 권장: 컨테이너 상태 확인 (선택)
    time.sleep(3)

    # 2단계: 발행
    r2 = requests.post(
        f"{BASE_URL}/{ig_user_id}/media_publish",
        data={"creation_id": container_id, "access_token": access_token},
        timeout=60,
    ).json()
    return r2

def ig_run_due():
    """현재 시각 기준 예약 시간 지난 IG 게시물 발행"""
    env = load_env()
    ig_user_id = env.get("IG_USER_ID")
    access_token = env.get("FB_PAGE_ACCESS_TOKEN")  # Page token으로 IG도 접근 가능
    if not ig_user_id or not access_token:
        log("❌ .env에 IG_USER_ID / FB_PAGE_ACCESS_TOKEN 필요")
        return

    queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    now_ts = int(time.time())

    published = 0
    for post in queue:
        if post["ig_status"] != "pending":
            continue
        if post["scheduled_ts"] > now_ts:
            continue  # 아직 때 안 됨

        log(f"📸 IG 발행 중 #{post['index']}")
        result = ig_publish_now(ig_user_id, access_token, post["image_url"], post["caption"])

        if "id" in result:
            post["ig_status"] = "published"
            post["ig_post_id"] = result["id"]
            post["ig_published_at"] = dt.datetime.now().isoformat()
            published += 1
            log(f"   ✅ 성공: {post['ig_post_id']}")
        else:
            post["ig_status"] = "error"
            post["ig_error"] = result
            log(f"   ❌ 실패: {result}")
            # 에러는 다음번에 재시도하지 않도록 error 상태 유지

        time.sleep(2)

    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"✅ IG 완료: {published}개 발행")

# ─── 상태 조회 ────────────────────────────────────────────
def status():
    if not QUEUE_FILE.exists():
        print("큐 파일 없음. --build 먼저 실행")
        return
    queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    fb_counts = {"pending": 0, "scheduled": 0, "error": 0}
    ig_counts = {"pending": 0, "published": 0, "error": 0}
    for p in queue:
        fb_counts[p["fb_status"]] = fb_counts.get(p["fb_status"], 0) + 1
        ig_counts[p["ig_status"]] = ig_counts.get(p["ig_status"], 0) + 1
    print(f"\n총 {len(queue)}개")
    print(f"FB: {fb_counts}")
    print(f"IG: {ig_counts}")

# ─── main ────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="posts_queue.json 생성")
    parser.add_argument("--content-dir", default=str(ROOT_DIR / "departments/media/src/tax_content_output"))
    parser.add_argument("--image-url-base", default="https://ghdejr11-beep.github.io/cheonmyeongdang/tax-images")
    parser.add_argument("--start-date", default=dt.datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--fb-schedule-all", action="store_true", help="FB 전체 네이티브 예약")
    parser.add_argument("--ig-run-due", action="store_true", help="IG 시간 된 것만 즉시 발행 (cron용)")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    if args.build:
        build_queue(args.content_dir, args.image_url_base, args.start_date)
    if args.fb_schedule_all:
        fb_schedule_all()
    if args.ig_run_due:
        ig_run_due()
    if args.status:
        status()

    if not any([args.build, args.fb_schedule_all, args.ig_run_due, args.status]):
        parser.print_help()

if __name__ == "__main__":
    main()
