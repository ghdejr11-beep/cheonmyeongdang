# 천명당 그룹 — 마스터 지침서 (Company-Wide CLAUDE.md)

> 이 파일은 천명당 그룹 **전사 공통 규칙**입니다. 각 부서별 지침은 `departments/<부서명>/CLAUDE.md` 를 참고하세요.

## 🏢 회사 구조

```
대표이사 (CEO)
├── 🔮 천명당팀         (departments/cheonmyeongdang)     [글로벌]
├── 📺 미디어팀          (departments/media)                [글로벌]
├── 🛡️  보험다보여팀      (departments/insurance-daboyeo)    [한국]
├── 📚 전자책팀          (departments/ebook)                [글로벌]
├── 🎮 게임팀            (departments/game)                 [글로벌]
├── 💼 세무팀            (departments/tax)                  [한국→글로벌 확장 가능]
└── 🗺️  여행지도팀        (departments/travelmap)            [한국]
```

## 👥 조직도 (AI 구현)

| 직급 | 구현 방식 | 파일 위치 |
|---|---|---|
| 대표이사 (CEO) | 사람 = 유저 | — |
| 총괄팀장 (GM) | Subagent (부서별 1명) | `.claude/agents/gm-*.md` |
| 팀장 (Team Lead) | Subagent (하위팀별 1명) | `.claude/agents/lead-*.md` |
| 사원·대리 | 일반 도구 실행 (Edit/Write/Bash) | — |

## 📜 전사 규칙

1. **명령 주체**: CEO(유저) 1인. 모든 실행은 CEO의 지시로만 시작.
2. **보고 체계**: 매일 **09:00 KST** 각 총괄팀장이 텔레그램으로 일일 보고.
3. **수익 단위**: 기본 `KRW`, 글로벌 부서는 `USD` 병기.
4. **경쟁 KPI**: 월간 순수익(매출 - 비용). `hq/scoreboard.md` 에서 자동 집계.
5. **예산 가드레일**: 1회 실행에 **$5(약 7,000원) 초과** 비용이 예상되면 반드시 CEO 확인.
6. **브랜치 정책**: 개발은 `claude/*` 브랜치에서. `main` 직접 커밋 금지.
7. **보안**: API 키는 `.env` 에만. `.env` 는 gitignore. 대화창/커밋에 키 절대 노출 금지.
8. **언어 정책**: 전사 기본 한국어. 글로벌 부서 코드·콘텐츠는 영어 1순위.

## 🌏 글로벌 vs 한국 정책

| 부서 | 타겟 | 주력 언어 | 결제 |
|---|---|---|---|
| 천명당 | 🌏 Global | English → Korean | Stripe, PayPal → Toss |
| 미디어 | 🌏 Global | English | YouTube/TikTok payouts |
| 보험다보여 | 🇰🇷 Korea only | Korean | Toss, Kakao Pay |
| 전자책 | 🌏 Global | English (Amazon KDP) | KDP royalties (USD) |
| 게임 | 🌏 Global | English | App Store/Play Store |
| 세무 | 🇰🇷 Korea → expansion | Korean | Toss |
| 여행지도 | 🇰🇷 Korea | Korean | API 판매 (기업 B2B) |

## 🏆 수익 우선순위 (현재)

```
🥇 1순위: 📚 전자책팀   — Amazon KDP, 즉시 시작 가능
🥈 2순위: 📺 미디어팀   — YouTube 영어 숏폼, 2~3개월
🥉 3순위: 🔮 천명당팀   — 기존 사이트 글로벌화, 3~6개월
  4순위: 💼 세무팀     — 외부 서비스 판매
  5순위: 🛡️ 보험다보여 — 정부 API 심사 대기
  6순위: 🎮 게임팀     — 기획 단계
  7순위: 🗺️ 여행지도팀  — 기획 단계
```

## 🤖 서브에이전트 호출 규칙

CEO가 저(Claude)에게 명령 → 저는 아래 순서로 위임:

1. **부서 전체 관련 명령** → 해당 **총괄팀장 subagent** 호출 (예: "유튜브팀 보고해")
2. **특정 업무 명령** → 총괄팀장이 **팀장 subagent** 호출 (예: "전자책 표지 만들어")
3. **실행 작업** → 팀장이 일반 도구(Edit/Write/Bash) 직접 사용

## 📂 공통 경로

- `hq/scoreboard.md` — 월간 수익 랭킹
- `hq/daily-report-template.md` — 일일 보고 양식
- `departments/<부서>/revenue.md` — 부서별 월간 수익 기록
- `departments/<부서>/roadmap.md` — 부서별 로드맵
- `.env.example` — 환경변수 템플릿
