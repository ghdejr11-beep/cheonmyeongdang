# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-05-01 00:00 | **비용**: $0.0014

**요약**: Claude Agent SDK 분류 재판정 및 PR 자동 생성 구조 설계 필요

## 메모
Claude Agent SDK의 도구 호출(tool_use) 패턴으로 분류 재판정 에이전트 구현 가능. 1) 분류 재판정 도구(tool): 기존 분류 재검토 2) auto_fix 도구: 코드 수정 자동 생성 3) GitHub API 통합으로 PR 자동 생성. Messages API 기반 agentic loop 필요. 의존성: anthropic SDK ≥ 0.7.0, GitHub token 권한(repo/contents/pulls)
