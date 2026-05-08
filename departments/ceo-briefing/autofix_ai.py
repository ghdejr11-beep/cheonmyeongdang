#!/usr/bin/env python3
"""
AI autofix — 매칭 안 된 TODO를 Claude Haiku 로 분석/초안 작성.

예산 관리:
  MONTH_BUDGET_USD (기본 $10) 초과하면 스킵.
  사용량은 autofix_budget.json 에 누적.
  80% 도달 시 텔레그램 경고 (다음 브리핑에서).

절대 자동 실행하지 않음:
  - 생성한 코드는 ai_drafts/{date}_{slug}.md 로만 저장
  - git commit / npm install / DB 수정 등 실제 반영은 사용자 검토 후

사용:
    from autofix_ai import ai_process_todo, budget_state
    r = ai_process_todo(dept="media", text="실제 Vercel Analytics API 연동")
    # r = {"ok": True, "action": "code_draft", "path": "...", "cost_usd": 0.003}
"""
import os
import json
import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
DRAFTS_DIR = BASE / "ai_drafts"
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
BUDGET_FILE = BASE / "autofix_budget.json"
SECRETS = Path(r"D:\cheonmyeongdang\.secrets")

# 모델 (저렴+빠름)
MODEL = "claude-haiku-4-5-20251001"
# Haiku 4.5 공식 가격: $1/MTok input, $5/MTok output (2025-10 발표)
PRICE_INPUT_PER_MTOK = 1.0
PRICE_OUTPUT_PER_MTOK = 5.0

MONTH_BUDGET_USD = float(os.environ.get("AUTOFIX_MONTH_BUDGET_USD", "10.0"))
MAX_PER_CALL_USD = 0.10  # 단일 호출 최대 비용 (안전장치)


def _load_key():
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip()
    return None


def _load_budget():
    if not BUDGET_FILE.exists():
        return {"month": datetime.date.today().strftime("%Y-%m"), "spent_usd": 0.0, "calls": 0, "history": []}
    d = json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
    this_month = datetime.date.today().strftime("%Y-%m")
    if d.get("month") != this_month:
        # 월 바뀌면 리셋
        d = {"month": this_month, "spent_usd": 0.0, "calls": 0, "history": []}
    return d


def _save_budget(d):
    BUDGET_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def budget_state():
    """현재 이번 달 사용량 요약."""
    d = _load_budget()
    return {
        "month": d["month"],
        "spent_usd": round(d["spent_usd"], 4),
        "remaining_usd": round(MONTH_BUDGET_USD - d["spent_usd"], 4),
        "budget_usd": MONTH_BUDGET_USD,
        "calls": d["calls"],
        "utilization_pct": round(100 * d["spent_usd"] / MONTH_BUDGET_USD, 1),
    }


def _estimate_cost(in_tokens, out_tokens):
    return (in_tokens / 1_000_000) * PRICE_INPUT_PER_MTOK + (out_tokens / 1_000_000) * PRICE_OUTPUT_PER_MTOK


def ai_process_todo(dept: str, text: str, context: str = "") -> dict:
    """TODO 한 개를 Claude Haiku 로 분석/초안 작성.
    반환: {ok, action, path?, summary?, cost_usd, reason?}
    """
    state = _load_budget()
    if state["spent_usd"] >= MONTH_BUDGET_USD:
        return {"ok": False, "reason": f"월 예산 ${MONTH_BUDGET_USD} 소진", "cost_usd": 0}

    key = _load_key()
    if not key:
        return {"ok": False, "reason": "ANTHROPIC_API_KEY 없음", "cost_usd": 0}

    try:
        import anthropic
    except ImportError:
        return {"ok": False, "reason": "anthropic SDK 미설치", "cost_usd": 0}

    client = anthropic.Anthropic(api_key=key)

    system = (
        "당신은 쿤스튜디오 1인 AI 스튜디오의 자동 처리 엔진입니다. "
        "부서별 TODO 항목을 분석해서 다음 중 하나로 분류하고 결과를 JSON으로만 반환하세요:\n"
        "1. action='code_draft' — 코드 초안 작성 가능한 경우. code 필드에 Python/JS 코드 포함 (80줄 이내)\n"
        "2. action='research_note' — 리서치/설계 필요. note 필드에 300자 이내 조사 결과\n"
        "3. action='user_only' — 사용자 본인인증/결제/외부 콘솔 로그인 필수\n"
        "4. action='skip' — 이미 해결됐거나 불명확해서 처리 불필요\n\n"
        "응답 형식 (JSON만, 마크다운 코드블록 X):\n"
        '{"action": "...", "summary": "한국어 50자 이내", "code"?: "...", "note"?: "...", "user_action"?: "..."}'
    )
    user = f"부서: {dept}\nTODO: {text}\n컨텍스트: {context or '(없음)'}"

    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    except Exception as e:
        return {"ok": False, "reason": f"API 오류: {str(e)[:100]}", "cost_usd": 0}

    in_tok = msg.usage.input_tokens
    out_tok = msg.usage.output_tokens
    cost = _estimate_cost(in_tok, out_tok)

    if cost > MAX_PER_CALL_USD:
        # 안전장치 (비정상 토큰)
        return {"ok": False, "reason": f"호출 비용 ${cost:.4f} > 상한 ${MAX_PER_CALL_USD}", "cost_usd": cost}

    # 응답 파싱
    raw = msg.content[0].text.strip()
    # JSON 파싱 (마크다운 래퍼 제거)
    if raw.startswith("```"):
        raw = raw.strip("`").split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw[:-3]
    try:
        parsed = json.loads(raw)
    except Exception as e:
        # 파싱 실패 → note로 저장
        parsed = {"action": "research_note", "summary": "파싱실패", "note": raw[:500]}

    # draft 파일 저장
    out = {"ok": True, "action": parsed.get("action", "skip"),
           "summary": parsed.get("summary", ""), "cost_usd": round(cost, 6),
           "in_tok": in_tok, "out_tok": out_tok}

    if parsed.get("action") in ("code_draft", "research_note"):
        today = datetime.date.today().isoformat()
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in (dept + "_" + text[:40]))[:80]
        fname = DRAFTS_DIR / f"{today}_{slug}.md"
        body = f"# {dept}: {text}\n\n"
        body += f"**생성**: {datetime.datetime.now():%Y-%m-%d %H:%M} | **비용**: ${cost:.4f}\n\n"
        body += f"**요약**: {parsed.get('summary','')}\n\n"
        if parsed.get("code"):
            body += "## 코드 초안\n```python\n" + parsed["code"] + "\n```\n\n"
        if parsed.get("note"):
            body += "## 메모\n" + parsed["note"] + "\n"
        fname.write_text(body, encoding="utf-8")
        out["path"] = str(fname)

    if parsed.get("action") == "user_only":
        out["user_action"] = parsed.get("user_action", "")

    # 예산 갱신
    state["spent_usd"] += cost
    state["calls"] += 1
    state["history"].append({
        "at": datetime.datetime.now().isoformat(),
        "dept": dept, "text": text[:80],
        "action": out["action"], "cost_usd": round(cost, 6),
    })
    state["history"] = state["history"][-200:]  # 최근 200건만
    _save_budget(state)
    return out


if __name__ == "__main__":
    # 단독 테스트
    r = ai_process_todo(
        dept="intelligence",
        text="실제 Vercel Analytics API 연동",
        context="sales_collector.py:109",
    )
    print(json.dumps(r, ensure_ascii=False, indent=2))
    print("\n현재 예산:", json.dumps(budget_state(), ensure_ascii=False, indent=2))
