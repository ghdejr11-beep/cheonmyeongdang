# medium_crosspost — ARCHIVED (2026-05-06)

## 상태: 비활성 (archived)

Medium은 **2025-01-01 부로 신규 Integration Token 발급을 중단**했다.
([medium.com docs](https://github.com/Medium/medium-api-docs))

기존 토큰 보유자만 Medium API를 계속 사용할 수 있고, 우리는 가입 시점이 그 이후라
신규 발급 불가 → 자동 cross-post 경로 차단됨.

## 대안 (현재 가동 중)

| 채널 | 상태 | 대시보드 |
|------|------|----------|
| dev.to | ✅ live (5/6 first post) | https://dev.to/_fc63310e498280508abfb |
| Hashnode | ✅ live (5 posts) | https://kunstudio.hashnode.dev |
| Bluesky 큐레이션 | ✅ live (2,681 posts/day) | @kunstudio.bsky.social |
| Pinterest 4lang | ✅ live (39 pins queued) | (queue) |
| Quora drafts | ✅ daily auto-draft | output/ |
| TikTok EN shorts | ✅ daily | (Upload-Post) |
| SEO blog factory | ✅ 5x daily | blog/en/ |
| YT 3CH (wealth/inner/whisper) | ✅ AM+PM | YouTube |
| Bluesky 직접 발행 (multi_poster) | ✅ live | @kunstudio.bsky.social |
| Mastodon/Discord/Threads/IG/FB | ✅ live | (multi_poster) |
| X (Twitter) | ⚠️ rate-limited (free tier 50/day) | @deokgune_ai |

Medium 채널 손실분은 dev.to + Hashnode + Substack(beehiiv) 3채널이 충분히 커버.
publish.py 스크립트는 향후 토큰 정책 변경 대비 보관.

## 재활성화 트리거

만약 Medium이 token 발급 재개하면:
1. https://medium.com/me/settings → Integration tokens
2. `.secrets` 에 `MEDIUM_API_TOKEN=<key>` 추가
3. schtask 등록 (현재 없음): `KunStudio_Medium_Crosspost_Daily`

그 전까지는 **콘텐츠 생산 시간 = dev.to + Hashnode + Bluesky 강화에 투입**.
