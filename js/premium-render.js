/**
 * 천명당 유료 사주 상세 풀이 — 결과 렌더링
 * PremiumSaju.generateReport() 결과를 HTML로 변환합니다.
 */

(function(root) {
  'use strict';

  function renderPremiumResult(report, targetElId) {
    var el = document.getElementById(targetElId);
    if (!el) return;

    var r = report;
    var saju = r.saju;
    var isMarried = r.userContext && r.userContext.marital === 'married';
    var isDivorced = r.userContext && r.userContext.marital === 'divorced';
    var hasChildren = r.userContext && r.userContext.children > 0;

    var html = '';

    // ═══════════════════════════════════════
    // 헤더
    // ═══════════════════════════════════════
    html += '<div class="premium-header">';
    html += '<div class="premium-badge">PREMIUM</div>';
    html += '<h2>천명당 사주 상세 풀이</h2>';
    html += '<p class="premium-info">' + r.basic.입력.양력 + ' ' + r.basic.입력.시간 + ' | ' + r.basic.입력.성별 + ' | ' + r.basic.띠 + '띠</p>';
    html += '<p class="premium-ganji">' + saju.summary + '</p>';
    html += '<p class="premium-hanja">' + saju.summary_한자 + '</p>';
    html += '</div>';

    // ═══════════════════════════════════════
    // 1. 일간 심층 분석
    // ═══════════════════════════════════════
    var id = r.ilganDetail;
    if (id && id.nature) {
      html += '<div class="premium-section">';
      html += '<h3>1. 일간 심층 분석 — ' + id.nature + '</h3>';
      html += '<p class="premium-text">' + id.desc + '</p>';
      html += '<div class="premium-grid-2">';
      html += '<div class="premium-card"><h5>💼 적합 직업</h5><p>' + id.career + '</p></div>';
      html += '<div class="premium-card"><h5>💰 재물 패턴</h5><p>' + id.wealth + '</p></div>';
      html += '</div>';
      html += '<div class="premium-card"><h5>🏥 건강 포인트</h5><p>' + id.health_tip + '</p></div>';
      html += '</div>';
    }

    // ═══════════════════════════════════════
    // 2. 오행 분포 + 용신
    // ═══════════════════════════════════════
    html += '<div class="premium-section">';
    html += '<h3>2. 오행 분포 & 용신</h3>';
    html += '<div class="premium-ohaeng">';
    var elNames = ['목','화','토','금','수'];
    var elColors = {'목':'#2ecc71','화':'#e74c3c','토':'#f1c40f','금':'#ecf0f1','수':'#3498db'};
    var total = r.ohaeng.total || 8;
    elNames.forEach(function(name) {
      var cnt = r.ohaeng[name] || 0;
      var pct = Math.round(cnt / total * 100);
      html += '<div class="ohaeng-item">';
      html += '<span class="ohaeng-name" style="color:' + elColors[name] + '">' + name + '</span>';
      html += '<div class="ohaeng-bar"><div class="ohaeng-fill" style="width:' + pct + '%;background:' + elColors[name] + '"></div></div>';
      html += '<span class="ohaeng-cnt">' + cnt + '</span>';
      html += '</div>';
    });
    html += '</div>';
    html += '<div class="premium-card" style="border-left:3px solid ' + elColors[r.yongshin.용신] + '">';
    html += '<h5>용신: ' + r.yongshin.용신 + ' | 희신: ' + r.yongshin.희신 + ' | 기신: ' + r.yongshin.기신 + '</h5>';
    html += '<p>' + r.yongshin.설명 + '</p>';
    html += '</div></div>';

    // ═══════════════════════════════════════
    // 3. 신살 분석
    // ═══════════════════════════════════════
    if (r.shinsal.length > 0) {
      html += '<div class="premium-section">';
      html += '<h3>3. 신살 분석</h3>';
      r.shinsal.forEach(function(s) {
        var icon = s.type === 'positive' ? '✨' : s.type === 'neutral' ? '⚡' : '⚠️';
        html += '<div class="premium-card shinsal-card">';
        html += '<h5>' + icon + ' ' + s.name + ' (' + s.hanja + ') — ' + s.position + '</h5>';
        html += '<p>' + s.description + '</p>';
        html += '</div>';
      });
      html += '</div>';
    }

    // ═══════════════════════════════════════
    // 4. 건강운
    // ═══════════════════════════════════════
    if (r.health.length > 0) {
      html += '<div class="premium-section">';
      html += '<h3>4. 건강운</h3>';
      r.health.forEach(function(h) {
        var icon = h.type === 'excess' ? '🔴' : h.type === 'deficient' ? '⚪' : '🟡';
        html += '<div class="premium-card health-card">';
        html += '<h5>' + icon + ' ' + h.element + ' ' + (h.type === 'excess' ? '과다' : '부족') + ' → ' + h.organ + '</h5>';
        html += '<p><strong>관련 부위:</strong> ' + h.body + '</p>';
        html += '<p><strong>주의 증상:</strong> ' + h.description + '</p>';
        html += '<p>' + h.advice + '</p>';
        if (h.foods) {
          html += '<p><strong>🥗 보양 음식:</strong> ' + h.foods.join(', ') + '</p>';
        }
        html += '</div>';
      });
      html += '</div>';
    }

    // ═══════════════════════════════════════
    // 5. 부부운/연애운
    // ═══════════════════════════════════════
    html += '<div class="premium-section">';
    var loveTitle = isMarried ? '5. 부부운 · 가정운' : isDivorced ? '5. 새 인연운' : '5. 연애 · 결혼운';
    html += '<h3>' + loveTitle + '</h3>';

    // 십신 기반 분석
    var spouseStar = r.userContext.gender === 'M' ? '정재' : '정관';
    var loverStar = r.userContext.gender === 'M' ? '편재' : '편관';
    var hasSpouse = false, hasLover = false;
    r.sipsinList.forEach(function(s) {
      if (s.천간 && (s.천간.십신 === spouseStar || s.지지.십신 === spouseStar)) hasSpouse = true;
      if (s.천간 && (s.천간.십신 === loverStar || s.지지.십신 === loverStar)) hasLover = true;
    });

    html += '<div class="premium-card">';
    if (isMarried) {
      html += '<p class="premium-text">';
      if (hasSpouse && hasLover) html += '배우자운과 대인관계운이 모두 활발한 사주입니다. 가정과 사회적 활동의 균형이 중요합니다. 배우자와의 소통 시간을 확보하면서 사회 활동도 병행하세요.';
      else if (hasSpouse) html += '배우자와의 인연이 깊고 안정적인 사주입니다. 서로의 신뢰가 탄탄하며, 가정 내 화합이 잘 이루어집니다.';
      else if (hasLover) html += '현재 부부 관계에서 재정립의 기운이 있습니다. 이는 위기가 아니라 관계를 더 깊게 만드는 과정입니다. 배우자와 깊은 대화를 나누세요.';
      else html += '가정운이 잠시 소강 상태이나, 이는 각자의 성장에 집중하는 시기입니다. 작은 관심 표현을 잊지 마세요.';
      html += '</p>';
      if (hasChildren) {
        var childCnt = r.userContext.children >= 3 ? '3명 이상의' : r.userContext.children + '명의';
        html += '<p class="premium-text"><strong>자녀운:</strong> ' + childCnt + ' 자녀를 둔 가정으로서, 자녀 교육과 가정의 안정에 큰 에너지를 쏟는 시기입니다. 각 자녀의 개성을 인정하고 독립성을 키워주는 양육이 중요합니다.</p>';
      }
    } else {
      if (hasSpouse) html += '<p class="premium-text">배우자운이 뚜렷한 사주입니다. 안정적이고 좋은 인연을 만날 가능성이 높습니다.</p>';
      else if (hasLover) html += '<p class="premium-text">이성 인연이 많은 사주입니다. 진지한 관계로 발전시키려면 신중한 선택이 필요합니다.</p>';
      else html += '<p class="premium-text">현재는 자기 발전에 집중하는 시기입니다. 때가 되면 좋은 인연이 자연스럽게 찾아옵니다.</p>';
    }
    html += '</div></div>';

    // ═══════════════════════════════════════
    // 6. 초년/중년/말년
    // ═══════════════════════════════════════
    html += '<div class="premium-section">';
    html += '<h3>6. 인생 3막 — 초년 · 중년 · 말년</h3>';
    html += '<div class="premium-grid-3">';
    var phaseLabels = {early: '🌱 초년 (0~30세)', middle: '🌳 중년 (30~60세)', late: '🍂 말년 (60세~)'};
    var phaseKeys = ['early','middle','late'];
    phaseKeys.forEach(function(key) {
      var pillars = r.phases[key] || [];
      html += '<div class="premium-card phase-card">';
      html += '<h5>' + phaseLabels[key] + '</h5>';
      html += '<p>' + r.phasesSummary[key] + '</p>';
      if (pillars.length > 0) {
        html += '<div class="phase-daeun">';
        pillars.forEach(function(dp) {
          html += '<span class="daeun-chip">' + dp.간지 + ' (' + dp.startAge + '~' + dp.endAge + ')</span>';
        });
        html += '</div>';
      }
      html += '</div>';
    });
    html += '</div></div>';

    // ═══════════════════════════════════════
    // 7. 올해 운세 (세운)
    // ═══════════════════════════════════════
    var yd = r.yearlyDetail;
    html += '<div class="premium-section">';
    html += '<h3>7. ' + yd.year + '년 세운 — ' + yd.간지 + '(' + yd.한자 + ')년</h3>';
    html += '<div class="premium-card yearly-card">';
    html += '<p><strong>올해의 십신:</strong> ' + yd.십신 + ' | <strong>12운성:</strong> ' + yd.운성 + '</p>';
    if (yd.detail && yd.detail.career) {
      html += '<p><strong>💼 직업운:</strong> ' + yd.detail.career + '</p>';
      html += '<p><strong>💰 재물운:</strong> ' + yd.detail.wealth + '</p>';
      html += '<p><strong>💑 관계운:</strong> ' + yd.detail.relation + '</p>';
    }
    html += '</div></div>';

    // ═══════════════════════════════════════
    // 8. 월별 운세 (1~12월)
    // ═══════════════════════════════════════
    html += '<div class="premium-section">';
    html += '<h3>8. ' + yd.year + '년 월별 운세</h3>';
    html += '<div class="monthly-grid">';
    r.monthlyFortunes.forEach(function(mf) {
      var scoreColor = mf.score >= 80 ? '#2ecc71' : mf.score >= 60 ? '#f1c40f' : '#e74c3c';
      html += '<div class="monthly-card">';
      html += '<div class="monthly-header">';
      html += '<span class="monthly-month">' + mf.month + '월</span>';
      html += '<span class="monthly-score" style="color:' + scoreColor + '">' + mf.score + '점</span>';
      html += '</div>';
      html += '<div class="monthly-ganji">' + mf.간지 + ' (' + mf.십신 + ')</div>';
      html += '<p class="monthly-summary">' + mf.summary + '</p>';
      html += '<div class="monthly-stars">';
      html += '<div>💰 재물 ' + mf.wealth + '</div>';
      html += '<div>💕 연애 ' + mf.love + '</div>';
      html += '<div>💪 건강 ' + mf.health + '</div>';
      html += '<div>📈 직업 ' + mf.career + '</div>';
      html += '</div>';
      html += '<div class="monthly-days">';
      html += '<span class="lucky-day">길일: ' + mf.lucky_day + '일</span>';
      html += '<span class="caution-day">주의일: ' + mf.caution_day + '일</span>';
      html += '</div>';
      html += '</div>';
    });
    html += '</div></div>';

    // ═══════════════════════════════════════
    // 9. 시간대별 운세
    // ═══════════════════════════════════════
    html += '<div class="premium-section">';
    html += '<h3>9. 시간대별 운세</h3>';
    html += '<div class="hourly-grid">';
    r.hourlyFortune.forEach(function(h) {
      var ratingColor = {'활동적':'#2ecc71','안정':'#3498db','재물':'#f1c40f','주의':'#e74c3c','보통':'#95a5a6'};
      html += '<div class="hourly-card" style="border-left:3px solid ' + (ratingColor[h.rating] || '#888') + '">';
      html += '<strong>' + h.name + '</strong> <span class="hourly-time">' + h.time + '</span>';
      html += '<span class="hourly-rating" style="color:' + (ratingColor[h.rating] || '#888') + '">' + h.rating + '</span>';
      html += '<p>' + h.advice + '</p>';
      html += '</div>';
    });
    html += '</div></div>';

    // ═══════════════════════════════════════
    // 10. 행운 코디
    // ═══════════════════════════════════════
    var lc = r.luckyCodi;
    html += '<div class="premium-section">';
    html += '<h3>10. 행운 코디</h3>';
    html += '<div class="premium-grid-2">';

    html += '<div class="premium-card">';
    html += '<h5>🎨 행운 색상</h5>';
    html += '<div class="color-swatches">';
    lc.lucky_colors.hex.forEach(function(hex, i) {
      html += '<div class="color-swatch" style="background:' + hex + '"><span>' + lc.lucky_colors.colors[i] + '</span></div>';
    });
    html += '</div>';
    html += '<p style="margin-top:8px;font-size:0.8rem;color:#888;">보조색: ' + lc.sub_colors.colors.join(', ') + '</p>';
    html += '</div>';

    html += '<div class="premium-card">';
    html += '<h5>🧭 행운 방위 · 숫자</h5>';
    html += '<p><strong>주 방위:</strong> ' + lc.direction + ' | <strong>보조:</strong> ' + lc.sub_direction + '</p>';
    html += '<p><strong>행운 숫자:</strong> ' + lc.numbers.join(', ') + ' | <strong>보조:</strong> ' + lc.sub_numbers.join(', ') + '</p>';
    html += '</div>';

    html += '<div class="premium-card" style="grid-column:1/-1">';
    html += '<h5>🍽️ 행운 음식</h5>';
    html += '<p>' + lc.foods.join(' | ') + '</p>';
    html += '<p style="font-size:0.8rem;color:#888;">보조: ' + lc.sub_foods.join(' | ') + '</p>';
    html += '</div>';
    html += '</div></div>';

    // ═══════════════════════════════════════
    // 11. 바이오리듬
    // ═══════════════════════════════════════
    var bio = r.biorhythm;
    html += '<div class="premium-section">';
    html += '<h3>11. 오늘의 바이오리듬</h3>';
    html += '<div class="bio-grid">';
    var bioItems = [
      {name: '💪 신체', value: bio.physical, color: '#e74c3c'},
      {name: '💕 감정', value: bio.emotional, color: '#e67e22'},
      {name: '🧠 지성', value: bio.intellectual, color: '#3498db'},
      {name: '✨ 직관', value: bio.intuitive, color: '#9b59b6'},
    ];
    function bioStateLabel(v) {
      if (v >= 80) return '최고조';
      if (v >= 30) return '좋음';
      if (v >= -29) return '평이';
      if (v >= -79) return '저조';
      return '최저';
    }
    bioItems.forEach(function(b) {
      var width = Math.abs(b.value) / 2; // 반쪽 바라서 /2
      var isPositive = b.value >= 0;
      var state = bioStateLabel(b.value);
      html += '<div class="bio-item">';
      html += '<span class="bio-label">' + b.name + '</span>';
      html += '<div class="bio-bar">';
      if (isPositive) {
        html += '<div class="bio-fill-pos" style="width:' + width + '%;background:' + b.color + '"></div>';
      } else {
        html += '<div class="bio-fill-neg" style="width:' + width + '%;background:' + b.color + ';opacity:0.7"></div>';
      }
      html += '</div>';
      html += '<span class="bio-value" style="color:' + b.color + '">' + b.value + '%<span class="bio-state">(' + state + ')</span></span>';
      html += '</div>';
    });
    html += '</div></div>';

    // ═══════════════════════════════════════
    // 12. 대운 흐름 (전체)
    // ═══════════════════════════════════════
    html += '<div class="premium-section">';
    html += '<h3>12. 대운 흐름 (' + r.daeun.direction + ')</h3>';
    var currentAge = new Date().getFullYear() - parseInt(r.basic.입력.양력);

    // 대운 십신별 해석
    var daeunDesc = {
      '비견': '독립심이 강해지고 경쟁이 치열해지는 시기. 자기 힘으로 길을 개척합니다.',
      '겁재': '재물 변동이 크고 파트너/동료와의 갈등 주의. 보증/투자 신중히.',
      '식신': '먹고 사는 복이 풍성한 시기. 건강하고 편안하며 여유로운 삶.',
      '상관': '창의력 폭발, 기존 틀을 깨는 혁신의 시기. 자유직/예술에 유리.',
      '편재': '큰 돈이 움직이는 시기. 사업 확장, 투자 기회. 리스크 관리 필수.',
      '정재': '안정적 수입, 가정 화목. 부동산/저축에 유리한 시기.',
      '편관': '변화와 도전, 조직 내 갈등 가능. 준비된 자에게 승진/도약의 기회.',
      '정관': '명예와 인정을 받는 시기. 승진, 사회적 지위 상승.',
      '편인': '독창적 아이디어, 전문성 강화. 새로운 분야 공부/자격증에 유리.',
      '정인': '학문/교육의 발전기. 어른/스승의 도움. 안정적 성장.',
    };

    r.daeun.pillars.forEach(function(dp) {
      var isCurrent = currentAge >= dp.startAge && currentAge <= dp.endAge;
      var desc = daeunDesc[dp.십신_천간] || '';
      html += '<div class="daeun-detail-card' + (isCurrent ? ' current' : '') + '">';
      html += '<div class="daeun-detail-header">';
      html += '<span class="daeun-age-label">' + dp.startAge + '~' + dp.endAge + '세' + (isCurrent ? ' ★현재' : '') + '</span>';
      html += '<span class="daeun-ganji-label">' + dp.간지 + ' (' + dp.한자 + ')</span>';
      html += '<span class="daeun-sipsin-label">' + dp.십신_천간 + ' / ' + dp.운성 + '</span>';
      html += '</div>';
      if (desc) html += '<p class="daeun-desc">' + desc + '</p>';
      html += '</div>';
    });
    html += '</div>';

    // ═══════════════════════════════════════
    // 13. 종합 조언
    // ═══════════════════════════════════════
    html += '<div class="premium-section premium-conclusion">';
    html += '<h3>📜 종합 조언</h3>';
    html += '<div class="premium-card" style="border-color:var(--gold);background:rgba(201,168,76,0.05)">';
    html += '<p class="premium-text">';
    html += id.nature + '의 성격을 가진 당신은 ' + (id.career || '다양한 분야') + '에서 두각을 나타낼 수 있습니다. ';
    html += '용신인 ' + r.yongshin.용신 + '의 기운을 보강하여 ';
    html += '행운 색상(' + lc.lucky_colors.colors[0] + ')과 행운 방위(' + lc.direction + ')를 활용하세요. ';
    if (isMarried) {
      html += '기혼자로서 가정의 안정과 배우자와의 소통이 가장 중요하며, ';
      if (hasChildren) html += '자녀 교육에도 균형 잡힌 관심이 필요합니다. ';
    }
    html += '올해는 ' + yd.십신 + '운으로 ' + (yd.detail.career || '좋은 기회가 있는 해') + '입니다. ';
    html += '건강 관리(' + (id.health_tip || '규칙적 운동') + ')도 잊지 마세요.';
    html += '</p>';
    html += '</div></div>';

    // ═══════════════════════════════════════
    // 푸터
    // ═══════════════════════════════════════
    html += '<div class="premium-footer">';
    html += '<p>천명당 사주 상세 풀이 — 쿤스튜디오</p>';
    html += '<p>본 풀이는 정통 명리학 원리에 기반한 AI 분석 결과입니다.</p>';
    html += '<button class="btn-gold premium-pdf-btn" onclick="downloadPremiumPDF()">📄 PDF 다운로드</button>';
    html += '</div>';

    // ═══════════════════════════════════════
    // 14. AI 맞춤 상담
    // ═══════════════════════════════════════
    html += '<div class="premium-section">';
    html += '<h3>💬 AI 사주 상담</h3>';
    html += '<p class="premium-text" style="margin-bottom:12px;">사주 분석 결과를 기반으로 궁금한 점을 질문해보세요.</p>';
    html += '<div class="ai-chat-area">';
    html += '<div id="ai-chat-messages" class="ai-messages"></div>';
    html += '<div class="ai-input-wrap">';
    html += '<input type="text" id="ai-chat-input" placeholder="예: 올해 이직해도 될까요?" onkeypress="if(event.key===\'Enter\')askAiSaju()">';
    html += '<button class="btn-gold" onclick="askAiSaju()" style="padding:10px 20px;white-space:nowrap;">질문하기</button>';
    html += '</div>';
    html += '<div class="ai-suggestions">';
    html += '<span onclick="askAiSajuPreset(this)">올해 이직 운은?</span>';
    html += '<span onclick="askAiSajuPreset(this)">재물운을 높이려면?</span>';
    html += '<span onclick="askAiSajuPreset(this)">건강 관리 조언</span>';
    html += '<span onclick="askAiSajuPreset(this)">부부 관계 개선법</span>';
    html += '<span onclick="askAiSajuPreset(this)">내 적성에 맞는 부업</span>';
    html += '</div>';
    html += '</div></div>';

    el.innerHTML = html;
    el.style.display = 'block';
  }

  // ─── 잠금/해제 헬퍼 (2026-04-27 월회원권 추가) ───
  // 월회원권 OR 단건 결제 OR 종합 풀이 보유 시 사주 풀이 OK
  // 외부 호출 예: PremiumRender.shouldRender('saju')
  function shouldRender(feature) {
    if (root.CmEntitlement && typeof root.CmEntitlement.canUnlock === 'function') {
      return root.CmEntitlement.canUnlock(feature || 'saju');
    }
    return false;
  }

  // 잠금 화면 HTML (월회원권 가치 제안 카드)
  // 정책: 월회원권은 사주/궁합 무제한, 종합 풀이는 별도 결제 필요
  function lockedHtml(feature) {
    var f = feature || 'saju';
    var label = ({ saju: '사주 정밀 풀이', gunghap: '궁합', comprehensive: '종합 풀이' }[f]) || '유료 풀이';
    var coveredByMonthly = (f !== 'comprehensive'); // 종합 풀이는 월회원 미포함

    var monthlyPitch = coveredByMonthly
      ? ('월회원권(₩9,900/월)으로 <strong style="color:#e8c97a;">사주·궁합 무제한 + 매일 카톡 운세</strong><br>또는 ' + label + ' 단건 결제(₩9,900)로 이번 한 번만 열람할 수 있습니다.')
      : ('종합 풀이는 단건 결제(<strong style="color:#e8c97a;">₩15,000</strong>)로만 열람 가능합니다.<br>사주+궁합 묶음 패키지로 <strong style="color:#e8c97a;">24% 할인</strong>된 가격입니다.');

    var ctaButton = coveredByMonthly
      ? '<button class="btn-gold" onclick="window.openOrder && window.openOrder(\'무제한 사주 구독권 (3일 무료체험)\', 9900)">월회원권 시작 (3일 무료)</button>'
      : '<button class="btn-gold" onclick="window.openOrder && window.openOrder(\'종합 풀이\', 15000)">종합 풀이 결제 (₩15,000)</button>';

    return [
      '<div class="premium-section premium-locked" style="text-align:center;padding:32px 20px;">',
      '<div style="font-size:2.4rem;margin-bottom:12px;">🔒</div>',
      '<h3 style="font-family:Gowun Batang,serif;color:var(--gold2,#e8c97a);font-size:1.2rem;margin-bottom:14px;">' + label + ' 잠금 해제</h3>',
      '<p style="color:#a89880;font-size:0.92rem;line-height:1.7;margin-bottom:18px;">',
      monthlyPitch,
      '</p>',
      ctaButton,
      '</div>'
    ].join('');
  }

  root.PremiumRender = {
    render: renderPremiumResult,
    shouldRender: shouldRender,
    lockedHtml: lockedHtml,
  };

})(typeof self !== 'undefined' ? self : this);
