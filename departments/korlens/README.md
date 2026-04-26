# KORLENS 부서 (쿤스튜디오)

> **같은 한국, 다른 관점** — 4가지 관점 AI 큐레이션 여행 웹서비스

## 개요
- **대표**: 홍덕훈
- **서비스명**: KORLENS
- **URL**: https://korlens.vercel.app
- **기술스택**: Next.js 16 · TypeScript · Tailwind CSS 4 · Claude Haiku 4.5 · TourAPI 4종
- **리포지토리**: `C:\Users\hdh02\Desktop\korlens`
- **현재 단계**: 2026 관광데이터 활용 공모전 접수 완료 (5/6 마감)

## 핵심 기능
1. 17개 광역시도 × 4관점 (외국인/커플/가족/솔로) 매트릭스
2. Claude Haiku로 768개 하이라이트 사전 생성 JSON 캐싱
3. 혼잡도 3단계 필터 + 🔥 인기 뱃지
4. AI 큐레이터 챗봇 (장소 카드 인라인 렌더)
5. 상세 페이지 (4관점 + 영문 토글 + 카카오·네이버 지도 딥링크 + 저장·공유)
6. 무장애 편의시설 태그 (열린관광 API)

## 팀 조직
- 🛠️ **개발팀**: 기능 구현 + Vercel 배포 (쿤스튜디오 단독)
- 💬 **고객센터팀**: `support_agent.py` — 텔레그램 /korlens_support 처리
- 📊 **수집부 연계**: `../intelligence/watch.py korlens` — 경쟁사 모니터링
- 🎯 **공모전 연계**: `../intelligence/contests_watch.py` — 지원 가능 공모전 발굴

## 주요 경쟁사 (수집부 추적)
- 대한민국 구석구석 (공식, korean.visitkorea.or.kr)
- 트리플 (triple.guide)
- 마이리얼트립 (myrealtrip.com)
- Mindtrip (mindtrip.ai) · Layla (layla.ai)

## 주요 일정
- 2026-05-06 16:00: 공모전 접수 마감 (완료)
- 2026-05 중: 예비심사 + OT
- 2026-05~09: 서비스 개발·컨설팅 지원
- 2026-10: 1차·최종심사
- 2026-11: 시상식
