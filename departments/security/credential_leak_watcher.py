#!/usr/bin/env python3
"""Credential leak watcher — staged diff에서 hardcoded secret 감지.

사용법 1) 수동 실행:
    python departments/security/credential_leak_watcher.py
    → 현재 staged diff 검사. leak 발견 시 exit 1 + 위반 라인 출력.

사용법 2) pre-commit hook 등록:
    copy departments\\security\\credential_leak_watcher.py .git\\hooks\\pre-commit
    (Windows) — 이후 git commit 시 자동 검사.

사용법 3) 전체 working tree 검사:
    python departments/security/credential_leak_watcher.py --all
    → 작업 디렉토리 전체 (staged 외) 스캔.

탐지 패턴:
- PayPal LIVE Client ID:    AY[A-Za-z0-9_-]{60,}
- PayPal LIVE Client Secret: E[A-Za-z0-9_-]{60,}P
- OpenAI / Anthropic key:   sk-[A-Za-z0-9_-]{20,}
- Google API key:           AIza[A-Za-z0-9_-]{35}
- AWS Access Key:           AKIA[0-9A-Z]{16}
- Slack token:              xox[abp]-[A-Za-z0-9-]{20,}
- Generic high-entropy in PAYPAL_/STRIPE_/API_ assignment

False positive 줄이기:
- .secrets, .env*, *.lock 파일 skip
- 주석 라인 (#, //) skip
- example/sample/test/placeholder 단어 포함 라인 skip
- 길이 < 30자 토큰 skip
"""
import os
import re
import sys
import subprocess
from pathlib import Path

# 검사 제외 파일
SKIP_FILES = {
    ".secrets", ".env", ".env.local", ".env.production", ".env.development",
}
SKIP_SUFFIXES = (".lock", ".min.js", ".map", ".png", ".jpg", ".pdf", ".pickle", ".pyc")
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".vercel", "dist", "build", "android"}

# Skip if these substrings appear in the matched line (likely placeholder)
PLACEHOLDER_HINTS = (
    "your_", "example", "sample", "placeholder", "<replace", "TODO",
    "xxxxx", "<your-", "REPLACE_ME", "FAKE_",
)

# (이름, regex, min_match_len)
PATTERNS = [
    ("PayPal Client ID (LIVE)",
     re.compile(r"\bAY[A-Za-z0-9_\-]{60,90}\b"), 60),
    ("PayPal Client Secret (LIVE)",
     re.compile(r"\bE[A-Za-z0-9_\-]{60,90}\b"), 60),
    ("OpenAI / Anthropic API key",
     re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_\-]{20,}\b"), 30),
    ("Google API key",
     re.compile(r"\bAIza[A-Za-z0-9_\-]{35}\b"), 39),
    ("AWS Access Key",
     re.compile(r"\bAKIA[0-9A-Z]{16}\b"), 20),
    ("Slack token",
     re.compile(r"\bxox[abp]-[A-Za-z0-9-]{20,}\b"), 30),
    ("GitHub PAT",
     re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"), 36),
    ("Generic high-entropy assignment",
     re.compile(r"(?:PAYPAL|STRIPE|TOSS|KAKAO|API|SECRET|TOKEN|KEY)_[A-Z_]*\s*=\s*['\"]([A-Za-z0-9_\-]{30,})['\"]"), 30),
]


def should_skip_file(rel_path: str) -> bool:
    p = Path(rel_path)
    if p.name in SKIP_FILES:
        return True
    if any(part in SKIP_DIRS for part in p.parts):
        return True
    if rel_path.endswith(SKIP_SUFFIXES):
        return True
    return False


def is_likely_placeholder(line: str) -> bool:
    low = line.lower()
    return any(h.lower() in low for h in PLACEHOLDER_HINTS)


def scan_text(file_label: str, text: str) -> list:
    """Return list of (file, line_no, pattern_name, snippet) violations."""
    violations = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        # skip comments
        stripped = line.lstrip()
        if stripped.startswith(("#", "//", "*", "<!--")):
            continue
        if is_likely_placeholder(line):
            continue
        for name, regex, min_len in PATTERNS:
            for m in regex.finditer(line):
                token = m.group(0)
                if len(token) < min_len:
                    continue
                # capture group for generic
                if "Generic" in name and m.lastindex:
                    token = m.group(1)
                    if len(token) < min_len:
                        continue
                snippet = line.strip()
                if len(snippet) > 200:
                    snippet = snippet[:200] + "..."
                violations.append((file_label, line_no, name, snippet))
                break  # one pattern per line is enough
    return violations


def get_staged_diff() -> dict:
    """Return {filepath: added_lines_text} from staged diff."""
    try:
        files = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            text=True, encoding="utf-8", errors="replace",
        ).strip().splitlines()
    except Exception as e:
        sys.stderr.write(f"[leak-watcher] git diff failed: {e}\n")
        return {}

    result = {}
    for f in files:
        if should_skip_file(f):
            continue
        try:
            content = subprocess.check_output(
                ["git", "show", f":{f}"], text=True, encoding="utf-8", errors="replace",
            )
            result[f] = content
        except Exception:
            continue
    return result


def scan_working_tree() -> dict:
    """Return {filepath: text} for all tracked + untracked files (excluding ignored)."""
    try:
        files = subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            text=True, encoding="utf-8", errors="replace",
        ).strip().splitlines()
    except Exception as e:
        sys.stderr.write(f"[leak-watcher] git ls-files failed: {e}\n")
        return {}

    result = {}
    for f in files:
        if should_skip_file(f):
            continue
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fp:
                result[f] = fp.read()
        except Exception:
            continue
    return result


def main():
    mode = "staged"
    if "--all" in sys.argv:
        mode = "all"

    if mode == "staged":
        targets = get_staged_diff()
        label = "staged diff"
    else:
        targets = scan_working_tree()
        label = "working tree"

    if not targets:
        print(f"[leak-watcher] {label}: no files to scan")
        return 0

    all_violations = []
    for filepath, text in targets.items():
        violations = scan_text(filepath, text)
        all_violations.extend(violations)

    if not all_violations:
        print(f"[leak-watcher] {label}: {len(targets)} files scanned — clean")
        return 0

    print(f"[leak-watcher] CRITICAL: {len(all_violations)} potential credential leak(s) in {label}!")
    print("=" * 70)
    for f, ln, name, snippet in all_violations:
        print(f"  {f}:{ln}  [{name}]")
        print(f"    {snippet}")
        print()
    print("=" * 70)
    print("Action: review each line. Move secret to .secrets and load via os.environ.")
    print("Bypass (NOT recommended): git commit --no-verify")
    return 1


if __name__ == "__main__":
    sys.exit(main())
