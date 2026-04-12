"""
Pexels 무료 영상 다운로더.

Claude 가 가사에서 추출한 키워드로 Pexels 영상을 검색·다운로드한다.
lyrics_watcher.py 에서 호출됨.

환경변수: PEXELS_API_KEY (무료, https://www.pexels.com/api/)
"""

import os
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional


def _get_pexels_key() -> str:
    """호출 시점에 환경변수에서 키를 읽음 (모듈 로딩 시점이 아님)."""
    return (os.environ.get("PEXELS_API_KEY") or "").strip()


def search_videos(query: str, orientation: str = "landscape",
                  per_page: int = 3, min_duration: int = 5,
                  max_duration: int = 30) -> list[dict]:
    """Pexels 영상 검색. 결과 리스트 반환.

    Args:
        query: 검색어 (영어 권장)
        orientation: landscape / portrait / square
        per_page: 최대 결과 수
        min_duration: 최소 길이 (초)
        max_duration: 최대 길이 (초)

    Returns:
        [{"id": 123, "url": "https://...", "duration": 15, "width": 1920, ...}, ...]
    """
    if not _get_pexels_key():
        return []

    params = urllib.parse.urlencode({
        "query": query,
        "orientation": orientation,
        "per_page": per_page,
        "size": "medium",  # Full HD
    })
    url = f"https://api.pexels.com/videos/search?{params}"
    req = urllib.request.Request(url, headers={
        "Authorization": _get_pexels_key(),
        "User-Agent": "DeokguneAI/1.0",
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[pexels] 검색 실패 ({query}): {e}")
        return []

    results = []
    for video in data.get("videos", []):
        duration = video.get("duration", 0)
        if duration < min_duration or duration > max_duration:
            continue

        # HD 이상 파일 찾기
        best_file = None
        for vf in video.get("video_files", []):
            w = vf.get("width", 0)
            if w >= 1280 and vf.get("file_type") == "video/mp4":
                if not best_file or w > best_file.get("width", 0):
                    best_file = vf

        if best_file:
            results.append({
                "id": video["id"],
                "url": best_file["link"],
                "duration": duration,
                "width": best_file.get("width", 0),
                "height": best_file.get("height", 0),
            })

    return results


def download_video(url: str, save_path: str, timeout: int = 60) -> bool:
    """영상 1개 다운로드."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "DeokguneAI/1.0",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            with open(save_path, "wb") as f:
                f.write(resp.read())
        return os.path.exists(save_path) and os.path.getsize(save_path) > 10000
    except Exception as e:
        print(f"[pexels] 다운로드 실패: {e}")
        return False


def get_clips_for_keywords(keywords: list[str], tmp_dir: str,
                           clips_per_keyword: int = 1) -> list[str]:
    """키워드 리스트 → 각 키워드별 영상 1개씩 다운로드.

    Returns:
        다운로드된 영상 파일 경로 리스트
    """
    clips = []
    seen_ids = set()

    for kw in keywords:
        results = search_videos(kw, per_page=3)
        downloaded = 0

        for r in results:
            if r["id"] in seen_ids:
                continue
            seen_ids.add(r["id"])

            filename = f"pexels_{r['id']}.mp4"
            filepath = os.path.join(tmp_dir, filename)

            if download_video(r["url"], filepath):
                clips.append(filepath)
                downloaded += 1
                print(f"[pexels] '{kw}' → {filename} ({r['duration']}초, {r['width']}x{r['height']})")

            if downloaded >= clips_per_keyword:
                break

        if downloaded == 0:
            print(f"[pexels] '{kw}' → 영상 없음 (스킵)")

    return clips


def extract_keywords_from_lyrics(lyrics_text: str, api_key: str = None) -> list[str]:
    """Claude 에게 가사 분석 → 영어 키워드 리스트 추출.

    Args:
        lyrics_text: 한국어 가사 텍스트
        api_key: Anthropic API 키

    Returns:
        ["window sunlight", "walking dog", "rainbow sky", ...]
    """
    if not api_key:
        api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        return _fallback_keywords(lyrics_text)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""아래 한국어 노래 가사를 분석해서 뮤직비디오에 어울리는 **영어 검색 키워드** 를 추출해.
각 키워드는 Pexels (무료 영상 사이트) 에서 검색할 용도야.

규칙:
1. 가사의 감정·장면·이미지를 영어 키워드로 변환
2. 키워드당 2~3단어 (예: "window sunlight", "rainy street", "dog park")
3. 8~12개 추출
4. 추상적인 것 (love, sadness) 보단 **구체적 장면** (couple walking beach, empty room morning)
5. JSON 배열만 출력

가사:
{lyrics_text[:2000]}

출력 예시:
["window morning light", "empty pet bed", "walking trail autumn", "rainbow after rain"]"""

        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in msg.content if hasattr(b, "text"))

        # JSON 추출
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            keywords = json.loads(text[start:end])
            return [str(k).strip() for k in keywords if k][:12]
    except Exception as e:
        print(f"[pexels] Claude 키워드 추출 실패: {e}")

    return _fallback_keywords(lyrics_text)


def _fallback_keywords(lyrics_text: str) -> list[str]:
    """Claude 없을 때 기본 키워드."""
    # 한국어 키워드 → 영어 매핑 (자주 나오는 감성 키워드)
    mapping = {
        "창가": "window morning light",
        "햇살": "sunlight through window",
        "비": "rain drops window",
        "바다": "ocean waves sunset",
        "산책": "walking path nature",
        "무지개": "rainbow sky clouds",
        "별": "stars night sky",
        "꽃": "flowers blooming spring",
        "눈물": "rain on glass",
        "사랑": "couple silhouette sunset",
        "이별": "empty bench park",
        "추억": "old photographs memories",
        "강아지": "dog playing park",
        "고양이": "cat sleeping window",
        "밤": "city lights night",
        "아침": "sunrise morning sky",
        "겨울": "snow falling trees",
        "봄": "cherry blossoms spring",
        "가을": "autumn leaves falling",
        "여름": "beach summer waves",
    }

    keywords = []
    for kr, en in mapping.items():
        if kr in lyrics_text:
            keywords.append(en)

    if not keywords:
        keywords = ["nature peaceful landscape", "sunset clouds sky",
                     "morning light room", "rain window cozy"]

    return keywords[:10]
