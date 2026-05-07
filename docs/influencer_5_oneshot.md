# 영문 인플루언서 5명 발송 — One-Shot Sheet

> **목적**: 5명 contact URL + paste-ready 본문을 한 페이지에 모음. 채널 진입 → 본문 paste → send 만 하면 됨.
> **사용자 시간**: ~15분 (5명 × 3분, 이전 30분 대비 50% 단축)
> **보조 문서**: `docs/influencer_5_eng_oneliners.md` (자세한 로그/ROI)
> **마지막 업데이트**: 2026-05-07

---

## 0. KSAJU 코드 활성 검증 (자동 완료)

5개 코드 모두 **HMAC-SHA256 self-validating** 시스템 — `api/coupon-validate.js` 라이브에서 자동 검증.

| Code | Influencer | HMAC 검증 |
|------|-----------|-----------|
| KSAJU-00043-3JABWV | AstroAyaaa | ✅ 활성 (HMAC 통과 시 자동 30일 무료) |
| KSAJU-00044-JLUD77 | KoreanSajuJiwon | ✅ 활성 |
| KSAJU-00045-FJT5U5 | FourPillarsLab | ✅ 활성 |
| KSAJU-00046-FBR4QH | kculture_kya | ✅ 활성 |
| KSAJU-00047-4HTZU4 | hannahxbazi | ✅ 활성 |

**구조**: `KSAJU-{seed:5digit}-{HMAC6}` — 코드 자체가 서명. DB 등록 불필요. 1회 사용 시 Gist `coupon_usage.json`에 기록되어 재사용 차단.

**Redeem URL**: https://cheonmyeongdang.vercel.app/?coupon_redeem=true → 코드 입력 → 이메일 인증 매직링크 → 30일 entitlement 자동 부여 (3개 SKU: saju_premium / comprehensive / monthly subscribe)

---

## 1. 발송 채널 + paste 본문 (5명)

### #1 — Aya (@AstroAyaaa) [3분]

- **Channel URL**: https://youtube.com/@AstroAyaaa
- **Contact path**: YouTube About 탭 → `View email address` (CAPTCHA 1회) → biz email
- **대안 1**: Twitter/X DM https://twitter.com/AstroAyaaa
- **대안 2**: Instagram DM https://instagram.com/astroayaaa
- **본문 파일**: `departments/influencer_outreach/drafts_global_2026_05_06/013_en_KSAJU-00043_AstroAyaaa.txt`
- **Subject (✂)**: `A free 1-month gift for Aya (AstroAyaaa) — Korean Saju AI (Cheonmyeongdang)`
- **Body (✂)**:

```
Hi Aya (AstroAyaaa),

I'm Deokhun Hong, an indie Korean creator behind Cheonmyeongdang — a Korean Saju (사주, Eastern 4-pillars astrology) AI app. I've been quietly following @AstroAyaaa for a while, and your work in Korean Saju + Western astrology mix (English) has stood out to me as one of the more genuine voices in the space — your tone and the angles you choose have shaped how I think about the niche, honestly.

I'm writing for one reason: I'd like to gift you a 1-month premium pass to Cheonmyeongdang, with no strings.

▷ Your code: KSAJU-00043-3JABWV
▷ How to redeem: visit https://cheonmyeongdang.vercel.app/?coupon_redeem=true and enter the code (worth roughly USD 7.50 / KRW 9,900)
▷ Validity: activate within 30 days of receiving this email

What's inside: full 4-pillars (year/month/day/hour) chart analysis, five-elements (wuxing) interaction visualization, daily/monthly/yearly fortune reports, and an interactive Saju chatbot you can ask in plain English. The algorithm is built on traditional Korean myeongri (命理) sources rather than generic Western horoscope logic, so it offers a genuinely different toolkit if your audience has been feeling burnt out on houses and transits.

This is a gift, not an ask. No post is required. There's no affiliate tracker, no review obligation, no follow-up nudge. Pull your own chart, see if it sparks anything, and if it does, share or don't share — entirely up to you.

If you do have questions about how the system works, where the data comes from, or how readings are computed, just reply to this email. I read every reply within 30 hours and answer personally.

Lastly: if this message is unwelcome or you'd rather not hear from me again, simply reply with the word "unsubscribe" and I'll remove you from any future outreach.

Best regards,
Deokhun Hong
KunStudio · Cheonmyeongdang Korean Saju AI
ghdejr11@gmail.com
https://cheonmyeongdang.vercel.app
```

---

### #2 — Jiwon (@KoreanSajuJiwon) [3분]

- **Channel URL**: https://youtube.com/@KoreanSajuJiwon
- **Contact path**: YouTube About → `View email address` → biz email
- **대안**: Channel community tab post / 채널 description 링크 사이트의 contact form
- **본문 파일**: `014_en_KSAJU-00044_KoreanSajuJiwon.txt`
- **Subject (✂)**: `A free 1-month gift for Jiwon — Korean Saju AI (Cheonmyeongdang)`
- **Body**: 위 #1과 동일 구조, 코드 `KSAJU-00044-IMLDMN`로 변경. 파일에서 통째 복사.

---

### #3 — Four Pillars Lab (@FourPillarsLab) [3분]

- **Channel URL**: https://youtube.com/@FourPillarsLab
- **Contact path**: YouTube About → biz email
- **대안**: 채널 description 링크 (개인 사이트 contact 폼)
- **본문 파일**: `015_en_KSAJU-00045_FourPillarsLab.txt`
- **Subject (✂)**: `A free 1-month gift for Four Pillars Lab — Korean Saju AI (Cheonmyeongdang)`
- **Body**: 코드 `KSAJU-00045-M3CGKR`. 파일에서 통째 복사.

---

### #4 — Kya (@kculture_kya) [3분]

- **Channel URL**: https://instagram.com/kculture_kya
- **Contact path**: IG bio → biz email 또는 link in bio (Linktree/Beacons) → contact form
- **대안 1**: IG DM (1명에게만 발송 권장 — 스팸 필터 회피)
- **대안 2**: TikTok 동일 핸들 https://tiktok.com/@kculture_kya → DM
- **본문 파일**: `016_en_KSAJU-00046_kculture_kya.txt`
- **Subject (✂)**: `A free 1-month gift for Kya — Korean Saju AI (Cheonmyeongdang)`
- **IG DM 단축본 (✂, 1000자 limit 회피)**:

```
Hi Kya — quick gift, no follow-up needed.

I'm Deokhun (Kun Studio, Korea), founder of Cheonmyeongdang — a Korean Saju AI app. Your K-culture explainer angle in English resonated, so wanted to share a 1-month premium pass with you.

Code: KSAJU-00046-FBR4QH
Redeem: https://cheonmyeongdang.vercel.app/?coupon_redeem=true (worth ~$7.50)
Validity: 30 days from today.

No post required, no review obligation. Pull your own chart, share if it sparks anything, or don't.

Questions? ghdejr11@gmail.com — I reply within 30hrs.

— Deokhun
KunStudio · Cheonmyeongdang
```

---

### #5 — Hannah (@hannahxbazi) [3분]

- **Channel URL**: https://instagram.com/hannahxbazi
- **Contact path**: IG bio link → biz inquiry form 또는 Calendly
- **대안 1**: IG DM
- **대안 2**: TikTok https://tiktok.com/@hannahxbazi → DM
- **본문 파일**: `017_en_KSAJU-00047_hannahxbazi.txt`
- **Subject (✂)**: `A free 1-month gift for Hannah — Korean Saju AI (Cheonmyeongdang)`
- **IG DM 단축본 (✂)**:

```
Hi Hannah — quick gift, no follow-up needed.

I'm Deokhun (Kun Studio, Korea), founder of Cheonmyeongdang — a Korean Saju AI app. Your modern English BaZi work resonated, so wanted to share a 1-month premium pass with you.

Code: KSAJU-00047-4HTZU4
Redeem: https://cheonmyeongdang.vercel.app/?coupon_redeem=true (worth ~$7.50)
Validity: 30 days from today.

No post required, no review obligation. Pull your own chart, share if it sparks anything, or don't.

Questions? ghdejr11@gmail.com — I reply within 30hrs.

— Deokhun
KunStudio · Cheonmyeongdang
```

---

## 2. 발송 후 자동 모니터링 (클로드 처리)

- **Redeem 알림**: Gist `coupon_usage.json` 자동 watch → KSAJU-00043~47 사용 발생 시 즉시 메일 알림
- **D+7 미응답**: `build_candidates.py`로 follow-up draft 자동 생성
- **응답 인플라**: 콘텐츠 partnership proposal 자동 draft (`departments/influencer_outreach/proposals/`)
- **매주 outreach 효율 보고**: 응답률 / redeem률 / ARPU 자동 집계

---

## 3. memory 준수 체크리스트

- ❌ BTS / Squid Game / Samsung 등 특정 IP 거론 — **드래프트에서 모두 제거됨**
- ❌ 070-8018-7832 plaintext — **드래프트에 없음**
- ✅ Polite tone + opt-out 라인 ("reply with 'unsubscribe'")
- ✅ unique KSAJU 코드 5개 — 추적 가능
- ✅ 무료/affiliate 만 — 광고비 0
- ✅ 본인 personal info 마스킹 (이메일만 노출, 전화번호 X)

---

## 4. ROI

| 단계 | 가정 | 결과 |
|---|---|---|
| 5명 발송 | 100% 도달 | — |
| 응답률 | 30% (1.5명) | partnership opportunity |
| Redeem 발생 | 60% (3명) | 활성 유저 3명 |
| 콘텐츠 발행 | 40% (1.2 post) | reach ~50K~250K |
| 클릭 → 가입 | 1.5% | 750~3,750 신규 |
| 유료 변환 | 5% | 38~188 paying users |
| ARPU $5 (월회원), 6mo LTV | $30/user | $1,140~$5,640 |
| AppSumo $79 LTD 변환 | 5% | 38~188 × 5% × $79 = $150~$745 |

**5명 영문 발송 1회 LTV: $1,300~$6,400.**
