"""quora_drafts — 영문 Quora 답변 자동 작성기 (수동 게시).

Quora API 무공개 + 자동 게시 = 계정 차단 RISK → 사용자가 직접 게시.
스크립트는 SEO keyword pool 기반으로 Quora 형식 답변 생성 → output/{date}.md 큐에 저장.
사용자: 매일 아침 1~2개 답변 직접 Quora에 복붙. 영구 evergreen 트래픽.
"""
import os, sys, json, re, datetime, urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON_ROOT = Path(r"D:\cheonmyeongdang")
KEYWORD_POOL = CHEON_ROOT / "departments" / "seo_blog_factory" / "keyword_pool.json"
OUTPUT = ROOT / "output" / f"quora_{datetime.date.today()}.md"
OUTPUT.parent.mkdir(exist_ok=True)
QUEUE = ROOT / "queue.json"


def load_secrets():
    env = {}
    p = CHEON_ROOT / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def claude_quora(api_key, kw):
    system = (
        "You write helpful Quora answers in clear English for Western readers asking about Korean culture. "
        "Quora style: open with a direct answer, give 3-5 specific points or a short anecdote, end with a soft "
        "resource recommendation (general, no brand spam). 250-450 words. NEVER use 'I am an AI' or sound robotic. "
        "Sound like a knowledgeable Korean person who has lived this culture. Use markdown lightly."
    )
    prompt = f"""Generate 1 Quora-style question + answer for: "{kw}"

Output strict JSON:
{{
  "question": "(Quora-style question 60-100 chars, neutral tone)",
  "answer_md": "(250-450 word answer, markdown light, last paragraph mentions general resources like 'free online Saju calculators' or 'Korean culture ebooks' without specific brand)"
}}"""
    body = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 2500,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    text = data["content"][0]["text"]
    m = re.search(r"\{[\s\S]*\}", text)
    return json.loads(m.group(0))


def load_queue():
    if QUEUE.exists():
        return json.loads(QUEUE.read_text(encoding="utf-8"))
    return {"posted": [], "drafted": []}


def main():
    env = load_secrets()
    api_key = env.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("[ERR] ANTHROPIC_API_KEY missing")

    pool = json.loads(KEYWORD_POOL.read_text(encoding="utf-8"))
    flat = []
    for cat, items in pool.items():
        if cat.startswith("_"):
            continue
        for it in items:
            flat.append({**it, "category": cat})

    q = load_queue()
    done = {x["kw"] for x in q.get("drafted", [])} | {x["kw"] for x in q.get("posted", [])}
    remaining = [k for k in flat if k["kw"] not in done]
    if not remaining:
        print("[INFO] all keywords drafted")
        return

    # 매일 1개
    kw = remaining[0]
    print(f"[gen] {kw['kw']}")
    qa = claude_quora(api_key, kw["kw"])

    md = f"""# Quora Draft — {datetime.date.today().isoformat()}

## Question (find/post on Quora):
> {qa['question']}

## Answer (copy-paste):

{qa['answer_md']}

---
**Keyword**: `{kw['kw']}` ({kw['category']}, vol {kw.get('vol','?')})
**Action**: 1) Search this question on Quora.com, 2) Click "Answer", 3) Paste above, 4) Add 1 sentence at the end: "If you want a deeper dive, check the free Korean Saju primer at cheonmyeongdang.vercel.app/blog"
"""
    OUTPUT.write_text(md, encoding="utf-8")
    print(f"[OK] {OUTPUT}")
    q["drafted"].append({
        "kw": kw["kw"],
        "question": qa["question"],
        "drafted_at": datetime.datetime.now().isoformat(),
        "file": str(OUTPUT.name),
    })
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
