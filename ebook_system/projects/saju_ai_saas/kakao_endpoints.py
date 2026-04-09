"""
카카오 i 오픈빌더 스킬 엔드포인트.

server.py 의 FastAPI 앱에 mount 되어 카카오톡 챗봇 webhook 을 처리한다.

스킬 응답 포맷 (검색 확인 — 카카오 i 오픈빌더 v2.0):
  {
    "version": "2.0",
    "template": {
      "outputs": [{"simpleText": {"text": "..."}}],
      "quickReplies": [{"label": "...", "action": "message", "messageText": "..."}]
    }
  }

엔드포인트 (Kakao i Open Builder 의 스킬 URL 에 등록):
  POST /kakao/saju          - 생년월일 받아서 사주 계산 + 첫 해석
  POST /kakao/chat          - 후속 질문 (사용자 ID 기반 세션)
  POST /kakao/welcome       - 친구추가 환영 메시지

세션 저장:
  사주 결과는 SQLite 의 users 테이블에 user_key (카카오톡 사용자 ID) 로 저장
  → 다음 요청 때 자동 조회

비즈니스 인증:
  카카오 i 오픈빌더 → AI 챗봇 사용 시 영업일 2~3일 승인 필요 (검색 팩트)
"""

import json
import re
import sqlite3
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

import config
from saju_calc import calculate_saju, format_saju_for_claude


router = APIRouter(prefix="/kakao", tags=["kakao"])


# ============================================================
# 카카오 응답 포맷 헬퍼
# ============================================================
def kakao_simple_text(text: str, quick_replies: Optional[list[dict]] = None) -> dict:
    """카카오 i 오픈빌더 v2.0 simpleText 응답 생성."""
    template: dict = {"outputs": [{"simpleText": {"text": text[:1000]}}]}
    if quick_replies:
        template["quickReplies"] = quick_replies
    return {"version": "2.0", "template": template}


def kakao_basic_card(
    title: str, description: str, buttons: Optional[list[dict]] = None
) -> dict:
    """basicCard 형식 (제목 + 설명 + 버튼)."""
    card: dict = {
        "title": title[:50],
        "description": description[:400],
    }
    if buttons:
        card["buttons"] = buttons[:3]
    return {
        "version": "2.0",
        "template": {"outputs": [{"basicCard": card}]},
    }


def quick_reply(label: str, message: str) -> dict:
    return {
        "label": label[:14],
        "action": "message",
        "messageText": message[:1000],
    }


# ============================================================
# 카카오톡 사용자 → SQLite 조회/저장
# ============================================================
def db_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_kakao_table():
    """server.py 의 init_db() 가 이미 호출되지만 카카오 컬럼 추가."""
    conn = db_conn()
    try:
        # 기존 users 테이블에 kakao_user_key 컬럼 없으면 추가
        cur = conn.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in cur.fetchall()}
        if "kakao_user_key" not in columns:
            try:
                conn.execute("ALTER TABLE users ADD COLUMN kakao_user_key TEXT")
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_users_kakao "
                    "ON users(kakao_user_key)"
                )
                conn.commit()
            except sqlite3.OperationalError:
                pass
    finally:
        conn.close()


def get_user_by_kakao(user_key: str) -> Optional[dict]:
    conn = db_conn()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE kakao_user_key = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (user_key,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def save_user_kakao(user_key: str, year: int, month: int, day: int,
                    hour: int, minute: int, saju: dict) -> str:
    """카카오 사용자 + 사주 결과 저장. 임의의 session_id 반환."""
    import secrets
    session_id = secrets.token_urlsafe(12)
    conn = db_conn()
    try:
        conn.execute(
            """INSERT INTO users
            (session_id, kakao_user_key, birth_year, birth_month, birth_day,
             birth_hour, birth_minute, saju_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id, user_key, year, month, day, hour, minute,
                json.dumps(saju, ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return session_id


# ============================================================
# 생년월일 파싱 (자연어)
# ============================================================
BIRTH_PATTERNS = [
    # 1990년 3월 15일 14시 30분
    re.compile(
        r"(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일"
        r"(?:\s*(\d{1,2})\s*시(?:\s*(\d{1,2})\s*분)?)?"
    ),
    # 1990.03.15 14:30 또는 1990-03-15 14:30
    re.compile(
        r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})"
        r"(?:\s+(\d{1,2})[:시](\d{1,2})?)?"
    ),
    # 19900315 14:30 (8자리 + 시간)
    re.compile(r"(\d{4})(\d{2})(\d{2})(?:\s+(\d{1,2})[:시](\d{1,2})?)?"),
]


def parse_birth(text: str) -> Optional[tuple[int, int, int, int, int]]:
    """텍스트에서 생년월일시 추출. 못 찾으면 None.
    시·분 없으면 12:00 기본.
    """
    text = text.strip()
    for pat in BIRTH_PATTERNS:
        m = pat.search(text)
        if m:
            try:
                y = int(m.group(1))
                mo = int(m.group(2))
                d = int(m.group(3))
                h = int(m.group(4)) if m.lastindex and m.lastindex >= 4 and m.group(4) else 12
                mi = int(m.group(5)) if m.lastindex and m.lastindex >= 5 and m.group(5) else 0
                if 1900 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 31:
                    return y, mo, d, h, mi
            except (ValueError, IndexError):
                continue
    return None


# ============================================================
# Claude 호출 (server.py 와 동일 로직 — 별도 함수로 분리)
# ============================================================
async def ask_claude_kakao(saju: dict, history: list, question: str) -> str:
    """카카오톡 응답용 Claude 호출. 짧고 핵심만 (1000자 제한)."""
    import os
    import anthropic

    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        return "[서버 설정 오류] 잠시 후 다시 시도해주세요."

    client = anthropic.Anthropic(api_key=api_key)
    saju_context = format_saju_for_claude(saju)

    system_prompt = (
        config.SYSTEM_PROMPT
        + "\n\n[현재 상담자의 사주]\n"
        + saju_context
        + "\n\n[중요] 카카오톡 응답이라 답변은 반드시 800자 이내, "
        "친근한 톤, 이모지 1~2개. 핵심만."
    )

    recent = history[-(config.MAX_TURNS * 2):]
    messages = [{"role": m["role"], "content": m["content"]} for m in recent]
    messages.append({"role": "user", "content": question})

    try:
        msg = client.messages.create(
            model=config.MODEL,
            max_tokens=600,  # 카카오톡 1000자 제한 여유
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=messages,
        )
        return "".join(b.text for b in msg.content if b.type == "text")
    except anthropic.APIError as e:
        return f"[일시 오류] AI 서버 점검 중. 잠시 후 다시. ({type(e).__name__})"
    except Exception as e:
        return f"[오류] {str(e)[:100]}"


# ============================================================
# 엔드포인트 1: 환영 메시지 (친구추가 시)
# ============================================================
@router.post("/welcome")
async def kakao_welcome(request: Request):
    return JSONResponse(
        kakao_simple_text(
            "🔮 안녕하세요! 덕구네 AI 사주 상담사입니다.\n\n"
            "당신의 사주를 풀어드릴게요. "
            "생년월일시를 알려주세요.\n\n"
            "예시:\n"
            "  1990년 3월 15일 14시 30분\n"
            "  1990.03.15 14:30",
            quick_replies=[
                quick_reply("📅 생년월일 입력", "1990년 3월 15일 14시 30분"),
                quick_reply("❓ 사용법", "사용법 알려줘"),
            ],
        )
    )


# ============================================================
# 엔드포인트 2: 사주 계산 + 첫 해석
# ============================================================
@router.post("/saju")
async def kakao_saju(request: Request):
    body = await request.json()
    user_key = body.get("userRequest", {}).get("user", {}).get("id", "anonymous")
    user_text = body.get("userRequest", {}).get("utterance", "").strip()

    init_kakao_table()

    # 생년월일 파싱 시도
    parsed = parse_birth(user_text)
    if not parsed:
        return JSONResponse(
            kakao_simple_text(
                "⚠️ 생년월일을 정확히 입력해주세요.\n\n"
                "예시:\n"
                "  1990년 3월 15일 14시 30분\n"
                "  1990.03.15 14:30\n\n"
                "(시간 모르면 생일만 적어도 OK)",
                quick_replies=[
                    quick_reply("예시로 시도", "1990년 3월 15일 14시 30분"),
                ],
            )
        )

    year, month, day, hour, minute = parsed

    # 사주 계산
    try:
        saju = calculate_saju(year, month, day, hour, minute)
    except Exception as e:
        return JSONResponse(
            kakao_simple_text(f"⚠️ 사주 계산 중 오류: {str(e)[:80]}")
        )

    # SQLite 저장 (user_key 기준)
    save_user_kakao(user_key, year, month, day, hour, minute, saju)

    # Claude 첫 해석
    first_q = "제 사주를 간단히 해석해주시고, 어떤 성향인지 800자 이내로 알려주세요."
    answer = await ask_claude_kakao(saju, [], first_q)

    # 사주 8글자 요약 + Claude 답변
    pillars = [
        f"년주: {saju['year_pillar']['gan_kr']}{saju['year_pillar']['ji_kr']}",
        f"월주: {saju['month_pillar']['gan_kr']}{saju['month_pillar']['ji_kr']}",
        f"일주: {saju['day_pillar']['gan_kr']}{saju['day_pillar']['ji_kr']}",
        f"시주: {saju['hour_pillar']['gan_kr']}{saju['hour_pillar']['ji_kr']}",
    ]
    pillars_text = " · ".join(pillars)

    response_text = (
        f"🔮 당신의 사주\n{pillars_text}\n\n"
        f"━━━━━━━━━━━━━\n"
        f"{answer}\n\n"
        f"━━━━━━━━━━━━━\n"
        f"💬 무엇이든 물어보세요!"
    )

    return JSONResponse(
        kakao_simple_text(
            response_text,
            quick_replies=[
                quick_reply("💕 연애운", "올해 연애운 어때?"),
                quick_reply("💰 재물운", "올해 재물운은?"),
                quick_reply("💼 직장운", "직장 운세 알려줘"),
                quick_reply("🌟 종합운세", "올해 전반적인 운세는?"),
            ],
        )
    )


# ============================================================
# 엔드포인트 3: 후속 질문 (세션 기반)
# ============================================================
@router.post("/chat")
async def kakao_chat(request: Request):
    body = await request.json()
    user_key = body.get("userRequest", {}).get("user", {}).get("id", "anonymous")
    question = body.get("userRequest", {}).get("utterance", "").strip()

    if not question:
        return JSONResponse(
            kakao_simple_text("질문을 입력해주세요.")
        )

    init_kakao_table()
    user = get_user_by_kakao(user_key)

    if not user:
        return JSONResponse(
            kakao_simple_text(
                "❗ 먼저 생년월일을 알려주세요.\n\n"
                "예: 1990년 3월 15일 14시 30분",
                quick_replies=[quick_reply("📅 생년월일", "사주 보기")],
            )
        )

    saju = json.loads(user["saju_json"])

    # 사용 횟수 체크 (server.py 와 동일 로직)
    used = user.get("free_queries_used") or 0
    status = user.get("subscription_status") or "trial"

    if status == "trial" and used >= config.FREE_TRIAL_QUERIES:
        return JSONResponse(
            kakao_simple_text(
                f"🎯 무료 체험 {config.FREE_TRIAL_QUERIES}회를 모두 사용하셨어요.\n\n"
                f"월 {config.PRICE_MONTHLY:,}원으로 무제한 이용하실 수 있습니다!\n\n"
                f"7일 100% 환불 보장 ✅",
                quick_replies=[
                    quick_reply("💳 구독하기", "구독하기"),
                    quick_reply("🌐 웹 사용", "웹사이트 알려줘"),
                ],
            )
        )

    # 대화 히스토리 (간단 버전 — 카카오는 stateless 라서 매번 새 세션)
    history: list[dict] = []
    answer = await ask_claude_kakao(saju, history, question)

    # 사용 횟수 증가
    if status == "trial":
        conn = db_conn()
        try:
            conn.execute(
                "UPDATE users SET free_queries_used = free_queries_used + 1 "
                "WHERE kakao_user_key = ?",
                (user_key,),
            )
            conn.commit()
        finally:
            conn.close()

    remaining = ""
    if status == "trial":
        left = config.FREE_TRIAL_QUERIES - (used + 1)
        if left >= 0:
            remaining = f"\n\n💡 무료 체험 {left}회 남음"

    return JSONResponse(
        kakao_simple_text(
            answer + remaining,
            quick_replies=[
                quick_reply("💕 연애", "연애운"),
                quick_reply("💰 재물", "재물운"),
                quick_reply("💼 직장", "직장운"),
                quick_reply("🌟 종합", "종합운세"),
            ],
        )
    )


# ============================================================
# 엔드포인트 4: 헬스체크 (Kakao 가 webhook 검증 시 사용)
# ============================================================
@router.get("/health")
async def kakao_health():
    return {"status": "ok", "service": "kakao saju bot"}
