/* 신년운세 Enhanced View — Claude.ai 디자인 톤 (warm minimal + big typography + terracotta accents)
   ?focus=sinnyeon 시 사주 결과 페이지의 12개월 운세 위에 종합 view inject.
   사주 결과 r.monthlyFortunes 데이터 활용 → Hero + 연간 종합 + 4 분야 + 12개월 + 다짐. */

(function() {
  if (window._cmSinnyeonLoaded) return;
  window._cmSinnyeonLoaded = true;

  // CSS Claude-style 톤
  var style = document.createElement('style');
  style.textContent = ''
    + '#sinnyeon-enhanced { background: linear-gradient(135deg, rgba(174,86,48,0.10), rgba(201,168,76,0.04)); border: 1px solid rgba(174,86,48,0.30); border-radius: 24px; padding: 36px 32px; margin: 40px auto 28px; max-width: 920px; box-shadow: 0 8px 40px rgba(174,86,48,0.10); }'
    + '.sn-hero { text-align: center; margin-bottom: 36px; }'
    + '.sn-hero-badge { display: inline-block; padding: 6px 18px; background: rgba(174,86,48,0.18); border: 1px solid rgba(174,86,48,0.4); border-radius: 999px; color: #d8825e; font-size: 0.72rem; letter-spacing: 0.22em; font-weight: 700; margin-bottom: 16px; text-transform: uppercase; }'
    + '.sn-hero-title { font-family: \'Noto Serif KR\', serif; font-size: 2rem; color: var(--gold2, #e0c060); font-weight: 700; line-height: 1.35; margin: 10px 0 6px; letter-spacing: -0.01em; }'
    + '.sn-hero-sub { color: var(--text2, #a89985); font-size: 0.95rem; letter-spacing: 0.04em; margin: 0; }'
    + '.sn-summary { display: flex; gap: 32px; align-items: center; background: rgba(0,0,0,0.20); border: 1px solid rgba(174,86,48,0.20); border-radius: 18px; padding: 28px; margin-bottom: 24px; }'
    + '.sn-score-big { font-family: \'Playfair Display\', \'Noto Serif KR\', serif; font-size: 5rem; color: #e8c97a; font-weight: 900; line-height: 1; flex-shrink: 0; text-shadow: 0 2px 12px rgba(232,201,122,0.20); }'
    + '.sn-score-label { font-size: 1.6rem; margin-left: 6px; opacity: 0.6; font-weight: 600; }'
    + '.sn-score-desc { flex: 1; }'
    + '.sn-score-title { color: var(--gold2, #e0c060); font-size: 1.05rem; font-weight: 700; margin-bottom: 10px; letter-spacing: 0.02em; }'
    + '.sn-score-desc p { color: var(--text, #e8e0d0); font-size: 0.92rem; line-height: 1.7; margin: 6px 0; }'
    + '.sn-score-desc b { color: #e8c97a; }'
    + '.sn-domains { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }'
    + '.sn-domain { background: rgba(255,255,255,0.04); border: 1px solid rgba(174,86,48,0.18); border-radius: 14px; padding: 22px 14px 18px; text-align: center; transition: transform .2s, border-color .2s; }'
    + '.sn-domain:hover { transform: translateY(-2px); border-color: rgba(174,86,48,0.5); }'
    + '.sn-domain-hanja { font-family: \'Noto Serif KR\', serif; font-size: 2rem; line-height: 1; color: #ae5630; font-weight: 800; margin-bottom: 8px; opacity: 0.85; }'
    + '.sn-domain-label { color: var(--text2, #a89985); font-size: 0.78rem; letter-spacing: 0.16em; margin-bottom: 8px; }'
    + '.sn-domain-score { font-family: \'Playfair Display\', \'Noto Serif KR\', serif; font-size: 2rem; color: var(--gold2, #e0c060); font-weight: 800; line-height: 1; margin-bottom: 4px; }'
    + '.sn-domain-bar { height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; margin-top: 10px; }'
    + '.sn-domain-bar-fill { height: 100%; background: linear-gradient(90deg, #ae5630, #e8c97a); transition: width 0.6s; border-radius: 3px; }'
    + '.sn-vow { background: linear-gradient(135deg, rgba(201,168,76,0.10), rgba(174,86,48,0.06)); border: 1px solid rgba(201,168,76,0.25); border-radius: 18px; padding: 24px 28px; margin-top: 8px; }'
    + '.sn-vow-title { font-family: \'Noto Serif KR\', serif; font-size: 1.15rem; color: var(--gold2, #e0c060); font-weight: 700; margin-bottom: 14px; letter-spacing: 0.02em; }'
    + '.sn-vow-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap: 12px; }'
    + '.sn-vow-item { background: rgba(0,0,0,0.18); border-left: 3px solid #ae5630; border-radius: 8px; padding: 12px 14px; }'
    + '.sn-vow-item b { color: #e8c97a; display: block; margin-bottom: 4px; font-size: 0.82rem; letter-spacing: 0.05em; }'
    + '.sn-vow-item span { color: var(--text, #e8e0d0); font-size: 0.88rem; line-height: 1.55; }'
    + '@media (max-width: 720px) {'
    +   ' .sn-domains { grid-template-columns: repeat(2, 1fr); }'
    +   ' .sn-summary { flex-direction: column; text-align: center; gap: 16px; padding: 22px 18px; }'
    +   ' .sn-score-big { font-size: 3.8rem; }'
    +   ' .sn-hero-title { font-size: 1.5rem; }'
    +   ' #sinnyeon-enhanced { padding: 24px 18px; margin: 28px auto 20px; border-radius: 18px; }'
    + '}';
  document.head.appendChild(style);

  function avgStars(mfArray, field) {
    var sum = 0, cnt = 0;
    mfArray.forEach(function(m) {
      var v = String(m[field] || '');
      var stars = (v.match(/[★⭐]/g) || []).length;
      if (stars === 0) {
        // 숫자 파싱 시도
        var num = parseFloat(v);
        if (!isNaN(num) && num > 0 && num <= 5) stars = num;
      }
      if (stars > 0) { sum += stars; cnt++; }
    });
    return cnt > 0 ? Math.round((sum / cnt) * 20) : 70; // 5★ → 100
  }

  function getUserName() {
    try {
      var ui = JSON.parse(localStorage.getItem('cm_user_info') || '{}');
      return (ui.name || '').trim() || '고객';
    } catch (e) { return '고객'; }
  }

  function findMonthlyEl() {
    return document.querySelector('.monthly-grid, [class*="monthly-grid"]');
  }

  function getYearLabel(year) {
    var stems = ['갑','을','병','정','무','기','경','신','임','계'];
    var branches = ['자','축','인','묘','진','사','오','미','신','유','술','해'];
    var animals = { '자':'쥐','축':'소','인':'호랑이','묘':'토끼','진':'용','사':'뱀','오':'말','미':'양','신':'원숭이','유':'닭','술':'개','해':'돼지' };
    var elements = { '갑':'木 (양)','을':'木 (음)','병':'火 (양)','정':'火 (음)','무':'土 (양)','기':'土 (음)','경':'金 (양)','신':'金 (음)','임':'水 (양)','계':'水 (음)' };
    var stemIdx = (year - 4) % 10;
    var branchIdx = (year - 4) % 12;
    var stem = stems[stemIdx], branch = branches[branchIdx];
    return { ganji: stem + branch + '년', animal: animals[branch], element: elements[stem] };
  }

  window.renderSinnyeonEnhanced = function() {
    try {
      // 이미 렌더돼 있으면 제거 후 재렌더 (입력 변경 시 정확한 데이터 표시)
      var existing = document.getElementById('sinnyeon-enhanced');
      if (existing && existing.parentElement) existing.parentElement.removeChild(existing);
      var r = window._lastReport || window._lastSajuResult;
      if (!r) {
        console.warn('[sinnyeon] no _lastSajuResult — needs saju analysis first');
        return;
      }
      // monthlyFortunes 없으면 PremiumSaju로 자동 생성 (무료 사주에는 미포함)
      if (!r.monthlyFortunes || !r.monthlyFortunes.length) {
        if (window.PremiumSaju && typeof window.PremiumSaju.generateMonthlyFortunes === 'function') {
          try {
            var yearGen = new Date().getFullYear();
            var userCtxGen = r._userContext || { marital: 'unknown', children: -1, gender: 'M' };
            r.monthlyFortunes = window.PremiumSaju.generateMonthlyFortunes(r, yearGen, userCtxGen);
            console.log('[sinnyeon] auto-generated monthlyFortunes:', r.monthlyFortunes.length);
          } catch (genErr) {
            console.error('[sinnyeon] generateMonthlyFortunes failed', genErr);
            return;
          }
        } else {
          console.warn('[sinnyeon] PremiumSaju.generateMonthlyFortunes not available');
          return;
        }
      }
      var mf = r.monthlyFortunes;
      if (!mf.length) { console.warn('[sinnyeon] empty monthlyFortunes'); return; }
      var year = new Date().getFullYear();
      var yearInfo = getYearLabel(year);
      var name = getUserName();

      // 연간 종합 점수 (월 평균)
      var totalScore = Math.round(mf.reduce(function(s, m) { return s + (m.score || 70); }, 0) / mf.length);

      // 분야별 평균
      var wealthScore = avgStars(mf, 'wealth');
      var loveScore = avgStars(mf, 'love');
      var healthScore = avgStars(mf, 'health');
      var careerScore = avgStars(mf, 'career');

      // 최고/최저 월
      var bestMonth = mf.reduce(function(b, m) { return (m.score || 0) > (b.score || 0) ? m : b; }, mf[0]);
      var worstMonth = mf.reduce(function(w, m) { return (m.score || 100) < (w.score || 100) ? m : w; }, mf[0]);

      // 연간 톤 메시지
      var toneMsg = '';
      if (totalScore >= 80) toneMsg = '대운의 흐름이 강한 한 해. 도전과 확장을 두려워하지 마세요.';
      else if (totalScore >= 70) toneMsg = '안정과 성장이 균형을 이루는 한 해. 꾸준함이 큰 결실로 이어집니다.';
      else if (totalScore >= 60) toneMsg = '준비와 정리의 시기. 무리한 확장보다 내실을 다지는 데 집중하세요.';
      else toneMsg = '도전적인 흐름이 있는 한 해. 신중한 결정과 작은 변화부터 시작하세요.';

      var html = '<div id="sinnyeon-enhanced">' +
        '<div class="sn-hero">' +
          '<div class="sn-hero-badge">' + year + ' ' + yearInfo.ganji + ' · ' + yearInfo.animal + '의 해</div>' +
          '<h2 class="sn-hero-title">' + escapeHtml(name) + '님의 ' + year + '년 한 해의 흐름</h2>' +
          '<p class="sn-hero-sub">12개월 월별 운세 · 분야별 점수 · 길일 캘린더 · 새해 다짐 가이드</p>' +
        '</div>' +
        '<div class="sn-summary">' +
          '<div class="sn-score-big">' + totalScore + '<span class="sn-score-label">점</span></div>' +
          '<div class="sn-score-desc">' +
            '<div class="sn-score-title">' + year + ' 연간 종합 운세</div>' +
            '<p>' + toneMsg + '</p>' +
            '<p>최고의 달 — <b>' + bestMonth.month + '월</b> (' + bestMonth.score + '점) · ' + escapeHtml(bestMonth.summary || '큰 흐름이 열리는 시기') + '</p>' +
            '<p>신중한 달 — <b>' + worstMonth.month + '월</b> (' + worstMonth.score + '점) · ' + escapeHtml(worstMonth.summary || '준비와 정리의 시기') + '</p>' +
          '</div>' +
        '</div>' +
        '<div class="sn-domains">' +
          renderDomain('財', '재물', wealthScore) +
          renderDomain('情', '연애', loveScore) +
          renderDomain('壽', '건강', healthScore) +
          renderDomain('業', '직업', careerScore) +
        '</div>' +
        '<div class="sn-vow">' +
          '<div class="sn-vow-title">' + year + ' 새해 다짐 가이드</div>' +
          '<div class="sn-vow-list">' +
            '<div class="sn-vow-item"><b>강점 키우기</b><span>' + getStrongDomain(wealthScore, loveScore, healthScore, careerScore) + '</span></div>' +
            '<div class="sn-vow-item"><b>약점 보완</b><span>' + getWeakDomain(wealthScore, loveScore, healthScore, careerScore) + '</span></div>' +
            '<div class="sn-vow-item"><b>최고의 달 활용</b><span>' + bestMonth.month + '월에 큰 결정·도전·시작</span></div>' +
            '<div class="sn-vow-item"><b>주의 시기 대비</b><span>' + worstMonth.month + '월엔 휴식·점검·내실</span></div>' +
          '</div>' +
        '</div>' +
      '</div>';

      var wrap = document.createElement('div');
      wrap.innerHTML = html;
      var enhancedEl = wrap.firstChild;

      // monthly-grid가 없으면 enhanced view 안에 12개월 카드 직접 그리기 (무료 사주 시)
      var monthlyEl = findMonthlyEl();
      if (!monthlyEl) {
        // 12개월 카드 직접 inject
        var monthlyHtml = '<h3 style="font-family:Noto Serif KR,serif;color:var(--gold2,#e0c060);font-size:1.15rem;margin:24px 0 14px;text-align:center;">' + year + '년 월별 운세</h3>' +
          '<div class="monthly-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;">';
        mf.forEach(function(m) {
          var sc = m.score || 70;
          var col = sc >= 80 ? '#2ecc71' : sc >= 60 ? '#f1c40f' : '#e74c3c';
          monthlyHtml += '<div style="background:rgba(0,0,0,0.20);border:1px solid var(--border,#2a2e3e);border-radius:10px;padding:14px;">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
              '<span style="font-family:Noto Serif KR,serif;font-size:1.05rem;color:var(--gold2,#e0c060);font-weight:700;">' + m.month + '월</span>' +
              '<span style="font-family:Playfair Display,serif;font-size:1.25rem;color:' + col + ';font-weight:800;">' + sc + '점</span>' +
            '</div>' +
            (m.간지 ? '<div style="font-size:0.78rem;color:var(--text2,#a89985);margin-bottom:6px;">' + escapeHtml(m.간지) + ' (' + escapeHtml(m.십신 || '') + ')</div>' : '') +
            (m.summary ? '<p style="font-size:0.82rem;color:var(--text,#e8e0d0);line-height:1.5;margin:6px 0;">' + escapeHtml(m.summary) + '</p>' : '') +
            '<div style="display:flex;flex-wrap:wrap;gap:8px;font-size:0.72rem;color:var(--text2,#a89985);margin-top:8px;">' +
              (m.wealth ? '<span>💰 ' + escapeHtml(m.wealth) + '</span>' : '') +
              (m.love ? '<span>💕 ' + escapeHtml(m.love) + '</span>' : '') +
              (m.health ? '<span>💪 ' + escapeHtml(m.health) + '</span>' : '') +
              (m.career ? '<span>📈 ' + escapeHtml(m.career) + '</span>' : '') +
            '</div>' +
            (m.lucky_day ? '<div style="margin-top:8px;font-size:0.74rem;"><span style="color:#5dd5b8;">길일: ' + m.lucky_day + '일</span> · <span style="color:#e87070;">주의: ' + (m.caution_day || '-') + '일</span></div>' : '') +
            '</div>';
        });
        monthlyHtml += '</div>';
        // enhanced view 안에 monthly section 추가 (sn-vow 위에)
        var vowEl = enhancedEl.querySelector('.sn-vow');
        var monthlyWrap = document.createElement('div');
        monthlyWrap.innerHTML = monthlyHtml;
        if (vowEl) vowEl.parentElement.insertBefore(monthlyWrap, vowEl);
        else enhancedEl.appendChild(monthlyWrap);
      }
      // 12개월 운세 grid 위에 inject (있으면 그 자리, 없으면 saju-result 맨 위)
      if (monthlyEl && monthlyEl.parentElement) {
        var section = monthlyEl.closest('.premium-section') || monthlyEl.parentElement;
        section.parentElement.insertBefore(enhancedEl, section);
      } else {
        var sajuResult = document.getElementById('saju-result');
        if (sajuResult) sajuResult.insertBefore(enhancedEl, sajuResult.firstChild);
      }
    } catch (e) {
      console.error('[sinnyeon] render failed', e);
    }
  };

  function renderDomain(hanja, label, score) {
    return '<div class="sn-domain">' +
      '<div class="sn-domain-hanja">' + hanja + '</div>' +
      '<div class="sn-domain-label">' + label + '</div>' +
      '<div class="sn-domain-score">' + score + '</div>' +
      '<div class="sn-domain-bar"><div class="sn-domain-bar-fill" style="width:' + Math.min(100, score) + '%;"></div></div>' +
    '</div>';
  }

  function getStrongDomain(w, l, h, c) {
    var arr = [{n:'재물',v:w,a:'재물 흐름이 강한 해. 투자·이직·창업 적기'},
               {n:'연애',v:l,a:'관계 운이 좋은 해. 새로운 만남·결혼·관계 강화'},
               {n:'건강',v:h,a:'건강 운이 강한 해. 체력·체질 개선 도전'},
               {n:'직업',v:c,a:'커리어 도약의 해. 승진·이직·새 프로젝트'}];
    arr.sort(function(a,b){return b.v - a.v;});
    return arr[0].n + ' (' + arr[0].v + '점) — ' + arr[0].a;
  }

  function getWeakDomain(w, l, h, c) {
    var arr = [{n:'재물',v:w,a:'무리한 지출·투자 자제, 저축 우선'},
               {n:'연애',v:l,a:'성급한 결정 X, 감정 정리 시간'},
               {n:'건강',v:h,a:'정기 검진·휴식·생활 리듬 점검'},
               {n:'직업',v:c,a:'성과보다 안정·내실, 새 프로젝트 자제'}];
    arr.sort(function(a,b){return a.v - b.v;});
    return arr[0].n + ' (' + arr[0].v + '점) — ' + arr[0].a;
  }

  function escapeHtml(s) {
    return String(s || '').replace(/[&<>"']/g, function(c) {
      return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c];
    });
  }
})();
