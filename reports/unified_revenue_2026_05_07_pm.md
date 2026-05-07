# Unified Revenue Report — 2026-05-07 PM (data for 2026-05-06 + 글로벌 라이브 D+1)

**Generated:** 2026-05-07 오후 자동 사이클 (사용자 깨어 있는 동안)
**Source:** `departments/sales-collection/unified_revenue.py` + 수동 cross-check
**FX:** 1 USD = ₩1,380 (수동 갱신값)

---

## TL;DR

**어제(2026-05-06) 통합 매출: ₩0**

오전 보고와 동일. 글로벌 v3.5 라이브 D+1 trafic acquisition 단계. 매출 발생 시점은 7~30일 lag 정상 구간 진입 중. 본 보고는 **신규 콘텐츠 자산 35개 사전 작성 완료**까지 합쳐서 매출 leading indicator 강화 진행 상황 정리.

---

## 채널별 매출 (어제 기준, KRW 환산)

| 채널 | 매출 (KRW) | 매출 (USD) | Collector status |
|---|---:|---:|---|
| AdMob | ₩0 | $0.00 | ok |
| YouTube | ₩0 | $0.00 | ok |
| Gumroad | ₩0 | $0.00 | ok |
| KDP | ₩0 | $0.00 | **no_data** |
| 크티 | ₩0 | ₩0 | **awaiting_input** |
| **합계 (자동 합산)** | **₩0** | — | — |

**미연결 채널 (수동 cross-check 필요):**

| 채널 | 어제 추정 | 비고 |
|---|---:|---|
| PayPal Smart Buttons (천명당 V2) | $0 | 5/6 라이브, D+1 첫 결제 대기 |
| Etsy (KORLENS 리스팅) | $0 | 5/6 글로벌 launch 직후 |
| Lemon Squeezy | $0 | 미가입 |
| 천명당 V2 KR PG (토스/갤럭시아) | ₩0 | 라이브키 발급 후 진행 중 |

---

## 이동 평균 / 누적

- **7일 평균:** ₩0/일 (라이브 D+1 정상)
- **30일 누적:** ₩0
- **전일 대비:** N/A

---

## 5/7 자동 사이클 — 신규 콘텐츠 자산 35개 사전 작성 완료

매출 leading indicator 강화를 위해 5/7 PM 사이클에서 다음 자산 작성:

| 영역 | 자산 | 위치 | 합계 |
|---|---|---|---:|
| Beehiiv newsletter | Issue #6~#10 (5주치 사전 작성, 1100~1200 word/issue, 모두 UTM 포함) | `departments/beehiiv/issue_6~10_*.md` | 5건 |
| Reddit drafts | r/Astrology #21~25 (5건) + r/AsianBeauty #26 (1건) + r/koreanwave #27~30 (4건) | `departments/marketing/reddit_drafts_2026_05_07/21~30_*.md` | 10건 |
| Quora drafts | EN #21~40 (Day Master / Ten Gods / Five Elements / 궁합 / 2026 Byeongo / lunar-vs-solar / Sinsal / health 등 핵심 long-tail 키워드 전부 커버) | `departments/quora/drafts_2026_05_07/21~40_*.md` | 20건 |
| **합계** | | | **35건** |

기존 자산 합산:

- Beehiiv: 5 → **10 issue (D+9 주차 publish 풀 채움)**
- Reddit: 20 → **30 draft (5/8~6/3 publish 풀 채움)**
- Quora: 20 → **40 draft (EN 우선 long-tail SEO acquisition)**

---

## Collector 상태 진단 (PM 재확인)

| Collector | Status | 액션 |
|---|---|---|
| admob | ok | 정상. AdMob app revenue 미발생 |
| youtube | ok | 정상. yt_dashboard.daily_summary() OK |
| gumroad | ok | 정상. Gumroad sales feed 0건 |
| kdp | no_data | 셀렉터 / 토큰 만료 추정. 다음 사이클 점검 |
| kreatie | awaiting_input | 수동 입력 채널. 사용자 turn 시 입력 필요 |

---

## 인프라 헬스 (참고)

5/6 천명당 v3.5 글로벌 SaaS 라이브 D+1 24시간 데이터.

- 결제 funnel: 라이브 (PayPal Smart Buttons + V2 KR PG)
- 4 lang (ko/en/ja/zh): SEO blog 발행 진행 중
- 11 schtask: 정상 가동 중 (briefing/blog factory/SNS/replies)
- 5/7 PM: 콘텐츠 leading indicator 35건 사전 작성 완료
- 50 인플라 outreach 응답 모니터 v2 강화

**해석:** 글로벌 라이브 D+1 → 인지 단계. 매출 발생까지 7~30일 lag 정상. 5/7 PM 사이클은 acquisition 자산 (Beehiiv 5주치 + Reddit/Quora 30 draft) 사전 작성으로 lag 단축 시도.

---

## 다음 자동 사이클에서 처리

- KDP scraper `no_data` 원인 진단 (셀렉터/토큰)
- PayPal collector 추가 (Smart Buttons live이므로 매출 가능성 가장 높은 채널)
- Etsy collector 추가 (KORLENS 리스팅)
- 천명당 V2 결제 → 자체 DB 합산 endpoint
- Beehiiv issue #6 (7/8 publish) 사전 review
- Reddit draft 5/8부터 daily 1건 publish 시작 (24h 간격 준수)
- Quora draft 5/8부터 daily 2건 publish 시작 (계정 분산)

---

## 원본 JSON

```json
{
  "status": "ok",
  "date": "2026-05-06",
  "fx_usd_krw": 1380,
  "yesterday_total_krw": 0,
  "yesterday_by_channel_krw": {
    "admob": 0, "youtube": 0, "gumroad": 0, "kdp": 0, "kreatie": 0
  },
  "vs_day_before": { "previous_total_krw": 0, "delta_pct": null, "label": "N/A" },
  "seven_day_avg_krw": 0,
  "thirty_day_total_krw": 0,
  "channel_status": {
    "admob": "ok", "youtube": "ok", "gumroad": "ok",
    "kdp": "no_data", "kreatie": "awaiting_input"
  }
}
```

저장 위치: `departments/sales-collection/data/unified_revenue_daily.json` (90일 rolling)
