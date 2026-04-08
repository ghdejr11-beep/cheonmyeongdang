"""
AI 멘토봇 — PREMIUM 구매자 전용 챗봇 서버.

아키텍처:
1. 고객이 Gumroad 에서 PREMIUM 구매 → Gumroad 가 라이선스 키 자동 발급 (Gumroad 내장 기능)
2. 고객이 멘토봇 URL 접속 → 라이선스 키 입력
3. 서버가 Gumroad API 로 키 검증 → 유효하면 세션 쿠키 발급
4. 고객이 질문 → 서버가 책 내용을 컨텍스트로 Claude API 호출 → 답변 반환

사용자(책 저자)가 할 일: 0%
  - Gumroad 에서 "라이선스 키 활성화" 체크박스 ON (1회, 1분)
  - 이 서버를 Render.com 에 배포 (1회, 5분)
  - 환경변수 2개 설정 (ANTHROPIC_API_KEY, GUMROAD_PRODUCT_ID)

이후 모든 고객 등록·인증·답변이 100% 자동.
"""

import os
import hmac
import hashlib
import secrets
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Cookie, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic

# ============================================================
# 설정
# ============================================================
ROOT = Path(__file__).parent
BOOK_PATH = ROOT / "book.md"
STATIC_DIR = ROOT / "static"

ANTHROPIC_API_KEY = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
GUMROAD_PRODUCT_ID = (os.environ.get("GUMROAD_PRODUCT_ID") or "").strip()
SESSION_SECRET = os.environ.get("SESSION_SECRET") or secrets.token_urlsafe(32)
MODEL = os.environ.get("MENTOR_MODEL", "claude-haiku-4-5")
MAX_TURNS = 10  # 유지할 대화 턴 수 (user+assistant 쌍 기준)

# ============================================================
# 책 내용 로드 (프롬프트 캐싱용)
# ============================================================
if BOOK_PATH.exists():
    BOOK_CONTENT = BOOK_PATH.read_text(encoding="utf-8")
    print(f"[init] 책 로드 완료: {len(BOOK_CONTENT):,} 자")
else:
    BOOK_CONTENT = "[책 내용 없음 — book.md 파일이 서버에 없습니다. prepare_book.py 실행 필요]"
    print(f"[init] 경고: {BOOK_PATH} 없음")

SYSTEM_PROMPT = f"""너는 "AI 부업 시스템" 전자책의 공식 AI 멘토다.
책을 구매한 독자의 질문에 책 내용을 근거로 구체적이고 실전적으로 답변한다.

[답변 원칙]
1. 책에 있는 내용을 최우선 근거로 사용. 책에 없으면 "책에는 직접 다루지 않지만..." 하고 일반 지식으로 보완.
2. 친근하지만 전문적. "~합니다" 체.
3. 추상론 금지. 즉시 실행 가능한 단계별 방법 제시.
4. 프롬프트 예시가 필요하면 코드 블록으로 보여줌.
5. 답변 끝에 "📖 책 챕터 X 에서 더 자세히 볼 수 있습니다" 식으로 챕터 안내.
6. 한국어로만 답변.
7. 답변 길이: 200~600자 정도. 간단한 질문엔 짧게.
8. 광고·다른 상품 언급 금지. 오직 이 책 내용에만 집중.

[책 전체 내용]
{BOOK_CONTENT}
"""

# ============================================================
# Claude 클라이언트
# ============================================================
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


# ============================================================
# 세션 관리 (stateless signed cookie)
# ============================================================
def sign_session(license_key: str) -> str:
    sig = hmac.new(
        SESSION_SECRET.encode(),
        license_key.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{license_key}|{sig}"


def verify_session(token: str) -> Optional[str]:
    try:
        key, sig = token.split("|", 1)
    except ValueError:
        return None
    expected = hmac.new(
        SESSION_SECRET.encode(),
        key.encode(),
        hashlib.sha256,
    ).hexdigest()
    return key if hmac.compare_digest(sig, expected) else None


# ============================================================
# Gumroad 라이선스 검증
# ============================================================
async def verify_gumroad_license(license_key: str) -> bool:
    """Gumroad API 로 라이선스 키 유효성 확인.
    문서: https://help.gumroad.com/article/76-license-keys
    """
    if not GUMROAD_PRODUCT_ID:
        print("[warn] GUMROAD_PRODUCT_ID 미설정")
        return False
    try:
        async with httpx.AsyncClient(timeout=10) as http:
            r = await http.post(
                "https://api.gumroad.com/v2/licenses/verify",
                data={
                    "product_id": GUMROAD_PRODUCT_ID,
                    "license_key": license_key,
                    # 검증만, 사용 횟수 증가 안 함 (사용자가 계속 접속할 수 있게)
                    "increment_uses_count": "false",
                },
            )
        if r.status_code != 200:
            return False
        data = r.json()
        if not data.get("success", False):
            return False
        # 환불된 구매는 거부
        purchase = data.get("purchase", {})
        if purchase.get("refunded") or purchase.get("chargebacked"):
            return False
        return True
    except Exception as e:
        print(f"[error] Gumroad 검증 실패: {e}")
        return False


# ============================================================
# FastAPI 앱
# ============================================================
app = FastAPI(title="AI 멘토봇", version="1.0.0")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse("<h1>index.html 파일이 없습니다</h1>", status_code=500)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "book_loaded": len(BOOK_CONTENT) > 500,
        "book_size": len(BOOK_CONTENT),
        "gumroad_configured": bool(GUMROAD_PRODUCT_ID),
        "claude_configured": bool(client),
        "model": MODEL,
    }


class VerifyRequest(BaseModel):
    license_key: str


@app.post("/verify")
async def verify(req: VerifyRequest, response: Response):
    """라이선스 키 검증 → 세션 쿠키 발급"""
    key = req.license_key.strip()
    if not key or len(key) < 8:
        raise HTTPException(status_code=400, detail="유효하지 않은 라이선스 키입니다")

    ok = await verify_gumroad_license(key)
    if not ok:
        raise HTTPException(
            status_code=401,
            detail="라이선스 키가 유효하지 않거나 환불된 구매입니다. 구매 확인 이메일에서 키를 확인하세요.",
        )

    session_token = sign_session(key)
    response.set_cookie(
        key="mentor_session",
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 365,  # 1년
        secure=True,
    )
    return {"success": True, "message": "인증 성공. 이제 질문하실 수 있습니다."}


@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie("mentor_session")
    return {"success": True}


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


@app.post("/chat")
async def chat(req: ChatRequest, mentor_session: Optional[str] = Cookie(None)):
    """책 내용을 컨텍스트로 Claude API 호출"""
    if not mentor_session:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")

    license_key = verify_session(mentor_session)
    if not license_key:
        raise HTTPException(status_code=401, detail="세션이 만료되었습니다. 다시 로그인해주세요.")

    if not client:
        raise HTTPException(status_code=500, detail="서버에 API 키가 설정되지 않았습니다")

    if not req.messages:
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다")

    # 최근 MAX_TURNS 턴만 유지 (컨텍스트 절약)
    recent = req.messages[-(MAX_TURNS * 2):]
    messages = [{"role": m.role, "content": m.content} for m in recent]

    # 마지막 메시지가 user 여야 함
    if messages[-1]["role"] != "user":
        raise HTTPException(status_code=400, detail="마지막 메시지는 user 여야 합니다")

    try:
        # 프롬프트 캐싱으로 책 내용 재전송 비용 90% 절감
        msg = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=messages,
        )
        text = "".join(b.text for b in msg.content if b.type == "text")
        return {
            "response": text,
            "usage": {
                "input_tokens": msg.usage.input_tokens,
                "output_tokens": msg.usage.output_tokens,
                "cache_read_tokens": getattr(msg.usage, "cache_read_input_tokens", 0) or 0,
                "cache_creation_tokens": getattr(msg.usage, "cache_creation_input_tokens", 0) or 0,
            },
        }
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="요청이 너무 많습니다. 잠시 후 다시 시도해주세요.")
    except anthropic.APIError as e:
        print(f"[error] Claude API: {e}")
        raise HTTPException(status_code=500, detail=f"AI 서버 오류가 발생했습니다")


# ============================================================
# 로컬 실행용
# ============================================================
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print(f"[start] 포트 {port} 에서 서버 시작")
    print(f"[start] Claude: {'OK' if client else 'MISSING KEY'}")
    print(f"[start] Gumroad Product ID: {'SET' if GUMROAD_PRODUCT_ID else 'MISSING'}")
    uvicorn.run(app, host="0.0.0.0", port=port)
