"""Anthropic Batch API helper — 50% off for non-real-time work.

Anthropic Batch API:
- POST /v1/messages/batches with N requests (up to 100K)
- Returns batch_id, polled async
- Results returned as .jsonl file URL
- 50% discount on input + output tokens
- Up to 24h to complete (usually <1h for small batches)

Use cases for KunStudio:
- 500 Korean names/week (instead of 50/day)
- 27 KDP book metadata seasonal refresh
- 100 Pinterest pin descriptions/week
- Hashnode 50-post backfill

DO NOT use for: real-time content (SEO blog factory daily, TikTok captions, Quora drafts)
since those need <2min latency.
"""
import os, sys, json, urllib.request, urllib.error, time, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON = Path(r"D:\cheonmyeongdang")
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)


def log(msg, batch_name="default"):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    log_file = LOG_DIR / f"batch_{batch_name}_{datetime.date.today()}.log"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_secrets():
    env = {}
    p = CHEON / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def submit_batch(api_key, requests_list):
    """POST /v1/messages/batches.

    requests_list: [
      {
        "custom_id": "name-001",
        "params": {
          "model": "claude-sonnet-4-6",
          "max_tokens": 1024,
          "messages": [...]
        }
      },
      ...
    ]
    """
    body = json.dumps({"requests": requests_list}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages/batches",
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def poll_batch(api_key, batch_id, max_wait_sec=3600, poll_interval=30):
    """Poll until batch is ended (succeeded/failed/canceled/expired)."""
    end = time.time() + max_wait_sec
    while time.time() < end:
        req = urllib.request.Request(
            f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            status = json.loads(r.read())
        log(f"  poll: status={status.get('processing_status')} done={status.get('request_counts', {}).get('succeeded', 0)}/{sum(status.get('request_counts', {}).values()) if status.get('request_counts') else '?'}")
        if status.get("processing_status") == "ended":
            return status
        time.sleep(poll_interval)
    raise TimeoutError(f"batch {batch_id} not ended within {max_wait_sec}s")


def fetch_results(api_key, results_url):
    """GET the results .jsonl file (signed URL)."""
    req = urllib.request.Request(
        results_url,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read().decode("utf-8")


def parse_jsonl_results(jsonl_text):
    """Each line is one custom_id's result."""
    results = {}
    for line in jsonl_text.splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            cid = obj.get("custom_id")
            r = obj.get("result", {})
            if r.get("type") == "succeeded":
                msg = r.get("message", {})
                content = msg.get("content", [{}])[0].get("text", "")
                results[cid] = {"ok": True, "text": content, "usage": msg.get("usage")}
            else:
                results[cid] = {"ok": False, "error": r}
        except Exception as e:
            results[f"_parse_error_{len(results)}"] = {"ok": False, "error": str(e), "raw": line[:200]}
    return results


# ─── Convenience: high-level run ──────────────────────────────────────────
def run_batch(requests_list, batch_name="default", max_wait=3600):
    """Submit + poll + fetch + parse in one call. Returns dict[custom_id -> result]."""
    secrets = load_secrets()
    api_key = secrets.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY missing in .secrets")

    log(f"submitting batch with {len(requests_list)} requests...", batch_name)
    submit_resp = submit_batch(api_key, requests_list)
    batch_id = submit_resp["id"]
    log(f"batch_id={batch_id} status={submit_resp.get('processing_status')}", batch_name)

    log(f"polling batch (max {max_wait}s)...", batch_name)
    final_status = poll_batch(api_key, batch_id, max_wait_sec=max_wait)

    results_url = final_status.get("results_url")
    if not results_url:
        raise RuntimeError(f"no results_url: {final_status}")

    log(f"fetching results from {results_url[:80]}...", batch_name)
    jsonl = fetch_results(api_key, results_url)

    parsed = parse_jsonl_results(jsonl)
    succeeded = sum(1 for r in parsed.values() if r.get("ok"))
    log(f"[done] {succeeded}/{len(requests_list)} succeeded. ~50% cheaper than realtime API.", batch_name)
    return parsed


if __name__ == "__main__":
    # Smoke test: 3 simple Korean greetings
    sample = [
        {
            "custom_id": f"greet-{i}",
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 200,
                "messages": [{"role": "user", "content": f"Translate '{kw}' to natural Korean. Output JSON: {{\"ko\":\"...\"}}"}],
            },
        }
        for i, kw in enumerate(["good morning", "thank you", "see you tomorrow"])
    ]
    print("[+] Smoke test: 3 greetings via Batch API (50% off)")
    results = run_batch(sample, batch_name="smoketest", max_wait=600)
    for cid, r in results.items():
        print(f"  {cid}: {r.get('text', r.get('error'))[:100] if r.get('ok') else r.get('error')}")
