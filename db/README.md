# 천명당 DB 부트스트랩

데이터 부서 #12 — Supabase 프로젝트 신규 생성 시 이 폴더의 SQL을 그대로 적용하면 즉시 GA4 보완 + 매출 SoT(Single Source of Truth)가 작동한다.

## 설치 (사용자 1회 작업)

1. https://supabase.com/dashboard 에서 신규 프로젝트 생성 (Region: ap-northeast-2 Seoul)
2. 좌측 메뉴 **SQL Editor** → New query → `supabase_events_bootstrap.sql` 전체 붙여넣기 → **Run**
3. 좌측 **Project Settings → API** 에서 두 키 복사
   - `Project URL` (예: `https://xxxxx.supabase.co`)
   - `service_role` 키 (절대 클라이언트 노출 X)
4. Vercel → Settings → Environment Variables 에 등록
   - `SUPABASE_URL` = 위 Project URL
   - `SUPABASE_SERVICE_ROLE` = service_role 키 (Production + Preview 모두)
5. Redeploy 시 `api/log-event.js` 가 자동으로 events 테이블에 적재 시작

## 코드에서 호출

서버사이드(api/*.js):
```js
await fetch(`${process.env.SUPABASE_URL}/rest/v1/rpc/log_event`, {
  method: 'POST',
  headers: {
    apikey: process.env.SUPABASE_SERVICE_ROLE,
    Authorization: `Bearer ${process.env.SUPABASE_SERVICE_ROLE}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    p_event_name: 'pay_success',
    p_session_id: sessionId,
    p_user_id: userId,
    p_sku: 'jongsose',
    p_amount_krw: 29900,
    p_props: { gateway: 'kakaopay', utm_source: 'instagram' }
  }),
});
```

클라이언트(브라우저)는 절대 service_role 호출 X — `/api/log-event` 프록시 endpoint를 추가해 호출 (12-function 한도 주의).

## 분석 쿼리

```sql
-- 일별 PV/UU
select * from events_daily;

-- 결제 퍼널 (방문→CTA→시도→성공)
select * from payment_funnel limit 14;

-- SKU별 30일 매출
select * from sku_revenue_30d;

-- 코호트 7일 리텐션
select * from retention_7d;
```

## 핵심 이벤트 명명 규칙

| event_name | 발생 위치 | 필수 props |
|---|---|---|
| `page_view` | 모든 페이지 onload | `page_path` |
| `cta_click` | 결제/구독 버튼 | `sku`, `cta_label` |
| `pay_attempt` | PortOne/PayPal 호출 직전 | `sku`, `amount_krw`, `gateway` |
| `pay_success` | 결제 confirm 200 후 | `sku`, `amount_krw`, `gateway`, `order_id` |
| `pay_fail`    | 결제 실패 | `sku`, `error_code` |
| `refund`      | webhook 환불 수신 | `sku`, `amount_krw`, `reason` |

## 개인정보 보호

- `events.props` 안에 **이메일/전화/생년월일 절대 INSERT 금지**
- IP는 `ip_hash = sha256(ip + daily_salt)` 형태만
- `pg_cron` 활성화 시 90일 초과 이벤트 자동 파기 (privacy.html 보유기간 정책 일치)
- RLS: anon/authenticated 둘 다 read 차단, service_role만 접근

## 적용 체크리스트

- [ ] 1. Supabase 프로젝트 생성 (사용자)
- [ ] 2. SQL 적용 (사용자)
- [ ] 3. Vercel env 등록 (사용자)
- [ ] 4. `api/log-event.js` 신규 endpoint 추가 (자동 — 사용자 승인 후)
- [ ] 5. `index.html` / `success.html` 에 page_view + pay_success 호출 추가 (자동)
- [ ] 6. 14일 후 `payment_funnel` 뷰로 첫 퍼널 분석 (자동 schtask)
