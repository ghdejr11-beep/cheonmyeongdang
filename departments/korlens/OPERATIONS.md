# KORLENS 부서 운영 가이드

## 📂 디렉토리 구조
```
departments/korlens/
├── README.md              # 부서 개요·팀·경쟁사·일정
├── OPERATIONS.md          # (이 파일) 운영 가이드
├── support_agent.py       # 고객센터 자동 처리 에이전트
├── support_queue.json     # 고객 티켓 큐 (자동 생성)
└── docs/                  # 자료실
```

## 🔄 자동 운영 일정 (Windows 스케줄러)

| 태스크 | 실행 시간 | 설명 |
|---|---|---|
| `KunStudio_Intelligence` | 매일 00:30 | `watch.py all` — KORLENS 경쟁사 6개 포함 모니터링 |
| `KunStudio_Contests` | 매일 09:05 | 공모전 포털 6개 크롤 → 지원가능만 텔레그램 알림 |
| `KunStudio_SupportQueue` | 10분마다 | 고객센터 티켓 자동 처리 |

### 스케줄 등록/갱신
```cmd
cd C:\Users\hdh02\Desktop\cheonmyeongdang\departments\ceo-briefing
register_all_schedules.bat
```
※ 관리자 권한 CMD로 실행 권장.

## 💬 고객센터 수동 실행
```bash
# 테스트 티켓 생성
python departments/korlens/support_agent.py test

# 큐 확인
python departments/korlens/support_agent.py list
```

### 처리 흐름
1. 텔레그램/웹폼 → 티켓 enqueue
2. `classify()` → `faq|bug_report|feature_req|data_issue|general`
3. FAQ는 즉시 자동 응답 (영어/무료/지역/혼잡도/무장애/챗봇 등)
4. 그 외는 CEO에게 텔레그램 알림 → 수동 대응

## 🎯 공모전 수집부 (`intelligence/contests_watch.py`)

### 수집 소스 (6개 포털)
- 링커리어 · 위비티 · 콘테스트코리아 · 씽굿 · 올콘 · 컨테츠21

### 지원 가능 판단 규칙
- **포함 키워드**: 개발·AI·데이터·IT·앱·웹·창업·SW·해커톤 등
- **제외 키워드**: 청소년·취업캠프·양성과정·여성한정·재학생한정 등

### 수동 실행
```bash
python departments/intelligence/contests_watch.py          # 새 공모전만 알림
python departments/intelligence/contests_watch.py --all    # 전체 목록 출력
python departments/intelligence/contests_watch.py --reset  # 상태 초기화
```

### 리포트 위치
```
departments/intelligence/data/contests_YYYY-MM-DD.json
departments/intelligence/data/contests_seen.json  # 누적 중복 방지
```

## 🛠️ 개발 작업 연결

| 작업 | 경로 |
|---|---|
| 소스코드 | `C:\Users\hdh02\Desktop\korlens` |
| 로컬 dev | `npm run dev` (port 3458) |
| 프로덕션 | `https://korlens.vercel.app` |
| Vercel 대시보드 | `kunstudio/korlens` |
| 하이라이트 캐시 | `data/highlights/{contentId}.json` (192개) |

## 📞 긴급 연락
- Telegram: 쿤스튜디오 봇 (기존 TG_CHAT)
- 공모전 사무국: gongmo@stunning.kr
