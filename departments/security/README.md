# 🛡️ 보안부서 (Security)

> 쿤스튜디오 전 서비스 통합 보안 관리 — **자동 점검 · 자동 수정 · 해킹 방지**

## 📋 관리 대상 서비스

| 서비스 | 경로 | 프로덕션 URL |
|---|---|---|
| 🔍 KORLENS | `~/Desktop/korlens` | https://korlens.vercel.app |
| 💰 세금N혜택 | `~/Desktop/cheonmyeongdang/departments/tax/server` | https://tax-n-benefit-api.vercel.app |
| 🔮 천명당 | `~/Desktop/cheonmyeongdang` | (app) |
| 🎮 HexDrop | `~/Desktop/hexdrop` | (Play Store) |
| 📖 전자책 | `~/Desktop/cheonmyeongdang_ebook` | (KDP) |
| 🎨 크티 프롬프트 | `~/Desktop/cheonmyeongdang/departments/digital-products/prompts` | (크티) |

## 🔄 자동 실행 스케줄

| 스크립트 | 빈도 | 작업 |
|---|---|---|
| `security_audit.py` | **매일 03:00** | 전체 감사 (시크릿/의존성/.env/커밋 이력) |
| `intrusion_watch.py` | **5분마다** | Vercel 트래픽 이상 탐지 (401/403/429 급증) |
| `uptime_monitor.py` | **5분마다** | Vercel/GitHub Pages 가동 감시 (288회/일, 3연속 실패시 텔레그램 알림) |

## ⏱ Uptime Monitor — Vercel + GitHub Pages 가동 감시

- 신규 파일: `uptime_monitor.py`
- 출력 로그: `data/uptime_log.jsonl` (체크 1건 = 1줄, 일자별 append)
- 대상 자동 발견: `departments/**/*.{html,js,md,py}` 에서 `*.vercel.app`/`*.github.io` URL 추출 → `data/monitor_targets.json` 누적
- 알림 정책: 3회 연속 실패시 1차 텔레그램, 복구시 다운타임 합계 알림 (false positive 방지)
- 인증 필요한 endpoint(`/api/chat` 등)는 자동 발견에서 제외 (시드만 모니터)

### 수동 실행
```bash
python departments/security/uptime_monitor.py            # 1회 체크 + 알림
python departments/security/uptime_monitor.py --once     # 조용히 1회 (cron용)
python departments/security/uptime_monitor.py --discover # 모니터 대상 자동발견만
python departments/security/uptime_monitor.py --status   # 현재 다운/UP 상태
```

### Windows Task Scheduler 등록 (5분마다)
PowerShell 관리자 권한으로:
```powershell
$action = New-ScheduledTaskAction -Execute "python.exe" `
  -Argument "D:\cheonmyeongdang\departments\security\uptime_monitor.py --once" `
  -WorkingDirectory "D:\cheonmyeongdang\departments\security"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Minutes 5) `
  -RepetitionDuration ([TimeSpan]::FromDays(3650))
Register-ScheduledTask -TaskName "KunStudio_UptimeMonitor" `
  -Action $action -Trigger $trigger `
  -Description "Vercel/GH Pages 5분마다 uptime check + 알림" `
  -RunLevel Highest -Force
```

또는 schtasks (CMD):
```bash
schtasks /Create /TN "KunStudio_UptimeMonitor" ^
  /TR "python.exe D:\cheonmyeongdang\departments\security\uptime_monitor.py --once" ^
  /SC MINUTE /MO 5 /F
```

### CEO 브리핑 v2 통합
`briefing_v2.py` 의 `build_message()` 안에서 `build_uptime_section(24)` 호출됨 (revenue 다음, departments 직전).
출력: 총 다운타임 / 평균 응답시간 / 가장 느린 서비스 / 장애 TOP3.

## 🚨 자동 대응 (보고 없이 알아서 수정)

1. **시크릿 하드코딩 발견** → 즉시 `.env.local`로 이동 권장 로그 + CEO 텔레그램 긴급
2. **.env 파일이 git staged** → 자동 `git rm --cached .env*` + 알림
3. **npm 취약점** → `npm audit fix` 자동 실행 (Breaking change 없을 때만)
4. **Vercel 환경변수 노출 의심** → 토큰 재발급 CEO 알림
5. **비정상 트래픽 (5분 내 429 급증)** → Vercel Firewall 룰 추가 권장 + 텔레그램 긴급

## 🔧 수동 실행
```bash
# 전체 보안 감사
python departments/security/security_audit.py

# 특정 서비스만
python departments/security/security_audit.py korlens

# 해킹 시도 탐지 (5분 구간)
python departments/security/intrusion_watch.py

# 자동 수정 (dry-run)
python departments/security/auto_fix.py --dry-run
```

## 📊 리포트 위치
- `logs/audit_YYYY-MM-DD.json` — 일일 감사 리포트
- `logs/intrusion_YYYY-MM-DD.log` — 침입 탐지 로그
- `logs/auto_fix.log` — 자동 수정 내역
