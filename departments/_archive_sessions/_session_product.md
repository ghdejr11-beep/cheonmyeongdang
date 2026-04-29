# 🔵 PRODUCT 세션 (앱·서비스)

이 세션을 열면 **오직 이 부서들만** 작업한다. 다른 부서 만지지 않는다.

## ✅ 이 세션 범위
- `departments/cheonmyeongdang/` — 천명당 앱 (사주/꿈해몽)
- `departments/korlens/` — 외국인 관광객 렌즈
- `departments/travelmap/` — 여행 지도
- `departments/game/` — HexDrop, 게임 개발
- `departments/digital-products/` 중 **앱 기능** (전자책 판매 X)
- Play Console / TestFlight / Toss Mini App 배포
- 앱인토스(AppsInToss) 통합

## ❌ 이 세션에서 만지지 말 것
- 매출 집계, 결제 플로우 → 🟢 REVENUE 세션
- SNS 홍보, 쇼츠 생성 → 🟠 MEDIA 세션
- KDP 전자책, 보험, 세금

## 🎯 이 세션의 KPI
- **DAU/MAU** / 유지율 (D1/D7/D30)
- 앱 버전별 크래시 프리 세션
- 신규 설치 수 / 앱스토어 별점

## 🔑 자주 쓰는 명령
```bash
# 천명당
cd departments/cheonmyeongdang/app && npm run build
./gradlew bundleRelease

# korlens
cd departments/korlens && npm run dev

# HexDrop
cd Desktop/hexdrop && npx cap sync
```

## 📂 공통 의존
- `.secrets` — Google Play / Apple / Firebase / Supabase
- 키스토어: `D:\새키스토어.jks`, `Desktop\cheonmyeongdang-release.jks`
