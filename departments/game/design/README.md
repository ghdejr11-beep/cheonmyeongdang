# 🎨 게임 디자인팀

> KunStudio 게임 디자인 표준화 + 매번 손대지 않게 템플릿/플레이북 보유

## 미션
- 게임 출시 시 디자인 검수 시간 80% 단축
- KunStudio 6게임 일관된 비주얼 정체성 유지
- 신규 게임 = 템플릿 복제 → 색상/캐릭터만 교체

## KunStudio 6게임 등록 디자인 메모

| 게임 | 메인 색상 | 캐릭터 | 콘셉트 | 출시 상태 |
|------|----------|--------|--------|----------|
| **Bubble Pop Blast** | `#FF9864` 황혼 오렌지 | 황금곰 (idle/cheer/sad) | sunset 캐주얼 + Bossa Nova BGM | BETA FLOW |
| **Gem Cascade** | `#9B59B6` 보석 보라 | 6보석 (5% 표정) | 매치-3 + 7이펙트 | BETA FLOW |
| **Stack Builder** | `#3498DB` 시원 파랑 | 큰눈 캐릭터 4표정 | 하이퍼 캐주얼 + 펜타토닉 | BETA FLOW |
| **Bottle Sort Korea** | `#E74C3C` 한국 적 | (없음) | 오방색·한복·한약방·단오 4챕터 | BETA FLOW |
| **Tetris AI Battle** | `#2ECC71` 형광 | (없음) | 데스매치 + 5+콤보 GREAT/AMAZING/INSANE | BETA FLOW |
| **HexDrop** | `#FF6B35` 헥스 오렌지 | (없음) | 6각 블록 매치 | BETA FLOW (ID 다름) |

## 디렉토리 구조
```
design/
├── README.md (이 파일)
├── brand_guide.md (색상·폰트·로고)
├── templates/
│   ├── start_screen.html (시작화면 템플릿)
│   ├── game_over.html
│   ├── pause_modal.html
│   └── tutorial_overlay.html
├── characters/
│   ├── mascot_palette.json (캐릭터별 색상)
│   ├── mascot_emotions.md (idle/cheer/sad/angry/surprised 룰)
│   └── design_specs.md
├── assets/
│   ├── icons/ (공용 아이콘 SVG)
│   ├── sounds/ (효과음)
│   └── bgm/ (배경음악)
├── playbooks/
│   ├── new_game_checklist.md (신규 게임 디자인 체크리스트 30항목)
│   ├── ui_consistency.md (UI 일관성 규칙)
│   └── ascii_naming.md (자산 명명 규칙)
└── logs/
    └── design_decisions.md (왜 이 색/폰트를 선택했는지 기록)
```

## 신규 게임 만들 때 워크플로
1. `playbooks/new_game_checklist.md` 30항목 체크
2. `templates/start_screen.html` 복제 → 색상/제목만 교체
3. `characters/mascot_palette.json` 에 신규 캐릭터 색상 추가
4. `assets/icons/` 에서 공용 아이콘 가져옴 (재사용)
5. `logs/design_decisions.md` 에 왜 이렇게 했는지 메모

## 업데이트
- 2026-04-26: 부서 신설
- 향후: KDP 표지 룰 (`departments/ebook/`) 참조해서 게임 표지/feature 그래픽도 표준화
