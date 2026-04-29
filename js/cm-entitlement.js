/**
 * 천명당 — 유료 콘텐츠 잠금 해제 (entitlement) 헬퍼
 * 2026-04-27 추가: 월회원권(monthly_premium) 도입에 따른 OR 조건 통합 체크
 * 2026-04-27 (저녁) 정책 확정: 종합 풀이는 월회원에 포함되지 않음 → 별도 결제만
 *
 * 사용 예 (premium-saju.js / premium-render.js / index.html 어디서나):
 *   if (window.CmEntitlement.canUnlockSaju()) { ...풀이 표시... }
 *
 * 잠금 해제 정책 (최종):
 *   ┌──────────────────────┬──────────┬──────────┐
 *   │ 콘텐츠                │ 월회원   │ 단건결제 │
 *   ├──────────────────────┼──────────┼──────────┤
 *   │ 사주 정밀 풀이        │ 무료     │ 9,900    │
 *   │ 궁합                  │ 무료     │ 9,900    │
 *   │ 종합 풀이             │ ✗별도결제│ 15,000   │
 *   │ 매일 카톡 운세        │ 전용     │ -        │
 *   └──────────────────────┴──────────┴──────────┘
 *
 *   - 사주 / 궁합 → 월회원 OR 단건 (OR 조건)
 *   - 종합 풀이   → 단건 결제만 (월회원도 별도 ₩15,000 결제 필요)
 *
 * 데이터 소스 (전부 localStorage, 추후 서버 영수증 검증으로 강화 예정):
 *   - cm_subscription : 활성 구독 + expiresAt (월회원권)
 *   - cm_purchases    : 1회성 구매 SKU 배열 (saju_premium / gunghap / comprehensive_reading)
 *   - cm_orders       : 결제 이력 (status === 'completed') — fallback 데이터
 */
(function(root) {
  'use strict';

  // 월회원권 SKU ID 후보 (정책: monthly_premium / 현 코드: subscribe_monthly_9900)
  var MONTHLY_SKUS = ['monthly_premium', 'subscribe_monthly_9900'];

  // 단건 결제 SKU ↔ 풀이 매핑
  var SKU_PER_FEATURE = {
    saju:          ['saju_premium', 'saju_detail_29900'],            // 사주 정밀 풀이
    gunghap:       ['gunghap', 'compat_detail_9900'],                // 궁합
    comprehensive: ['comprehensive_reading'],                          // 종합 풀이
  };

  function safeParse(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key) || ''); }
    catch (e) { return fallback; }
  }

  /**
   * 월회원권(구독) 활성 여부
   * - cm_subscription.active === true
   * - expiresAt 미래
   */
  function hasActiveMonthly() {
    var sub = safeParse('cm_subscription', null);
    if (!sub || !sub.active) return false;
    if (sub.sku && MONTHLY_SKUS.indexOf(sub.sku) === -1) {
      // sku 필드가 명시됐는데 월회원권이 아니면 무시
      return false;
    }
    if (sub.expiresAt) {
      var exp = new Date(sub.expiresAt).getTime();
      if (isNaN(exp) || exp < Date.now()) return false;
    }
    return true;
  }

  /**
   * 특정 SKU 단건 결제 보유 여부
   * - cm_purchases (배열) 우선 확인
   * - cm_orders 의 status === 'completed' 항목을 fallback 으로 확인
   */
  function hasPurchase(skuList) {
    if (!skuList || !skuList.length) return false;
    var purchases = safeParse('cm_purchases', []);
    if (Array.isArray(purchases)) {
      for (var i = 0; i < skuList.length; i++) {
        if (purchases.indexOf(skuList[i]) !== -1) return true;
      }
    }
    // fallback: cm_orders 검사
    var orders = safeParse('cm_orders', []);
    if (Array.isArray(orders)) {
      for (var j = 0; j < orders.length; j++) {
        var o = orders[j];
        if (o && o.status === 'completed' && o.skuId && skuList.indexOf(o.skuId) !== -1) {
          return true;
        }
      }
    }
    return false;
  }

  function canUnlockSaju() {
    // 사주 정밀 풀이: 월회원 OR 단건
    return hasActiveMonthly() || hasPurchase(SKU_PER_FEATURE.saju);
  }
  function canUnlockGunghap() {
    // 궁합: 월회원 OR 단건
    return hasActiveMonthly() || hasPurchase(SKU_PER_FEATURE.gunghap);
  }
  function canUnlockComprehensive() {
    // ⚠️ 종합 풀이: 단건 결제(₩15,000)만 잠금 해제. 월회원 무관.
    return hasPurchase(SKU_PER_FEATURE.comprehensive);
  }

  /**
   * 임의 feature 키 ('saju' | 'gunghap' | 'comprehensive') 로 일괄 체크
   * 외부에선 이 함수 1개로 통일해서 호출 권장
   * 종합 풀이는 월회원이라도 단건 결제가 별도 필요 (정책 2026-04-27)
   */
  function canUnlock(feature) {
    if (feature === 'comprehensive') {
      // 종합 풀이는 월회원 보너스 없음 — 단건 결제만 인정
      return hasPurchase(SKU_PER_FEATURE.comprehensive);
    }
    if (hasActiveMonthly()) return true; // 월회원권은 사주/궁합 OK
    var skus = SKU_PER_FEATURE[feature];
    return skus ? hasPurchase(skus) : false;
  }

  /**
   * 월회원이지만 종합 풀이는 별도 결제가 필요한 상태인지
   * → UX 안내 메시지 분기에 사용
   */
  function needsComprehensiveUpsell() {
    return hasActiveMonthly() && !hasPurchase(SKU_PER_FEATURE.comprehensive);
  }

  /**
   * 단건 결제 기록 (네이티브 IAP / 토스 결제 콜백에서 호출)
   * @param {string} skuId
   */
  function recordPurchase(skuId) {
    if (!skuId) return;
    var purchases = safeParse('cm_purchases', []);
    if (!Array.isArray(purchases)) purchases = [];
    if (purchases.indexOf(skuId) === -1) {
      purchases.push(skuId);
      try { localStorage.setItem('cm_purchases', JSON.stringify(purchases)); } catch(e) {}
    }
  }

  root.CmEntitlement = {
    hasActiveMonthly: hasActiveMonthly,
    canUnlockSaju: canUnlockSaju,
    canUnlockGunghap: canUnlockGunghap,
    canUnlockComprehensive: canUnlockComprehensive,
    canUnlock: canUnlock,
    needsComprehensiveUpsell: needsComprehensiveUpsell,
    recordPurchase: recordPurchase,
    // 디버그/외부 매핑 노출
    MONTHLY_SKUS: MONTHLY_SKUS,
    SKU_PER_FEATURE: SKU_PER_FEATURE,
  };
})(typeof window !== 'undefined' ? window : this);
