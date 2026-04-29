# 비서부 (Secretary)

쿤스튜디오 1인기업의 비서 역할 — 메일 분류·요약·정리·고객 응대 큐 관리.

## 업무 목록

### 1. Gmail 자동 분류 + 요약 (`secretary.py`)
- 받은편지함 최근 N시간 메일을 분류
- 파트너사 / KDP 거절 / 광고·스팸 / 일반 / 피싱 의심 으로 카테고리화
- 텔레그램으로 요약 보고
- KDP 거절 메일 → `edit_queue.json` 으로 자동 전달 (편집부)
- 실행: `python secretary.py 24` (24시간 분량)

### 2. Gmail 자동 정리 (`gmail_organizer.py`) ⭐ 신규
받은편지함을 라벨로 자동 분류하고, 오래된 광고 메일을 안전하게 archive.

#### 자동 분류 라벨 (5개)
| 라벨 | 적용 조건 |
|------|----------|
| 🔴[중요] | 키워드: 입금/결제/환불/정산/세무/법무/통지/통보/청구, invoice, payment, tax 등 |
| 🟡[답장필요] | 키워드: 문의/질문/요청/부탁/회신, 또는 제목에 `?` 포함 |
| 🔵[광고-뉴스레터] | 발신자: noreply, no-reply, newsletter, promo, marketing, deals 등 / 제목: 광고, sale, %off |
| ⚪[개발자] | 발신자 도메인: github, vercel, supabase, anthropic, gumroad, google, kakao, naver 등 |
| ⏰[오래된광고] | 광고 라벨 + 30일 이상 = Inbox 에서 archive 시 부여 |

#### 자동 archive 정책
- 🔵[광고-뉴스레터] 라벨 + 30일 이상 메일 → Inbox 에서 제거 + ⏰[오래된광고] 라벨 부여
- archive 는 **영구 삭제 X** — Gmail 검색 `label:⏰[오래된광고]` 로 언제든 복구 가능
- 신뢰 발신자(KDP, Toss, Apple, 국세청, Play Console 등)는 archive 보호

#### 절대 금지
- ❌ 메일 영구 삭제 (Trash 이동, Delete 모두 금지) — 사용자만 가능
- ❌ 화이트리스트 발신자 archive

#### CLI
```bash
# 최초 1회 OAuth 인증 (브라우저 동의)
python gmail_organizer.py --auth

# 분류만
python gmail_organizer.py --classify

# 30일+ 광고 archive
python gmail_organizer.py --archive-old

# 텔레그램 보고
python gmail_organizer.py --report

# 일일 자동 작업 (분류 + archive + 보고)
python gmail_organizer.py --all
```

#### 자동 스케줄
- 작업명: `KunStudio_GmailOrganize`
- 시간: 매일 09:30
- 실행: `python gmail_organizer.py --all`
- 등록: `powershell -ExecutionPolicy Bypass -File register_gmail_organize.ps1`
- 로그: `logs/gmail_organize.log`

### 3. 편집부 큐 (`edit_queue.json`)
- KDP 거절 메일이 자동으로 쌓이는 대기열
- 편집부(`editor.py`)가 읽어서 표지·메타데이터 수정 → 재제출

### 4. KDP 인스펙터 (`inspect_kdp.py`)
- KDP 도서 상태 조회 보조 도구

## 파일 구조
```
secretary/
├── credentials.json          # Google OAuth 클라이언트 (moonlit-sounds 프로젝트)
├── token.json                # OAuth 토큰 (자동 생성, .gitignore 권장)
├── secretary.py              # 메일 분류 + KDP 거절 라우팅
├── gmail_organizer.py        # 자동 정리 (라벨 + archive)
├── editor.py                 # 편집부 (KDP 거절 처리)
├── inspect_kdp.py            # KDP 보조
├── register_gmail_organize.ps1   # gmail_organizer 스케줄 등록
├── register_schedule.bat     # secretary 스케줄 등록
├── edit_queue.json           # 편집부 대기열
├── archive/                  # 처리 완료 메일 백업
├── logs/                     # 자동 실행 로그
└── output/                   # 보고서 출력
```

## 텔레그램
- Bot: `KunStudio_Briefing_Bot`
- Chat: 사용자 개인 (`8556067663`)
- 모든 자동 보고는 동일 봇/채팅으로 발송

## 보안 규칙
- `credentials.json`, `token.json` 절대 커밋 금지 (.gitignore)
- 영구 삭제·자동 답장은 코드에 구현하지 않음 (사용자 승인 필수)
- 피싱 의심 메일은 텔레그램 경고 + 보호 (자동 처리 안 함)
