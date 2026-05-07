# Unified Revenue Report — 2026-05-07 (data for 2026-05-06)

**Generated:** 2026-05-07 새벽 자동 처리 (사용자 잠자는 중)  
**Source:** `departments/sales-collection/unified_revenue.py --collect`  
**FX:** 1 USD = ₩1,380 (수동 갱신값)

---

## TL;DR

**어제(2026-05-06) 통합 매출: ₩0**

매출 0이라도 가식 없이 있는 그대로 보고합니다. 인프라/파이프라인은 살아 있고, 채널 collector 4/5가 정상 응답 중입니다. 매출 발생 = 트래픽/유입 단계 문제이지 시스템 문제 아님.

---

## 채널별 매출 (어제 기준, KRW 환산)

| 채널 | 매출 (KRW) | 매출 (USD 원본) | Collector status |
|---|---:|---:|---|
| 📱 AdMob | ₩0 | $0.00 | ok |
| ▶️ YouTube | ₩0 | $0.00 | ok |
| 🛒 Gumroad | ₩0 | $0.00 | ok |
| 📚 KDP | ₩0 | $0.00 | **no_data** |
| 🎨 크티 | ₩0 | ₩0 | **awaiting_input** |
| **합계** | **₩0** | — | — |

> 노출되지 않은 채널: PayPal · Etsy · 천명당 V2 결제 · Lemon Squeezy 는 unified_revenue.py 에 collector 미연결. 별도 모니터링 필요.

---

## 이동 평균 / 누적

- **7일 평균**: ₩0/일
- **30일 누적**: ₩0
- **전일 대비**: N/A (전일도 0이라 % 계산 불가)

---

## Collector 상태 진단

| Collector | Status | 액션 |
|---|---|---|
| admob | ok | 정상. 매출 0 = 진짜 0. AdMob app revenue 미발생 |
| youtube | ok | 정상. yt_dashboard.daily_summary() 응답 OK |
| gumroad | ok | 정상. Gumroad sales feed 0건 (어제 신규 결제 없음) |
| kdp | no_data | KDP scraper가 어제치 royalty 못 가져옴 — 로그 확인 필요 |
| kreatie | awaiting_input | 크티는 수동 입력 채널. 사용자가 ₩ 직접 입력해야 합산 |

**우선 조치(다음 자동 사이클)**:
1. KDP scraper `no_data` 원인 확인 → 로그인 세션 만료 가능성 높음
2. 크티는 수동 입력이라 0이 정상 (사용자 깨면 입력 시도)
3. PayPal/Etsy/V2 collector를 unified_revenue.py 에 추가하면 진짜 매출 노출 가능 (별도 PR)

---

## 인프라 헬스 (참고)

5/6 천명당 v3.5 글로벌 SaaS 라이브 직후 24시간 데이터.
- 결제 funnel: 라이브 (PayPal Smart Buttons + V2 KR PG)
- 4 lang (ko/en/ja/zh): SEO blog 발행 진행 중
- 11 schtask: 정상 가동 중 (briefing/blog factory/SNS/replies)
- 50 인플라 outreach 발송 완료, 응답 대기 중 (이번 새벽 monitor v2 강화)

**해석**: 글로벌 라이브 D+1 → 인지 단계. 매출 발생까지 7~30일 lag 정상. 트래픽 acquisition (Pinterest pin/Etsy 리스팅/SEO blog 인덱싱)이 매출 leading indicator.

---

## 다음 자동 사이클에서 처리

- KDP scraper `no_data` 원인 진단 (1차: 토큰 갱신, 2차: 셀렉터 변화)
- PayPal collector 추가 (Smart Buttons live이므로 매출 가능성 가장 높은 채널)
- Etsy collector 추가 (KORLENS 리스팅 기준)
- 천명당 V2 결제 → 자체 DB 합산 endpoint 추가

---

## 원본 JSON (자동 저장)

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
