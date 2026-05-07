"""Shared safety guard for all auto-mailers.

Usage:
    from send_guard import validate_outbound, GuardFailure

    try:
        validate_outbound(subject=subj, body=body, recipient=to_addr)
    except GuardFailure as e:
        # SKIP this email -- log + alert telegram
        log(f'[GUARD] SKIPPED {to_addr}: {e}')
        continue

    # safe to send

Rules (HARD — never bypass without explicit user approval):
1. body.strip() length >= MIN_BODY_LEN (default 250)
2. NO placeholder tokens (Lorem ipsum, TODO, {{, TBD, FILL_ME, [placeholder], XXX_, plain XXXX)
   exception: '010-XXXX-XXXX' phone-mask is allowed (per memory rule)
3. subject.strip() not empty
4. recipient must contain '@' and a TLD
5. body cannot equal a known generic-ack template (블랙리스트 string match)
"""
import os
import re

MIN_BODY_LEN = 250

# 외부 기관 도메인 — 자동 send 절대 X (drafts만, 사용자 검토 후 1클릭 send)
# 5/7 KoDATA 빈 hwp 사고 학습 (memory feedback_external_mail_user_review_first.md)
EXTERNAL_ORG_DOMAINS = [
    'kodata.co.kr', 'k-startup.go.kr', 'kakaopaycorp.com',
    'naverpay.com', 'kakao.vc', 'antler.co', 'kakaobrain.com',
    'd2sf.com', 'naverd2sf.com', 'touraz.kr', 'kreonet.kr',
    'sba.kr', 'innovation.go.kr', 'kibo.or.kr', 'koss.go.kr',
    'tossbank.com', 'tosspayments.com',
]

# 빈 양식 의심 첨부 (사고 패턴)
SUSPICIOUS_HWP_SIZE_RANGE = (90_000, 110_000)  # KoDATA 빈 의뢰서 ~98KB
DOCX_PLACEHOLDER_PATTERNS = [
    r'\[회사명\]', r'\[대표자명\]', r'\{\{.+\}\}',
    r'_______+', r'\(작성\)', r'\(예시\)',
    r'XXX[-_]', r'TBD', r'TODO',
]

PLACEHOLDER_TOKENS = [
    'Lorem ipsum', 'TODO', '{{', 'TBD',
    '[placeholder]', '[PLACEHOLDER]',
    'FILL_ME', 'XXX_', '__REPLACE__',
]

# Body strings that should NEVER be sent as-is (generic acks, ChatGPT-style filler)
BLACKLISTED_BODY_PATTERNS = [
    r'메일\s*잘\s*받았습니다.{0,80}내용\s*검토\s*후\s*회신드리겠습니다',
    r'^\s*안녕하세요[,.]?\s*$',
    r'^\s*감사합니다[.]?\s*$',
]


class GuardFailure(Exception):
    """Raised when an outbound email fails safety validation."""
    pass


def is_external_org(recipient: str) -> bool:
    """수신자가 외부 기관(정부/공공/심사) 도메인이면 True."""
    r = (recipient or '').lower()
    return any(d in r for d in EXTERNAL_ORG_DOMAINS)


def validate_attachments(paths: list[str]) -> None:
    """첨부 파일 검증. 빈 hwp / placeholder docx / 빈 pdf form 발견 시 GuardFailure."""
    import zipfile
    for p in paths or []:
        if not os.path.exists(p):
            raise GuardFailure(f'ATTACHMENT_MISSING: {p}')
        size = os.path.getsize(p)
        ext = p.lower().rsplit('.', 1)[-1]

        # hwp 빈 양식 의심 (KoDATA 사고 패턴)
        if ext == 'hwp' and SUSPICIOUS_HWP_SIZE_RANGE[0] <= size <= SUSPICIOUS_HWP_SIZE_RANGE[1]:
            raise GuardFailure(f'SUSPICIOUS_EMPTY_HWP: {os.path.basename(p)} {size}B (in suspicious range)')

        # docx placeholder
        if ext == 'docx':
            try:
                with zipfile.ZipFile(p, 'r') as z:
                    text = z.read('word/document.xml').decode('utf-8', errors='ignore')
                for pat in DOCX_PLACEHOLDER_PATTERNS:
                    if re.search(pat, text):
                        raise GuardFailure(f'DOCX_PLACEHOLDER: {os.path.basename(p)} matches {pat!r}')
            except (zipfile.BadZipFile, KeyError):
                raise GuardFailure(f'DOCX_BROKEN: {os.path.basename(p)}')


def validate_outbound(subject: str, body: str, recipient: str,
                      min_body_len: int = MIN_BODY_LEN,
                      allow_short: bool = False,
                      attachments: list[str] | None = None,
                      allow_external_org: bool = False):
    """Raise GuardFailure if outbound email looks unsafe to send.

    Args:
        subject: email subject
        body: plain-text body (signature included is fine)
        recipient: 'to' address
        min_body_len: minimum stripped body length
        allow_short: bypass length check (only for system mails like
                     "쿠폰 활성화 링크" 짧은 알림 — caller must explicitly opt in)
    """
    s = (subject or '').strip()
    b = (body or '').strip()
    r = (recipient or '').strip()

    if not r or '@' not in r or '.' not in r.split('@')[-1]:
        raise GuardFailure(f'BAD_RECIPIENT: {r!r}')

    if not s:
        raise GuardFailure('EMPTY_SUBJECT')

    if not allow_short and len(b) < min_body_len:
        raise GuardFailure(f'BODY_TOO_SHORT: {len(b)} < {min_body_len}')

    # placeholder check
    for tok in PLACEHOLDER_TOKENS:
        if tok in b:
            raise GuardFailure(f'PLACEHOLDER_IN_BODY: {tok!r}')
        if tok in s:
            raise GuardFailure(f'PLACEHOLDER_IN_SUBJECT: {tok!r}')

    # plain XXXX exception: '010-XXXX-XXXX' phone-mask is intentional
    if 'XXXX' in b and '010-XXXX' not in b and '010 XXXX' not in b:
        raise GuardFailure('XXXX_IN_BODY_NOT_PHONE_MASK')

    # blacklisted body templates
    for pat in BLACKLISTED_BODY_PATTERNS:
        if re.search(pat, b, flags=re.IGNORECASE):
            raise GuardFailure(f'BLACKLISTED_TEMPLATE: matches {pat[:50]!r}')

    # 외부 기관 자동 send 차단 (5/7 KoDATA 사고 학습)
    if is_external_org(r) and not allow_external_org:
        raise GuardFailure(f'EXTERNAL_ORG_AUTO_SEND_BLOCKED: {r} - drafts에 저장 후 사용자 검토 필수')

    # 첨부 검증
    if attachments:
        validate_attachments(attachments)

    return True


def safe_send(send_fn, *, subject: str, body: str, recipient: str,
              allow_short: bool = False, log_fn=print, **kwargs):
    """Wrapper: validate → call send_fn(**kwargs) only if safe.

    Returns send_fn result on success, None if guard blocked.
    """
    try:
        validate_outbound(subject=subject, body=body, recipient=recipient,
                          allow_short=allow_short)
    except GuardFailure as e:
        log_fn(f'[GUARD-BLOCK] to={recipient} subj="{subject[:50]}" reason={e}')
        return None
    return send_fn(**kwargs)


if __name__ == '__main__':
    # Self-test
    test_cases = [
        # (label, kwargs, should_pass)
        ('valid', dict(subject='Hi', body='안녕하세요. ' * 50, recipient='a@b.com'), True),
        ('empty body', dict(subject='Hi', body='', recipient='a@b.com'), False),
        ('short body', dict(subject='Hi', body='hi', recipient='a@b.com'), False),
        ('no @', dict(subject='Hi', body='안녕' * 100, recipient='abc'), False),
        ('placeholder', dict(subject='Hi', body='Hello [placeholder] body ' * 20, recipient='a@b.com'), False),
        ('XXXX phone OK', dict(subject='Hi', body='연락처 010-XXXX-XXXX 로 연락주세요. ' * 15, recipient='a@b.com'), True),
        ('XXXX bad', dict(subject='Hi', body='Code: XXXX something here ' * 15, recipient='a@b.com'), False),
        ('blacklisted ack', dict(subject='Re: x',
                                 body='안녕하세요. 메일 잘 받았습니다. 내용 검토 후 회신드리겠습니다. ' * 5,
                                 recipient='a@b.com'), False),
        ('empty subj', dict(subject='', body='안녕' * 200, recipient='a@b.com'), False),
    ]
    for label, kw, want_pass in test_cases:
        try:
            validate_outbound(**kw)
            ok = True
            err = ''
        except GuardFailure as e:
            ok = False
            err = str(e)
        result = 'PASS' if ok == want_pass else 'FAIL'
        print(f'[{result}] {label}: ok={ok} err={err}')
