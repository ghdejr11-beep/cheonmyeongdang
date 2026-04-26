"""
ElevenLabs Music API 래퍼
- Creator Plan: 110K 크레딧/월, 1591 크레딧/분
- 상업 사용 가능 (Creator 이상)
- 최대 22분 생성 (BGM은 루프로 10시간 만듦)

환경변수:
  ELEVENLABS_API_KEY — .secrets 에 등록됨
"""
from __future__ import annotations
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

API_BASE = "https://api.elevenlabs.io/v1"


class ElevenLabsError(RuntimeError):
    pass


def _get_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise ElevenLabsError(
            "ELEVENLABS_API_KEY 미설정 — .secrets 에 ELEVENLABS_API_KEY=xxx 추가 후 export 하세요."
        )
    return key


def _post(path: str, payload: dict, timeout: int = 120) -> bytes:
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": _get_key(),
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore") if e.fp else ""
        raise ElevenLabsError(f"HTTP {e.code} {path}: {body[:500]}") from e


def generate_music(
    prompt: str,
    dest: Path,
    *,
    duration_seconds: int = 300,
    influence: float = 0.7,
) -> Path:
    """
    BGM 음악 생성 후 MP3 저장.

    Args:
        prompt: 음악 설명 (예: "528Hz deep sleep ambient drone, soft rain")
        dest: 저장 경로 (예: Path("output/sleep.mp3"))
        duration_seconds: 생성 길이 (최대 1320초=22분)
        influence: 프롬프트 반영 강도 0.0~1.0

    Returns:
        저장된 Path
    """
    if duration_seconds > 1320:
        duration_seconds = 1320

    payload = {
        "text": prompt,
        "duration_seconds": duration_seconds,
        "prompt_influence": influence,
    }

    audio_bytes = _post("/sound-generation", payload, timeout=300)

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(audio_bytes)
    return dest


def get_credits() -> dict:
    """남은 크레딧 조회"""
    url = f"{API_BASE}/user/subscription"
    req = urllib.request.Request(
        url,
        headers={"xi-api-key": _get_key(), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def estimate_credits(duration_seconds: int) -> int:
    """크레딧 소비량 추정 (1591 크레딧/분)"""
    return int(duration_seconds / 60 * 1591)


if __name__ == "__main__":
    import sys

    # .secrets 로드
    secrets_path = Path(__file__).parents[5] / ".secrets"
    if secrets_path.exists():
        for line in secrets_path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    try:
        sub = get_credits()
        used = sub.get("character_count", 0)
        limit = sub.get("character_limit", 0)
        print(f"크레딧 사용: {used:,} / {limit:,}")
    except ElevenLabsError as e:
        print(f"[키 오류] {e}")
        sys.exit(1)

    prompt = (
        "ultra deep sleep ambient drone, 528Hz healing solfeggio frequency, "
        "soft rain on temple roof, no melody, pure meditation soundscape"
    )
    out = Path("D:/documents/쿤스튜디오/bgm_output/elevenlabs_samples/sleep_test2.mp3")
    print(f"생성 중... (예상 크레딧: {estimate_credits(300):,})")
    result = generate_music(prompt, out, duration_seconds=300)
    print(f"저장 완료: {result} ({result.stat().st_size // 1024}KB)")
