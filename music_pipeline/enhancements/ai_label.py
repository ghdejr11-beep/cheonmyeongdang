"""AI 합성 미디어 라벨 자동 주입 + human-input 증거 문구 생성.

YouTube 2025.7 정책: `containsSyntheticMedia=True` 또는 설명란에 명시적
human-input 표시가 없으면 영구 데모네타이즈 위험.

youtube_uploader.py 의 `upload_to_youtube()` 에서 호출:

    from music_pipeline.enhancements.ai_label import (
        inject_ai_label, append_human_input_footer,
    )

    description = append_human_input_footer(description, style_name)
    body = inject_ai_label(body)
"""

from __future__ import annotations


HUMAN_INPUT_FOOTER_TEMPLATE = """

━━━━━━━━━━━━━━━━━━━
✍️ Human Input (YouTube 2025.7 정책 준수)
• Lyrics: 덕구 (수작업 작사 / 수정)
• Arrangement prompt: 덕구 (Suno 프롬프트 디렉션)
• Visuals: 덕구 (편집·색보정·자막 타이밍)
• Curation: 덕구 (트랙 선정·믹싱 순서)
• Style direction: {style_ko}
━━━━━━━━━━━━━━━━━━━
"""

STYLE_KO_MAP = {
    "lofi": "로파이",
    "sleep": "수면·앰비언트",
    "rain": "빗소리·자연음",
    "meditation": "명상",
    "jazz": "재즈·카페",
    "study": "스터디·집중",
    "classical": "클래식",
    "electronic": "일렉트로닉·신스웨이브",
    "pop": "팝·발라드",
    "kpop": "K-POP",
    "general": "릴랙싱 BGM",
}


def inject_ai_label(body: dict) -> dict:
    """YouTube Data API `videos.insert` body 에 AI 합성 미디어 라벨 주입.

    2025.7 이후 정책상 필수. 미적용 시 수동 라벨 강요 또는 데모네타이즈.
    하위호환을 위해 두 필드 모두 세팅 (Google 이 둘 다 받음).
    """
    if "status" not in body:
        body["status"] = {}
    # 구버전 필드 (일부 클라이언트)
    body["status"]["containsSyntheticMedia"] = True
    # 신버전 필드 (2025.7+ 권장)
    body["status"].setdefault("madeForKids", False)
    body["status"].setdefault("selfDeclaredMadeForKids", False)
    return body


def append_human_input_footer(description: str, style_name: str = "general") -> str:
    """기존 설명 뒤에 human-input 증거 블록을 붙인다.

    이미 'Human Input' 이 있으면 중복 삽입하지 않는다.
    """
    if not description:
        description = ""
    if "Human Input" in description:
        return description

    style_ko = STYLE_KO_MAP.get(style_name, style_name)
    footer = HUMAN_INPUT_FOOTER_TEMPLATE.format(style_ko=style_ko)

    # YouTube 5000자 제한 고려
    combined = description.rstrip() + footer
    if len(combined) > 4950:
        # 기존 설명을 잘라서 footer 를 반드시 포함
        cutoff = 4950 - len(footer)
        combined = description[:cutoff].rstrip() + footer
    return combined


if __name__ == "__main__":
    # 빠른 테스트
    body = {"snippet": {"title": "test"}}
    body = inject_ai_label(body)
    assert body["status"]["containsSyntheticMedia"] is True

    desc = "이 영상은 테스트용 설명입니다."
    result = append_human_input_footer(desc, "jazz")
    assert "재즈" in result
    assert "Human Input" in result

    # 중복 방지
    again = append_human_input_footer(result, "jazz")
    assert again.count("Human Input") == 1

    print("✓ ai_label.py 자체 테스트 통과")
