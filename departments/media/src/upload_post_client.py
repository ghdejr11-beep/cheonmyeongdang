#!/usr/bin/env python3
"""
Upload-Post.com Python 클라이언트 — 공식 심사된 서버로 TikTok/YouTube/IG/X 등 자동 배포.

엔드포인트 (공식 docs 기준):
  POST https://api.upload-post.com/api/upload          (video)
  POST https://api.upload-post.com/api/upload_photos   (photos)

인증: Authorization: Apikey {UPLOADPOST_API_KEY}

쿤스튜디오 프로필 매핑 (4채널 YouTube + TikTok 대기):
  kunstudio           → TikTok (4/29 후), IG/X/Threads/FB 등
  healing_sleep_realm → YouTube Healing Sleep Realm
  whisper_atlas       → YouTube Whisper Atlas
  wealth_blueprint    → YouTube Wealth Blueprint
  inner_archetypes    → YouTube Inner Archetypes

사용:
    from upload_post_client import post_video, post_to_all_youtube
    # 단일 채널
    r = post_video(
        video_path="D:/path/shorts.mp4",
        user="healing_sleep_realm",
        platforms=["youtube"],
        title="Deep Sleep 10h",
        description="528Hz..."
    )
    # 4채널 YouTube 일괄
    r = post_to_all_youtube(video_path=..., title=..., description=...)
"""
import os
import json
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
SECRETS = ROOT / ".secrets"

API_BASE = "https://api.upload-post.com/api"


def _load_secrets():
    env = {}
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def _multipart(fields, files):
    """순수 stdlib으로 multipart/form-data 빌드."""
    import uuid
    boundary = f"----KunStudioBoundary{uuid.uuid4().hex}"
    lines = []
    for k, v in fields:
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{k}"'.encode())
        lines.append(b"")
        if isinstance(v, str):
            lines.append(v.encode("utf-8"))
        else:
            lines.append(v)
    for field_name, filepath in files:
        with open(filepath, "rb") as f:
            data = f.read()
        filename = os.path.basename(filepath)
        ctype = "video/mp4" if filepath.lower().endswith(".mp4") else "application/octet-stream"
        lines.append(f"--{boundary}".encode())
        lines.append(
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode()
        )
        lines.append(f"Content-Type: {ctype}".encode())
        lines.append(b"")
        lines.append(data)
    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    body = b"\r\n".join(lines)
    return body, boundary


def post_video(video_path, user, platforms, title="", description="", extra=None, env=None):
    """Upload-Post 통해 동영상 업로드.

    Args:
        video_path: 로컬 mp4 경로
        user: Upload-Post 프로필명 (kunstudio/healing_sleep_realm/...)
        platforms: ["youtube", "tiktok", "instagram", "x", "facebook" 등]
        title: 제목
        description: 설명
        extra: 플랫폼별 추가 필드 (예: {"hashtags": "#sleep"})
    Returns:
        (ok: bool, response: dict|str)

    SSL EOF 방지 (2026-05-01):
      - requests 라이브러리로 전환 (urllib stdlib의 SSL EOF 빈발 → requests는 더 안정)
      - file streaming (메모리에 800MB 통째로 안 올림)
      - read timeout 600s (3h/8h 영상 처리 시간 충분히 확보)
      - retry 자동 (개별 호출 단의 1회 retry, 상위 upload_to_channel에서 추가 3회)
    """
    env = env or _load_secrets()
    key = env.get("UPLOADPOST_API_KEY", "").strip()
    if not key:
        return False, "no UPLOADPOST_API_KEY"
    p = Path(video_path)
    if not p.exists():
        return False, f"video not found: {video_path}"

    # requests 사용 (SSL EOF 빈도 ↓)
    try:
        import requests  # type: ignore
    except ImportError:
        # fallback: 기존 urllib 방식
        return _post_video_urllib(video_path, user, platforms, title, description, extra, env, key)

    data = {"user": user, "title": title}
    if description:
        data["description"] = description
    # platform[] 다중값
    data["platform[]"] = list(platforms)
    if extra:
        for k, v in extra.items():
            data[k] = v

    headers = {
        "Authorization": f"Apikey {key}",
        "User-Agent": "KunStudio-UploadPost/2.0",
        # Connection: close 로 keep-alive 미스 방지 (큰 업로드에 유리)
        "Connection": "close",
    }

    # streaming multipart — 메모리 효율 + SSL EOF ↓
    last_err = None
    for attempt in range(2):
        try:
            with open(video_path, "rb") as f:
                files = {"video": (p.name, f, "video/mp4")}
                # connect=30s, read=600s (큰 파일 + 서버 백그라운드 핸드오프 대기)
                r = requests.post(
                    f"{API_BASE}/upload",
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=(30, 600),
                )
            try:
                resp_data = r.json()
            except Exception:
                resp_data = r.text
            return (r.status_code == 200), resp_data
        except requests.exceptions.SSLError as e:
            last_err = f"SSL: {e}"
        except requests.exceptions.Timeout as e:
            last_err = f"timeout: {e}"
        except requests.exceptions.ConnectionError as e:
            last_err = f"conn: {e}"
        except Exception as e:
            return False, f"error: {e}"
        # retry once with small backoff
        if attempt == 0:
            import time as _t
            _t.sleep(5)
    return False, f"error: {last_err}"


def _post_video_urllib(video_path, user, platforms, title, description, extra, env, key):
    """레거시 urllib fallback (requests 없을 때)."""
    fields = [("user", user), ("title", title)]
    if description:
        fields.append(("description", description))
    for p in platforms:
        fields.append(("platform[]", p))
    if extra:
        for k, v in extra.items():
            fields.append((k, v))

    files = [("video", video_path)]
    body, boundary = _multipart(fields, files)

    req = urllib.request.Request(
        f"{API_BASE}/upload",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Apikey {key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "KunStudio-UploadPost/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            raw = r.read().decode("utf-8")
            try:
                data = json.loads(raw)
            except Exception:
                data = raw
            return (r.status == 200), data
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')[:400]}"
    except Exception as e:
        return False, f"error: {e}"


# ───────── 4채널 YouTube 일괄 ─────────

YT_CHANNELS = [
    ("healing_sleep_realm", "Healing Sleep Realm"),
    ("whisper_atlas", "Whisper Atlas"),
    ("wealth_blueprint", "Wealth Blueprint"),
    ("inner_archetypes", "Inner Archetypes"),
]


def post_to_all_youtube(video_path, title="", description=""):
    """4채널 YouTube 에 동일 영상 동시 업로드 (니치 맞는 채널만 골라쓰는게 보통 더 좋음)."""
    results = {}
    env = _load_secrets()
    for user, label in YT_CHANNELS:
        ok, r = post_video(video_path, user=user, platforms=["youtube"],
                           title=title, description=description, env=env)
        results[label] = {"ok": ok, "response": str(r)[:200]}
    return results


def post_to_channel(video_path, channel_key, title="", description=""):
    """단일 YT 채널에 업로드. channel_key: healing_sleep_realm/whisper_atlas/wealth_blueprint/inner_archetypes"""
    return post_video(video_path, user=channel_key, platforms=["youtube"],
                      title=title, description=description)


# ───────── 메인 프로필 (kunstudio) 다채널 ─────────

def post_to_kunstudio(video_path, title="", description="",
                     platforms=("instagram", "x", "threads", "facebook")):
    """kunstudio 프로필에 여러 플랫폼 동시 업로드. TikTok은 4/29 이후 추가."""
    return post_video(video_path, user="kunstudio", platforms=list(platforms),
                      title=title, description=description)


if __name__ == "__main__":
    # 드라이런: 프로필/키 확인
    env = _load_secrets()
    print("API key:", ("set" if env.get("UPLOADPOST_API_KEY") else "NOT SET"))
    print("프로필 매핑:")
    for u, lbl in YT_CHANNELS:
        print(f"  {u} -> YT {lbl}")
    print("  kunstudio -> IG/X/Threads/FB (+TikTok 4/29 후)")
