# Product-Market Fit 측정 도구 (Sean Ellis 기준, 2026-05-05)

**기준**: Sean Ellis "How would you feel if you could no longer use [PRODUCT]?" 응답 중 "Very disappointed" ≥ 40% = PMF 달성.

## 1. landing inline 1문항 (한국어)

천명당 index.html 푸터 위에 삽입:

```html
<section class="pmf-survey" id="pmf-survey" style="background:#0f1224;padding:24px;border-radius:12px;margin:32px 0;text-align:center">
  <h3 style="color:#c9a84c;margin-bottom:14px">한 가지만 여쭤볼게요</h3>
  <p style="margin-bottom:18px">천명당을 더 이상 사용할 수 없게 된다면 어떤 기분일까요?</p>
  <div id="pmf-options" style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap">
    <button data-pmf="very_disappointed">매우 실망</button>
    <button data-pmf="somewhat_disappointed">조금 실망</button>
    <button data-pmf="not_disappointed">신경 안 씀</button>
    <button data-pmf="never_used">사용 안 해봄</button>
  </div>
  <p id="pmf-thanks" style="display:none;color:#9a9080;margin-top:14px">감사합니다 ✓</p>
</section>
<script>
document.querySelectorAll('#pmf-options button').forEach(function(b){
  b.addEventListener('click', function(){
    var v = b.getAttribute('data-pmf');
    try { localStorage.setItem('cm_pmf_answer', v); } catch(_){}
    try { if (window.gtag) window.gtag('event', 'pmf_survey', { answer: v }); } catch(_){}
    try { if (window.cm && window.cm.event) window.cm.event('pmf_survey', { answer: v }); } catch(_){}
    document.getElementById('pmf-options').style.display = 'none';
    document.getElementById('pmf-thanks').style.display = 'block';
  });
});
</script>
```

## 2. 영문 버전 (en/index.html)

```html
<h3>One quick question</h3>
<p>How would you feel if you could no longer use Cheonmyeongdang?</p>
<button data-pmf="very_disappointed">Very disappointed</button>
<button data-pmf="somewhat_disappointed">Somewhat disappointed</button>
<button data-pmf="not_disappointed">Not disappointed</button>
<button data-pmf="never_used">N/A — haven't tried</button>
```

## 3. 응답 수집

- GA4 이벤트 `pmf_survey` 자동 적재
- Supabase events 테이블 (cm-events.js)
- 결과 추적: `departments/intelligence/pmf_responses.json` (수동 export)

## 4. 분석 임계값

| 'Very disappointed' 비율 | 진단 |
|------------------------|------|
| ≥ 40% | PMF 달성 → 트래픽/광고 풀가동 |
| 25~40% | PMF 근접 → 핵심 사용자 인터뷰 (TOP 5) |
| < 25% | PMF 미달 → 핵심 가치 재정의 |

## 5. 응답 50건 모이면 후속 분석 자동 트리거 (briefing 통합)
