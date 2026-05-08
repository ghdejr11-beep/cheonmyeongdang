"""
Strip emoji/decorative pictographs from cheonmyeongdang HTML files.
Keeps: hanja, Korean text, ASCII, HTML numeric entities (&#xxxxx;), CSS.
Removes: pictographic emoji (U+1F300-1F9FF, 1FA00-1FAFF, 1F1E0-1F1FF, 1F600-1F64F, 1F680-1F6FF)
         + dingbats/misc-symbols emoji (U+2600-27BF) + variation selectors / ZWJ
Replaces: ★★★★★ -> 5.0 (preserves rating semantics)
Cleans:   trailing/leading whitespace from emoji-stripped strings.
"""
import re
import sys
import os
import io
import shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = r"D:\cheonmyeongdang"
TARGETS = [
    "index.html",
    "pay.html",
    "success.html",
    "restore.html",
    "support.html",
    "fail.html",
    "blog/2026-zodiac-fortune.html",
]

# Pictographic / emoji codepoint ranges to strip.
EMOJI_RE = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"   # regional indicators (flags)
    "\U0001F300-\U0001F5FF"   # symbols & pictographs
    "\U0001F600-\U0001F64F"   # emoticons
    "\U0001F680-\U0001F6FF"   # transport & map
    "\U0001F700-\U0001F77F"   # alchemical
    "\U0001F780-\U0001F7FF"   # geometric
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"   # supplemental symbols & pictographs
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "☀-➿"           # misc symbols + dingbats (★ ✓ ✨ ⭐ ✅ ☀ etc)
    "⌀-⏿"           # misc technical
    "⬀-⯿"           # extra arrows / stars
    "️"                  # variation selector
    "‍"                  # zero-width joiner
    "]"
)

# Tally of removed characters
removed = {}

def strip_emoji(s):
    def repl(m):
        ch = m.group(0)
        # Skip ZWJ/VS — invisible, just delete silently
        if ch in ("️", "‍"):
            return ""
        removed[ch] = removed.get(ch, 0) + 1
        return ""
    return EMOJI_RE.sub(repl, s)

def clean_whitespace(s):
    # Collapse runs of spaces
    s = re.sub(r"  +", " ", s)
    # Trim spaces immediately before tag close > or before <
    s = re.sub(r" +<", "<", s)
    s = re.sub(r"> +", ">", s)
    # Inside attribute values like onclick='openOrder('  사주', ...)' fix '  ' -> ' '
    # already covered above
    # Strip leading/trailing whitespace inside common text-only tags? Keep this conservative.
    # Replace stray empty 'span > /span' with nothing? skip — could break CSS.
    return s

# Pre-pass replacements (semantic preservation)
PRE_REPLACEMENTS = [
    # Five black-stars rating -> "5.0"
    ("★★★★★", "5.0"),
    # 4-star and 3-star rating fallbacks (just in case)
    ("★★★★", "4.0"),
    ("★★★", "3.0"),
]

stats = []
for rel in TARGETS:
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.exists(path):
        print(f"SKIP missing: {path}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()
    work = original
    # Save backup once if absent
    bak = path + ".bak"
    if not os.path.exists(bak):
        shutil.copyfile(path, bak)
    # Apply pre-replacements
    pre_changes = 0
    for old, new in PRE_REPLACEMENTS:
        cnt = work.count(old)
        if cnt:
            pre_changes += cnt
            work = work.replace(old, new)
    # Strip emoji
    before_len = len(work)
    work = strip_emoji(work)
    after_len = len(work)
    # Whitespace cleanup
    work = clean_whitespace(work)
    # Count modified lines
    diff_lines = sum(
        1
        for a, b in zip(original.splitlines(), work.splitlines())
        if a != b
    )
    # Account for line count changes
    if len(original.splitlines()) != len(work.splitlines()):
        diff_lines = max(diff_lines, abs(len(original.splitlines()) - len(work.splitlines())))
    if work != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(work)
    stats.append({
        "file": rel,
        "bytes_before": len(original.encode("utf-8")),
        "bytes_after": len(work.encode("utf-8")),
        "modified_lines": diff_lines,
        "star_rating_replacements": pre_changes,
    })

print("=== Per-file stats ===")
for s in stats:
    print(s)
print()
print("=== Removed characters (top 30) ===")
for ch, cnt in sorted(removed.items(), key=lambda x: -x[1])[:30]:
    try:
        print(f"  {ch}  U+{ord(ch):04X}  x{cnt}")
    except Exception:
        print(f"  ?  x{cnt}")
print(f"Total removed: {sum(removed.values())} (distinct {len(removed)})")
