"""
공통 텔레그램 알림 라이브러리.

모든 AI 부서가 import 해서 쓴다. 외부 의존성 없음 (urllib 만 사용).

환경변수:
  TELEGRAM_BOT_TOKEN  - BotFather 가 준 봇 토큰
  TELEGRAM_CHAT_ID    - 메시지 받을 chat id

사용 예:
  from scripts.lib.telegram_notify import notify
  notify("✅ 분석부 작업 완료")

또는 markdown 형식:
  notify("*굵게* 와 _기울임_", parse_mode="Markdown")
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional


class TelegramNotifyError(Exception):
    pass


def _get_credentials() -> tuple[str, str]:
    token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    chat_id = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    if not token:
        raise TelegramNotifyError("TELEGRAM_BOT_TOKEN 환경변수 없음")
    if not chat_id:
        raise TelegramNotifyError("TELEGRAM_CHAT_ID 환경변수 없음")
    return token, chat_id


def notify(
    message: str,
    parse_mode: Optional[str] = None,
    disable_web_page_preview: bool = True,
    silent: bool = False,
) -> dict:
    """텔레그램 메시지 1개 전송.

    Args:
        message: 보낼 텍스트 (최대 4096자, 초과 시 자동 분할)
        parse_mode: None / "Markdown" / "MarkdownV2" / "HTML"
        disable_web_page_preview: True 면 링크 미리보기 숨김
        silent: True 면 알림음 없이 (조용한 알림)

    Returns:
        Telegram API 응답 dict (마지막 메시지 기준)

    Raises:
        TelegramNotifyError: 토큰/chat_id 누락 또는 API 에러
    """
    token, chat_id = _get_credentials()

    # 4096자 초과 시 분할
    chunks = _split_long_message(message, 4000)

    last_response = None
    for chunk in chunks:
        last_response = _send_one(token, chat_id, chunk, parse_mode,
                                  disable_web_page_preview, silent)
    return last_response


def _split_long_message(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        # 줄바꿈 기준으로 자르려고 시도
        cut = text.rfind("\n", 0, limit)
        if cut == -1 or cut < limit // 2:
            cut = limit
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return chunks


def _send_one(
    token: str,
    chat_id: str,
    text: str,
    parse_mode: Optional[str],
    disable_web_page_preview: bool,
    silent: bool,
) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": disable_web_page_preview,
        "disable_notification": silent,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise TelegramNotifyError(
            f"Telegram API HTTP {e.code}: {error_body}"
        ) from e
    except Exception as e:
        raise TelegramNotifyError(f"Telegram 전송 실패: {e}") from e


def notify_safe(message: str, **kwargs) -> bool:
    """예외 안 던지는 버전. 실패해도 print 만 하고 False 반환.
    cron 작업이 알림 실패로 죽지 않게 할 때 사용.
    """
    try:
        notify(message, **kwargs)
        return True
    except Exception as e:
        print(f"[telegram_notify] 실패: {e}")
        return False


if __name__ == "__main__":
    # 직접 실행 시 테스트 메시지 발송
    import sys
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "🤖 텔레그램 알림 테스트"
    try:
        result = notify(msg)
        print(f"✓ 전송 성공: message_id={result.get('result', {}).get('message_id')}")
    except TelegramNotifyError as e:
        print(f"✗ 전송 실패: {e}")
        sys.exit(1)
