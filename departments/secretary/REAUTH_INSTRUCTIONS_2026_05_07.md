# 5/7 새벽 — Gmail OAuth 재인증 필요

## 상황
사용자 잠자는 동안 메일 답장 draft 작성 시도했으나, **Gmail OAuth 토큰 두 개 모두 Google 에 의해 revoke 됨** (`invalid_grant: Token has been expired or revoked`).

원인: Google Cloud OAuth 앱이 "Testing" 상태인 경우 refresh_token 7일 만료. 5/6 만료 추정.

## 사용자 액션 (30초)
일어나서 1회만 실행:

```bash
cd D:\cheonmyeongdang
python departments/secretary/reauth_2026_05_07.py
```

브라우저 열림 → `ghdejr11@gmail.com` 로그인 → "허용" 클릭

## 그 다음 (자동)
재인증 끝나면 즉시:

```bash
python departments/secretary/scan_inbox_2026_05_07.py
```

→ 24시간 받은편지함 스캔
→ 우선순위 분류 (RED/ORANGE/YELLOW/GREEN)
→ 답장 가능한 메일 Gmail draft 자동 작성
→ 사용자는 Gmail 에서 검토 후 1클릭 send

## 영구 해결책 (선택)
Google Cloud Console → OAuth 동의 화면 → "프로덕션으로 게시" (testing → production)
→ refresh_token 만료 없음.
단, OAuth 검증 안 받은 상태면 ghdejr11@gmail.com 만 OK.
