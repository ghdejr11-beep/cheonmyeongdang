# CODEF 연동 사용법

## 엔드포인트
- `POST /api/connect` — 간편인증으로 connectedId 발급 (CODEF_HOST: sandbox/api.codef.io)
- `POST /api/income` — 지급명세서(원천징수) 조회
- `POST /api/tax-report` — 종합소득세 신고결과 조회
- `POST /api/refund` — 환급금 조회
- `POST /api/tax-cert-all` — **세무 증명서 4종 일괄 발급** (사업자등록증명/부가세 과세표준/소득금액/납세증명서)

## /api/tax-cert-all 사용법
```bash
curl -X POST https://tax-n-benefit-api.vercel.app/api/tax-cert-all \
  -H "Content-Type: application/json" \
  -d '{
    "connectedId": "<connect API로 받은 값>",
    "identity": "주민번호13자리",
    "biz_no": "1234567890",
    "year": "2025",
    "types": ["businessReg","vat","income","taxPayment"]
  }'
```
응답: `data.businessReg / data.vat / data.income / data.taxPayment` 각 항목별 `{ ok, code, message, data }`. 한 항목이 실패해도 나머지 진행됨 (`partial: true` 표시).

## 환경변수
`CODEF_ENV` / `CODEF_CLIENT_ID` / `CODEF_CLIENT_SECRET` / `CODEF_PUBLIC_KEY` / `CODEF_SERVICE_NO=000007456002` (프로덕션 승인 완료, 전체 권한).
