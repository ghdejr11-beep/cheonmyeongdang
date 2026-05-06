# AdMob OAuth 1클릭 셋업 가이드

> **시급도**: 🟡 매출 추적 (AdMob 광고 매출 자동 수집)
> **사용자 시간**: ~5분
> **매출 임팩트**: AdMob 매출 자동 통합 → unified_revenue.py에 일별 자동 기록 (수동 추적 시간 30분/주 절감)
> **마지막 업데이트**: 2026-05-06

복붙 텍스트 ✂ 표시.

---

## 0. 사전 점검 (자동 완료)

- ✅ OAuth 셋업 스크립트: `departments/sales-collection/admob_auth_setup.py`
- ✅ 광고 단위 자동 생성: `departments/sales-collection/admob_create_units.py`
- ✅ 매출 수집기: `departments/sales-collection/admob_collector.py`
- ✅ Scopes 정의 완료: `admob.readonly` + `admob.monetization` + `admob.report`
- ✅ Token 저장 경로: `.secrets_admob_token.json` (gitignore)

---

## 1. Google Cloud Console 프로젝트 생성 (2분)

**URL**: https://console.cloud.google.com

1. 우측 상단 프로젝트 드롭다운 → `New Project`

| 필드 | 답변 (✂ 복붙) |
|-----|---|
| Project name | `cheonmyeongdang-admob` |
| Organization | `(공란 — 개인 계정)` |
| Location | `No organization` |

2. `Create` → 자동 선택됨.

---

## 2. AdMob API 활성화 (30초)

1. 좌측 햄버거 메뉴 → `APIs & Services` → `Library`
2. 검색: `AdMob API`
3. 결과 클릭 → `Enable` 1클릭.

---

## 3. OAuth Client ID 생성 (2분)

1. 좌측 메뉴 → `APIs & Services` → `Credentials`
2. 상단 `+ Create Credentials` → `OAuth client ID` 선택

⚠️ **OAuth consent screen 미설정시 먼저 셋업 요구**:

| 필드 | 답변 (✂ 복붙) |
|-----|---|
| User Type | `External` |
| App name | `Cheonmyeongdang AdMob Sync` |
| User support email | `ghdejr11@gmail.com` |
| Developer contact | `ghdejr11@gmail.com` |
| Scopes | `Skip` (스크립트가 직접 요구) |
| Test users | `ghdejr11@gmail.com` 1개 추가 |

`Save and Continue` → 모든 단계 통과 → `Back to Dashboard`.

3. 다시 `Create Credentials` → `OAuth client ID`:

| 필드 | 답변 (✂ 복붙) |
|-----|---|
| Application type | `Desktop app` |
| Name | `cheonmyeongdang-admob-desktop` |

`Create` → JSON 다운로드 버튼 클릭.

---

## 4. client_secret.json 저장 (10초)

다운로드한 JSON 파일을 정확히 이 경로로 이동:

```
C:\Users\hdh02\Desktop\cheonmyeongdang\departments\sales-collection\client_secret.json
```

**파일명 정확히 `client_secret.json`** (스크립트가 이 이름으로 찾음).

---

## 5. OAuth Flow 실행 (30초)

PowerShell:

```powershell
cd C:\Users\hdh02\Desktop\cheonmyeongdang\departments\sales-collection
python admob_auth_setup.py
```

→ 브라우저 자동 오픈 → `ghdejr11@gmail.com` 로그인 → `Continue` (검증되지 않은 앱 경고시 `Advanced` → `Go to ... (unsafe)`) → 권한 3개 모두 `Allow`

→ 자동으로 `.secrets_admob_token.json` 저장 완료.

---

## 6. AdMob Publisher ID 확인 + .secrets 등록 (1분)

1. https://apps.admob.com → 좌측 `Settings` → `Account Information`
2. **Publisher ID** 복사 (`pub-XXXXXXXXXXXXXXXX` 형식)
3. `.secrets` 파일 편집 (✂ 추가):

```
ADMOB_PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX
ADMOB_OAUTH_TOKEN_PATH=C:/Users/hdh02/Desktop/cheonmyeongdang/.secrets_admob_token.json
```

---

## 7. 테스트 (30초)

```powershell
cd C:\Users\hdh02\Desktop\cheonmyeongdang\departments\sales-collection
python admob_collector.py
```

→ 어제 매출 데이터 출력 확인 (예: `Yesterday: ₩1,234, Impressions: 123, eCPM: $0.12`).

---

## 8. 사용자만 가능한 액션 (4건)

1. Google Cloud 프로젝트 생성 (1클릭)
2. OAuth Client ID 생성 + JSON 다운로드 (1클릭 × 2)
3. OAuth consent (브라우저 1클릭 — 권한 승인)
4. AdMob Publisher ID 복사 + .secrets paste (수동 1줄)

**총 ~5분**.

---

## 9. 완료 후 자동 후속

- 매일 09:00 schtask `unified_revenue.py` 실행시 AdMob 매출 자동 합산
- 일별 매출 보고서 메일 (briefing_v2)에 AdMob 라인 자동 포함
- AdMob 광고 단위 추가시 `admob_create_units.py` 1회 실행으로 일괄 생성
- token expire 자동 refresh (refresh_token 활용)

---

## 10. 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `client_secret.json 없음` | 파일명/경로 틀림 | `departments/sales-collection/client_secret.json` 정확히 |
| `Access blocked: This app's request is invalid` | OAuth consent 미설정 | Step 3의 consent screen 셋업 먼저 |
| `Token expired and refresh failed` | refresh_token 만료 | `python admob_auth_setup.py` 재실행 (1회만) |
| `403 The user does not have permission` | AdMob 계정 미활성 | https://apps.admob.com 로그인 후 가입 완료 확인 |

---

## ROI

- **즉시**: AdMob 매출 자동 추적 → 수동 30분/주 절감
- **30일**: 광고 단위 최적화 (eCPM 추적 → 저성과 ad unit 자동 alert)
- **90일**: AdMob 매출 ₩50K~₩200K/월 가시화 → 광고 배치 A/B 테스트 자동화
