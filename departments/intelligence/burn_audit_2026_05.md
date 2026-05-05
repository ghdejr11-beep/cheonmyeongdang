# 자금 흐름 audit — 2026-05 (D-Day burn rate)

**측정일**: 2026-05-05
**기간**: 월 비용 vs 월 매출

## 월 비용 내역 (확정 / 추정)

| 항목 | 비용 | 매출 직결도 | 결정 |
|-----|------|-----------|------|
| Vercel Pro/Hobby | $0 (Hobby) | ★★★★★ (천명당 메인) | 유지 |
| Claude API | $20~50/월 (변동) | ★★★★ | 유지 (배치 우선) |
| Suno Pro | $24/월 | ★★ (Sori Atlas 매출 0) | 매출 30일 0건 시 다운그레이드 |
| Hetzner CX22 | ₩7,000/월 (~$5) | ★ (Sori Atlas 24/7 송출, 매출 0) | **D+30 매출 0이면 cancel** |
| Upload-Post | $192/년 (~$16/월) | ★★★ (5/5 프로필 활용) | 유지 |
| 도메인 (cheonmyeongdang.com / korlens.app / 기타) | ~$60/년 (~$5/월) | ★★★★ | 유지 |
| Postiz Railway | $5/월 (Hobby) | ★★ | 유지 |
| Gumroad | 매출의 10%+0.30 | n/a | 거래 수수료 (per-tx) |
| PayPal | 매출의 4.4%+$0.30 | n/a | 거래 수수료 (per-tx) |

**고정비 합산 (월)**: 약 $75 ~ $105 (₩100,000 ~ ₩145,000)

## 매출 0 채널의 비용 지출 (D+30 강제 검토)

1. **Sori Atlas Hetzner ₩7,000/월** — 매출 0 + Suno Pro $24 합산 = 월 약 $29 (₩40,000) 매몰
   → D+30 매출 0이면 Hetzner 즉시 cancel, Suno Pro는 K-Wisdom 채널 BGM 재활용 검토
2. **WhisperAtlas schtask (이미 disabled)** — 비용은 0, 시간만 소요. OK
3. **Upload-Post** — 5/5 프로필 활용 중이므로 OK

## 손익분기점 (D+100 KPI 매핑)

- 손익분기 (cover monthly burn): 월 매출 약 $100~150
- D+30 KPI ($100): 거의 손익분기
- D+60 KPI ($500): 흑자 전환
- D+100 KPI ($2,000): 안정 흑자 + 재투자 가능

## 자동 모니터링

`departments/intelligence/burn_monthly.py` (예정):
- 월 1일 자동 실행 → Vercel API + Anthropic console + PayPal 수수료 합산
- 매출 0 채널 cost > $5 면 Telegram alert

## 사용자 1클릭 액션 (D+30 매출 0 시)
```bash
# Hetzner 인스턴스 power off (요금 정지)
# 콘솔: https://console.hetzner.cloud → Servers → ⋮ → Power off
# 또는 hcloud CLI:
hcloud server poweroff sori-atlas-247
```
