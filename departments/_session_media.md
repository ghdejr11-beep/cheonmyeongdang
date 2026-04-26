# 🟠 MEDIA 세션 (홍보·콘텐츠)

이 세션을 열면 **오직 이 부서들만** 작업한다. 다른 부서 만지지 않는다.

## ✅ 이 세션 범위
- `departments/media/` — SNS 포스팅 (Postiz/Telegram/Bluesky/Discord 등)
- `departments/media/src/faceless/` — AI Side Hustle 쇼츠 자동화
- `departments/intelligence/` — 경쟁사 분석, 트렌드 수집
- `departments/secretary/` — 공지/CS/뉴스레터
- Naver 블로그, 쿠팡 파트너스 로테이터 (수익 아닌 포스팅 관점)

## ❌ 이 세션에서 만지지 말 것
- 매출/결제 → 🟢 REVENUE 세션
- 앱 기능/배포 → 🔵 PRODUCT 세션
- KDP 업로드 (책 자체는 revenue), 단 홍보 문구는 여기

## 🎯 이 세션의 KPI
- **도달(Reach)** — 플랫폼별 노출 수
- 전환율 (클릭 → 방문 → 결제)
- 채널별 팔로워 성장
- 쇼츠 업로드 수 / 평균 조회수

## 🔑 자주 쓰는 명령
```bash
cd departments/media/src
python auto_promo.py                 # 다채널 통합 홍보
python multi_poster.py "테스트 메시지"   # 직접 API (Bluesky/Discord/Mastodon/Reddit)
python postiz_poster.py              # Postiz 경유
python faceless/shorts_pipeline.py    # 쇼츠 생성
python ../scheduler/unified_poster.py # 큐 기반 스케줄러
```

## 🔌 현재 연결 상태 (2026-04-24)
- ✅ Telegram (KunStudio) — Postiz 경유 가동
- ✅ YouTube (AI Side Hustle) — 매일 06:00 자동 업로드
- 🟡 Bluesky/Discord/Mastodon — `multi_poster.py` 준비, 키 추가 대기
- 🟡 Reddit — PRAW 코드 준비, OAuth 키 대기
- ❌ X/Instagram/Threads — Developer App 생성 필요 (CREDENTIALS_GUIDE.md 참고)

## 📂 공통 의존
- `.secrets` — 모든 SNS 토큰
- `shared/coupang_rotator.py` (5포스트당 1회 쿠팡 파트너스 자동 삽입, 공정위 문구)
