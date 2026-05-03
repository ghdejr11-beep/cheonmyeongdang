# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-05-02 23:13 | **비용**: $0.0014

**요약**: Claude Agent SDK를 활용한 세금 분류 재판정 및 자동 PR 생성 프로세스 설계

## 메모
Claude Agent SDK는 현재 공개 문서상 '분류 재판정' 자동화와 'PR 자동생성' 기능을 직접 지원하지 않습니다. 대신 (1) Claude API의 vision/batch 처리로 세금 분류 재판정, (2) GitHub Actions + REST API로 PR 자동생성 조합 권장. 필요시 SDK 기능 한계 확인 후 하이브리드 접근.
