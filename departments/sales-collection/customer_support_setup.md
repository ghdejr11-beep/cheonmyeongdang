# 고객 지원 인프라 셋업 (2026-05-05)

**목표**: support@ alias + Tally 폼 + Telegram inbox 일원화.

## 1. Gmail Alias (사용자 5분 작업)

`ghdejr11@gmail.com` 에 `support+cheonmyeongdang@` plus addressing 또는 alias 추가:

1. https://mail.google.com → 우측 상단 톱니 → 모든 설정 보기
2. **계정 및 가져오기** → **다른 이메일 주소 추가**
3. 이름: "천명당 고객지원", 이메일: `support@cheonmyeongdang.app` (도메인 미보유 시 plus addressing 사용)
4. SMTP 서버: smtp.gmail.com / 포트 587 / TLS
5. 검증 코드 입력 → 완료

**대안 (도메인 없이 즉시)**: `ghdejr11+support@gmail.com` 으로 라우팅 (Gmail plus addressing 자동 동작).

## 2. Tally 폼 (자동 가능, 무료)

https://tally.so → New Form → 4개 필드:
- 이메일
- 문의 카테고리 (결제 / 환불 / 기능 / 기타)
- 문의 내용 (textarea)
- 주문번호 (선택)

폼 URL을 천명당 footer + KORLENS landing 에 embed.

## 3. Telegram Inbox 자동 라우팅

기존 `departments/telegram_inbox/` 활용. Tally → Webhook → Telegram bot → schtask 매시간 unread 체크.

## 4. SLA 정책

| 우선순위 | 응답 시간 | 케이스 |
|---------|----------|------|
| P0 | 30분 | 결제 실패, 환불 요청 |
| P1 | 4시간 | 기능 오류, 다운로드 실패 |
| P2 | 24시간 | 일반 문의, 기능 제안 |

## 5. landing 추가 위치

천명당 index.html / KORLENS landing.html 푸터에:
```html
<p>고객지원: <a href="mailto:ghdejr11+support@gmail.com">ghdejr11+support@gmail.com</a> · <a href="TALLY_URL">문의 폼</a> · 평균 답변 4시간 (영업일)</p>
```
