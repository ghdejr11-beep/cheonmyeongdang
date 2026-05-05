# AI 콘텐츠 품질 — 본인 얼굴/목소리 30초 인트로 가이드 (사용자만 가능)

**문제**: K-Wisdom / 천명당 / 다른 채널 모두 100% AI generated → YouTube 2026 AI slop 정책 위험 (memory whisper_atlas_pivot).
**해결**: 매 영상 첫 30초만 본인 얼굴 / 목소리 인서트 → "human-verified" 신호.

## 1. 장비 (이미 보유)

- 갤럭시 폰 카메라 (4K) — 추가 구매 X
- 무선 마이크 또는 폰 내장 (조용한 방이면 OK)
- 자연광 (창가 / 오전 10~12시)

## 2. 30초 인트로 스크립트 템플릿 (한국어 / 영문)

### 한국어 (천명당 / K-Wisdom 한국어 콘텐츠)
> "안녕하세요, 쿤스튜디오 홍덕훈입니다.
> 오늘은 [주제] 에 대해 정리해봤어요.
> 천명당의 무료 풀이를 만들면서 알게 된 [insight 1줄] 도 함께 공유드립니다.
> 끝까지 보시면 [구체적 가치] 받으실 수 있어요. 시작합니다."

### 영문 (K-Wisdom global / en/saju)
> "Hi, I'm Hong, the founder of KunStudio in Korea.
> Today we're looking at [topic].
> One thing I learned while building Cheonmyeongdang's free Saju engine: [insight].
> Stick around — by the end you'll [specific value]. Let's start."

## 3. 촬영 워크플로우 (5분/영상)

1. 폰 거치 → 정면 frame (아이레벨)
2. 자연광 측면 (정면 라이트 X — flat 보임)
3. 30초 1테이크 OK 면 끝 (NG 2회 max)
4. 클로드에게 영상 파일 경로 알려주면 → ffmpeg 자동 cut + 색보정 + 자막 + AI generated 본문 영상 앞에 자동 결합

## 4. 자동화 가능 부분 (클로드)

- ffmpeg 자동 결합 (`departments/media/src/intro_merger.py` — 사용자 30초 클립 + AI 본문 자동 prepend)
- 자막 자동 생성 (Whisper API, $0.006/분)
- 썸네일 자동 (얼굴 frame 1장 추출 + 텍스트 오버레이)
- 업로드 자동 (Upload-Post API)

## 5. 빈도 권장

- 첫 1주: 매 영상 30초 인트로 (5건)
- 2주~: 주 3건 인트로 + 주 4건 AI only (mix 가 더 자연스러움)
- 1개월~: ratio 측정 후 조정 (engagement 증가하는 패턴 유지)

## 6. 회피 표현 (memory `legal_safety_first`)

- 의료 효과 / 투자 보장 / 도박 권유 표현 X
- 특정 업체·연예인 거론 X (memory `no_specific_company_names`)
- 본인 전화번호 / 주민번호 마스킹 (memory `phone_number_masking`)

## 7. 사용자 1클릭 액션

폰으로 30초 인트로 1개 촬영 → D:\ 어딘가 저장 → "intro 찍었어, 영상 X 에 합쳐줘" 라고 알려주시면 ffmpeg 자동 결합 + 업로드.
