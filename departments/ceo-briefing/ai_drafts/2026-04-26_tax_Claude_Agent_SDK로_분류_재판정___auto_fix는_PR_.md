# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-04-26 21:00 | **비용**: $0.0014

**요약**: Claude Agent SDK 분류 재판정 + PR 자동생성 기능 설계

## 메모
Claude Agent SDK의 tool_use 기능으로 분류 로직 구현 가능. (1) 분류 재판정: messages API + tool_choice로 multi-turn agent 패턴 (2) auto_fix PR 생성: GitHub API 연동해서 branch/commit/PR 자동화. 사전 검토: SDK 버전, GitHub token 관리, git 로컬 환경 구성 필요. 예상 구현: 200-300줄, 별도 config 파일 권장.
