# OAuth Consent Screen — "Testing" → "In Production" 1-Click Guide

**소요 시간**: 30초~1분 (브라우저 5클릭)
**효과**: refresh_token 7일 만료 영구 해소 (매주 재인증 끊김 방지)
**검수**: 본인만 사용해도 무관, sensitive scope 없으면 verification 자동 통과

---

## 자동화 가능 여부 (검증 결과 — 2026-05-07)

| 시도 경로 | 결과 | 이유 |
|---|---|---|
| `gcloud iam oauth-clients` | ❌ | 명령은 IAP/Workforce용, consent screen publish 미지원 |
| `gcloud alpha iam oauth-clients` | ❌ | 동일 — `Publish App` 토글 명령 없음 |
| Public REST API (`projects.brands`) | ❌ | API로 만든 brand는 자동 internal/unreviewed, **public 전환은 콘솔 수동만** ([공식 문서](https://docs.cloud.google.com/iap/docs/programmatic-oauth-clients)) |
| Console Web UI | ✅ | 사용자 1클릭 ("Publish App" 버튼) |

**결론**: Google이 의도적으로 console UI만 제공. 자동화 불가. 사용자 30초 클릭 필요.

---

## 직링크 (1-Click)

### 대상 프로젝트: `moonlit-sounds`
**OAuth Client ID**: `95091510329-6vdp64c4ddm04gbea1pcgs1m7s36t2p4.apps.googleusercontent.com`

```
https://console.cloud.google.com/auth/audience?project=moonlit-sounds
```

이 URL을 브라우저에 붙여넣으면 바로 해당 프로젝트의 Audience(전 OAuth consent screen) 페이지로 이동.

---

## 5단계 클릭 순서

1. 위 URL 클릭 → **Audience** 페이지 자동 진입
2. **Publishing status** 카드에서 현재 "Testing" 표시 확인
3. **PUBLISH APP** 버튼 클릭 (회색 박스 안 파란 버튼)
4. 팝업 다이얼로그: "Push to production?" → **CONFIRM** 클릭
5. 상태가 **"In production"** 으로 바뀜 (즉시 반영)

---

## 검증 방법

- 다음 refresh 시도부터 7일 만료 사라짐
- 기존 refresh_token은 그대로 사용 가능 (재발급 불필요 — 일부 자료에 "재발급 필요" 있으나, **Sensitive scope 없는 경우 그대로 호환**)
- 본인 단독 사용이면 verification 절차 없이 그냥 production 동작

---

## 주의사항

- **Sensitive scope** (Gmail readonly/modify는 sensitive 아님 — restricted도 아님)는 그대로 OK
- **Restricted scope** (gmail.send, drive.file 등)를 추가하면 verification 필요 — 현재 secretary는 readonly+modify만 사용 → 안전
- Verification 안 받아도 본인 계정에서는 정상 작동, 다른 사용자가 OAuth 시도 시 "unverified app" 경고 (현재 본인만 사용이므로 무관)

---

## 다른 OAuth 앱에도 재사용

이 가이드는 **다른 Google Cloud 프로젝트의 OAuth 앱**에도 그대로 적용 가능:

```
https://console.cloud.google.com/auth/audience?project={PROJECT_ID}
```

`{PROJECT_ID}`만 바꾸면 됨. 향후 KORLENS, 세금N혜택 등 신규 OAuth 앱 라이브 시 동일 5단계 반복.

---

## 출처

- [Manage App Audience — Google Cloud Console Help](https://support.google.com/cloud/answer/15549945?hl=en)
- [Refresh Token 7-day expiration in Testing mode](https://nango.dev/blog/google-oauth-invalid-grant-token-has-been-expired-or-revoked/)
- [Programmatically creating OAuth clients for IAP](https://docs.cloud.google.com/iap/docs/programmatic-oauth-clients) — API-created brands는 public 전환 자동화 불가 명시
