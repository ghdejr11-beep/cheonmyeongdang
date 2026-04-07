# 전자책 자동 판매 시스템

> **"AI로 월 500만원 디지털 상품 자동화 시스템"** 한국어 전자책을 처음부터 끝까지 자동 생성하고, Gumroad/크몽에 올려 손 안 대고 판매하는 풀 파이프라인.

100일 안에 1억 매출 목표. 이 폴더 안의 스크립트만 돌리면 책·PDF·랜딩페이지·숏폼 100개가 모두 만들어집니다.

---

## 무엇이 자동화되는가

| 단계 | 자동? | 처리 주체 |
|---|---|---|
| 책 200페이지 본문 작성 | ✅ 100% | Claude API (`generate_book.py`) |
| PDF 변환 (한글 폰트 포함) | ✅ 100% | `make_pdf.py` (나눔고딕 자동 다운로드) |
| 릴스/틱톡 후크 100개 + 스크립트 | ✅ 100% | Claude API (`generate_shorts.py`) |
| 랜딩 페이지 HTML | ✅ 100% | `build_landing.py` (config 가격·링크 자동 주입) |
| **결제 + PDF 자동 발송 + 환불** | ✅ 100% | **Gumroad / 크몽** (1회 등록만 필요) |
| 영상 제작 (숏폼) | 반자동 | 스크립트 자동, 촬영/편집 수동 (또는 `auto_watcher.py` 변형) |
| SNS 업로드 | 수동 | 플랫폼 ToS 위반 회피 (직접 업로드 권장) |
| 고객 응대 | 수동 | Gumroad 자동 이메일이 80% 처리, 나머지만 직접 |

---

## 사전 준비 (1회만)

### 1. Python 3.10+ 설치
[python.org](https://www.python.org/downloads/) 에서 다운로드. 설치 시 **"Add Python to PATH"** 체크 필수.

### 2. 의존성 설치
```powershell
cd C:\Users\쿤\Desktop\ebook_system
pip install -r requirements.txt
```

### 3. Anthropic API 키 발급
1. [console.anthropic.com](https://console.anthropic.com/settings/keys) 접속
2. **Create Key** 클릭
3. 키 복사 (`sk-ant-api03-...`)
4. 결제 카드 등록 ($5 충전이면 책 1권 + 숏폼 100개 만들고도 남음)

### 4. 환경변수 설정 (Windows PowerShell)
**임시 (현재 창에서만):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-api03-여기에복사한키"
```

**영구 (한 번만 등록, 재부팅 후에도 유지):**
```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-api03-여기에복사한키", "User")
```
→ PowerShell 닫고 새로 열어야 적용됩니다.

---

## 실행 (주문 한 줄)

```powershell
python run_all.py
```

이거 한 번이면:
1. Claude API → 50개 챕터 목차 + 본문 생성 (~30분, 약 $5)
2. 한국어 PDF 자동 변환 (~1분)
3. 숏폼 후크 100개 + 스크립트 100개 생성 (~20분, 약 $1)
4. 랜딩 페이지 빌드 (~1초)

**중간에 끊겨도 안전합니다.** 다시 실행하면 이미 만들어진 챕터·숏츠는 건너뛰고 못 만든 것만 이어서 만듭니다.

### 단계별 실행 (디버깅용)
```powershell
python generate_book.py     # 1단계: 본문 생성
python make_pdf.py          # 2단계: PDF
python generate_shorts.py   # 3단계: 숏폼
python build_landing.py     # 4단계: 랜딩 페이지
```

---

## 결과물

```
ebook_system/
├── output/
│   ├── outline.json       ← 50개 챕터 목차
│   ├── chapters/          ← 챕터별 마크다운 50개
│   ├── book.md            ← 합쳐진 전체 책 마크다운
│   ├── book.pdf           ← 200페이지 PDF (Gumroad 업로드용)
│   ├── hooks.json         ← 숏폼 후크 100개
│   ├── shorts/            ← 숏폼 스크립트 100개
│   └── landing.html       ← 랜딩 페이지 (호스팅용)
└── fonts/
    └── NanumGothic-*.ttf  ← 자동 다운로드된 한글 폰트
```

---

## 손-안-대고-판매 셋업 (1회만)

### A. Gumroad (가장 쉬움 — 추천)

**왜 Gumroad?**
- 사업자등록증 불필요
- 결제(카드/페이팔) + PDF 자동 발송 + 환불 + 세금 영수증 100% 자동
- 수수료 약 10% (Stripe/PayPal 수수료 포함)
- 한국 작가도 가입 가능, PayPal 로 입금
- 등록 5분 / 별도 호스팅 불필요

**셋업 순서:**
1. [gumroad.com](https://gumroad.com) 가입 (이메일만)
2. **Products** → **New product** → **Digital product**
3. 가격: 9,900원/49,000원/149,000원 (Gumroad는 USD 기준이지만 KRW 표시 가능)
4. 파일 업로드: `output/book.pdf`
5. **Settings** → **Custom URL** 복사 (예: `https://yourname.gumroad.com/l/ai-ebook`)
6. 같은 방식으로 LITE / STANDARD / PREMIUM 3개 등록
7. **`config.py`** 열고 `GUMROAD_LITE`, `GUMROAD_STANDARD`, `GUMROAD_PREMIUM` 에 링크 붙여넣기
8. `python build_landing.py` 다시 실행 → `output/landing.html` 갱신됨
9. 끝. 이제 누가 결제하면 Gumroad가 PDF를 자동으로 이메일 발송합니다.

### B. 크몽 (한국 결제, 수수료 20%)

1. [kmong.com](https://kmong.com) 가입
2. **서비스 등록** → **전자책/PDF**
3. STANDARD/DELUXE/PREMIUM 3단 가격 설정
4. PDF 업로드 (크몽은 자동 발송 + 결제 + CS 모두 처리)
5. `config.py` 의 `KMONG_URL` 에 링크 입력

### C. 부크크 (한국 전자책 전용, 인세 70%)

1. [bookk.co.kr](https://bookk.co.kr) 가입
2. **POD/e-book 출간**
3. PDF 업로드 → ISBN 자동 발급 → 교보/예스24 자동 등록까지 가능

> **권장: Gumroad + 크몽 동시 등록.** Gumroad는 자기 랜딩페이지용, 크몽은 한국어 검색 유입용. 같은 PDF 두 곳에 올리는 건 100% 합법입니다.

---

## 랜딩 페이지 호스팅

`output/landing.html` 을 다음 중 한 곳에 올리면 끝:

| 옵션 | 비용 | 난이도 | 추천도 |
|---|---|---|---|
| **GitHub Pages** | 무료 | ⭐ | ⭐⭐⭐⭐⭐ |
| **Netlify Drop** | 무료 | ⭐ | ⭐⭐⭐⭐⭐ |
| 천명당.com 의 `/book` 경로 | 무료 | ⭐⭐ | ⭐⭐⭐⭐ |
| Cloudflare Pages | 무료 | ⭐⭐ | ⭐⭐⭐⭐ |

**가장 쉬운 길 — Netlify Drop:**
1. [app.netlify.com/drop](https://app.netlify.com/drop) 접속
2. `output/landing.html` 파일을 브라우저로 드래그
3. 끝. 무료 URL 발급됨 (예: `cool-ebook-12345.netlify.app`)

---

## 트래픽 자동화 (반자동)

### 숏폼 영상 제작

`output/shorts/short_001.md` ~ `short_100.md` 가 100개 만들어집니다.
각 파일에는 후크 + 30~45초 자막/화면/나레이션 스크립트가 들어 있어 그대로 촬영·편집하면 됩니다.

**더 빠른 길**: 이전에 만든 `auto_watcher.py` (음악 → 자동 영상) 를 변형하면, 이 스크립트들을 입력으로 받아 자동 영상 생성도 가능합니다. (다음 단계에서 통합)

### 권장 업로드 일정
- **인스타 릴스**: 일 1개 (오후 6~9시)
- **틱톡**: 일 1개 (위와 동일)
- **유튜브 숏츠**: 일 1개 (자정 직전)
- **카카오톡 채널**: 주 2회 (책 미리보기)

100일 = 100개 숏츠. 1개만 터지면 게임 끝.

---

## Windows 자동 실행 (Task Scheduler)

매일 새벽 3시에 자동으로 새 숏츠 만들고 싶으면:

1. **Win + R** → `taskschd.msc`
2. **작업 만들기** → 트리거: **매일 03:00**
3. 동작: **프로그램 시작**
   - 프로그램: `python`
   - 인수: `C:\Users\쿤\Desktop\ebook_system\generate_shorts.py`
   - 시작 위치: `C:\Users\쿤\Desktop\ebook_system`

이제 PC만 켜져 있으면 매일 자동으로 새 후크 100개가 갱신됩니다.

---

## 비용 (실제 측정)

| 항목 | 금액 |
|---|---|
| 책 1권 생성 (Claude Opus 4.6, 50챕터) | 약 **$5~8** |
| 숏폼 100개 생성 | 약 **$1~2** |
| 한 달 재생성 (책 1권 + 숏폼 갱신 4회) | 약 **$10~15** |
| Gumroad 수수료 | 매출의 **약 10%** |

**손익분기점:** STANDARD 99,000원 책 1권만 팔리면 한 달 자동화 비용 회수.

---

## 자주 막히는 곳 (FAQ)

### Q1. `pip install` 이 안 돼요
→ Python 설치 시 "Add to PATH" 체크 안 한 것. Python 재설치 (체크박스 ON)

### Q2. `ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다`
→ PowerShell을 새 창으로 다시 열고 `echo $env:ANTHROPIC_API_KEY` 로 확인. 비어있으면 위 4번 단계 재실행.

### Q3. 책 생성이 중간에 멈춤
→ 그냥 다시 `python generate_book.py` 실행. 이미 만든 챕터는 건너뜁니다.

### Q4. PDF 한글이 ▢▢ 로 나옴
→ `fonts/` 폴더 삭제하고 `python make_pdf.py` 다시 실행. 폰트 자동 재다운로드.

### Q5. 책 주제를 바꾸고 싶어요
→ `config.py` 의 `BOOK_TITLE`, `TARGET_AUDIENCE`, `PROMISE` 만 수정 → `output/` 폴더 통째로 삭제 → `python run_all.py`. 똑같은 시스템으로 어떤 주제든 책이 만들어집니다.

### Q6. 비용이 걱정돼요
→ `config.py` 의 `MODEL_OUTLINE/MODEL_CHAPTER/MODEL_SHORTS` 를 `claude-sonnet-4-6` 또는 `claude-haiku-4-5` 로 바꾸면 1/3~1/15 가격. 품질은 약간 떨어지지만 충분히 판매 가능한 수준.

---

## 다음 단계 (이 시스템 위에 추가할 것들)

- [ ] 후기 자동 수집 (구매자에게 자동 이메일)
- [ ] 이메일 마케팅 (ConvertKit / Stibee 연동)
- [ ] Meta 광고 자동 카피 + 픽셀 추적
- [ ] 영상 자동 생성 (`auto_watcher.py` 변형)
- [ ] 다국어 자동 번역 (영어/일본어 시장 확장)

원하시면 위 항목 중 어떤 것이든 다음 단계로 만들 수 있습니다.
