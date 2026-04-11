# 천명당 그룹 (Cheonmyeongdang Group)

> **An ancient Eastern wisdom, reimagined for today.**
> 7개 부서로 구성된 디지털 비즈니스 그룹 — 본진 천명당 사이트부터 AI 영상·전자책·보험 앱·게임·세무·여행지도까지.

## 🏢 조직도

```
                      대표이사 (CEO)
                           │
  ┌────────┬────────┬──────┼──────┬────────┬────────┐
  🔮        📺        🛡️        📚        🎮        💼        🗺️
 천명당    미디어    보험      전자책    게임      세무      여행지도
 (글로벌) (글로벌)  (한국)    (글로벌)  (글로벌)  (한국)    (한국)
```

| 부서 | 코드 | 타겟 | 상태 | 수익 우선순위 |
|---|---|---|---|---|
| 🔮 천명당팀 | `departments/cheonmyeongdang` | 🌏 Global | 운영 중 (사주·관상·손금) | 🥉 3 |
| 📺 미디어팀 | `departments/media` | 🌏 Global | 기획 | 🥈 2 |
| 🛡️ 보험다보여팀 | `departments/insurance-daboyeo` | 🇰🇷 Korea | 프로토타입 + 심사 대기 | 5 |
| 📚 전자책팀 | `departments/ebook` | 🌏 Global | 기획 | 🥇 **1** |
| 🎮 게임팀 | `departments/game` | 🌏 Global | placeholder | 6 |
| 💼 세무팀 | `departments/tax` | 🇰🇷 Korea | placeholder | 4 |
| 🗺️ 여행지도팀 | `departments/travelmap` | 🇰🇷 Korea | placeholder | 7 |

## 🚀 빠른 시작

```bash
# 1. clone
git clone <repo-url>
cd cheonmyeongdang

# 2. 환경변수 설정
cp .env.example .env
# .env 파일 열어서 실제 API 키 채우기

# 3. Claude Code 실행
claude
```

## 📜 주요 문서

- [`CLAUDE.md`](./CLAUDE.md) — 전사 마스터 지침
- [`hq/scoreboard.md`](./hq/scoreboard.md) — 월간 수익 랭킹
- [`hq/daily-report-template.md`](./hq/daily-report-template.md) — 일일 보고 양식
- [`.env.example`](./.env.example) — 환경변수 템플릿

## 🤖 AI 조직

이 리포지토리는 **Claude Code 서브에이전트** 기반으로 운영됩니다.
- 총괄팀장 7명 + 팀장 20명 = AI 에이전트 **27개**
- 모두 `.claude/agents/` 에 정의됨

CEO(유저)가 명령 → 총괄팀장 호출 → 팀장 호출 → 실행.

## 🌐 본진 사이트 (천명당)

기존 사주·관상·손금 사이트는 `departments/cheonmyeongdang/` 으로 이전 예정.
- 사주: `saju-engine.js` + `knowledge.json`
- 관상: `face-female.png`, `face-male.png`
- 손금: `palm-canva.png`, `palm-svg.html`
