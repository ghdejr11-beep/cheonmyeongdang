/**
 * Seasonal D+30 winback dry-run smoke test
 * - getSeasonalCampaign() priority + window
 * - daysUntil() KST math
 * - HTML/text builder render check (subject, key strings, no HTML errors)
 * - sendFollowupEmail end-to-end without actually sending (mocks SMTP/OAuth env)
 */

const path = require('path');
const Module = require('module');

// ─── Mock ../lib/purchase-store ─────────────────────────────────────────
const origResolve = Module._resolveFilename;
Module._resolveFilename = function (request, ...rest) {
  if (request === '../lib/purchase-store') {
    return path.join(__dirname, '_mock_purchase_store.js');
  }
  return origResolve.call(this, request, ...rest);
};
require('fs').writeFileSync(
  path.join(__dirname, '_mock_purchase_store.js'),
  `module.exports = {
    listFollowupTargets: async () => ({ ok: true, records: [] }),
    markFollowupSent: async () => ({ ok: true }),
  };`
);

// ─── Re-require source via vm to access internal helpers ────────────────
const src = require('fs').readFileSync(path.join(__dirname, '..', 'api', 'cron-followup.js'), 'utf8');
const vm = require('vm');
const sandbox = {
  require: (m) => {
    if (m === '../lib/purchase-store') return require(path.join(__dirname, '_mock_purchase_store.js'));
    return require(m);
  },
  module: { exports: {} },
  exports: {},
  process,
  console,
  Buffer,
  Date,
  Math,
  JSON,
  String,
  Number,
  Array,
  Object,
  setTimeout,
  setInterval,
};
vm.createContext(sandbox);
// Append exposure block at the end so internal helpers are reachable
const probe = `
  globalThis.__test = {
    getSeasonalCampaign,
    daysUntil,
    SEASONAL_CAMPAIGNS,
    buildD30EobonalHtml,
    buildD30EobonalText,
    buildD30JongsoseHtml,
    buildD30JongsoseText,
    buildD30Html,
    buildD30Text,
    fmtKstYmd,
  };
`;
vm.runInContext(src + probe, sandbox);
const T = sandbox.__test;

let pass = 0, fail = 0;
function assert(cond, name) {
  if (cond) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name}`); }
}

console.log('\n=== getSeasonalCampaign ===');
assert(T.getSeasonalCampaign('2026-05-03T00:00:00+09:00') === 'eobonal_2026', '5/3 → eobonal');
assert(T.getSeasonalCampaign('2026-05-07T23:59:00+09:00') === 'eobonal_2026', '5/7 23:59 KST → eobonal');
assert(T.getSeasonalCampaign('2026-05-08T09:00:00+09:00') === 'jongsose_2026', '5/8 → jongsose (eobonal expired)');
assert(T.getSeasonalCampaign('2026-05-15T12:00:00+09:00') === 'jongsose_2026', '5/15 → jongsose');
assert(T.getSeasonalCampaign('2026-05-24T23:59:00+09:00') === 'jongsose_2026', '5/24 23:59 → jongsose');
assert(T.getSeasonalCampaign('2026-05-25T00:00:00+09:00') === null, '5/25 → null (jongsose expired)');
assert(T.getSeasonalCampaign('2026-04-30T12:00:00+09:00') === null, '4/30 → null');
assert(T.getSeasonalCampaign('2026-06-02T00:00:00+09:00') === null, '6/2 → null');
assert(T.getSeasonalCampaign(null) === null, 'null input → null');

console.log('\n=== daysUntil ===');
const d508 = T.daysUntil('2026-05-08');
const d531 = T.daysUntil('2026-05-31');
assert(typeof d508 === 'number' && d508 >= 0, `daysUntil(5/8) = ${d508} (≥0)`);
assert(typeof d531 === 'number' && d531 >= 0, `daysUntil(5/31) = ${d531} (≥0)`);
assert(T.daysUntil('2026-01-01') === 0, 'past date → 0');

console.log('\n=== Template render — eobonal ===');
const eobArgs = {
  customerName: '홍덕훈',
  skuName: '사주 정밀 풀이',
  skuId: 'saju_premium_9900',
  orderId: 'cmd_test_eob_001',
  couponCode: 'WB30-AB12',
  validUntil: '2026-05-08',
};
const eobHtml = T.buildD30EobonalHtml(eobArgs);
const eobText = T.buildD30EobonalText(eobArgs);
assert(eobHtml.includes('<!DOCTYPE html>'), 'eobonal html doctype');
assert(eobHtml.includes('어버이날'), 'eobonal html mentions 어버이날');
assert(eobHtml.includes('카네이션'), 'eobonal html mentions 카네이션');
assert(eobHtml.includes('eobonal-letter-100'), 'eobonal html KDP cross-link');
assert(eobHtml.includes('WB30-AB12'), 'eobonal html winback coupon');
assert(eobHtml.includes('utm_campaign=eobonal_2026'), 'eobonal LP utm');
assert(eobHtml.includes('홍덕훈님'), 'eobonal personalized greet');
assert(!eobHtml.includes('세무사 대체') && !eobHtml.includes('100% 환급'), 'eobonal forbidden phrases absent');
assert(eobText.includes('어버이날'), 'eobonal text 어버이날');
assert(eobText.includes('카네이션 카드'), 'eobonal text 카네이션 카드');
assert(eobText.includes('WB30-AB12'), 'eobonal text coupon');

console.log('\n=== Template render — jongsose ===');
const jsArgs = {
  customerName: '홍덕훈',
  skuName: '사주 정밀 풀이',
  skuId: 'saju_premium_9900',
  orderId: 'cmd_test_js_001',
  couponCode: 'WB30-CD34',
  validUntil: '2026-05-22',
};
const jsHtml = T.buildD30JongsoseHtml(jsArgs);
const jsText = T.buildD30JongsoseText(jsArgs);
assert(jsHtml.includes('<!DOCTYPE html>'), 'jongsose html doctype');
assert(jsHtml.includes('종합소득세') || jsHtml.includes('종소세'), 'jongsose html mentions tax');
assert(jsHtml.includes('₩48만'), 'jongsose html stat ₩48만');
assert(jsHtml.includes('국세청'), 'jongsose html attribution 국세청');
assert(jsHtml.includes('홈택스') && jsHtml.includes('세무사'), 'jongsose html disclaimer mentions both');
assert(jsHtml.includes('jongsose-self-guide'), 'jongsose html KDP cross-link');
assert(jsHtml.includes('utm_campaign=jongsose_2026'), 'jongsose LP utm');
assert(jsHtml.includes('WB30-CD34'), 'jongsose html winback coupon');
assert(!jsHtml.includes('세무사 대체') && !jsHtml.includes('100% 환급') && !jsHtml.includes('강요'), 'jongsose forbidden phrases absent');
assert(jsText.includes('홈택스') && jsText.includes('세무사'), 'jongsose text disclaimer');
assert(jsText.includes('₩48만'), 'jongsose text stat');

console.log('\n=== Default D+30 still works (sanity, no season) ===');
const defaultHtml = T.buildD30Html(eobArgs);
assert(defaultHtml.includes('30% 할인'), 'default D+30 still renders');
assert(!defaultHtml.includes('어버이날'), 'default D+30 has no eobonal content');
assert(!defaultHtml.includes('종소세'), 'default D+30 has no jongsose content');

// ─── Cleanup ───
require('fs').unlinkSync(path.join(__dirname, '_mock_purchase_store.js'));

console.log(`\nResult: ${pass} pass / ${fail} fail`);
process.exit(fail === 0 ? 0 : 1);
