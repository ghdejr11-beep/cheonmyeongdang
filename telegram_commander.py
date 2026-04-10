"""
텔레그램 양방향 명령 봇.

너가 외출 중에 텔레그램으로 명령하면 AI 가 실행하는 시스템.
Long-polling 방식 → PC 에서 실행 (HTTPS/Render 불필요).

사용법:
  python telegram_commander.py
  또는 telegram_commander.bat 더블클릭

명령어:
  /노래 [주제]    — Claude 가 가사 5곡 생성 → lyrics_drop/*.txt 저장
  /리포트          — 분석부 즉시 실행 → 결과 텔레그램 전송
  /상태            — 전체 시스템 상태 확인
  /사주 [생년월일]  — 사주 즉시 풀기
  /도움말          — 사용 가능한 명령어 목록
  (일반 텍스트)     — Claude 가 자유 대화

환경변수:
  TELEGRAM_BOT_TOKEN  — 봇 토큰
  ANTHROPIC_API_KEY   — Claude API 키 (선택, 없으면 AI 기능 비활성)
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path

# ============================================================
# 설정
# ============================================================
# .secrets 파일에서 키 자동 로드 (환경변수 매번 안 쳐도 됨)
# ============================================================
def load_secrets():
    """스크립트 폴더의 .secrets 파일에서 KEY=VALUE 읽어서 환경변수 설정.
    이미 환경변수 있으면 덮어쓰지 않음 (환경변수 우선).
    .secrets 파일은 .gitignore 에 추가되어 GitHub 에 안 올라감.
    """
    secrets_path = Path(__file__).resolve().parent / ".secrets"
    if not secrets_path.exists():
        return
    try:
        for line in secrets_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and not os.environ.get(key):
                os.environ[key] = value

    except Exception as e:
        print(f"[경고] .secrets 읽기 실패: {e}")


load_secrets()

TOKEN = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
ANTHROPIC_KEY = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()

HOME = Path.home()
LYRICS_DROP = HOME / "Desktop" / "lyrics_drop"
LYRICS_DROP.mkdir(parents=True, exist_ok=True)

POLL_INTERVAL = 2  # 초
LAST_UPDATE_ID = 0


# ============================================================
# 텔레그램 API 헬퍼
# ============================================================
def tg_api(method: str, data: dict = None) -> dict:
    """Telegram Bot API 호출."""
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    if data:
        payload = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, method="POST")
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[TG API 에러] {method}: {e}")
        return {"ok": False}


def send_message(chat_id, text: str, reply_to: int = None):
    """텔레그램 메시지 보내기 (4096자 자동 분할)."""
    chunks = []
    while text:
        if len(text) <= 4000:
            chunks.append(text)
            break
        cut = text.rfind("\n", 0, 4000)
        if cut < 2000:
            cut = 4000
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")

    for chunk in chunks:
        data = {"chat_id": chat_id, "text": chunk}
        if reply_to:
            data["reply_to_message_id"] = reply_to
        tg_api("sendMessage", data)
        reply_to = None  # 첫 청크만 reply


def send_typing(chat_id):
    """'입력 중...' 표시."""
    tg_api("sendChatAction", {"chat_id": chat_id, "action": "typing"})


# ============================================================
# Claude API 호출
# ============================================================
def ask_claude(prompt: str, system: str = None, max_tokens: int = 1000) -> str:
    """Claude Haiku 4.5 호출. 실패 시 에러 메시지 반환."""
    if not ANTHROPIC_KEY:
        return "[오류] ANTHROPIC_API_KEY 환경변수가 없습니다."
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        kwargs = {
            "model": "claude-haiku-4-5",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        msg = client.messages.create(**kwargs)
        return "".join(b.text for b in msg.content if hasattr(b, "text"))
    except Exception as e:
        return f"[Claude 오류] {type(e).__name__}: {str(e)[:200]}"


# ============================================================
# 명령어 핸들러
# ============================================================
def cmd_help(chat_id, args: str):
    """사용 가능한 명령어 목록."""
    send_message(chat_id,
        "🤖 덕구네 AI 팀 명령어\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "/노래 [주제]  — 가사 5곡 생성 (lyrics_drop 저장)\n"
        "/리포트       — 분석부 즉시 실행\n"
        "/상태         — 시스템 상태 확인\n"
        "/사주 [생년월일] — AI 사주 풀기\n"
        "/도움말       — 이 메시지\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "일반 메시지 → Claude 자유 대화"
    )


def cmd_song(chat_id, args: str):
    """가사 생성 → lyrics_drop/*.txt 저장."""
    if not args.strip():
        send_message(chat_id, "주제를 입력해주세요.\n예: /노래 펫로스 강아지 추모")
        return

    send_typing(chat_id)
    send_message(chat_id, f"🎵 '{args}' 주제로 가사 5곡 생성 중...")

    prompt = f"""너는 한국어 작사가다.
주제: {args}

아래 형식으로 가사 5곡을 작성해라:
- 각 곡마다 [곡 제목] 으로 시작
- [Verse], [Chorus], [Bridge] 등 구조 포함
- 가사 자체만 출력 (설명 금지)
- 감정적, 진심 있는 톤
- 각 곡 15~25줄

5곡 모두 작성하라."""

    system = "너는 K-POP/발라드 전문 작사가. 한국어로만 작성. 감정적이고 진실된 가사."
    result = ask_claude(prompt, system=system, max_tokens=4000)

    if result.startswith("["):
        send_message(chat_id, result)
        return

    # 곡별 분리 → lyrics_drop/*.txt 저장
    songs = []
    current_title = ""
    current_lines = []

    for line in result.split("\n"):
        if line.strip().startswith("[곡") or line.strip().startswith("# "):
            if current_title and current_lines:
                songs.append((current_title, "\n".join(current_lines)))
            # 제목 추출
            title = line.strip().replace("[곡 ", "").replace("]", "").replace("# ", "")
            title = title.strip(":：- ").strip()
            if not title:
                title = f"song_{len(songs)+1}"
            current_title = title
            current_lines = []
        else:
            current_lines.append(line)

    if current_title and current_lines:
        songs.append((current_title, "\n".join(current_lines)))

    if not songs:
        # 분리 실패 → 전체를 1개 파일로
        safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in args[:20])
        path = LYRICS_DROP / f"{safe}.txt"
        path.write_text(result, encoding="utf-8")
        send_message(chat_id,
            f"✅ 가사 생성 완료 (1개 파일)\n"
            f"📂 {path.name}\n\n"
            f"Suno 에서 노래 만들고 같은 폴더에 MP3 넣으면 자동 업로드됩니다."
        )
        return

    saved = []
    for title, lyrics in songs:
        safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in title[:30])
        path = LYRICS_DROP / f"{safe}.txt"
        path.write_text(lyrics.strip(), encoding="utf-8")
        saved.append(f"  📝 {path.name}")

    send_message(chat_id,
        f"✅ 가사 {len(saved)}곡 생성 완료!\n"
        f"📂 lyrics_drop/ 에 저장됨:\n"
        + "\n".join(saved)
        + "\n\nSuno 에서 노래 만들고 같은 폴더에 MP3 넣으면 자동 업로드됩니다."
    )


def cmd_report(chat_id, args: str):
    """분석부 즉시 실행."""
    send_typing(chat_id)
    send_message(chat_id, "📊 분석부 실행 중...")

    try:
        script_dir = Path(__file__).resolve().parent
        sys.path.insert(0, str(script_dir))
        from scripts.teams.analytics_team import build_report
        report = build_report()
        send_message(chat_id, report)
    except Exception as e:
        send_message(chat_id, f"❌ 분석부 실행 실패: {type(e).__name__}: {str(e)[:200]}")


def cmd_status(chat_id, args: str):
    """시스템 상태."""
    send_typing(chat_id)

    checks = []

    # Python
    checks.append(f"🐍 Python {sys.version.split()[0]}")

    # 핵심 파일 존재 여부
    script_dir = Path(__file__).resolve().parent
    key_files = {
        "lyrics_watcher.py": script_dir / "lyrics_watcher.py",
        "auto_watcher.py": script_dir / "auto_watcher.py",
        "youtube_uploader.py": script_dir / "youtube_uploader.py",
        "사주 SaaS server.py": script_dir / "ebook_system" / "projects" / "saju_ai_saas" / "server.py",
        "카카오 endpoints": script_dir / "ebook_system" / "projects" / "saju_ai_saas" / "kakao_endpoints.py",
    }
    for name, path in key_files.items():
        mark = "✅" if path.exists() else "❌"
        checks.append(f"  {mark} {name}")

    # API 키
    checks.append(f"🔑 ANTHROPIC_API_KEY: {'✅' if ANTHROPIC_KEY else '❌'}")
    checks.append(f"🔑 TELEGRAM_BOT_TOKEN: {'✅' if TOKEN else '❌'}")

    # lyrics_drop 파일
    mp3s = list(LYRICS_DROP.glob("*.mp3"))
    txts = list(LYRICS_DROP.glob("*.txt"))
    checks.append(f"📂 lyrics_drop: MP3 {len(mp3s)}개, TXT {len(txts)}개")

    # music_drop 파일
    music_drop = HOME / "Desktop" / "music_drop"
    if music_drop.exists():
        m_files = list(music_drop.glob("*.*"))
        audio = [f for f in m_files if f.suffix.lower() in (".mp3", ".wav", ".m4a", ".flac")]
        checks.append(f"📂 music_drop: 오디오 {len(audio)}개")

    send_message(chat_id,
        "🤖 덕구네 AI 팀 시스템 상태\n"
        f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        + "\n".join(checks)
    )


def cmd_saju(chat_id, args: str):
    """AI 사주 풀기."""
    if not args.strip():
        send_message(chat_id, "생년월일을 입력해주세요.\n예: /사주 1990년 3월 15일 14시 30분")
        return

    send_typing(chat_id)

    try:
        script_dir = Path(__file__).resolve().parent
        sys.path.insert(0, str(script_dir / "ebook_system" / "projects" / "saju_ai_saas"))
        from saju_calc import calculate_saju, format_saju_for_claude
        from kakao_endpoints import parse_birth

        parsed = parse_birth(args)
        if not parsed:
            send_message(chat_id, "⚠️ 생년월일을 인식하지 못했어요.\n예: 1990년 3월 15일 14시 30분")
            return

        year, month, day, hour, minute = parsed
        saju = calculate_saju(year, month, day, hour, minute)
        saju_text = format_saju_for_claude(saju)

        prompt = f"""사주 정보:
{saju_text}

이 사주를 한국어로 친근하게 풀어줘. 800자 이내.
성격, 올해 운세, 주의할 점 포함."""

        system = "너는 30년 경력 명리학 전문가. 따뜻하고 희망적으로, 한국어로 답변."
        answer = ask_claude(prompt, system=system, max_tokens=800)

        pillars = [
            f"년: {saju['year_pillar']['gan_kr']}{saju['year_pillar']['ji_kr']}",
            f"월: {saju['month_pillar']['gan_kr']}{saju['month_pillar']['ji_kr']}",
            f"일: {saju['day_pillar']['gan_kr']}{saju['day_pillar']['ji_kr']}",
            f"시: {saju['hour_pillar']['gan_kr']}{saju['hour_pillar']['ji_kr']}",
        ]

        send_message(chat_id,
            f"🔮 사주 8글자\n{' · '.join(pillars)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n{answer}"
        )
    except Exception as e:
        send_message(chat_id, f"❌ 사주 계산 실패: {type(e).__name__}: {str(e)[:200]}")


def cmd_freeform(chat_id, text: str):
    """일반 대화 → Claude."""
    send_typing(chat_id)
    system = (
        "너는 덕구네 AI 팀의 총괄 비서다. 사용자는 100일 안에 10억 매출 달성이 목표. "
        "사업 아이디어, 마케팅, 기술, 코딩 관련 질문에 한국어로 짧고 핵심만 답한다. "
        "모르는 건 모른다고 하고, 외부 서비스 정보는 검색 후 답해야 한다."
    )
    answer = ask_claude(text, system=system)
    send_message(chat_id, answer)


# 명령어 라우터
COMMANDS = {
    "/도움말": cmd_help,
    "/help": cmd_help,
    "/start": cmd_help,
    "/노래": cmd_song,
    "/song": cmd_song,
    "/리포트": cmd_report,
    "/report": cmd_report,
    "/상태": cmd_status,
    "/status": cmd_status,
    "/사주": cmd_saju,
}


# ============================================================
# 메시지 처리
# ============================================================
def handle_message(message: dict):
    """수신된 메시지 1개 처리."""
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()
    if not chat_id or not text:
        return

    print(f"[수신] {text}")

    # 명령어 분리
    parts = text.split(None, 1)
    cmd = parts[0].lower() if parts else ""
    args = parts[1] if len(parts) > 1 else ""

    handler = COMMANDS.get(cmd)
    if handler:
        try:
            handler(chat_id, args)
        except Exception as e:
            send_message(chat_id, f"❌ 명령 실행 오류: {type(e).__name__}: {str(e)[:200]}")
    else:
        # 명령어 아닌 일반 텍스트 → Claude 자유 대화
        cmd_freeform(chat_id, text)


# ============================================================
# Long-polling 루프
# ============================================================
def poll_loop():
    """텔레그램 서버에서 새 메시지를 가져와서 처리하는 무한 루프."""
    global LAST_UPDATE_ID

    print("=" * 50)
    print("🤖 덕구네 AI 팀 텔레그램 명령 봇")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"🔑 ANTHROPIC_API_KEY: {'OK' if ANTHROPIC_KEY else 'MISSING'}")
    print(f"📂 lyrics_drop: {LYRICS_DROP}")
    print("=" * 50)
    print("텔레그램에서 /도움말 보내서 시작하세요.")
    print("종료: Ctrl+C")
    print()

    while True:
        try:
            params = {
                "offset": LAST_UPDATE_ID + 1,
                "timeout": 20,
                "allowed_updates": '["message"]',
            }
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(url)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except urllib.error.URLError:
                time.sleep(POLL_INTERVAL)
                continue

            if not data.get("ok"):
                time.sleep(POLL_INTERVAL)
                continue

            for update in data.get("result", []):
                update_id = update.get("update_id", 0)
                if update_id > LAST_UPDATE_ID:
                    LAST_UPDATE_ID = update_id
                message = update.get("message")
                if message:
                    handle_message(message)

        except KeyboardInterrupt:
            print("\n종료.")
            return
        except Exception as e:
            print(f"[에러] {type(e).__name__}: {e}")
            time.sleep(5)


# ============================================================
# 진입점
# ============================================================
def main():
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN 환경변수 필요")
        print("PowerShell: $env:TELEGRAM_BOT_TOKEN = '너의봇토큰'")
        return 1

    # 토큰 검증
    me = tg_api("getMe")
    if not me.get("ok"):
        print(f"ERROR: 봇 토큰 무효. getMe 실패: {me}")
        return 1
    bot_name = me.get("result", {}).get("first_name", "?")
    print(f"✅ 봇 연결 OK: {bot_name}")

    poll_loop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
