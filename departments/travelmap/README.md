# 🗺️ travelmap 부서

## 목적
KORLENS(경주 특화 AI 관광 큐레이션, `C:\Users\hdh02\Desktop\korlens\`) 의 장소 DB·지도 레이어 담당. TourAPI 연동, 경주 768개 관광지 큐레이션, 지역 크리에이터 콘텐츠 수집.

## 담당 프로젝트
- KORLENS Vercel (korlens.vercel.app)
- 경주 관광지 DB 확장 (768 → 1500 목표)
- 4관점 매트릭스 (외국인/커플/가족/솔로)

## 주요 파일
- `daily_check.py` — KORLENS 라이브 상태 + Vercel 배포 모니터링
- `run_daily.bat` — Windows Task Scheduler용

## 외부 의존
- 한국관광공사 TourAPI
- 경주시 문화관광 공공데이터
- 열린관광 API (무장애 편의시설)
- Supabase (현지인 픽 DB)
- 카카오 로그인 (사용자 인증)

## 모니터링 지표
- Vercel 응답 200 OK
- Supabase 연결 상태
- 카카오 KOE205 에러 발생 여부
- 일일 접속자 수

## 알림
- 이상 감지 시 Telegram 봇
