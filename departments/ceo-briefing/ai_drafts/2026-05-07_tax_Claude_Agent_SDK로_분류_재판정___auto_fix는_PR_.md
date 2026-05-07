# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-05-07 12:01 | **비용**: $0.0015

**요약**: Claude Agent SDK 기반 분류 재판정 및 PR 자동생성 시스템 설계 필요

## 메모
Claude Agent SDK를 활용한 세무 분류 재판정 자동화: (1) 기존 분류 규칙을 Agent에 학습시켜 판정 정확도 향상, (2) auto_fix 로직으로 오류 항목 자동 수정, (3) GitHub API 연동하여 PR 자동 생성. 필요 요소: Agent 프롬프트 설계, 분류 룰셋 정의, Git 토큰 관리, PR 템플릿 구성. Claude API 문서의 tool_use 활용 권장.
