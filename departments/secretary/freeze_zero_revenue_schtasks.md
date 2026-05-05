# 매출 0 채널 schtask 동결 가이드 (2026-05-05)

**목표**: 매출 0인데 매일 자동 작업으로 운영 비용·시간을 잡아먹는 schtask 일괄 비활성화. 운영부담 #6.

## 동결 후보 (사용자 확인 후 1줄씩 실행)

| TaskName | 이유 | 동결 명령 |
|---------|------|----------|
| `KunStudio_WhisperAtlas_*` | YT 2026 AI slop 정책으로 자동 삭제 위험 (memory 5/1) | `schtasks /Change /TN "KunStudio_WhisperAtlas_Daily" /DISABLE` |
| `KunStudio_SoriAtlas_*` | Hetzner CX22 ₩7,000/월 비용 vs 매출 0 | `schtasks /Change /TN "KunStudio_SoriAtlas_24x7" /DISABLE` |
| `KunStudio_AISideHustle_Shorts` | 매출 0, 워밍업 단계 (재등록 대기 중) | `schtasks /Change /TN "KunStudio_AISideHustle_Shorts" /DISABLE` |
| `KunStudio_HealingSleepRealm_*` | 채널 폐기 결정 (memory 4/29) | `schtasks /Change /TN "KunStudio_HealingSleepRealm_Daily" /DISABLE` |

## 활성 유지 (매출 직결)

- `KunStudio_KWisdom_Daily 07:00` (글로벌 K-콘텐츠, 천명당/세금N혜택 cross-sell)
- `KunStudio_CEO_Briefing_*` (운영 가시성)
- `KunStudio_Revenue_Daily` (매출 보고)
- `KunStudio_Telegram_Inbox_*` (고객 응대)

## 검증 명령
```powershell
# 현재 활성 schtask 목록 (KunStudio_*)
schtasks /Query /FO LIST | Select-String "TaskName.*KunStudio"

# 동결 후 상태 확인
schtasks /Query /TN "KunStudio_WhisperAtlas_Daily" /FO LIST | Select-String "Status"
```

## 재활성 (매출 발생 시)
```powershell
schtasks /Change /TN "KunStudio_WhisperAtlas_Daily" /ENABLE
```

## 사용자 1클릭 액션
PowerShell 관리자 권한으로 위 4개 동결 명령 그대로 복붙 → 분기당 약 30시간/₩7,000 비용 절감.
