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
import re

MIN_BODY_LEN = 250

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


def validate_outbound(subject: str, body: str, recipient: str,
                      min_body_len: int = MIN_BODY_LEN,
                      allow_short: bool = False):
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
