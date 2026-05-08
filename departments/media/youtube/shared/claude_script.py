#!/usr/bin/env python3
"""
Claude API로 유튜브 스크립트 자동 생성.

사용:
    from claude_script import generate
    script = generate(prompt="...", max_tokens=3000)
"""
import os, sys, urllib.request, json
from pathlib import Path

SECRETS = Path(r"D:\cheonmyeongdang\.secrets")


def _key():
    # 환경변수 우선
    env_key = os.environ.get("ANTHROPIC_API_KEY")
    if env_key:
        return env_key
    # .secrets 폴백
    if SECRETS.exists():
        for line in SECRETS.read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("ANTHROPIC_API_KEY 없음 (env 또는 .secrets)")


def generate(prompt, system="You are a YouTube script writer.", model="claude-sonnet-4-6", max_tokens=3000):
    key = _key()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps({
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }).encode(),
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    return data["content"][0]["text"]


if __name__ == "__main__":
    out = generate("Write a 30-second YouTube Short script about 'using Claude API for side income'. Plain text, no markdown, no emojis in body, natural spoken flow.", max_tokens=500)
    print(out)
