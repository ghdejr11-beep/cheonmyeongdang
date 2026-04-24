"""
apiframe.ai Suno API 래퍼
- Basic Plan: $19/월 1000 크레딧
- 상업 사용 가능 (royalty-free)
- 가사 + 스타일 + 길이 지정

환경변수:
  APIFRAME_API_KEY — https://apiframe.ai dashboard 에서 발급
"""
from __future__ import annotations
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Literal, Optional

API_BASE = "https://api.apiframe.pro"  # v1 엔드포인트 (docs.apiframe.ai/suno-ai-api)


class ApiframeError(RuntimeError):
    pass


def _get_key() -> str:
    key = os.environ.get("APIFRAME_API_KEY", "").strip()
    if not key:
        raise ApiframeError(
            "APIFRAME_API_KEY 미설정 — .secrets 에 APIFRAME_API_KEY=xxx 추가 후 "
            "export 하세요. 키 발급: https://apiframe.ai"
        )
    return key


def _post(path: str, payload: dict, timeout: int = 60) -> dict:
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {_get_key()}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore") if e.fp else ""
        raise ApiframeError(f"HTTP {e.code} {path}: {body[:500]}") from e


def _get(path: str, timeout: int = 30) -> dict:
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {_get_key()}"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def generate_song(
    prompt: str,
    *,
    instrumental: bool = True,
    lyrics: Optional[str] = None,
    style: Optional[str] = None,
    title: Optional[str] = None,
    model: Literal["V4", "V4_5", "V5"] = "V5",
) -> dict:
    """
    곡 생성 요청. 비동기 → task_id 반환.

    Args:
        prompt: 장르/분위기 묘사 (예: "deep meditation buddhist chant with tibetan bowls")
        instrumental: True면 가사 없음 (BGM 채널 기본값)
        lyrics: instrumental=False 인 경우 가사
        style: 추가 스타일 힌트
        title: 곡 제목

    Returns:
        {"task_id": str, "status": "pending", ...}
    """
    payload = {
        "prompt": prompt,
        "instrumental": instrumental,
        "model": model,
    }
    if lyrics and not instrumental:
        payload["lyrics"] = lyrics
    if style:
        payload["style"] = style
    if title:
        payload["title"] = title
    return _post("/suno/generate", payload)


def get_task(task_id: str) -> dict:
    """곡 생성 상태 조회. status: pending | complete | failed"""
    return _get(f"/suno/task/{task_id}")


def wait_and_download(
    task_id: str, dest: Path, *, max_wait: int = 300, poll_interval: int = 10
) -> Path:
    """완료 대기 후 MP3 다운로드."""
    elapsed = 0
    while elapsed < max_wait:
        info = get_task(task_id)
        status = info.get("status", "")
        if status == "complete":
            audio_url = info.get("audio_url") or info.get("clips", [{}])[0].get("audio_url")
            if not audio_url:
                raise ApiframeError(f"완료됐지만 audio_url 없음: {info}")
            req = urllib.request.Request(
                audio_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            dest.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(req, timeout=120) as r, dest.open("wb") as f:
                f.write(r.read())
            return dest
        if status == "failed":
            raise ApiframeError(f"생성 실패: {info}")
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise ApiframeError(f"{max_wait}초 초과 미완료 (task={task_id})")


def get_credits() -> dict:
    """남은 크레딧 조회"""
    return _get("/account/credits")


if __name__ == "__main__":
    # 간단 동작 테스트
    try:
        print("크레딧:", get_credits())
    except ApiframeError as e:
        print(f"[키 필요] {e}")
