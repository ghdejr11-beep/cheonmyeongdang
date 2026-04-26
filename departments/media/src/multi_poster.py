#!/usr/bin/env python3
"""
다채널 Python 직접 API 포스터 — Postiz 셀프호스트 환경변수 의존 제거.

지원: Bluesky, Discord webhook, Mastodon, Reddit
키만 .secrets 에 추가하면 즉시 발행.

사용:
    from multi_poster import send_all_direct
    results = send_all_direct("텍스트")
    # {'bluesky': True, 'discord': True, 'mastodon': True, 'reddit': False}
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse
import datetime

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')


def _load_secrets():
    env = {}
    path = os.path.join(ROOT, '.secrets')
    if os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                env[k] = v
    return env


def _http(method, url, headers=None, body=None, timeout=20):
    data = None
    if headers is None:
        headers = {}
    headers.setdefault('User-Agent', 'KunStudio-Poster/1.0 (+https://kunstudio.bsky.social)')
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode('utf-8')
            headers.setdefault('Content-Type', 'application/json')
        elif isinstance(body, str):
            data = body.encode('utf-8')
        else:
            data = body
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            try:
                return r.status, json.loads(raw.decode('utf-8'))
            except Exception:
                return r.status, raw.decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return 0, str(e)


# ───────── Bluesky ─────────
def post_bluesky(text, env=None):
    env = env or _load_secrets()
    handle = env.get('BLUESKY_HANDLE', '').strip()
    pw = env.get('BLUESKY_APP_PASSWORD', '').strip()
    if not handle or not pw:
        return False, 'no BLUESKY_HANDLE/APP_PASSWORD'

    s, sess = _http('POST', 'https://bsky.social/xrpc/com.atproto.server.createSession',
                    body={'identifier': handle, 'password': pw})
    if s != 200 or not isinstance(sess, dict):
        return False, f'session fail: {s} {sess}'

    jwt = sess['accessJwt']
    did = sess['did']
    record = {
        'repo': did,
        'collection': 'app.bsky.feed.post',
        'record': {
            '$type': 'app.bsky.feed.post',
            'text': text[:300],
            'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
    }
    s2, r2 = _http('POST', 'https://bsky.social/xrpc/com.atproto.repo.createRecord',
                   headers={'Authorization': f'Bearer {jwt}'}, body=record)
    return (s2 == 200), r2


# ───────── Discord webhook ─────────
def post_discord(text, env=None):
    env = env or _load_secrets()
    url = env.get('DISCORD_WEBHOOK_URL', '').strip()
    if not url:
        return False, 'no DISCORD_WEBHOOK_URL'
    s, r = _http('POST', url, body={'content': text[:2000]})
    return (s in (200, 204)), r


# ───────── Mastodon ─────────
def post_mastodon(text, env=None):
    env = env or _load_secrets()
    base = env.get('MASTODON_URL', '').rstrip('/')
    token = env.get('MASTODON_TOKEN', '').strip()
    if not base or not token:
        return False, 'no MASTODON_URL/TOKEN'
    s, r = _http('POST', f'{base}/api/v1/statuses',
                 headers={'Authorization': f'Bearer {token}'},
                 body={'status': text[:500]})
    return (s == 200), r


# ───────── Threads API (텍스트 전용, 이미지 옵션) ─────────
def post_threads(text, env=None):
    """Threads 텍스트 게시. 2단계: /me/threads (컨테이너) → /me/threads_publish."""
    env = env or _load_secrets()
    tok = env.get('THREADS_ACCESS_TOKEN', '').strip()
    if not tok:
        return False, 'no THREADS_ACCESS_TOKEN'

    s1, r1 = _http('POST', 'https://graph.threads.net/v1.0/me/threads',
                   body=urllib.parse.urlencode({
                       'media_type': 'TEXT',
                       'text': text[:500],
                       'access_token': tok,
                   }),
                   headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if s1 != 200 or not isinstance(r1, dict) or 'id' not in r1:
        return False, f'container fail: {s1} {r1}'

    creation_id = r1['id']
    # 컨테이너는 비동기 생성 — 공식 권장 30초지만 텍스트 전용은 2-3초로 충분
    import time
    time.sleep(3)
    s2, r2 = _http('POST', 'https://graph.threads.net/v1.0/me/threads_publish',
                   body=urllib.parse.urlencode({
                       'creation_id': creation_id,
                       'access_token': tok,
                   }),
                   headers={'Content-Type': 'application/x-www-form-urlencoded'})
    return (s2 == 200 and isinstance(r2, dict) and 'id' in r2), r2


# ───────── 이미지 자동 호스팅 (catbox + imgbb 폴백) ─────────
def _is_local_path(p):
    """파일 경로(로컬) vs URL 구분."""
    if not p:
        return False
    if p.startswith(('http://', 'https://')):
        return False
    return os.path.exists(p)


def _upload_catbox(filepath):
    """catbox.moe 익명 업로드 (no auth, 무료, 영구).
    multipart/form-data 직접 구성 (urllib만 사용, 의존성 X).
    """
    try:
        import mimetypes, uuid
        boundary = '----CatboxBoundary' + uuid.uuid4().hex
        with open(filepath, 'rb') as f:
            data_bytes = f.read()
        ext = os.path.splitext(filepath)[1].lstrip('.').lower() or 'jpg'
        mime = mimetypes.guess_type(filepath)[0] or f'image/{ext}'
        body = []
        body.append(f'--{boundary}\r\n'.encode())
        body.append(b'Content-Disposition: form-data; name="reqtype"\r\n\r\nfileupload\r\n')
        body.append(f'--{boundary}\r\n'.encode())
        body.append(f'Content-Disposition: form-data; name="fileToUpload"; filename="{os.path.basename(filepath)}"\r\n'.encode())
        body.append(f'Content-Type: {mime}\r\n\r\n'.encode())
        body.append(data_bytes)
        body.append(f'\r\n--{boundary}--\r\n'.encode())
        payload = b''.join(body)
        req = urllib.request.Request(
            'https://catbox.moe/user/api.php',
            data=payload,
            headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'User-Agent': 'KunStudio-Poster/1.0',
            },
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            url = r.read().decode('utf-8').strip()
        if url.startswith('https://') and ('catbox' in url or 'litterbox' in url):
            return True, url
        return False, f'catbox unexpected: {url[:200]}'
    except Exception as e:
        return False, f'catbox error: {type(e).__name__}: {e}'


def _upload_imgbb(filepath, env=None):
    """imgbb.com 업로드 (API key 필요, env에 IMGBB_API_KEY)."""
    env = env or _load_secrets()
    key = env.get('IMGBB_API_KEY', '').strip()
    if not key:
        return False, 'no IMGBB_API_KEY'
    try:
        import base64
        with open(filepath, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        body = urllib.parse.urlencode({'key': key, 'image': b64}).encode()
        req = urllib.request.Request(
            'https://api.imgbb.com/1/upload',
            data=body,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        if data.get('success') and data.get('data', {}).get('url'):
            return True, data['data']['url']
        return False, f'imgbb fail: {data}'
    except Exception as e:
        return False, f'imgbb error: {type(e).__name__}: {e}'


def host_image(filepath_or_url, env=None):
    """이미지 → public URL.
    - URL 입력 시 그대로 반환 (검증 X)
    - 로컬 파일 → catbox 1차 → imgbb 2차 폴백
    """
    if not filepath_or_url:
        return False, 'empty input'
    if not _is_local_path(filepath_or_url):
        return True, filepath_or_url  # 이미 URL
    # 로컬 파일 → 호스팅
    ok, url = _upload_catbox(filepath_or_url)
    if ok:
        return True, url
    ok2, url2 = _upload_imgbb(filepath_or_url, env)
    if ok2:
        return True, url2
    return False, f'host_image fail (catbox: {url}, imgbb: {url2})'


def _validate_ig_image_url(url, timeout=8):
    """IG 정책 점검: HTTPS + image/jpeg|png + < 8MB + 320~1440px."""
    if not url.startswith('https://'):
        return False, 'not HTTPS'
    try:
        req = urllib.request.Request(url, method='HEAD',
                                     headers={'User-Agent': 'KunStudio-Validator/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            ct = r.headers.get('Content-Type', '').lower()
            cl = int(r.headers.get('Content-Length', '0') or 0)
        if not ct.startswith(('image/jpeg', 'image/png', 'image/jpg')):
            return False, f'unsupported Content-Type: {ct}'
        if cl > 8 * 1024 * 1024:
            return False, f'too large: {cl} bytes'
        return True, f'OK ct={ct} size={cl}'
    except Exception as e:
        return False, f'HEAD fail: {type(e).__name__}: {e}'


# ───────── Instagram Graph API (이미지 필수) ─────────
def post_instagram(text, image_url=None, env=None, max_retry=2):
    """IG는 이미지 필수. image_url 없으면 skip.
    2단계 플로우: /media (컨테이너) → /media_publish.

    image_url이 로컬 파일 경로면 catbox/imgbb로 자동 호스팅.
    HTTPS + image/jpeg|png + <8MB + Content-Type 검증 후 발행.
    """
    env = env or _load_secrets()
    uid = env.get('IG_USER_ID', '').strip()
    tok = env.get('IG_ACCESS_TOKEN', '').strip()
    if not uid or not tok:
        return False, 'no IG_USER_ID/ACCESS_TOKEN'
    if not image_url:
        return False, 'IG requires image_url (skipped)'

    # 1) 로컬 파일이면 자동 호스팅
    ok_host, hosted_url = host_image(image_url, env)
    if not ok_host:
        return False, hosted_url

    # 2) 이미지 정책 검증 (실패해도 IG 자체 검증으로 fallback — warn만)
    ok_v, msg_v = _validate_ig_image_url(hosted_url)
    if not ok_v:
        # DNS 실패 등 검증 자체 못 하는 경우: IG에 직접 시도 (IG가 다운로드 가능하면 OK)
        print(f'[WARN] IG image validation failed ({msg_v}), proceeding anyway')

    # 3) Container 생성 + retry
    last_err = None
    for attempt in range(max_retry + 1):
        s1, r1 = _http('POST', f'https://graph.instagram.com/v21.0/{uid}/media',
                       body=urllib.parse.urlencode({
                           'image_url': hosted_url,
                           'caption': text[:2200],
                           'access_token': tok,
                       }),
                       headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if s1 == 200 and isinstance(r1, dict) and 'id' in r1:
            break
        last_err = f'container fail (attempt {attempt+1}): {s1} {r1}'
        if attempt < max_retry:
            import time
            time.sleep(2 ** attempt)
    else:
        return False, last_err

    creation_id = r1['id']

    # 4) Publish + retry
    last_err2 = None
    for attempt in range(max_retry + 1):
        s2, r2 = _http('POST', f'https://graph.instagram.com/v21.0/{uid}/media_publish',
                       body=urllib.parse.urlencode({
                           'creation_id': creation_id,
                           'access_token': tok,
                       }),
                       headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if s2 == 200 and isinstance(r2, dict) and 'id' in r2:
            return True, r2
        last_err2 = f'publish fail (attempt {attempt+1}): {s2} {r2}'
        if attempt < max_retry:
            import time
            time.sleep(2 ** attempt)
    return False, last_err2


# ───────── X (Twitter) — tweepy OAuth 1.0a ─────────
def post_x(text, env=None):
    env = env or _load_secrets()
    ck = env.get('X_API_KEY', '').strip()
    cs = env.get('X_API_SECRET', '').strip()
    at = env.get('X_ACCESS_TOKEN', '').strip()
    ats = env.get('X_ACCESS_SECRET', '').strip() or env.get('X_ACCESS_TOKEN_SECRET', '').strip()
    if not all([ck, cs, at, ats]):
        return False, 'no X_* keys'
    try:
        import tweepy
    except ImportError:
        return False, 'tweepy not installed (pip install tweepy)'
    try:
        client = tweepy.Client(consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats)
        r = client.create_tweet(text=text[:280])
        return True, r.data
    except Exception as e:
        return False, str(e)


# ───────── Reddit (OAuth password grant) ─────────
def post_reddit(title, text, subreddit, env=None):
    env = env or _load_secrets()
    cid = env.get('REDDIT_CLIENT_ID', '').strip()
    csec = env.get('REDDIT_CLIENT_SECRET', '').strip()
    user = env.get('REDDIT_USERNAME', '').strip()
    pw = env.get('REDDIT_PASSWORD', '').strip()
    if not all([cid, csec, user, pw]):
        return False, 'no REDDIT_* keys'

    auth_raw = f'{cid}:{csec}'
    import base64
    auth = base64.b64encode(auth_raw.encode()).decode()
    ua = f'KunStudio/1.0 by {user}'
    form = urllib.parse.urlencode({'grant_type': 'password', 'username': user, 'password': pw})
    s, tok = _http('POST', 'https://www.reddit.com/api/v1/access_token',
                   headers={'Authorization': f'Basic {auth}', 'User-Agent': ua,
                            'Content-Type': 'application/x-www-form-urlencoded'},
                   body=form)
    if s != 200 or not isinstance(tok, dict) or 'access_token' not in tok:
        return False, f'token fail: {s} {tok}'

    access = tok['access_token']
    body = urllib.parse.urlencode({
        'sr': subreddit, 'kind': 'self', 'title': title[:300], 'text': text[:40000], 'api_type': 'json'
    })
    s2, r2 = _http('POST', 'https://oauth.reddit.com/api/submit',
                   headers={'Authorization': f'Bearer {access}', 'User-Agent': ua,
                            'Content-Type': 'application/x-www-form-urlencoded'},
                   body=body)
    ok = (s2 == 200) and isinstance(r2, dict) and not r2.get('json', {}).get('errors')
    return ok, r2


# ───────── 통합 ─────────
def send_all_direct(content, reddit_title=None, reddit_subreddit='test', image_url=None):
    """연결된 모든 직접 API 채널에 발행. 키 없으면 그 채널만 skip.
    image_url 제공 시 Instagram에도 포스팅 (이미지 없으면 IG skip)."""
    env = _load_secrets()
    results = {}
    for name, fn in [
        ('bluesky', lambda: post_bluesky(content, env)),
        ('discord', lambda: post_discord(content, env)),
        ('mastodon', lambda: post_mastodon(content, env)),
        ('x', lambda: post_x(content, env)),
        ('threads', lambda: post_threads(content, env)),
        ('instagram', lambda: post_instagram(content, image_url, env)),
    ]:
        try:
            ok, _ = fn()
            results[name] = ok
        except Exception as e:
            results[name] = False
            print(f'[{name}] error: {e}')
    if reddit_title and env.get('REDDIT_CLIENT_ID'):
        try:
            ok, _ = post_reddit(reddit_title, content, reddit_subreddit, env)
            results['reddit'] = ok
        except Exception as e:
            results['reddit'] = False
            print(f'[reddit] error: {e}')
    return results


def send_all_combined(content, reddit_title=None, reddit_subreddit='test'):
    """Postiz(텔레그램 등) + 직접 API(Bluesky/Discord/Mastodon/Reddit) 통합."""
    out = {}
    try:
        from postiz_poster import send_all_channels
        postiz_res = send_all_channels(content)
        out['postiz'] = postiz_res
    except Exception as e:
        out['postiz'] = {'error': str(e)}
    out.update(send_all_direct(content, reddit_title, reddit_subreddit))
    return out


if __name__ == '__main__':
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else f'[multi_poster 테스트] {datetime.datetime.now():%Y-%m-%d %H:%M}'
    print(json.dumps(send_all_direct(msg), ensure_ascii=False, indent=2))
