# tax: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성

**생성**: 2026-05-07 09:01 | **비용**: $0.0016

**요약**: Claude Agent SDK 분류 재판정 및 PR 자동 생성 구현 방안 조사

## 메모
Claude Agent SDK는 현재 공식 문서에서 'tools' 기능으로 함수 호출을 지원합니다. 1) 분류 재판정: Claude가 tax 항목을 분석하여 카테고리 재할당하는 tool 설계 2) auto_fix PR 생성: GitHub API(PyGithub/Octokit)로 브랜치→PR 자동화 3) 통합 흐름: Agent가 분석 결과 기반 코드 수정 후 PR 생성 tool 호출. SDK 버전, 모델(claude-3.5-sonnet 권장), 인증(API key, GitHub token) 확인 필요.
