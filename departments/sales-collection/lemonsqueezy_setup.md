# Lemon Squeezy 가입 가이드 (사용자 30분 작업)

**목표**: PayPal 다음 두 번째 글로벌 결제 채널 확보. SaaS recurring 가능 (천명당 월회원 글로벌화).
**참고**: memory `stripe_korea_unavailable` — Stripe / Polar 한국 사업자 가입 불가. Lemon Squeezy 는 한국 사업자 OK (Merchant of Record).

## 1. 가입 (10분)

1. https://www.lemonsqueezy.com/ → Sign up
2. 이메일: `ghdejr11@gmail.com` (천명당/Vercel/Gumroad 통일)
3. 사업자 정보:
   - Business name: KunStudio (쿤스튜디오)
   - 사업자번호: 552-59-00848
   - 주소: (사업자등록증 주소)
   - 결제 받을 통화: USD (KRW 는 매출 적음, 환전 수수료 회피)
4. 은행 정보: Wise USD 계정 권장 (한국 원화 받기보다 USD 직수령 후 Wise 환전이 수수료 낮음)

## 2. Tax / KYC (15분)

- W-8BEN-E 양식 (외국 사업자 → 미국 세금 면제) — Lemon Squeezy 자동 안내
- 한국 거주자 특약 (Korea-US 조세조약) 자동 적용

## 3. 첫 상품 등록 (5분)

천명당 월회원 ($2.50/월 = ₩2,900/월) 글로벌 버전:
- Product type: Subscription
- Pricing: $2.50/month
- Trial: None (시작은 보수적)
- Variant: 1개만

## 4. 결제 통합 (자동 — 상품 등록 후 알려주세요)

Lemon Squeezy 는 hosted checkout URL 제공 → 천명당 pay.html 영문 영역에 버튼 추가만 하면 됨.

```html
<!-- pay.html — Lemon Squeezy 월회원 글로벌 -->
<a href="https://YOUR_STORE.lemonsqueezy.com/checkout/buy/PRODUCT_ID"
   class="btn-buy">Subscribe ($2.50/mo) — Global</a>
```

또는 JS overlay (lemon.js) 권장 (사용자 사이트 이탈 X).

## 5. 수수료

- 판매 수수료: 5% + $0.50/거래
- PayPal (4.4% + $0.30) 보다 약간 비싸지만 **한국 사업자 가능 + recurring 자동** 이 최대 강점
- 글로벌 매출 monthly recurring 확보 시 LTV ×3 효과

## 6. Webhook (자동 가능 — 가입 후 알려주세요)

Vercel `api/confirm-payment.js` 에 Lemon Squeezy webhook signature 검증 추가 (PayPal과 동일 방식). 12-function 한도 OK (compat.js 통합).

## 사용자 1클릭 액션
가입 완료 후 store URL + first product ID 알려주시면 → pay.html 자동 통합 + git commit 즉시 처리.
