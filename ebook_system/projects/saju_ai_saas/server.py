"""
사주 AI SaaS — FastAPI 서버.

엔드포인트:
  GET  /                  — 홈 페이지 (생년월일 입력 폼)
  POST /saju              — 사주 계산 + 첫 해석 반환
  POST /chat              — 이어지는 질문 (세션 기반)
  POST /subscribe         — 유료 구독 시작 (무료 체험 끝난 후)
  GET  /health            — 헬스체크

세션 관리: HMAC 서명 쿠키 (stateless)
DB: SQLite (구독자 정보 + 사용 횟수)

MVP 기능:
  1. 생년월일 입력 → 사주 계산 → Claude 해석
  2. 3회 무료 질문 (체험)
  3. 유료 구독 (Gumroad 링크로 유도)
  4. 구독자는 무제한 질문
"""

import os
import hmac
import hashlib
import secrets
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Cookie, Response, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic

import config
from saju_calc import calculate_saju, format_saju_for_claude


# ============================================================
# 설정
# ============================================================
ROOT = Path(__file__).parent
ANTHROPIC_API_KEY = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
SESSION_SECRET = os.environ.get("SESSION_SECRET") or secrets.token_urlsafe(32)
GUMROAD_SUBSCRIBE_URL = os.environ.get("GUMROAD_SUBSCRIBE_URL", "https://gumroad.com/l/saju-ai")

# Claude 클라이언트
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


# ============================================================
# SQLite DB 초기화
# ============================================================
def init_db():
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            birth_year INTEGER,
            birth_month INTEGER,
            birth_day INTEGER,
            birth_hour INTEGER,
            birth_minute INTEGER,
            saju_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            free_queries_used INTEGER DEFAULT 0,
            subscription_status TEXT DEFAULT 'trial',
            subscription_expires_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def db_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# 세션 관리 (HMAC 서명 쿠키)
# ============================================================
def sign_session(session_id: str) -> str:
    sig = hmac.new(
        SESSION_SECRET.encode(), session_id.encode(), hashlib.sha256
    ).hexdigest()
    return f"{session_id}|{sig}"


def verify_session(token: str) -> Optional[str]:
    if not token or "|" not in token:
        return None
    try:
        sid, sig = token.split("|", 1)
    except ValueError:
        return None
    expected = hmac.new(
        SESSION_SECRET.encode(), sid.encode(), hashlib.sha256
    ).hexdigest()
    return sid if hmac.compare_digest(sig, expected) else None


# ============================================================
# 구독 체크
# ============================================================
def can_ask_question(session_id: str) -> tuple[bool, str]:
    """
    질문할 수 있는지 체크.
    (가능여부, 메시지) 반환.
    """
    conn = db_conn()
    user = conn.execute(
        "SELECT * FROM users WHERE session_id = ?", (session_id,)
    ).fetchone()
    conn.close()

    if not user:
        return False, "먼저 생년월일을 입력해주세요"

    status = user["subscription_status"]

    # 구독자는 무제한
    if status == "active":
        expires = user["subscription_expires_at"]
        if expires:
            exp_dt = datetime.fromisoformat(expires)
            if exp_dt < datetime.now():
                return False, "구독이 만료되었습니다. 재구독해주세요"
        return True, "ok"

    # 체험 사용자: 3회 제한
    used = user["free_queries_used"] or 0
    if used >= config.FREE_TRIAL_QUERIES:
        return (
            False,
            f"무료 체험 {config.FREE_TRIAL_QUERIES}회를 모두 사용하셨습니다. "
            f"월 {config.PRICE_MONTHLY:,}원으로 무제한 이용하세요.",
        )

    return True, f"무료 체험 {config.FREE_TRIAL_QUERIES - used}회 남음"


# ============================================================
# Claude 에 사주 해석 요청
# ============================================================
async def ask_claude(saju: dict, history: list, new_question: str) -> str:
    """
    사주 정보 + 대화 히스토리 + 새 질문을 Claude 에 전달.
    """
    if not client:
        return "[서버 설정 오류] API 키가 없습니다. 잠시 후 다시 시도해주세요."

    # 사주 정보를 시스템 프롬프트 뒤에 추가
    saju_context = format_saju_for_claude(saju)
    system_prompt = config.SYSTEM_PROMPT + "\n\n[현재 상담자의 사주]\n" + saju_context

    # 메시지 구성 (최근 N 턴만)
    recent = history[-(config.MAX_TURNS * 2):]
    messages = [{"role": m["role"], "content": m["content"]} for m in recent]
    messages.append({"role": "user", "content": new_question})

    try:
        msg = client.messages.create(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},  # 사주 컨텍스트 캐싱
                }
            ],
            messages=messages,
        )
        text = "".join(b.text for b in msg.content if b.type == "text")
        return text
    except anthropic.APIError as e:
        return f"[죄송합니다] AI 서버 일시 오류가 발생했습니다. 잠시 후 다시 시도해주세요. ({type(e).__name__})"
    except Exception as e:
        return f"[오류] 예기치 않은 문제가 발생했습니다: {str(e)[:80]}"


# ============================================================
# FastAPI 앱
# ============================================================
app = FastAPI(title="사주 AI SaaS", version="0.1.0")

if config.STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")

# 카카오톡 챗봇 엔드포인트 (kakao_endpoints.py)
try:
    from kakao_endpoints import router as kakao_router
    app.include_router(kakao_router)
    print("[init] 카카오톡 챗봇 endpoint mounted at /kakao/*")
except ImportError as e:
    print(f"[init] 카카오톡 endpoint mount 실패 (무시): {e}")


# import 시점에 DB 초기화 (테스트·운영 모두 작동)
init_db()
print(f"[init] SQLite DB: {config.DB_PATH}")
print(f"[init] Claude: {'OK' if client else 'MISSING KEY'}")
print(f"[init] Model: {config.MODEL}")


@app.get("/", response_class=HTMLResponse)
async def index():
    html = config.STATIC_DIR / "index.html"
    if html.exists():
        return FileResponse(html)
    return HTMLResponse("<h1>index.html 누락</h1>", status_code=500)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "claude": bool(client),
        "model": config.MODEL,
        "product": config.PRODUCT_TITLE,
    }


class SajuRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0


@app.post("/saju")
async def create_saju(req: SajuRequest, response: Response):
    """
    생년월일 입력 → 사주 계산 + 첫 해석 반환 + 세션 쿠키 발급.
    """
    # 입력 검증
    if req.year < 1900 or req.year > 2100:
        raise HTTPException(status_code=400, detail="연도는 1900~2100 사이여야 합니다")
    if not (1 <= req.month <= 12):
        raise HTTPException(status_code=400, detail="월은 1~12 사이여야 합니다")
    if not (1 <= req.day <= 31):
        raise HTTPException(status_code=400, detail="일은 1~31 사이여야 합니다")

    # 사주 계산
    try:
        saju = calculate_saju(req.year, req.month, req.day, req.hour, req.minute)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"사주 계산 오류: {e}")

    # 세션 ID 생성
    session_id = secrets.token_urlsafe(16)
    session_token = sign_session(session_id)

    # DB 저장
    conn = db_conn()
    try:
        conn.execute(
            """INSERT INTO users
            (session_id, birth_year, birth_month, birth_day, birth_hour, birth_minute, saju_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                req.year, req.month, req.day, req.hour, req.minute,
                json.dumps(saju, ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    # Claude 에 첫 해석 요청 (무료 서비스)
    first_question = "제 사주를 간단히 해석해주시고, 제가 어떤 성향의 사람인지 알려주세요."
    answer = await ask_claude(saju, [], first_question)

    # 쿠키 발급
    response.set_cookie(
        key="saju_session",
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 365,  # 1년
        secure=False,  # HTTPS 배포 시 True
    )

    return {
        "saju": saju,
        "first_interpretation": answer,
        "free_queries_remaining": config.FREE_TRIAL_QUERIES,
        "message": f"사주 분석 완료. 지금부터 {config.FREE_TRIAL_QUERIES}회 무료로 질문하실 수 있습니다.",
    }


class ChatRequest(BaseModel):
    question: str


@app.post("/chat")
async def chat(req: ChatRequest, saju_session: Optional[str] = Cookie(None)):
    """
    세션 기반 대화. 사주 정보는 DB 에서 불러옴.
    """
    # 세션 검증
    if not saju_session:
        raise HTTPException(status_code=401, detail="먼저 생년월일을 입력해주세요")
    session_id = verify_session(saju_session)
    if not session_id:
        raise HTTPException(status_code=401, detail="세션이 만료되었습니다")

    # 질문 가능 여부
    can_ask, msg = can_ask_question(session_id)
    if not can_ask:
        raise HTTPException(
            status_code=402,
            detail={
                "message": msg,
                "subscribe_url": GUMROAD_SUBSCRIBE_URL,
                "price": config.PRICE_MONTHLY,
            },
        )

    # 사주 + 대화 히스토리 로드
    conn = db_conn()
    user = conn.execute(
        "SELECT * FROM users WHERE session_id = ?", (session_id,)
    ).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="사용자 정보 없음")

    saju = json.loads(user["saju_json"])

    # 최근 대화 N 턴
    rows = conn.execute(
        "SELECT question, answer FROM queries WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, config.MAX_TURNS),
    ).fetchall()
    history = []
    for row in reversed(rows):
        history.append({"role": "user", "content": row["question"]})
        history.append({"role": "assistant", "content": row["answer"]})

    # Claude 호출
    answer = await ask_claude(saju, history, req.question)

    # 저장 + 사용 횟수 증가
    conn.execute(
        "INSERT INTO queries (session_id, question, answer) VALUES (?, ?, ?)",
        (session_id, req.question, answer),
    )
    if user["subscription_status"] == "trial":
        conn.execute(
            "UPDATE users SET free_queries_used = free_queries_used + 1 WHERE session_id = ?",
            (session_id,),
        )
    conn.commit()
    conn.close()

    # 업데이트된 남은 횟수 가져오기
    conn = db_conn()
    user = conn.execute(
        "SELECT free_queries_used, subscription_status FROM users WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    conn.close()

    remaining = (
        config.FREE_TRIAL_QUERIES - (user["free_queries_used"] or 0)
        if user["subscription_status"] == "trial"
        else None
    )

    return {
        "answer": answer,
        "free_queries_remaining": remaining,
        "is_subscriber": user["subscription_status"] == "active",
    }


@app.get("/subscribe-info")
async def subscribe_info():
    """구독 정보 반환 (UI 에서 결제 버튼 만들 때)."""
    return {
        "monthly_price": config.PRICE_MONTHLY,
        "yearly_price": config.PRICE_YEARLY,
        "lifetime_price": config.PRICE_LIFETIME,
        "gumroad_url": GUMROAD_SUBSCRIBE_URL,
        "features": [
            "무제한 사주 질문",
            "매일 운세 푸시 알림",
            "사주 8글자 상세 해석",
            "연애·재물·건강·직장 전문 상담",
            "대화 내역 평생 보관",
        ],
    }


# ============================================================
# 로컬 실행
# ============================================================
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print(f"[start] 포트 {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
