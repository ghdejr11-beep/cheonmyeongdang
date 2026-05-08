# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-05-08 09:01 | **비용**: $0.0014

**요약**: Claude Agent SDK 통합 방식과 PR 자동 생성 파이프라인 설계 필요

## 메모
Claude Agent SDK를 통한 분류 재판정 로직: (1) 기존 분류 결과 입력 → Agent가 규칙 기반 재판정 (2) auto_fix 대상 식별 → GitHub API로 PR 자동 생성 권장. PR 템플릿(title/body/branch명), commit message, 리뷰어 할당 정책을 먼저 정의하고, Agent prompt에서 분류 기준(tax 규정 관련성, 위험도)을 명시해야 함.
