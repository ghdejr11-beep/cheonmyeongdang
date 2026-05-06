# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-05-06 21:01 | **비용**: $0.0017

**요약**: Claude Agent SDK 분류 재판정 로직 및 PR 자동화 설계 필요

## 메모
Claude Agent SDK를 활용한 세금 분류 재판정 시스템 구축을 위해: (1) Agent API를 통한 분류 모델 설계 (tool_use로 분류 판정), (2) 재판정 트리거 조건 정의 (신뢰도 임계값, 규칙 충돌 등), (3) auto_fix 로직 (수정된 분류 데이터 생성), (4) GitHub API/CLI를 통한 자동 PR 생성 (제목: fix/tax-classification-{id}, 본문에 재판정 사유 포함) 필요. 기존 세금 분류 API 스펙 확인 후 Agent 통합 방식 결정 권장.
