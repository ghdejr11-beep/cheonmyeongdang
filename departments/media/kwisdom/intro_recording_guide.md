# K-Wisdom 30초 인트로 녹화 가이드 (사용자 1회 액션)

**왜 필요한가**: YouTube 2026 AI slop 정책 회피. 본인 얼굴/목소리 30초가 25개 영상에 자동 합성됩니다.

**총 소요 시간**: 5분 (촬영 1분 + 재촬영 여유 4분)

---

## 1. 준비 (1분)

- 갤럭시 폰 (4K) — 거치대 또는 책 위에 세팅
- **자연광**: 창가, 오전 10~12시 권장 (정면에 라이트 두지 말 것 — flat하게 나옴)
- 옷: 무지 (단색 셔츠 OK), 패턴 X
- 배경: 책장 / 흰 벽 / 작업실 (간소하게)

---

## 2. 영문 스크립트 (30초, 외울 필요 X — 종이에 적어 화면 옆에 두기)

```
Hi, I'm Hong from KunStudio in Korea.

I run Cheonmyeongdang, a free Korean Saju engine,
and I share what I learn about Korean culture,
travel, design, and indie founder life.

Stick around to the end — there's always one
free tool you can use today. Let's go.
```

**팁**:
- 카메라 렌즈를 정확히 보기 (스크립트 읽지 말고 카메라 = "사람")
- 천천히 (약 110 단어/분 페이스)
- 마지막 "Let's go." 에서 살짝 미소

---

## 3. 촬영 (3분)

1. 폰 16:9 가로 모드, 4K 30fps
2. 1테이크 → OK면 끝
3. NG 시 최대 2회 재촬영
4. 30초 안 넘기면 OK (32~35초도 자동 trim)

---

## 4. 저장 + 알림

저장 위치: `D:\KunStudio\intro\kwisdom_intro_master.mp4`
(없으면 어디든 OK — 클로드에게 경로 알려주면 자동 이동)

녹화 후 클로드에게:
> "K-Wisdom 인트로 녹화 끝. 경로: D:\... \kwisdom_intro_master.mp4"

→ 자동 처리:
1. ffmpeg crop/색보정 (정사각형 잘림 방지)
2. 영문 자막 자동 (Whisper)
3. 25개 영상 본문에 자동 prepend
4. schtask `KunStudio_KWisdom_Daily` 가 매일 07:00 자동 업로드

---

## 5. 회피 사항 (memory feedback 준수)

- 본인 전화번호 / 사업자번호 / 주소 노출 X
- 다른 회사 / 연예인 / IP 실명 X
- 가족 / 박솔이 등 다른 사람 얼굴 X
- 천명당 / KORLENS / KunStudio 만 언급 OK

---

## 6. 향후 (선택)

3개월 뒤 새 인트로 녹화 권장 (옷/배경 변화 = 알고리즘 health 신호).
당장은 1개로 25 영상 충분.
