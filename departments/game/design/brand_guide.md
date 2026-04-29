# 🎨 KunStudio 게임 브랜드 가이드

## 1. 색상 시스템

### Primary Brand
- **KunStudio Gold**: `#FFD700` (로고 + CTA 강조)
- **KunStudio Black**: `#1A1A1A` (텍스트 + 배경)
- **KunStudio White**: `#FAFAFA` (UI 베이스)

### 게임별 메인 색상 (장르별)
| 게임 | 메인 | 액센트 | 다크 |
|------|------|--------|------|
| Bubble Pop Blast | `#FF9864` (sunset) | `#FFD86F` | `#3D2914` |
| Gem Cascade | `#9B59B6` (gem) | `#F1C40F` | `#2C0E3F` |
| Stack Builder | `#3498DB` (sky) | `#2ECC71` | `#0E2F4A` |
| Bottle Sort Korea | `#E74C3C` (한국 적) | `#F39C12` | `#7B0E07` |
| Tetris AI Battle | `#2ECC71` (네온) | `#FF00FF` | `#0F1A1A` |
| HexDrop | `#FF6B35` (hex) | `#1A535C` | `#0A0E27` |

### 기능별 색상 (모든 게임 공통)
- ✅ Success: `#2ECC71`
- ⚠️ Warning: `#F1C40F`
- ❌ Error: `#E74C3C`
- ℹ️ Info: `#3498DB`
- 💎 Combo: `#FF00FF` (모든 게임 콤보 강조)

## 2. 타이포그래피

### 한글
- **Heading**: Noto Sans KR Black (900) - 게임 타이틀
- **Body**: Noto Sans KR Bold (700) - UI 텍스트
- **Caption**: Noto Sans KR Regular (400) - 작은 라벨

### 영문
- **Heading**: "Bungee" / "Press Start 2P" (게임 느낌)
- **Body**: Inter / SF Pro Display
- **Mono**: JetBrains Mono (점수/타이머)

### 절대 금지
- ❌ Comic Sans
- ❌ Times New Roman
- ❌ Arial Bold (너무 generic)

## 3. 픽셀 그래픽 정책

### 사용 X (메모리 룰)
- 픽셀 아트는 사용하지 않음 (사용자 명시 룰)
- 이모지 X (게임 내 텍스트)

### 사용 O
- Lucide 아이콘 (벡터)
- 자체 SVG 아이콘
- Pillow로 자동 생성한 dot/circle/star 형태

## 4. 캐릭터 디자인 룰

### 마스코트 통일 룰
- 큰 눈 + 둥근 형태 (친근함)
- 4표정 필수: idle(😌), cheer(😄), sad(😢), surprised(😲)
- 3D vs 2D: 캐주얼은 2D flat, 시뮬레이션은 3D 가능
- 색상 캐릭터는 2~3가지 메인 색만 사용 (단순화)

### 특수 캐릭터
- Bubble Pop: 황금곰 — sunset 황금색 + 흰 배 + 검은 눈
- Stack Builder: 큰눈 미니 캐릭터 — `#FFE15D` + `#000`
- Gem Cascade: 6보석 모두 둥근 형태 (5% 확률 표정)

## 5. 사운드 / BGM

### BGM 룰
- 솔로: 100~108 BPM (편안)
- 배틀: 120~135 BPM (긴장)
- 시즌: 한국 5음계 또는 펜타토닉 (한국 정서)

### 효과음
- pop/swap: 짧은 sine wave 808Hz~1200Hz
- combo: ascending pentatonic (C-D-E-G-A)
- gameover: descending minor

## 6. UI 일관성

### 모든 게임 필수
- 시작화면: 큰 타이틀 (60% 비중) + Play 버튼 (24%) + 옵션 아이콘 (16%)
- 게임 오버: 점수 + Restart 버튼 + 메인 메뉴
- 일시정지: 모달 + 검은 반투명 배경 (rgba(0,0,0,0.6))
- 사운드 ON/OFF 토글: 우측 상단 고정

### 절대 금지
- ❌ 가운데 정렬 텍스트 + 좌측 정렬 텍스트 혼재
- ❌ 빨간 + 파란 동시 사용 (눈 피로)
- ❌ 그림자 5단계 이상 (단순함 유지)

## 7. 광고 통합

### AdMob 배너
- 위치: 화면 하단 (게임 영역 침해 X)
- 크기: 320×50 또는 728×90
- 게임 진행 중에는 X (시작/게임오버 화면만)

### 보상 광고
- "광고 보고 코인 +50" 류
- 사용자 선택형, 강제 X
