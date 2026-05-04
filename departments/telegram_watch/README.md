# telegram_watch — 텔레그램/로그 자동 문제 감지·해결 부서

## 목적
사용자가 텔레그램/브리핑/로그에서 발견하는 문제를 클로드가 **자동 감지 + 자동 처리**.
"왜 안 봤어?" 사고 방지.

## 작동 방식
1. **Sources** (24시간 내 변경된 파일):
   - `D:\scripts\kwisdom_pipeline.log`
   - `departments/ceo-briefing/output/`
   - `departments/intelligence/data/health_log.txt`
   - `departments/media/logs/`
2. **Patterns** (monitor.py PROBLEM_PATTERNS):
   - YouTube OAuth scope/import 오류 → 자동 fix
   - K-Wisdom 0재생 → 파이프라인 강제 재실행
   - Vercel 12-function 한도 초과 → 보고만 (수동 통합)
   - Supabase 테넌트 미등록 → 다음 실행 재시도
   - AdSense 미승인 → 정보성 (자동 처리 X, 시간만 흐름)
3. **Idempotency**: state/processed.json — 동일 문제 중복 처리 X
4. **Logging**: logs/watch_YYYY-MM-DD.log

## 등록
```cmd
schtasks /Create /TN KunStudio_TelegramWatch_Hourly /TR "python C:\Users\hdh02\Desktop\cheonmyeongdang\departments\telegram_watch\monitor.py" /SC HOURLY /F
```

## 신규 패턴 추가
`monitor.py` PROBLEM_PATTERNS 리스트에 dict 추가 + HANDLERS 등록.

## 미해결 큐
state.json 에서 `resolved: false` 항목 → CEO briefing에 포함 권장 (다음 작업).
