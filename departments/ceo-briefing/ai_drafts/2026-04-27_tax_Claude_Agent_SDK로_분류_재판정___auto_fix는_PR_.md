# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-04-27 21:00 | **비용**: $0.0015

**요약**: Claude Agent SDK 분류 재판정 로직 및 자동 PR 생성 방식 조사 필요

## 메모
Claude Agent SDK에서 분류 재판정(classification re-evaluation) 구현 방식 확인 필요: 1) Agent가 판정 결과를 검토하고 재분류하는 루프 구조 2) auto_fix 결과를 바탕으로 GitHub API/CLI를 통해 자동 PR 생성하는 워크플로우 3) 세금 관련 분류 규칙(카테고리별 세율 적용 등)의 정의. Claude API의 tool_use를 활용한 agent 구현 패턴 확인 필요.
