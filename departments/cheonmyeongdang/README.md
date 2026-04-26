# 🔮 cheonmyeongdang 부서

## 목적
천명당 웹(`C:\Users\hdh02\Desktop\cheonmyeongdang\index.html`) + 안드로이드 앱(`android/`) 유지보수, 꿈해몽·사주·관상·손금 콘텐츠 업데이트, 릴리즈 관리.

## 담당 프로젝트
- 천명당 웹 (ghdejr11-beep.github.io/cheonmyeongdang/)
- 천명당 Android 앱 (com.cheonmyeongdang.app)
- Google Play 내부 테스트 트랙

## 주요 파일
- `daily_check.py` — index.html 문법 검증 + 꿈해몽 DB 건강 체크 (매일 10:30 자동)
- `run_daily.bat` — Windows Task Scheduler 배치

## 수동 체크리스트 (릴리즈 전)
- [ ] versionCode bump (build.gradle)
- [ ] `npx cap sync android` — www → android/assets/public 동기화
- [ ] AAB 빌드: `cd android && ./gradlew.bat bundleRelease`
- [ ] Play Console 내부 테스트 업로드
- [ ] 꿈해몽 데이터 총량 유지 (현재 280+)

## 상태
- 최근 릴리즈: v1.3.0 (versionCode 7) — 2026-04-22 내부 테스트 게시
- AdMob App ID: `ca-app-pub-2954177434416880~7399025784` (천명당 전용)

## 알림 채널
- Telegram 봇 (`.secrets` TELEGRAM_*)
- Postiz 자동 게시 (네이버 블로그/카카오채널)
