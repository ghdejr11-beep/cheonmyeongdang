#!/usr/bin/env python3
"""
briefing_v2.collect_all() 결과를 output/revenue_YYYY-MM-DD.{json,md} 로 저장.

기존 briefing_v2.py 를 수정하지 않고 별도 스크립트로 hook.
사용: python revenue_output.py

Windows Task Scheduler 등록은 register_revenue_output.bat 참고.
"""
import os, sys, json, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"D:\cheonmyeongdang\departments\ceo-briefing")
sys.path.insert(0, str(BASE))

from briefing_v2 import collect_all  # noqa: E402

OUT_DIR = BASE / "output"
OUT_DIR.mkdir(exist_ok=True)

TODAY = datetime.date.today().isoformat()


def _fmt_krw(n):
    try: return f"₩{int(n):,}"
    except: return str(n)


def build_md(data):
    lines = [f"# 쿤스튜디오 수익 리포트 — {TODAY}", ""]
    rev = data.get("revenue", {})

    # Gumroad
    g = rev.get("gumroad", {})
    lines.append("## Gumroad")
    if g.get("error"): lines.append(f"- ⚠️ {g['error']}")
    if g.get("total_sales") is not None:
        lines.append(f"- 총 판매: {g.get('total_sales', 0)}건")
    if g.get("total_revenue_cents") is not None:
        lines.append(f"- 매출: ${g['total_revenue_cents']/100:.2f}")
    lines.append("")

    # KDP
    k = rev.get("kdp", {})
    lines.append("## Amazon KDP")
    if k.get("error"): lines.append(f"- ⚠️ {k['error']}")
    if k.get("royalty") is not None:
        lines.append(f"- 로열티: {_fmt_krw(k.get('royalty', 0))}")
    if k.get("units_sold") is not None:
        lines.append(f"- 판매권수: {k['units_sold']}권")
    lines.append("")

    # Coupang
    c = rev.get("coupang", {})
    lines.append("## 쿠팡 파트너스")
    if c.get("error"): lines.append(f"- ⚠️ {c['error']}")
    if c.get("commission") is not None:
        lines.append(f"- 커미션: {_fmt_krw(c['commission'])}")
    lines.append("")

    # Play
    p = rev.get("play", {})
    lines.append("## Google Play")
    if p.get("error"): lines.append(f"- ⚠️ {p['error']}")
    if p.get("installs") is not None:
        lines.append(f"- 설치: {p['installs']}")
    if p.get("revenue") is not None:
        lines.append(f"- 매출: {_fmt_krw(p.get('revenue', 0))}")
    lines.append("")

    # Departments
    depts = data.get("departments", {})
    if depts:
        lines.append("## 부서별 상태")
        for name, info in depts.items():
            lines.append(f"- **{name}**: {info}")
        lines.append("")

    return "\n".join(lines)


def main():
    print(f"[revenue_output] collect_all() …")
    data = collect_all()

    json_path = OUT_DIR / f"revenue_{TODAY}.json"
    md_path   = OUT_DIR / f"revenue_{TODAY}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(build_md(data))

    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
