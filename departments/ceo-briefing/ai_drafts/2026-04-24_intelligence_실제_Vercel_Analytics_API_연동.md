# intelligence: 실제 Vercel Analytics API 연동

**생성**: 2026-04-24 22:16 | **비용**: $0.0014

**요약**: Vercel Analytics API 연동 방식 및 인증 정보 조사 필요

## 메모
Vercel Analytics API는 REST/GraphQL 두 가지 방식 지원. 필수 항목: (1) Vercel 프로젝트 ID, (2) Access Token (팀/개인 토큰), (3) API 엔드포인트(https://api.vercel.com). sales_collector.py:109에서 해당 정보를 환경변수(.env)로 관리하거나 설정 파일에서 로드해야 함. 공식 문서: https://vercel.com/docs/analytics/quickstart
