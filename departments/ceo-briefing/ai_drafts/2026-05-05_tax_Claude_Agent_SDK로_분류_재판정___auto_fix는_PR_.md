# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-05-05 21:00 | **비용**: $0.0015

**요약**: Claude Agent SDK 분류 재판정 로직 설계 및 PR 자동 생성 파이프라인 검토 필요

## 메모
Claude Agent SDK의 tool_use 기반 분류 에이전트 구현 방식 확인 필요: 1) 분류 모델 선택 (classification vs routing), 2) auto_fix 판정 기준 명확화, 3) GitHub API를 통한 PR 자동 생성 권한/토큰 관리, 4) 재판정 실패 시 폴백 전략. tax 도메인 특화 프롬프트 및 분류 스키마 정의 후 초안 작성 권장.
