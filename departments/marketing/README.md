# Marketing 부서 — 매출 전환 카피·번들 자료 (정적)

**역할**: 캠페인 카피·티어 비교·번들 LP 등 정적 마케팅 산출물 보관
**활동 채널과의 차이**: 액티브 SNS·콘텐츠는 다른 부서가 담당. 이 폴더는 **공용 카피/구조 라이브러리**.

## 폴더 구성

| 폴더 | 내용 | 사용처 |
|------|------|--------|
| `mega_bundle_xuqbai/` | Bluesky 쓰레드 + Hashnode 아티클 + Pinterest 핀 카피 (Gumroad Mega Bundle $29.99) | 미디어 부서가 SNS 자동 발행 시 import |
| `subscription_copy/` | PayPal Subscriptions 영문 LP + KORLENS cross-promo | index.html / KORLENS 사이트가 참조 |
| `tier_comparison/` | 무료/Basic ₩2,900 / Pro ₩9,900 / Annual ₩29,900 비교표 (한·영) | LP + RapidAPI README + 영업 자료 |

## 다른 마케팅 부서와의 분담

| 부서 | 역할 | 이 폴더와의 관계 |
|------|------|------------------|
| `media/` | SNS 발행 자동화 (multi_poster.py, Postiz, Telegram) | 카피를 **이 폴더에서 import**해서 발행 |
| `pinterest_pins/` | 픽토그래프 pin 자동 생성 + 발행 | `mega_bundle_xuqbai/pinterest_pins.md` 와 카피 공유 |
| `seo_blog_factory/` | SEO 블로그 글 생성 + Vercel 배포 | tier 카피·gunghap 설명을 메타로 재사용 |
| `medium_crosspost/`, `devto_crosspost/`, `hashnode_crosspost/` | 글 cross-post | `mega_bundle_xuqbai/hashnode_article.md` 와 동일 base content 활용 |

## 새 카피 추가 규칙

1. **재사용 가능한 정적 카피**만 이 폴더 → 다른 부서가 import
2. 1회성 SNS 포스트 → 해당 SNS 부서 (`media/`, `bluesky_feed/` 등)
3. 영문/한글 짝 작성 권장 (글로벌 우선 전략 — memory)
4. 광고에 특정 업체·연예인·IP 거론 금지 (Samsung/BTS 등 — memory)

## 다음 작업 후보 (rolling backlog)

- `winback_d30/` — D+30 환불·미사용자 재타겟팅 카피 (현재 sales-collection 부서에서 처리, 카피만 분리 가능)
- `affiliate_partners/` — 제휴 30% 어필리에이트 모집 LP
- `b2b_pitch/` — RapidAPI 외 직접 B2B 영업용 1-pager (한국 SI/스타트업 대상)
