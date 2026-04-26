# 🟢 REVENUE 세션 (돈·매출)

이 세션을 열면 **오직 이 부서들만** 작업한다. 다른 부서 만지지 않는다.

## ✅ 이 세션 범위
- `departments/insurance-daboyeo/` — 보험 다 보여주는 서비스
- `departments/ebook/` — KDP 영문 전자책 (Deokgu Studio)
- `departments/tax/` — 세금N혜택
- `departments/digital-products/` — 크티 상품/디지털 자산
- 쿠팡 파트너스 관련 (media 부서에 로테이터 있지만 수익 관점은 여기)
- CODEF 정산, 수익집계 대시보드

## ❌ 이 세션에서 만지지 말 것
- 앱 개발 → 🔵 PRODUCT 세션
- SNS/콘텐츠/쇼츠 → 🟠 MEDIA 세션
- media/secretary/intelligence 부서

## 🎯 이 세션의 KPI
- **월 매출 합계** (모든 수익 창구)
- 신규 결제 건수 / ARPU / 환불률
- 채널별 ROI (KDP vs 크티 vs 보험 vs 쿠팡)

## 🔑 자주 쓰는 명령
```bash
python departments/ebook/kdp_uploader.py
python departments/insurance-daboyeo/scripts/insurance_match.py
python departments/tax/tax_flow.py
python reports/briefing.py            # 통합 매출 브리핑
```

## 📂 공통 의존
- `.secrets` — KDP/Amazon/쿠팡/토스 키
- `shared/coupang_rotator.py` (media에 있음 - import만)
