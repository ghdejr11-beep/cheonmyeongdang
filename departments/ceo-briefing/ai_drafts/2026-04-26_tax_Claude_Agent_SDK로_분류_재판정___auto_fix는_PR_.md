# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-04-26 15:33 | **비용**: $0.0014

**요약**: Claude Agent SDK 분류 재판정 및 auto_fix PR 자동생성 아키텍처 설계

## 메모
Claude Agent SDK를 활용한 세금 분류 재판정 시스템 구축 필요. (1) Agent가 기존 분류 데이터 분석 후 불일치 항목 식별 (2) auto_fix 로직으로 올바른 분류 제안 (3) GitHub API 연동해 PR 자동생성. 사전 정보: API 키 관리, 분류 규칙셋, 기존 데이터 스키마 확인 필수.
