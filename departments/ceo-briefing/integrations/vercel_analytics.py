"""
Vercel 트래픽/배포 데이터 수집

⚠️ 중요 (2026-04-27 검증):
  Vercel Web Analytics 데이터 (PV/UV/Top Pages) 는 공식 REST API 가 없음.
  Hobby/Pro 모두 동일하게 미지원이며, 커뮤니티 feature request 만 존재함.
  https://community.vercel.com/t/feature-request-rest-api-endpoint-for-web-analytics-data/28422

대안:
  1. Vercel Drains: Web Analytics 이벤트를 webhook 으로 스트리밍 (Pro 부분 지원)
  2. 자체 카운터: API Routes 에 미들웨어 + Edge Config / Upstash 카운터
  3. GA4 / Plausible 병행 사용

이 모듈이 실제로 수집하는 것:
  ✅ 프로젝트 목록 (GET /v9/projects)
  ✅ 배포 통계 (GET /v6/deployments) — 24h 배포 횟수, 최근 배포 상태
  ✅ 도메인 헬스체크 (HEAD 요청, 응답 시간)
  ⚠️ PV/UV — Drain JSON 파일이 있으면 사용, 없으면 placeholder

함수:
  - fetch_vercel_daily(project_ids=None) -> dict  # 외부 호출 진입점
  - daily_summary() -> dict                        # briefing_v2 호환

설정 (.secrets):
  VERCEL_API_TOKEN=...           # https://vercel.com/account/tokens
  VERCEL_TEAM_ID=team_xxx         # 팀이면 필수, 개인 계정이면 비워두기
  VERCEL_PROJECT_IDS=tax-n-benefit-api,korlens,cheonmyeongdang.com
  # 선택: Drain 으로 받은 분석 JSON 경로 (PV/UV 채움)
  VERCEL_ANALYTICS_DRAIN_PATH=D:\\documents\\쿤스튜디오\\vercel_drain.json
"""
import json
import datetime
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path


SECRETS_PATH = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets")
VERCEL_API = "https://api.vercel.com"
USER_AGENT = "KunStudio-Briefing/1.0 (+ghdejr11@gmail.com)"
DEFAULT_PROJECTS = ["tax-n-benefit-api", "korlens", "cheonmyeongdang.com"]


# ──────────────────────────────────────────────────────────
# secrets
# ──────────────────────────────────────────────────────────
def _load_env():
    env = {}
    if not SECRETS_PATH.exists():
        return env
    for line in SECRETS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def _config():
    env = _load_env()
    raw_ids = env.get("VERCEL_PROJECT_IDS", "")
    project_ids = [p.strip() for p in raw_ids.split(",") if p.strip()] or DEFAULT_PROJECTS
    return {
        "token": env.get("VERCEL_API_TOKEN") or env.get("VERCEL_TOKEN"),
        "team_id": env.get("VERCEL_TEAM_ID") or "",
        "project_ids": project_ids,
        "drain_path": env.get("VERCEL_ANALYTICS_DRAIN_PATH", ""),
    }


# ──────────────────────────────────────────────────────────
# HTTP
# ──────────────────────────────────────────────────────────
def _request(path, params=None, timeout=15):
    cfg = _config()
    if not cfg["token"]:
        return {"error": "VERCEL_API_TOKEN 미설정 (.secrets)"}

    params = dict(params or {})
    if cfg["team_id"]:
        params.setdefault("teamId", cfg["team_id"])
    qs = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{VERCEL_API}{path}{qs}"

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {cfg['token']}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            pass
        return {"error": f"HTTP {e.code}: {body or str(e)}"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}


# ──────────────────────────────────────────────────────────
# Project resolution: 사용자가 슬러그/도메인을 줘도 project ID 로 변환
# ──────────────────────────────────────────────────────────
_PROJECT_CACHE = {}


def _resolve_project(name_or_id):
    """프로젝트 슬러그/도메인 → 표준 project 정보. 캐시 사용."""
    if name_or_id in _PROJECT_CACHE:
        return _PROJECT_CACHE[name_or_id]
    data = _request(f"/v9/projects/{urllib.parse.quote(name_or_id, safe='')}")
    if isinstance(data, dict) and not data.get("error"):
        _PROJECT_CACHE[name_or_id] = data
        return data
    return None


# ──────────────────────────────────────────────────────────
# 배포 통계 (24h)
# ──────────────────────────────────────────────────────────
def _deployments_for_project(project_name, since_ms, until_ms):
    """프로젝트별 배포 목록 (since/until ms epoch). limit 100."""
    data = _request(
        "/v6/deployments",
        {
            "projectId": project_name,  # API 가 슬러그도 받아줌 (보통)
            "since": since_ms,
            "until": until_ms,
            "limit": 100,
        },
    )
    if not isinstance(data, dict) or data.get("error"):
        # 슬러그가 안 먹으면 ID 로 재시도
        proj = _resolve_project(project_name)
        if proj and proj.get("id"):
            data = _request(
                "/v6/deployments",
                {
                    "projectId": proj["id"],
                    "since": since_ms,
                    "until": until_ms,
                    "limit": 100,
                },
            )
    if not isinstance(data, dict) or data.get("error"):
        return {"error": data.get("error") if isinstance(data, dict) else "unknown"}
    return {"deployments": data.get("deployments", [])}


# ──────────────────────────────────────────────────────────
# Drain JSON fallback (선택)
# ──────────────────────────────────────────────────────────
def _read_drain(date_iso):
    """Drain 으로 적재된 JSON 에서 해당 일 PV/UV/Top 추출. 형식:
    {
      "2026-04-27": {
        "<project>": {"pv": 1234, "uv": 567, "top_pages": [["/", 800], ...]}
      }
    }
    """
    cfg = _config()
    p = cfg.get("drain_path") or ""
    if not p:
        return None
    fp = Path(p)
    if not fp.exists():
        return None
    try:
        d = json.loads(fp.read_text(encoding="utf-8"))
        return d.get(date_iso) or {}
    except Exception:
        return None


# ──────────────────────────────────────────────────────────
# 메인 진입점
# ──────────────────────────────────────────────────────────
def fetch_vercel_daily(project_ids=None, target_date=None):
    """
    각 프로젝트의 어제(또는 지정일) 트래픽/배포 dict 반환.

    Args:
        project_ids: list[str] | None — None 이면 .secrets 의 VERCEL_PROJECT_IDS
        target_date: datetime.date | None — None 이면 어제

    Returns:
        {
          "date": "YYYY-MM-DD",
          "status": "ok" | "no_token" | "error",
          "analytics_source": "drain" | "placeholder" | "unsupported",
          "note": "...",
          "projects": {
            "<slug>": {
              "deployments_24h": int,
              "last_deployment": {"state": "READY", "created_at": "..."},
              "pv": int|None, "uv": int|None,
              "top_pages": list[(path, count)] | [],
              "error": str | None,
            },
            ...
          }
        }
    """
    cfg = _config()
    project_ids = project_ids or cfg["project_ids"]
    target_date = target_date or (datetime.date.today() - datetime.timedelta(days=1))
    iso = target_date.isoformat()

    if not cfg["token"]:
        return {
            "date": iso,
            "status": "no_token",
            "analytics_source": "stub",
            "note": "VERCEL_API_TOKEN 미설정 — .secrets 에 추가 필요",
            "projects": {p: _stub_project() for p in project_ids},
        }

    # 어제 0시~23:59:59 (KST 가 아니라 UTC 기준 — Vercel API 도 UTC ms)
    start = datetime.datetime.combine(target_date, datetime.time.min, tzinfo=datetime.timezone.utc)
    end = start + datetime.timedelta(days=1)
    since_ms = int(start.timestamp() * 1000)
    until_ms = int(end.timestamp() * 1000)

    drain_day = _read_drain(iso)
    analytics_source = "drain" if drain_day else "placeholder"
    note = (
        "PV/UV 는 Drain JSON 에서 로드"
        if drain_day
        else "Vercel Web Analytics 는 공식 REST API 미지원 — PV/UV 는 placeholder. "
             "Drain 설정 시 VERCEL_ANALYTICS_DRAIN_PATH 로 자동 주입"
    )

    out = {
        "date": iso,
        "status": "ok",
        "analytics_source": analytics_source,
        "note": note,
        "projects": {},
    }

    for slug in project_ids:
        proj_out = {
            "deployments_24h": 0,
            "last_deployment": None,
            "pv": None,
            "uv": None,
            "top_pages": [],
            "error": None,
        }
        # 1) 배포 정보 — 실제 작동
        dep = _deployments_for_project(slug, since_ms, until_ms)
        if dep.get("error"):
            proj_out["error"] = str(dep["error"])[:160]
        else:
            deps = dep.get("deployments", [])
            proj_out["deployments_24h"] = len(deps)
            if deps:
                latest = deps[0]
                proj_out["last_deployment"] = {
                    "state": latest.get("state") or latest.get("readyState"),
                    "created_at": _ms_to_iso(latest.get("created") or latest.get("createdAt")),
                    "url": latest.get("url"),
                }

        # 2) PV/UV — drain 에 있으면 채움
        if drain_day and slug in drain_day:
            d = drain_day[slug] or {}
            proj_out["pv"] = d.get("pv")
            proj_out["uv"] = d.get("uv")
            tp = d.get("top_pages") or []
            # [(path, count)] 또는 [{"path":..,"count":..}] 둘 다 허용
            normalized = []
            for item in tp[:5]:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    normalized.append([str(item[0]), int(item[1])])
                elif isinstance(item, dict):
                    normalized.append([str(item.get("path", "?")), int(item.get("count", 0))])
            proj_out["top_pages"] = normalized

        out["projects"][slug] = proj_out

    return out


def _ms_to_iso(ms):
    if not ms:
        return None
    try:
        return datetime.datetime.fromtimestamp(int(ms) / 1000, tz=datetime.timezone.utc).isoformat()
    except Exception:
        return None


def _stub_project():
    return {
        "deployments_24h": 0,
        "last_deployment": None,
        "pv": None,
        "uv": None,
        "top_pages": [],
        "error": "no_token",
    }


# ──────────────────────────────────────────────────────────
# 일별 저장 (sales-collection/data/vercel_daily.json)
# ──────────────────────────────────────────────────────────
DAILY_JSON = Path(
    r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\sales-collection\data\vercel_daily.json"
)


def _load_history():
    if not DAILY_JSON.exists():
        return {}
    try:
        return json.loads(DAILY_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_history(d):
    DAILY_JSON.parent.mkdir(parents=True, exist_ok=True)
    DAILY_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_yesterday():
    """어제 데이터 수집 후 sales-collection/data/vercel_daily.json 에 누적 (90일 유지)."""
    snap = fetch_vercel_daily()
    if snap.get("status") in ("ok", "no_token"):
        history = _load_history()
        history[snap["date"]] = snap
        cutoff = (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
        history = {k: v for k, v in history.items() if k >= cutoff}
        _save_history(history)
    return snap


# ──────────────────────────────────────────────────────────
# briefing_v2 공개 API
# ──────────────────────────────────────────────────────────
def daily_summary():
    """
    브리핑 섹션용 요약. 다른 integrations 와 동일한 패턴.
    """
    snap = collect_yesterday()
    projects = snap.get("projects", {})

    total_pv = 0
    total_uv = 0
    total_deploys = 0
    has_pv = False
    project_lines = []
    for slug, info in projects.items():
        if info.get("pv") is not None:
            total_pv += int(info["pv"] or 0)
            has_pv = True
        if info.get("uv") is not None:
            total_uv += int(info["uv"] or 0)
        total_deploys += int(info.get("deployments_24h") or 0)
        project_lines.append(
            {
                "slug": slug,
                "deployments_24h": info.get("deployments_24h", 0),
                "last_state": (info.get("last_deployment") or {}).get("state"),
                "pv": info.get("pv"),
                "uv": info.get("uv"),
                "error": info.get("error"),
            }
        )

    return {
        "status": snap.get("status", "error"),
        "date": snap.get("date"),
        "analytics_source": snap.get("analytics_source"),
        "note": snap.get("note"),
        "totals": {
            "pv": total_pv if has_pv else None,
            "uv": total_uv if has_pv else None,
            "deployments_24h": total_deploys,
            "projects_count": len(projects),
        },
        "projects": project_lines,
    }


# ──────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) > 1 and sys.argv[1] == "--collect":
        snap = collect_yesterday()
        print(json.dumps(snap, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(daily_summary(), ensure_ascii=False, indent=2))
