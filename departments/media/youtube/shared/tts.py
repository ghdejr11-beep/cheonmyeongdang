#!/usr/bin/env python3
"""
edge-tts 래퍼 — MS Edge 브라우저 내장 TTS, **완전 무료, API 키 불필요**.

사용:
    from tts import synthesize
    synthesize("Hello world", "out.mp3", voice="en-US-GuyNeural")

인기 영어 voices (자연스러움 순):
  - en-US-GuyNeural       (남성, 깊은 목소리, 동기부여/다큐)
  - en-US-JennyNeural     (여성, 친근, 튜토리얼)
  - en-US-AriaNeural      (여성, 뉴스 앵커)
  - en-US-AndrewNeural    (남성, 팟캐스트 톤)
  - en-US-EmmaNeural      (여성, 편안한 대화)
  - en-GB-SoniaNeural     (영국 여성, 세련된 톤)

공식 무료, 상업 사용 가능.
"""
import asyncio, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def synthesize(text, out_path, voice="en-US-GuyNeural", rate="+0%", volume="+0%"):
    """
    text → mp3 파일.
      rate: "-50%" ~ "+100%" 속도
      volume: 음량
    """
    import edge_tts

    async def _run():
        communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
        await communicate.save(str(out_path))

    asyncio.run(_run())
    return Path(out_path)


if __name__ == "__main__":
    out = Path(r"D:\cheonmyeongdang-outputs\youtube\_tts_test.mp3")
    out.parent.mkdir(parents=True, exist_ok=True)
    synthesize(
        "This is a test of the Microsoft Edge text to speech for YouTube automation. Quality is excellent and it is completely free.",
        out,
        voice="en-US-GuyNeural",
    )
    print(f"✅ {out} ({out.stat().st_size/1024:.1f} KB)")
