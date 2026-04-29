# 🎮 신규 게임 디자인 체크리스트 (30항목)

> 매번 처음부터 디자인 안 하기 위한 표준 절차

## Phase 1: 기획 (5항목)
- [ ] 1. 게임 이름 + 패키지명 (`com.kunstudio.<name>`) 결정
- [ ] 2. 장르 분류 (퍼즐 / 캐주얼 / 시뮬레이션 / 액션)
- [ ] 3. 타겟 색상 선택 (`brand_guide.md` 게임별 메인 색상 표 참조)
- [ ] 4. 마스코트 필요 여부 결정 (있으면 `characters/mascot_palette.json` 추가)
- [ ] 5. 1줄 광고 카피 (예: "황금곰과 비누방울 터뜨려라")

## Phase 2: 시각 디자인 (10항목)
- [ ] 6. 시작화면 = `templates/start_screen.html` 복제 → 색상/제목 교체
- [ ] 7. 게임 오버 = `templates/game_over.html` 복제
- [ ] 8. 일시정지 모달 = `templates/pause_modal.html` 복제
- [ ] 9. 튜토리얼 = `templates/tutorial_overlay.html` 복제
- [ ] 10. 앱 아이콘 512×512 (Pillow 자동 생성, 단색 배경 + 게임 핵심 모티프)
- [ ] 11. Feature Graphic 1024×500 (그라데이션 배경 + 큰 캐릭터)
- [ ] 12. 휴대전화 스크린샷 1080×1920 × 4장 (게임 중 / 메뉴 / 결과 / 캐릭터)
- [ ] 13. 7인치 태블릿 1024×600 × 2장
- [ ] 14. 10인치 태블릿 1920×1200 × 2장
- [ ] 15. (옵션) Play Games 로고 600×400

## Phase 3: 사운드 (5항목)
- [ ] 16. BGM (Web Audio 합성 또는 `assets/bgm/` 재사용)
- [ ] 17. 효과음 4종 이상 (`assets/sounds/` 재사용 가능)
  - 시작 (game_start.mp3)
  - 액션 (action.mp3)
  - 콤보 (combo_pentatonic.mp3)
  - 게임오버 (gameover.mp3)
- [ ] 18. 사운드 ON/OFF 토글 우측 상단
- [ ] 19. 볼륨 슬라이더 (옵션 메뉴)
- [ ] 20. iOS Safari 자동재생 정책 회피 (사용자 첫 탭 후 BGM 시작)

## Phase 4: AdMob 통합 (3항목)
- [ ] 21. 배너 광고 ID 발급 + 시작/오버 화면만 노출
- [ ] 22. 보상 광고 (선택) — "광고 보고 코인 +50"
- [ ] 23. AdMob auth setup (`departments/sales-collection/admob_auth_setup.py` 활용)

## Phase 5: 빌드 + 출시 (5항목)
- [ ] 24. Capacitor wrap → Android Studio 빌드
- [ ] 25. AAB 서명 (`D:\kunstudio-games\kunstudio.keystore`)
- [ ] 26. Play Console 등록 (영어 메타 입력 패턴)
- [ ] 27. BETA FLOW ₩9,000 결제 (12명 14일)
- [ ] 28. 14일 후 프로덕션 출시 클릭

## Phase 6: 마케팅 (2항목)
- [ ] 29. multi_poster.py로 7채널 동시 발행 (시작 화면 스크린샷 + 1줄 카피)
- [ ] 30. AI Side Hustle 쇼츠 1편 (Pollinations + ElevenLabs TTS)

---

## 신규 게임 평균 디자인 시간 (목표)
- 1게임 처음부터 만들면: 8~16시간
- 이 체크리스트로 만들면: **3~5시간**
- KunStudio 자동 빌드 + 자동 메타 입력 사용 시: **1~2시간**

## 자동화 가능 항목 (이 폴더에 스크립트 추가 예정)
- `scripts/generate_assets.py` — 색상만 입력하면 아이콘/feature/태블릿 자동 생성
- `scripts/setup_capacitor.py` — Capacitor wrap 자동
- `scripts/admob_register.py` — AdMob 광고 단위 자동 발급

## 업데이트 룰
- 게임 출시 후: `logs/design_decisions.md` 에 "왜 이렇게 했는지" 1단락 기록
- 신규 패턴 발견: 이 체크리스트에 항목 추가
