# CLAUDE.md - 프로젝트 지침 및 분석 프레임워크

## 사용자 프로필
- 이름: 홍덕훈
- 환경: Windows, 노트북 + 집 PC (hdh02 계정)
- 경로: `C:\Users\쿤\Desktop\cheonmyeongdang\` (노트북), `C:\Users\hdh02\Desktop\cheonmyeongdang_ebook\` (집 PC)
- 수준: 초보자 (항상 쉽게, 전체 경로 표시)
- 100일 목표: 1억 / 24개월 목표: 100억

---

## 🧪 테스트 원칙 (⭐ 절대 원칙)

**"테스트할 때는 정확한 방식으로, 검증된 방법으로 한다."**

### 반드시 지킬 것

1. **가짜 데이터 말고 실제 데이터로 테스트**
   - 내가 지어낸 샘플 텍스트 ❌
   - 사용자가 실제로 쓰는 파일/데이터 ✅
   - 실제 파일에 접근 불가능하면 → 사용자에게 대표 샘플 받기

2. **검증된 방법만 사용**
   - 이전에 작동한 방식 먼저 시도 (예: reportlab 은 다른 프로젝트에서 검증됨)
   - 새로운 라이브러리는 "이게 될 것 같아" 대신 "이건 확실히 된다" 확인 후 사용
   - 샌드박스에서 통과했다고 → 사용자 환경에서도 된다고 가정 ❌
   - 사용자 환경 특수성 (Windows, Python 버전, 한글 경로) 먼저 확인

3. **통과 못 하면 커밋 금지**
   - 구문 검사 (py_compile) 통과 ✓
   - 실행 테스트 통과 ✓
   - 사용자가 직면할 에러 케이스 (한국어, 긴 문장, 특수문자) 통과 ✓
   - 위 3개 중 하나라도 실패 → 커밋하지 말고 수정

4. **사용자에게 "이거 돌려봐" 하기 전에 내가 먼저 돌려본다**
   - 샌드박스에서 실행 → 에러 재현 → 수정 → 재실행 → 통과 확인 → 그 다음 사용자에게
   - 사용자를 디버거로 쓰지 말 것 (시간·에너지 낭비)

5. **⭐⭐⭐ 모든 명령·주장·API 호출은 반드시 검색 후 팩트만 말한다 (최우선 절대 원칙) ⭐⭐⭐**
   - **적용 범위: 외부 서비스뿐 아니라 모든 기술적 주장 전부**
     - API 호출 형식, URL 파라미터, CLI 명령어 옵션, 배포 절차, 설정값
     - GitHub Actions, YouTube, Telegram, Suno, Anthropic, Render, Google Calendar, 카카오 등
   - **절차: 주장하기 전에 반드시 WebSearch → 공식 문서 확인 → 출처 URL 명시**
   - **금지 표현**: "기억으론", "보통", "~일 거다", "아마", "should work"
   - **허용 표현**: "검색 결과에 따르면 [URL]", "공식 문서 기준으로"
   - 모르면 **"모르겠다, 검색해볼게"** 라고 솔직히 말하고 검색
   - **API 호출 코드 작성 시**: 반드시 공식 API 문서의 실제 예제를 검색해서 확인 후 작성. 기억으로 추측해서 API 형식 만들지 말 것 (Render API 400 에러 재발 방지)
   - **재발 사례** (꼭 기억):
     - YouTube 15분 제한 → 검색 안 하고 "verify 가면 풀린다" 추측 → 사용자가 이미 검증된 상태인데 또 추측 → 망신
     - YouTube 12시간 한도 → 검색 안 하고 "12시간이 한도" 라고만 알려줌 → 사용자 영상 삭제됨
     - GitHub Actions workflow_dispatch → 검색 안 하고 "main 브랜치에서만 작동" 단언 → 맞긴 했지만 검색 후 답했어야 함
     - Suno + YouTube 수익화 → 처음엔 12시간 BGM 추천 → 나중에 검색해보니 정적 이미지 = 수익화 거절. 처음부터 검색했어야 함
     - Render API 형식 → 검색 안 하고 추측으로 JSON body 작성 → 400 Bad Request. 공식 문서 확인했어야 함

6. **라이브러리 호환성 함정 피하기**
   - `fpdf2`: 한국어 긴 문장 + 특수문자 조합에서 "Not enough horizontal space" 에러 → 사용 금지, reportlab 사용
   - `cryptography` 바인딩 이슈: 샌드박스에서 import 실패해도 사용자 Windows 에선 작동하는 경우 있음
   - API 키 환경변수: `\n` 자동 strip 필수
   - PowerShell vs CMD: Copy-Item / [Environment]:: 는 PowerShell 전용
   - **ffmpeg drawtext + 한국어 경로**: Windows ffmpeg 은 non-ASCII 폰트 경로 못 읽음 → ASCII 경로 (`C:\Windows\Fonts\malgun.ttf`) 사용
   - **subprocess Korean Windows**: `text=True` 만 쓰면 CP949 디코딩 크래시 → `encoding='utf-8', errors='replace'` 명시
   - **cmd.exe 배치 파일 인코딩**: `chcp 65001` 은 출력 코드페이지만 바꿈, **파서는 OEM 코드페이지 (CP949)** 라서 `→`, `✓` 같은 특수 unicode 가 echo 줄을 깨뜨림 → 배치 파일은 ASCII + Hangul 만 (특수 화살표·체크 금지)

### 실패 사례 기록 (재발 방지)

| 사례 | 원인 | 해결 |
|---|---|---|
| fpdf2 FPDFException | 긴 한국어 + 특수문자 | reportlab 으로 전환 |
| API 키 노출 (2회 이상) | 사용자가 로그를 가리지 않고 공유 | 코드에서 자동 strip + 절대 채팅에 키 쓰지 말라 강력 경고 |
| `[Environment]::SetEnvironmentVariable` 에러 | `:` 빠짐 + CMD 에서 실행 | PowerShell 명시 + 정확한 문법 |
| `/mobile` 명령 CMD 에서 실행 | Claude Code 내부 명령인데 CMD 에 입력 | Claude Code 세션 내부에서 실행해야 함 명시 |
| main 브랜치에 checkout 실패 | local 변경사항 (index.html) 충돌 | 별도 폴더에 clone (`cheonmyeongdang_ebook`) |
| YouTube 15분 제한 오진단 | 검색 안 하고 "verify 가면 풀린다" 추측 | 외부 서비스 정책은 무조건 검색 |
| YouTube 12시간 영상 삭제 | 12시간 한도 경계선 + 추측성 추천 | 길이 8시간으로 안전 마진, Suno 워크플로우로 전환 |
| auto_watcher.bat `'삭제' is not recognized` | `→` unicode 가 CP949 로 잘못 디코딩 → echo 분리 | 배치 파일은 ASCII + Hangul 만 |
| lyrics_watcher 검은 화면 | drawtext 가 non-ASCII 폰트 경로 (`C:\Users\쿤\...`) 못 읽음 | drawtext 제거, 자막은 `C:\Windows\Fonts\malgun.ttf` 로 |
| subprocess CP949 크래시 | `text=True` 가 OEM 코드페이지로 stderr 디코딩 | `encoding='utf-8', errors='replace'` |
| GitHub Actions workflow 안 보임 | workflow_dispatch UI 는 default branch 만 인식 | feature branch 에선 `push` 트리거 추가 |

---

## 완료된 작업 (2026년 4월 기준)

### 웹사이트 (천명당)
1. 손금/관상/꿈해몽 콘텐츠 시스템
2. 토스페이먼츠 결제 시스템 연동
3. GitHub Actions 원격 명령 시스템 (/운세업데이트 등)
4. SEO 메타 태그 + sitemap
5. Capacitor 모바일 앱 래핑 (진행 중)

### YouTube 자동화
6. playlist_maker.py 배경+글씨 수정
7. 애니메이션 + 음악 반응형 시각 효과
8. auto_watcher.py (폴더 감시 자동 업로드)
9. YouTube SSL 업로드 재시도 + 좀비 연결 재생성
10. 재생목록 자동 분류

### 전자책 시스템 (ebook_system/)
11. generate_book.py (50챕터 자동 생성)
12. make_pdf.py (reportlab 전환 완료)
13. 샘플 book.pdf (진짜 AI 부업 시스템 200p)
14. 랜딩 페이지 + 100일 로드맵 (launch/)
15. AI 멘토봇 (mentor_bot/, shared mode)
16. Gumroad 업로드 가이드 (UPLOAD_NOW.md)

### 추가 상품 (projects/)
17. 프롬프트 1,000개 팩 (prompt_pack_1000/)
18. 노션 템플릿 50개 (notion_templates_50/)
19. 퇴사 플레이북 (exit_playbook/)
20. **사주 AI SaaS MVP** (saju_ai_saas/) — 100억 프로젝트 1단계

---

## 진행 중
- 본책 생성 완료 (book.md 248KB)
- PDF 변환 (reportlab 으로 재작업)
- Gumroad 상품 등록 (LITE 1개 완료, STANDARD/PREMIUM/프롬프트 팩/노션 템플릿 대기)
- 사주 AI SaaS 배포 (Render.com)

## 예정
- 4권 전자책 Gumroad 완전 공개
- 사주 AI SaaS 공개 → 구독자 10,000명 → 연 100억
- 텔레그램 봇 (모바일 원격 제어)

---

## 📋 프로젝트 구조 (2026-04-09 기준)

```
cheonmyeongdang_ebook/
├── ebook_system/
│   ├── generate_book.py       # 50챕터 자동 생성
│   ├── make_pdf.py            # reportlab 기반 PDF 변환
│   ├── config.py              # 책 정보·가격
│   ├── dist/                  # 배포용 PDF (git 포함)
│   ├── output/                # 생성물 (gitignore)
│   ├── mentor_bot/            # PREMIUM AI 멘토봇
│   ├── launch/                # 100일 로드맵 + 마케팅
│   ├── projects/
│   │   ├── prompt_pack_1000/  # 29,900원 보조 상품
│   │   ├── notion_templates_50/ # 39,900원
│   │   ├── exit_playbook/     # 99,000원
│   │   └── saju_ai_saas/      # ⭐ 100억 프로젝트
│   └── UPLOAD_NOW.md          # Gumroad 업로드 복붙 자료
├── auto_watcher.py            # YouTube 자동 업로드
├── youtube_uploader.py        # 업로드 + SSL 재시도
├── index.html                 # 천명당 메인 페이지
└── CLAUDE.md                  # 이 파일
```

---

## 분석 프레임워크 (모든 명령에 적용)

### 1. 시장/니치 분석 구조
명령을 내릴 때 항상 아래 구조로 분석할 것:

#### TAM / SAM / SOM
- **TAM (Total Addressable Market)**: 전체 시장 규모
- **SAM (Serviceable Available Market)**: 실제 접근 가능한 시장
- **SOM (Serviceable Obtainable Market)**: 단기 확보 가능 시장

#### 수요를 만드는 핵심 트렌드 5개
- 검색 후 팩트 기반으로 분석
- 데이터/수치 포함

#### 아직 덜 공략된 기회 5개
- 경쟁이 낮고 수요가 있는 틈새

#### 이미 돈이 흐르는 영역 표시
- 매출/수익 데이터 기반

#### 출력 형식: 문장 아님, 구조화된 인사이트로 출력

---

### 2. 산업 문제 분석
명령을 내릴 때 산업의 가장 큰 문제 10개를 나열:

| 순위 | 문제 | 긴급도 (1~10) | 돈 낼 의향 (1~10) | 성장 속도 | 실제 불평 |
|------|------|--------------|-------------------|----------|----------|

- 긴급도 기준으로 점수화 (1~10)
- 돈 낼 의향 기준으로 점수화 (1~10)
- 가장 빠르게 커지는 문제 표시
- 사람들이 실제로 불평하는 문제 강조
- **표 형태로 출력**

---

### 3. 고전환 오퍼 설계
문제에 대한 오퍼를 만들 때:

- **이상적인 고객 정의**: 누구인가, 어떤 상황인가
- **명확한 가치 제안**: 한 문장으로 핵심 가치
- **가격 전략**: 저가 / 중가 / 프리미엄 3단계
- **보장 + 리스크 제거 요소 포함**
- **경쟁사보다 나은 이유**
- **출력 형식: 랜딩페이지 구조**

---

### 4. 성장 전략 (30일 100만 도달 계획)
성장 전략가처럼 행동:

- **핵심 유입 채널 5개**
- **채널별 콘텐츠 형태**
- **일별 실행 계획**
- **유기 + 유료 전략 혼합**
- **노력보다 레버리지 중심**
- **출력 형식: 단계별 시스템**

---

### 5. 바이럴 콘텐츠 전략
니치에 맞는 바이럴 콘텐츠:

- **고전환 훅 20개**
- **콘텐츠 포맷 10개**
- **감정 트리거**: 공포, 지위, 호기심 등
- **사람들이 공유하는 이유**
- **출력 형식: 반복 가능한 구조**

---

### 6. 경쟁자 분석
니치의 상위 경쟁자 5명 분석:

| 경쟁자 | 잘하는 것 | 약한 부분 | 놓치는 고객층 | 포지셔닝 공백 |
|--------|----------|----------|-------------|-------------|

- 내가 이 시장을 장악하는 전략 제시

---

## 🎯 행동 원칙

1. **항상 검색 후 팩트 기준으로 판단** - 추측하지 않고 데이터 기반
2. **팀을 만들어서 역할 배분** - 혼자 하지 말고 에이전트 활용
3. **대답 전 항상 테스트** - 코드는 구문 검사 + 실행 테스트 통과 후 전달
4. **초보자 눈높이** - 전체 경로 표시, 쉽게 설명
5. **구조화된 출력** - 문장이 아닌 표/구조/시각적 포맷
6. **테스트는 실제 데이터로** - 지어낸 샘플 금지, 검증된 방법 사용 (위 테스트 원칙 참조)
7. **API 키 절대 채팅에 쓰지 말 것** - 코드로 자동 strip, 사용자에게 강력 경고
8. **Windows/PowerShell 특수성 고려** - CMD vs PowerShell, 한글 경로, 환경변수
9. **⭐ 설명은 항상 시각적 + 복붙 1번으로 끝나게** (절대 원칙)
   - 사용자가 할 일 = **코드 블록 1개 복붙**으로 끝나야 함
   - 여러 단계 필요하면 **자동화 스크립트 1개**로 합치기
   - "이거 하고 저거 하고 다시 이거 하고" 식 산발적 안내 금지
   - 시각적 예시: PowerShell 화면이 어떻게 나올지 ASCII 박스로 보여주기
   - 파일 만들기 같은 건 **Read-Host 대화식 스크립트**로 자동화 (수동 메모장 작업 최소화)
   - **시간 낭비 = 최대의 적**. 사용자 시간 1분 아끼려면 내가 10분 더 써서 스크립트 만들기

---

## 🚨 자주 하는 실수 (재발 금지)

| 실수 | 원인 | 방지책 |
|---|---|---|
| API 키 노출 | 사용자가 로그 가리지 않고 공유 | 코드에서 자동 strip, 채팅에 키 쓰지 말라 절대 강조 |
| 다른 브랜치 작업 | main 브랜치에 ebook_system 없음 | 브랜치 확인 후 작업 시작, 별도 폴더 clone |
| CMD 에서 PowerShell 명령 | `[Environment]::`, `Copy-Item` 등 | PowerShell 창 사용 명시 |
| fpdf2 한국어 에러 | 긴 문장 + 특수문자 | reportlab 우선 사용 |
| 가짜 데이터로 테스트 후 사용자에게 넘김 | 샌드박스 제약 | 실제 데이터 샘플로 테스트 or 사용자 환경 특수성 사전 검증 |
