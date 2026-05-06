# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-05-07 00:01 | **비용**: $0.0016

**요약**: Claude Agent SDK 분류 재판정 로직 및 PR 자동 생성 파이프라인 설계 필요

## 메모
Claude Agent SDK를 활용한 세무 항목 분류 재판정 시스템 구축 필요: (1) Agent 스키마 설계 - tools로 분류 판정/검증 함수 연동 (2) auto_fix 로직 - 분류 오류 감지 시 수정안 생성 (3) PR 자동화 - GitHub API 또는 git 명령으로 브랜치/PR 생성 파이프라인. 기존 분류 데이터셋/오류 패턴 분석 후 프롬프트 구성 권장.
