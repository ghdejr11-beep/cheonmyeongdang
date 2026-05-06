# PayPal Reports API 권한 추가 가이드

**문제**: 자동 매출 모니터링 시 `403 NOT_AUTHORIZED` (Authorization failed due to insufficient permissions)

**원인**: PayPal Business 앱에 `/v1/reporting/transactions` 호출 권한 (Transaction Search) 미부여

**해결 (사용자 1클릭, 5분)**:

1. PayPal Developer Dashboard 접속
   - https://developer.paypal.com/dashboard/applications/live
   - 로그인: `ghdejr11@gmail.com` (Business 계정)

2. 본인 앱 (천명당 결제용, Client ID `AYSD0KCwhgKp9twL...`) 선택

3. **Live App settings → Features** 탭에서 **체크박스 추가**:
   - ☑️ **Transaction Search** (필수)
   - ☑️ **Invoicing** (선택, 자동 영수증 발송 시)
   - ☑️ **Subscriptions** (이미 체크됨, 천명당 정기결제용)
   - ☑️ **Payments** (이미 체크됨)

4. **Save Changes** 클릭

5. 5~10분 후 권한 활성화 → 자동 매출 모니터링 정상 작동

**확인 방법**: 다시 자동 스크립트 실행 시 `[TX] count=N` 으로 트랜잭션 표시되면 OK

**자동 매출 모니터링 효과 (권한 추가 후)**:
- 매일 09시 schtask가 PayPal 트랜잭션 자동 수집
- 신규 결제 발생 시 텔레그램 알림 (사용자 PC 매시 정각)
- 일/주/월 매출 보고서 자동 생성 (departments/sales-collection)
- Gumroad/Ko-fi와 통합 → 통합 매출 대시보드 자동 갱신
