# 영문 인플루언서 5명 발송 1클릭 가이드

> **시급도**: 🟢 매출 보조 (글로벌 audience 확보)
> **사용자 시간**: ~30분 (5명 × 6분 평균)
> **매출 임팩트**: 1명 변환률 5~10% 가정 → 5명 도달 audience ~250K → 신규 sub 50~250 → 천명당 ARPU $5~$10 → $250~$2,500 LTV
> **마지막 업데이트**: 2026-05-06

복붙 텍스트 ✂ 표시.

---

## 0. 사전 점검 (자동 완료)

- ✅ 5명 영문 인플루언서 draft 작성 완료: `departments/influencer_outreach/drafts_global_2026_05_06/013_en_KSAJU-00043` ~ `021_en_KSAJU-00051`
- ✅ KSAJU 쿠폰 코드 5개 사전 발행 (HMAC self-validating, `data/influencer_coupons_20k.json` 기반): `KSAJU-00043-3JABWV` / `KSAJU-00044-JLUD77` / `KSAJU-00045-FJT5U5` / `KSAJU-00046-FBR4QH` / `KSAJU-00047-4HTZU4`
- ✅ 본문 1.5K~2K chars (anti-spam 준수)
- ✅ Polite tone + opt-out line + memory 규칙 (BTS/연예인 거론 X / 070 mask)
- ✅ Outreach log: `departments/influencer_outreach/outreach_log.json`
- ✅ Targets seed: `departments/influencer_outreach/targets_seed.json`

---

## 1. 5명 인플라 정보 + 발송 채널

| # | Code | Handle | Name | Platform | Followers | Niche | 발송 채널 |
|---|---|---|---|---|---|---|---|
| 1 | KSAJU-00043 | @AstroAyaaa | Aya | YouTube | 85K | KR Saju + Western astrology mix (EN) | YT About 비즈문의 |
| 2 | KSAJU-00045 | @FourPillarsLab | Four Pillars Lab | YouTube | 12K | BaZi/Saju English education | YT About 비즈문의 |
| 3 | KSAJU-00048 | @k_diary_journals | K-Diary Journals | Pinterest | 67K | Korean diary aesthetic + zodiac | Pinterest contact form |
| 4 | KSAJU-00050 | @thekoreanwave_blog | The Korean Wave Blog | Blog | (n/a) | K-culture blog | Blog contact form |
| 5 | KSAJU-00051 | @elementsastro | Elements Astrology | Instagram | (varies) | Five elements astrology (EN) | IG biz inquiry / DM |

⚠️ **이메일 미공개** → contact-form/DM 채널 사용. 사용자가 본문 paste만 하면 됨.

---

## 2. 1번 — Aya (@AstroAyaaa) ✂

**채널**: YouTube About → `View email address` (CAPTCHA 1회) 또는 `Business inquiries:` 칸 이메일 캡처
**대안**: YouTube DM (구독자만) / Twitter @AstroAyaaa DM

```
파일 위치: departments/influencer_outreach/drafts_global_2026_05_06/013_en_KSAJU-00043_AstroAyaaa.txt
```

발송 단계:
1. https://youtube.com/@AstroAyaaa → About → 비즈문의 이메일 확인
2. 위 파일 전체 본문 복사 → 메일 본문 paste
3. Subject 줄 paste: `A free 1-month gift for Aya (AstroAyaaa) — Korean Saju AI (Cheonmyeongdang)`
4. From: `ghdejr11@gmail.com`
5. Send → outreach_log.json에 자동 기록 (수동 entry: `python departments/influencer_outreach/send_global_50.py --log-only --code KSAJU-00043 --channel youtube_email`)

---

## 3. 2번 — Four Pillars Lab (@FourPillarsLab) ✂

**채널**: YouTube About `Business inquiries:` 또는 채널 description 링크
**대안**: 채널 community tab / Twitter

```
파일: drafts_global_2026_05_06/015_en_KSAJU-00045_FourPillarsLab.txt
```

1. https://youtube.com/@FourPillarsLab → About 탭 → email 확인
2. 본문 paste + Subject + send.
3. log: `--code KSAJU-00045 --channel youtube_email`

---

## 4. 3번 — K-Diary Journals (@k_diary_journals) ✂

**채널**: Pinterest contact form (Pinterest는 직접 이메일 노출 X)
**URL**: https://pinterest.com/k_diary_journals → 우측 상단 `...` → `Contact creator`

```
파일: drafts_global_2026_05_06/018_en_KSAJU-00048_k_diary_journals.txt
```

1. Pinterest 프로필 진입
2. `Contact creator` 폼 오픈 (300자 limit — 본문 첫 단락 + 쿠폰 코드 + email 회신요청만)
3. 단축 본문 (✂ 복붙):

```
Hi K-Diary Journals,

I'm Deokhun (Kun Studio, Korea) — Cheonmyeongdang Korean Saju AI app. Loved your Korean diary x zodiac aesthetic.

Free 1-month premium pass: KSAJU-00048-XXXXXX (link: cheonmyeongdang.vercel.app/redeem).

If interested in a fuller intro, my email: ghdejr11@gmail.com.

No reply needed — gift is yours regardless. Thanks for what you make.
```

4. log: `--code KSAJU-00048 --channel pinterest_form`

---

## 5. 4번 — The Korean Wave Blog (@thekoreanwave_blog) ✂

**채널**: Blog `Contact` 페이지 (Wordpress/Substack/Tumblr 등)

```
파일: drafts_global_2026_05_06/020_en_KSAJU-00050_thekoreanwave_blog.txt
```

1. https://thekoreanwave.blog (또는 사용자 검색으로 정확 URL 확인) → `Contact` 또는 `About` 페이지
2. 폼 발송 또는 게시된 이메일 직접 발송
3. 본문 paste + Subject paste + send.
4. log: `--code KSAJU-00050 --channel blog_form`

---

## 6. 5번 — Elements Astrology (@elementsastro) ✂

**채널**: Instagram bio link → biz inquiry (Calendly/Tally 폼) / IG DM

```
파일: drafts_global_2026_05_06/021_en_KSAJU-00051_elementsastro.txt
```

1. https://instagram.com/elementsastro → bio link → biz form 또는 DM
2. IG DM 본문 (✂ 단축):

```
Hi Elements Astrology — quick gift, no follow-up needed.

I'm Deokhun (Kun Studio, Korea), founder of Cheonmyeongdang — Korean Saju AI app. Your 5-elements angle in English resonated.

1-month premium pass: KSAJU-00051-XXXXXX (cheonmyeongdang.vercel.app/redeem).

If review-curious, email: ghdejr11@gmail.com. Otherwise enjoy the gift.

— Deokhun
```

3. log: `--code KSAJU-00051 --channel instagram_dm`

---

## 7. 사용자만 가능한 액션 (5건 × 6분)

각 인플라마다:
1. 채널 진입 (URL 1클릭)
2. 본문 복붙 (draft 파일 → 폼/메일)
3. Send 버튼

**총 ~30분**.

---

## 8. 완료 후 자동 후속 (클로드 처리)

- 쿠폰 redeem 추적 (천명당 backend → KSAJU-00043~51 사용시 알림)
- 7일 후 미응답 인플라 → 폴로우업 메일 자동 draft (`departments/influencer_outreach/build_candidates.py` 활용)
- 응답 인플라 → 콘텐츠 partnership proposal 자동 생성
- 매주 outreach 효율 보고 (응답률, 변환률, ARPU)

---

## 9. ROI 추정

| 단계 | 가정 | 결과 |
|---|---|---|
| 5명 발송 | 100% 도달 | — |
| 응답률 | 30% (3명) | 콘텐츠 partnership 가능성 |
| 콘텐츠 발행 | 50% (1.5명 평균 1 post) | reach ~150K |
| 클릭 → 가입 변환 | 1% | 1,500 신규 user |
| 유료 변환 | 5% | 75 paying users |
| ARPU $5 (천명당 월회원) | LTV 6개월 | $2,250 |
| ARPU $79 (AppSumo LTD if active) | once | $5,925 |

**5명 영문 발송 1회 ROI: $2,250 ~ $8,000 LTV (보수~중간).**

---

## 10. 주의사항 (memory 준수)

- ❌ BTS/Squid Game/Samsung 등 특정 IP 거론 X (memory: `feedback_no_specific_company_names`)
- ❌ 070-8018-7832 plaintext 노출 X (memory: `feedback_phone_number_masking`)
- ✅ Polite tone + opt-out 라인 (memory: `feedback_dm_polite_tone`)
- ✅ unique KSAJU 코드로 개별 추적
- ✅ 무료/affiliate만 (memory: `feedback_zero_budget_global_channels`)
