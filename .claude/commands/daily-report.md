---
description: 모든 부서의 일일 보고를 09:00 KST 기준으로 수집·요약·텔레그램 전송
---

# 🕘 /daily-report — 일일 보고 실행

실행 시 다음 순서로 진행:

## 1. 현재 시각 확인
- 한국 시간 (KST) 기준.
- 09:00 KST가 아니어도 실행 가능하나 보고서 제목에 실제 시각 표시.

## 2. 7개 총괄팀장 병렬 호출

다음 subagent들을 **병렬로** 호출 (Agent tool 사용):

1. `gm-cheonmyeongdang` — 🔮 천명당팀
2. `gm-media` — 📺 미디어팀
3. `gm-insurance-daboyeo` — 🛡️ 보험다보여팀
4. `gm-ebook` — 📚 전자책팀
5. `gm-game` — 🎮 게임팀
6. `gm-tax` — 💼 세무팀
7. `gm-travelmap` — 🗺️ 여행지도팀

각 에이전트에 전달할 프롬프트:
```
일일 보고를 작성하라.

1. departments/<your-dept>/revenue.md 읽기
2. departments/<your-dept>/roadmap.md 읽기
3. departments/<your-dept>/CLAUDE.md 읽기 (미션·상태 파악)
4. hq/daily-report-template.md 양식 참고

출력: 텔레그램 메시지용 마크다운 (이모지 포함).
- 수익 (어제 매출·비용·순수익, 누적 월수익)
- 문제점 (2~3개)
- 개선 방안 (액션 아이템)
- 오늘 결과/계획
- 부서별 KPI

Placeholder 부서 (게임·여행지도)는 간단히 "대기 중" 보고.
```

## 3. 결과 집계

7개 리포트를 받으면:
1. `hq/scoreboard.md` 업데이트 (수익 랭킹 재정렬)
2. CEO 화면에 전체 요약 출력
3. 텔레그램 봇으로 7개 메시지 전송 (각 부서당 1개)
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` 환경변수 사용
   - API: https://api.telegram.org/bot{TOKEN}/sendMessage

## 4. CEO 최종 요약

출력 예시:
```
🏢 천명당 그룹 일일 보고 완료 | 2026-04-12 09:00 KST

📊 전사 요약
- 총 매출: ₩X,XXX,XXX
- 총 비용: ₩XXX,XXX
- 총 순수익: ₩X,XXX,XXX

🏆 오늘의 순위
🥇 1위: [부서] ₩XXX
🥈 2위: [부서] ₩XXX
🥉 3위: [부서] ₩XXX

⚠️ 전사 리스크
- ...

✅ 오늘 집중 과제
- ...

📨 텔레그램 전송 완료: 7/7
```

## 5. 에러 처리

- 특정 총괄팀장 호출 실패 시: 해당 부서만 "보고 실패" 표시, 나머지는 정상 진행
- 텔레그램 전송 실패 시: CEO에게 수동 알림 유도 (토큰·Chat ID 재확인)
- 환경변수 미설정 시: "텔레그램 미연결, 콘솔 출력만" 모드로 전환

## ⏰ 자동 실행 옵션 (추후)

Make.com 시나리오로 매일 09:00 KST 자동 실행 가능.
지금은 CEO가 수동으로 `/daily-report` 입력해야 함.
