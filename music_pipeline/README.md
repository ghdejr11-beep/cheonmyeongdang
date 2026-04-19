# music_pipeline — YouTube 자동 업로더 2026 최적화 애드온

기존 `auto_watcher.py` (8시간 BGM 루프) + `lyrics_watcher.py` (AI 작사작곡) +
`youtube_uploader.py` 에 **최소 수정으로 끼워 넣는** 강화 모듈 모음.

2026 유튜브 리서치(상위 채널 분석 + 정책 업데이트)를 기반으로 P1~P3
우선순위로 구성.

## 파일 구성

```
music_pipeline/
├── README.md                       ← 이 파일
├── INTEGRATION.md                  ← 기존 코드에 붙이는 구체 가이드
└── enhancements/
    ├── __init__.py
    ├── ai_label.py                 [P1] AI 합성 라벨 + human input 증거
    ├── chapter_generator.py        [P1] YouTube 챕터 자동 생성
    ├── ass_subtitles.py            [P2] ASS 자막 (Montserrat / 페이드)
    ├── thumbnail_maker.py          [P2] 장르별 썸네일 1280x720
    ├── pinned_comment.py           [P2] 업로드 직후 고정 댓글
    ├── shorts_extractor.py         [P3] 하이라이트 9:16 Shorts
    └── purpose_playlists.py        [P3] 용도 플리 다중 추가
```

## 우선순위별 요약

### 🥇 P1 — 수익화 방어 (지금 당장)
- **ai_label.py**: YouTube 2025.7 정책 — `containsSyntheticMedia=True`
  누락 시 영구 데모네타이즈. 설명에 human-input 증거 푸터 자동 주입.
- **chapter_generator.py**: 8시간 루프에 8개 챕터 자동 생성. 시청
  지속률 +10~20%. 3분 미만 곡은 자동 스킵.

### 🥈 P2 — 완성도 점프 (이번 주)
- **ass_subtitles.py**: SRT → ASS 변환으로 폰트·페이드·외곽선 자유도
  확보. 발라드/팝/로파이/감성 4개 프리셋.
- **thumbnail_maker.py**: 장르별 컬러 프리셋 + 한글 후킹 카피 + 장르
  영문 라벨 (Cafe Music BGM 공식). 후킹 카피 12종 내장.
- **pinned_comment.py**: 업로드 직후 본인 댓글 자동 게시 (플리 링크 +
  챕터 안내 + 다음 업로드 예고).

### 🥉 P3 — 알고리즘 공략 (이번 달)
- **shorts_extractor.py**: 롱폼에서 50초 Shorts 자동 추출. RMS 기반
  하이라이트 감지 (librosa 불필요). 9:16 블러 배경 + 훅 텍스트.
- **purpose_playlists.py**: "공부할 때", "카페 분위기" 등 12개 용도
  플리에 동시 추가. 검색 노출 2배.

## 설치

1. 이 폴더를 `C:\Users\쿤\Desktop\cheonmyeongdang\music_pipeline\` 로 복사
2. `pip install Pillow`
3. YouTube 에 용도 플리 12개 미리 생성 (INTEGRATION.md 참조)
4. 기존 `youtube_uploader.py` / `auto_watcher.py` / `lyrics_watcher.py`
   에 `INTEGRATION.md` 의 diff 적용

## 자체 테스트

모든 모듈은 `python 모듈명.py` 로 단독 실행 가능.
외부 의존성은 **Pillow** 와 **ffmpeg** (shorts_extractor 만) 뿐.

```bash
python enhancements/ai_label.py
python enhancements/chapter_generator.py
python enhancements/ass_subtitles.py
python enhancements/thumbnail_maker.py
python enhancements/pinned_comment.py
python enhancements/shorts_extractor.py
python enhancements/purpose_playlists.py
```

## 기대 효과 (2026 상위 채널 리서치 기반)

| 개선안 | 구현 시간 | 예상 효과 |
|---|---|---|
| P1 (라벨+챕터) | 30분 | 수익화 유지, 지속률 +10~20% |
| P2 (자막+썸네일+고정댓) | 1~2일 | CTR +30~50% |
| P3 (Shorts+용도플리) | 3~7일 | 유입 2배, 완성도 상용급 |

## 다음 단계 (여기 포함 안 됨)

- **비트 매칭** (BPM 감지 + Ken Burns 씬 전환) — librosa 필요
- **AI 생성 영상 클립** (Kling 3.0 / Runway Gen-4 / Veo 3.1) — API 키
- **립싱크** (Sync Labs API) — 분당 $0.50
- **24/7 라이브 스트림** (Lofi Girl 모델) — 별도 설계 필요
