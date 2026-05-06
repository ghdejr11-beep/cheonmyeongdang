/* ============================================================
   pdf-generator.js — 사주 결과 30페이지 PDF 다운로드
   ============================================================
   접근법: html2canvas(렌더링된 결과 → 이미지) + jsPDF(이미지 → PDF)
   - 한글 폰트 임베딩 회피 (브라우저 렌더 폰트 그대로 사용)
   - 결과 카드 영역을 페이지 단위로 자동 분할
   - 표지(1) + 30페이지 컨텐츠
   외부 의존: 무료 CDN(jsPDF, html2canvas) lazy load
   노출: window.downloadSajuPDF()  · window.PDFGen.generate(r, userInfo)
   ============================================================ */
(function(){
  'use strict';

  var JSPDF_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
  var H2C_CDN   = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';

  function loadScript(src) {
    return new Promise(function(resolve, reject){
      // 이미 로드되어 있으면 skip
      var existing = document.querySelector('script[src="'+src+'"]');
      if (existing) { resolve(); return; }
      var s = document.createElement('script');
      s.src = src;
      s.onload = function(){ resolve(); };
      s.onerror = function(){ reject(new Error('load failed: '+src)); };
      document.head.appendChild(s);
    });
  }

  function ensureLibs() {
    var p = [];
    if (typeof window.jspdf === 'undefined' && typeof window.jsPDF === 'undefined') p.push(loadScript(JSPDF_CDN));
    if (typeof window.html2canvas === 'undefined') p.push(loadScript(H2C_CDN));
    return Promise.all(p);
  }

  function getJsPDF() {
    if (window.jspdf && window.jspdf.jsPDF) return window.jspdf.jsPDF;
    if (window.jsPDF) return window.jsPDF;
    return null;
  }

  // 데이터 헬퍼 ───────────────────────────────────────────────
  function safeStem(saju, key) {
    if (!saju || !saju[key]) return '·';
    return (saju[key].stem || saju[key].천간 || '·') + (saju[key].branch || saju[key].지지 || '·');
  }
  function safe(o, p, def) {
    try { return o[p] != null ? o[p] : def; } catch(e) { return def; }
  }
  function getMonthlyData() {
    var months = [];
    var labels = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'];
    var pool = [
      '재물 흐름이 안정되며 새로운 기회가 들어옵니다. 지출보다 수입이 늘고, 작은 투자가 결실로 이어집니다.',
      '인간관계에서 변화가 있으나, 진심으로 다가가면 좋은 인연이 깊어집니다. 가족·동료의 협력이 큰 힘이 됩니다.',
      '직장·사업 운이 활발해지는 시기. 새 프로젝트나 도전이 유리합니다. 실수만 줄이면 결실이 따릅니다.',
      '건강 관리에 신경 쓸 시기. 무리한 업무는 피하고 휴식·운동의 균형을 맞추세요. 정신적 안정이 핵심.',
      '연애·결혼 운이 강화되는 달. 미혼은 좋은 인연을, 기혼은 부부간 화목한 시간을 보냅니다.',
      '학업·자격·시험 운이 따르는 시기. 새 분야 학습과 자격 도전이 길합니다. 집중력이 평소보다 높아집니다.',
      '문서·계약 관련 일이 활발합니다. 신중히 살피되 좋은 기회는 놓치지 마세요. 부동산·이사 운도 함께.',
      '뜻밖의 만남·여행 기회가 옵니다. 역마운이 강해지므로 변화·이동을 두려워 말고 받아들이세요.',
      '재물보다 명예·인정이 중요한 시기. 본인의 실력을 드러낼 기회가 옵니다. 욕심보다 정성으로.',
      '가정·내면을 정비하는 시기. 가족과의 시간, 자기성찰이 다음 도약의 발판이 됩니다.',
      '도전과 결단이 필요한 시기. 미루던 일을 정리하고 새 출발을 준비하세요. 결정은 신속하게.',
      '한 해 마무리와 새해 준비. 감사·휴식·계획의 시간. 내년 운기를 위해 몸·마음을 비우세요.'
    ];
    for (var i=0; i<12; i++) {
      months.push({ label: labels[i], text: pool[i] });
    }
    return months;
  }

  // 30페이지 HTML 빌드 ────────────────────────────────────────
  function buildPdfHTML(r, userInfo) {
    var saju = r['사주'] || {};
    var basic = r['기본정보'] || {};
    var ilgan = (basic['일간'] && basic['일간']['글자']) || '';
    var name = userInfo.name || '귀하';
    var birth = userInfo.birth || (basic['입력'] && basic['입력']['양력']) || '';
    var hour = userInfo.hour != null ? userInfo.hour : (basic['입력'] && basic['입력']['시']);
    var gender = userInfo.gender === 'F' ? '여자' : '남자';
    var today = new Date();
    var todayStr = today.getFullYear()+'-'+String(today.getMonth()+1).padStart(2,'0')+'-'+String(today.getDate()).padStart(2,'0');

    var sipsin = r['십신'] || [];
    var ohaeng = r['오행'] || {};
    var daeun = r['대운'] || {};
    var direction = daeun.direction || '순행';
    var startAge = daeun.startAge != null ? daeun.startAge : 0;

    // 페이지 공통 스타일
    var pageStyle = 'width:210mm;min-height:297mm;padding:18mm 16mm;box-sizing:border-box;background:#fff;color:#1a1206;font-family:"Noto Sans KR","Malgun Gothic",sans-serif;page-break-after:always;break-after:page;border-bottom:1px dashed #ccc;';
    var h2Style = 'color:#7d5a1a;font-size:22pt;margin:0 0 12mm 0;border-bottom:2px solid #c9a84c;padding-bottom:4mm;';
    var h3Style = 'color:#4a3318;font-size:14pt;margin:6mm 0 3mm 0;';
    var pStyle = 'font-size:11pt;line-height:1.85;color:#2a1f10;margin:0 0 4mm 0;';
    var noteStyle = 'font-size:9pt;color:#7a6a4e;margin-top:auto;';

    var html = '<div id="pdf-root" style="background:#fff;color:#1a1206;">';

    // PAGE 1 — 표지
    html += '<div style="'+pageStyle+'display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;background:linear-gradient(135deg,#fdf6e3,#f5e9c4);">';
    html += '<div style="font-size:38pt;color:#7d5a1a;font-weight:700;margin-bottom:10mm;">天命堂 · 사주 정밀 풀이</div>';
    html += '<div style="font-size:14pt;color:#4a3318;margin-bottom:30mm;">A4 30페이지 정통 명리학 보고서</div>';
    html += '<div style="font-size:13pt;color:#2a1f10;line-height:2.2;border:2px solid #c9a84c;padding:14mm 20mm;border-radius:6mm;background:#fff;">';
    html += '<div><strong>이름</strong> · '+name+'</div>';
    html += '<div><strong>생년월일</strong> · '+birth+'</div>';
    html += '<div><strong>태어난 시</strong> · '+(hour!=null?hour+'시':'미상')+'</div>';
    html += '<div><strong>성별</strong> · '+gender+'</div>';
    html += '<div><strong>일간(日干)</strong> · '+ilgan+'</div>';
    html += '</div>';
    html += '<div style="margin-top:auto;font-size:10pt;color:#7a6a4e;">생성일: '+todayStr+' · cheonmyeongdang.com</div>';
    html += '</div>';

    // PAGE 2 — 사주 8글자 + 십신
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">1. 사주 팔자 (四柱八字)</h2>';
    html += '<table style="width:100%;border-collapse:collapse;margin-bottom:8mm;">';
    html += '<thead><tr style="background:#fdf6e3;"><th style="padding:4mm;border:1px solid #c9a84c;">시주</th><th style="padding:4mm;border:1px solid #c9a84c;">일주</th><th style="padding:4mm;border:1px solid #c9a84c;">월주</th><th style="padding:4mm;border:1px solid #c9a84c;">년주</th></tr></thead>';
    html += '<tbody><tr style="font-size:24pt;text-align:center;">';
    html += '<td style="padding:6mm;border:1px solid #c9a84c;">'+safeStem(saju,'시주')+'</td>';
    html += '<td style="padding:6mm;border:1px solid #c9a84c;background:#fff7d6;">'+safeStem(saju,'일주')+'</td>';
    html += '<td style="padding:6mm;border:1px solid #c9a84c;">'+safeStem(saju,'월주')+'</td>';
    html += '<td style="padding:6mm;border:1px solid #c9a84c;">'+safeStem(saju,'년주')+'</td>';
    html += '</tr></tbody></table>';
    html += '<h3 style="'+h3Style+'">십신(十神) 분포</h3>';
    html += '<p style="'+pStyle+'">';
    var sipsinTxt = sipsin.map(function(s){
      return (s.위치||'') + ': ' + ((s.천간&&s.천간.십신)||'-') + ' / ' + ((s.지지&&s.지지.십신)||'-');
    }).join('<br>');
    html += sipsinTxt || '십신 데이터 없음';
    html += '</p>';
    html += '</div>';

    // PAGE 3 — 오행 분포 + 일간 톤
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">2. 오행 분포 + 일간 톤</h2>';
    html += '<p style="'+pStyle+'">';
    var ohaengTxt = '';
    if (ohaeng && typeof ohaeng === 'object') {
      Object.keys(ohaeng).forEach(function(k){ ohaengTxt += k + ': ' + ohaeng[k] + '개<br>'; });
    }
    html += ohaengTxt || '오행 데이터 분석 중';
    html += '</p>';
    html += '<h3 style="'+h3Style+'">일간 ('+ilgan+') 톤</h3>';
    var dayStemDesc = {
      '갑':'갑목(甲木) — 큰 나무. 강직·도전·리더십.',
      '을':'을목(乙木) — 꽃나무·풀. 부드러움·끈기·세심함.',
      '병':'병화(丙火) — 태양. 명랑·열정·표현력.',
      '정':'정화(丁火) — 촛불. 따뜻함·세심함·예술성.',
      '무':'무토(戊土) — 큰 산. 신뢰·안정·포용.',
      '기':'기토(己土) — 논밭. 실용·자상함·성실.',
      '경':'경금(庚金) — 큰 쇠. 결단·의리·강직.',
      '신':'신금(辛金) — 보석. 섬세·미적·완벽주의.',
      '임':'임수(壬水) — 바다. 지혜·포용·통찰.',
      '계':'계수(癸水) — 이슬. 직관·감수성·연구.'
    };
    html += '<p style="'+pStyle+'">'+(dayStemDesc[ilgan]||'본인의 일간 에너지를 정확히 분석한 결과입니다.')+'</p>';
    html += '</div>';

    // PAGE 4 — 신살(도화·역마·공망)
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">3. 신살(神煞) — 도화·역마·공망</h2>';
    html += '<h3 style="'+h3Style+'">도화살(桃花殺)</h3>';
    html += '<p style="'+pStyle+'">이성에게 매력 발산이 강한 사주의 특수성. 인연 기회가 많은 시기. 깊은 한 인연을 선택하는 안목이 핵심입니다.</p>';
    html += '<h3 style="'+h3Style+'">역마살(驛馬殺)</h3>';
    html += '<p style="'+pStyle+'">이동·해외·변화가 많은 사주. 영업·무역·물류·여행·콘텐츠·해외 진출에서 운이 풀립니다.</p>';
    html += '<h3 style="'+h3Style+'">공망(空亡)</h3>';
    html += '<p style="'+pStyle+'">공망지에 해당하는 운(대운/세운)에 결혼·이별·이동·이직 등 변동이 집중됩니다. 본인 사주의 일주 공망을 기준으로 시기를 가늠합니다.</p>';
    html += '</div>';

    // PAGE 5 — 신강·신약 + 용신
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">4. 신강·신약 + 용신(用神)</h2>';
    html += '<p style="'+pStyle+'">사주의 강약은 일간이 가진 에너지의 크기입니다. 신강(身強) 사주는 본인의 에너지를 외부로 쓰는 재성·관성 운에서 정점에 도달하고, 신약(身弱) 사주는 인성·비겁으로 본인을 보강해주는 운에서 정점에 도달합니다.</p>';
    html += '<h3 style="'+h3Style+'">용신(用神)</h3>';
    html += '<p style="'+pStyle+'">용신은 본 사주에 부족한 오행을 보강하여 운기를 균형 있게 만들어주는 핵심 기운입니다. 색·방향·숫자·요일을 일상에 녹여 적용하면 운기 상승 효과가 큽니다.</p>';
    html += '</div>';

    // PAGE 6 — 12운성
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">5. 12운성 (十二運星) — 4기둥 흐름</h2>';
    html += '<p style="'+pStyle+'">12운성은 일간이 각 지지에 놓였을 때의 에너지 상태를 12단계(절·태·양·장생·목욕·관대·건록·제왕·쇠·병·사·묘)로 나타냅니다. 4기둥의 12운성을 조합하면 인생 전체의 흐름이 보입니다.</p>';
    html += '<h3 style="'+h3Style+'">기둥별 12운성</h3>';
    html += '<p style="'+pStyle+'">년주: 조상·부모·초년 / 월주: 사회·청년기 / 일주: 본인·배우자궁 / 시주: 자녀·노년</p>';
    html += '<p style="'+pStyle+'">건록·제왕은 강한 시기, 절·태·묘는 정비·휴식의 시기. 약한 시기에 무리하지 않고 강한 시기에 도약하는 것이 핵심입니다.</p>';
    html += '</div>';

    // PAGE 7-8 — 대운 8개 흐름
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">6. 대운(大運) — 10년 단위 흐름 (전반)</h2>';
    html += '<p style="'+pStyle+'">대운은 10년 단위로 흐르는 큰 운기입니다. '+gender+'분의 경우 <strong>'+direction+'</strong>으로 흐르며, '+startAge+'세부터 시작됩니다.</p>';
    html += '<p style="'+pStyle+'">'+startAge+'세 ~ '+(startAge+9)+'세: 1대운 — 자아 형성·기초 다지기.</p>';
    html += '<p style="'+pStyle+'">'+(startAge+10)+'세 ~ '+(startAge+19)+'세: 2대운 — 학업·진로 결정·첫 도약.</p>';
    html += '<p style="'+pStyle+'">'+(startAge+20)+'세 ~ '+(startAge+29)+'세: 3대운 — 사회 진출·결혼 적령·재물 형성.</p>';
    html += '<p style="'+pStyle+'">'+(startAge+30)+'세 ~ '+(startAge+39)+'세: 4대운 — 인생 황금기 후보·전성기 진입.</p>';
    html += '</div>';

    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">6. 대운 — 10년 단위 흐름 (후반)</h2>';
    html += '<p style="'+pStyle+'">'+(startAge+40)+'세 ~ '+(startAge+49)+'세: 5대운 — 사회적 정점·재물 정점.</p>';
    html += '<p style="'+pStyle+'">'+(startAge+50)+'세 ~ '+(startAge+59)+'세: 6대운 — 경험·연륜의 황금기·후학 양성.</p>';
    html += '<p style="'+pStyle+'">'+(startAge+60)+'세 ~ '+(startAge+69)+'세: 7대운 — 정리·전수·내면 성숙.</p>';
    html += '<p style="'+pStyle+'">'+(startAge+70)+'세 ~ '+(startAge+79)+'세: 8대운 — 자녀·후학·여유.</p>';
    html += '<p style="'+pStyle+'">대운 방향이 '+direction+'이므로 '+(direction==='순행' ? '인생 후반(40~70대)에 운기가 강해지고 노년 활동이 길어집니다.' : '인생 전반(20~40대)에 운기가 빠르게 발현되어 조기 성공형, 30대 중반에 1차 정점이 옵니다.')+'</p>';
    html += '</div>';

    // PAGE 9-10 — 배우자운 정밀
    var spouseStar = gender === '남자' ? '정재(正財)' : '정관(正官)';
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">7. 배우자운 정밀 분석 (1)</h2>';
    html += '<p style="'+pStyle+'">'+gender+' 사주에서 <strong>'+spouseStar+'</strong>은 정식 배우자를 의미합니다. 본인 사주의 '+spouseStar+'의 강약·위치·다과를 통해 배우자감의 성향과 인연 시기를 가늠합니다.</p>';
    html += '<p style="'+pStyle+'">'+spouseStar+'이 천간에 투출(透出)되어 있으면 일찍 인연이 와서 결혼이 빠릅니다. 지지에만 있고 천간에 없으면 조용히 다가오는 인연으로 만혼(晩婚)의 가능성이 있습니다.</p>';
    html += '<p style="'+pStyle+'">'+spouseStar+'이 둘 이상이면 한 번의 인연으로는 마치지 않고 두 번에 걸쳐 깊어질 수 있습니다. 1차 결혼을 신중히 결정해야 합니다.</p>';
    html += '</div>';

    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">7. 배우자운 정밀 분석 (2)</h2>';
    html += '<p style="'+pStyle+'">배우자궁은 일지(日支)입니다. 일지의 12운성과 신살을 함께 봅니다.</p>';
    html += '<p style="'+pStyle+'">일지가 건록·제왕이면 배우자가 강건하고 책임감 있는 사람. 일지가 도화살에 닿으면 배우자가 매력적이고 인기 많은 사람.</p>';
    html += '<p style="'+pStyle+'">일주 공망에 닿는 시기에는 부부관계 변동이 일어날 수 있으므로, 그 시기에는 부부간 대화·여행·새 추억 만들기로 관계를 다져야 합니다.</p>';
    html += '</div>';

    // PAGE 11-12 — 자녀운
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">8. 자녀운 (1) — '+(gender==='남자'?'양육':'임신·출산')+'</h2>';
    if (gender === '남자') {
      html += '<p style="'+pStyle+'">남자 사주에서 자식은 <strong>관성(官星·정관/편관)</strong>으로 봅니다. 관성의 다과로 자녀 수와 인연을 가늠합니다.</p>';
      html += '<p style="'+pStyle+'">관성이 강하면 자녀가 본인의 사회적 명예를 높여주고, 관성이 약하면 자녀와의 소통보다 모범을 보이는 부정형(父情型)입니다.</p>';
    } else {
      html += '<p style="'+pStyle+'">여자 사주에서 자식은 <strong>식상(食傷·식신/상관)</strong>으로 봅니다. 식상이 강하면 임신·출산이 순조롭고 자녀가 표현력·창의력 풍부한 성품입니다.</p>';
      html += '<p style="'+pStyle+'">임신·출산 가장 좋은 시기는 본인 대운에서 식상이 들어오는 '+(startAge+10)+'~'+(startAge+30)+'세 사이입니다.</p>';
    }
    html += '</div>';

    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">8. 자녀운 (2) — 시주 자녀궁</h2>';
    html += '<p style="'+pStyle+'">자녀궁은 시주(時柱)입니다. 시주의 십신과 12운성을 함께 살펴 자녀와의 관계 흐름을 봅니다.</p>';
    html += '<p style="'+pStyle+'">시주가 길신이면 자녀와 효심 깊고 노년 의지처가 됩니다. 시주가 흉신이거나 공망에 닿으면 자녀와 거리가 멀어지는 시기가 있을 수 있으나, 정성을 기울이면 회복됩니다.</p>';
    html += '</div>';

    // PAGE 13-14 — 부모·형제·인성
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">9. 부모·인성운</h2>';
    html += '<p style="'+pStyle+'">인성(印星·정인/편인)은 부모(특히 어머니)·후원자·학업·자격증을 의미합니다. 인성이 강하면 부모의 도움·후원이 풍부하고, 학업·자격으로 성공합니다.</p>';
    html += '<p style="'+pStyle+'">인성이 약하면 자수성가형. 본인의 노력으로 일군 사주이며, 부모보다는 본인이 가족의 중심이 되는 흐름입니다.</p>';
    html += '</div>';

    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">10. 형제·동료운</h2>';
    html += '<p style="'+pStyle+'">비겁(比劫·비견/겁재)은 형제·자매·친구·동료·경쟁자를 의미합니다. 비겁이 적정하면 형제 1~2명, 동료와 협력이 좋고, 비겁이 너무 많으면 군겁쟁재(群劫爭財)로 재물 분배 갈등이 생길 수 있습니다.</p>';
    html += '<p style="'+pStyle+'">비겁이 약하면 외동 또는 형제 인연 적음. 독립적·단독 행동 사주로 본인의 자존감이 강합니다.</p>';
    html += '</div>';

    // PAGE 15-16 — 직업·승진·사업
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">11. 직업·승진·사업 시기 (1)</h2>';
    html += '<p style="'+pStyle+'">관성(官星)이 강하면 조직·공직·전문직 적합. 정관은 안정된 조직형, 편관은 경쟁·창업·해외 진출형입니다.</p>';
    html += '<p style="'+pStyle+'">재성(財星)이 강하면 본인의 기술·노하우로 큰돈을 만들어가는 자수성가 사업가형. 식상이 강하면 창의력·표현력 직업(예술·교육·디자인·콘텐츠)이 적합합니다.</p>';
    html += '</div>';

    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">11. 직업·승진·사업 시기 (2)</h2>';
    html += '<p style="'+pStyle+'">승진은 정관이 천간에 투출된 대운에 빠르게 옵니다. 사업운은 재성이 들어오는 대운에 활성화됩니다.</p>';
    html += '<p style="'+pStyle+'">대운 방향이 '+direction+'이므로, '+(direction==='순행' ? '40대 이후 사회적 정점이 옵니다. 조기 은퇴를 서두르지 마세요.' : '30대 중반에 1차 정점이 오므로 그 시기를 놓치지 말고 과감히 도전하세요.')+'</p>';
    html += '</div>';

    // PAGE 17-18 — 결혼 적령기
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">12. 결혼 적령기 (1)</h2>';
    if (gender === '남자') {
      html += '<p style="'+pStyle+'">남자의 결혼 적령기는 정재(正財)가 강해지는 대운입니다. 본 사주에서는 약 '+(startAge+20)+'~'+(startAge+30)+'세 사이가 1차 적령입니다.</p>';
      html += '<p style="'+pStyle+'">정재가 약하면 결혼이 늦거나(30대 후반~40대 초) 본인이 적극적으로 만들어가야 합니다. 만혼(晩婚)이 더 안정적인 사주도 있습니다.</p>';
    } else {
      html += '<p style="'+pStyle+'">여자의 결혼 적령기는 정관(正官)이 강해지는 대운입니다. 본 사주에서는 약 '+(startAge+18)+'~'+(startAge+28)+'세 사이가 1차 적령입니다.</p>';
      html += '<p style="'+pStyle+'">정관이 약하면 본인이 결혼보다 커리어를 더 중시할 수 있습니다. 늦은 결혼(30대 중반~) 또는 비혼 선택도 흉이 아닙니다.</p>';
    }
    html += '</div>';

    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">12. 결혼 적령기 (2) — 궁합 기준</h2>';
    html += '<p style="'+pStyle+'">배우자감 사주와의 궁합은 일주(일간+일지)의 합·충·형·해를 기준으로 봅니다. 일간끼리 합(合)이 되거나 일지끼리 삼합·육합이면 좋은 궁합입니다.</p>';
    html += '<p style="'+pStyle+'">단순히 띠 궁합만으로는 부족하며, 사주 8글자 전체의 보완 관계를 봐야 정확한 궁합 판단이 가능합니다.</p>';
    html += '</div>';

    // PAGE 19-20 — 인생 황금기
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">13. 인생 황금기 (1) — 4번째 대운</h2>';
    var goldenAge = startAge + 40;
    html += '<p style="'+pStyle+'">인생 황금기는 일반적으로 4번째 대운(약 <strong>'+(goldenAge-5)+'~'+(goldenAge+5)+'세</strong>)입니다. 신약 사주는 3번째 대운(약 '+(startAge+25)+'~'+(startAge+35)+'세)에 더 빠른 황금기가 올 수 있습니다.</p>';
    html += '<p style="'+pStyle+'">이 시기에 본인의 십신 능력이 최대로 발현되며, 사회적 인정·재물·명예·가정 안정이 한꺼번에 옵니다.</p>';
    html += '</div>';

    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">13. 인생 황금기 (2) — '+gender+' 특화</h2>';
    if (gender === '남자') {
      html += '<p style="'+pStyle+'">남자는 황금기 시기에 사회적 정점·재물 정점·가장(家長) 역할 정점이 한꺼번에 옵니다. 무리한 확장보다 지킬 것을 지키는 것이 중요합니다.</p>';
    } else {
      html += '<p style="'+pStyle+'">여자는 황금기 시기에 가정·자녀·본인 커리어 모두 안정되며 본인의 내면이 가장 단단해지는 시기입니다. 본인을 위한 시간을 따로 챙기세요.</p>';
    }
    html += '<p style="'+pStyle+'">이 시기를 놓치지 말고 큰 결정·큰 도약을 준비하세요. 다음 황금기까지는 10년이 걸립니다.</p>';
    html += '</div>';

    // PAGE 21-22 — 개운법
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">14. 개운법 (1) — 색·방향·숫자</h2>';
    html += '<p style="'+pStyle+'">본 사주의 일간 에너지에 부족한 용신을 보강하는 색·방향·숫자를 일상에 녹입니다. 휴대폰 배경, 지갑·옷의 색, 책상 방향, 행운 숫자를 활용한 비밀번호 등이 개운 효과가 있습니다.</p>';
    html += '<p style="'+pStyle+'">목(木): 초록·동쪽·3,8 / 화(火): 빨강·남쪽·2,7 / 토(土): 노랑·중앙·5,10 / 금(金): 흰색·서쪽·4,9 / 수(水): 검정·북쪽·1,6</p>';
    html += '</div>';

    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">14. 개운법 (2) — 직업·음식·보석</h2>';
    html += '<p style="'+pStyle+'">용신 오행에 해당하는 직업 분야가 가장 운이 풀립니다. 음식도 용신 오행에 해당하는 맛(목=신맛, 화=쓴맛, 토=단맛, 금=매운맛, 수=짠맛)을 적정히 챙기세요.</p>';
    html += '<p style="'+pStyle+'">보석·액세서리도 용신 오행에 맞춰 (목=옥/에메랄드, 화=루비/가넷, 토=시트린/호박, 금=다이아/실버, 수=사파이어/진주) 착용하면 효과가 있습니다.</p>';
    html += '</div>';

    // PAGE 23-28 — 매월 운세 12개월 (6페이지, 페이지당 2개월)
    var months = getMonthlyData();
    for (var i = 0; i < 12; i += 2) {
      html += '<div style="'+pageStyle+'">';
      html += '<h2 style="'+h2Style+'">15. '+(today.getFullYear())+'년 월별 운세 ('+months[i].label+'~'+months[i+1].label+')</h2>';
      html += '<h3 style="'+h3Style+'">'+months[i].label+'</h3>';
      html += '<p style="'+pStyle+'">'+months[i].text+'</p>';
      html += '<h3 style="'+h3Style+'">'+months[i+1].label+'</h3>';
      html += '<p style="'+pStyle+'">'+months[i+1].text+'</p>';
      html += '</div>';
    }

    // PAGE 29 — 종합 정리
    html += '<div style="'+pageStyle+'">';
    html += '<h2 style="'+h2Style+'">16. 종합 정리</h2>';
    html += '<p style="'+pStyle+'">본 사주의 강점은 일간 '+ilgan+'의 고유한 에너지에 있습니다. 약점은 부족한 오행에 있으며, 이는 용신 보강을 통해 충분히 만회 가능합니다.</p>';
    html += '<p style="'+pStyle+'">대운 방향이 '+direction+'이므로 '+(direction==='순행'?'인생 후반에 운기가 무르익습니다. 조급해하지 말고 꾸준히 쌓아가세요.':'인생 전반에 빠른 도약이 있습니다. 30대 중반의 1차 정점을 놓치지 마세요.')+'</p>';
    html += '<p style="'+pStyle+'">'+gender+'으로서의 특화 분석은 위 7가지 카드에서 정밀하게 다뤘습니다. 본 보고서를 곁에 두고 인생의 큰 결정마다 참고하세요.</p>';
    html += '</div>';

    // PAGE 30 — 표지(맺음)
    html += '<div style="'+pageStyle+'display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;background:linear-gradient(135deg,#f5e9c4,#fdf6e3);">';
    html += '<div style="font-size:32pt;color:#7d5a1a;font-weight:700;margin-bottom:10mm;">감사합니다</div>';
    html += '<p style="font-size:13pt;color:#2a1f10;line-height:2;max-width:140mm;">정통 명리학은 운명을 정해주는 것이 아니라,<br>본인의 강점과 약점을 알고 그에 맞춰 살아가는<br>지혜의 도구입니다.<br><br>본 보고서가 인생의 큰 결정에 도움이 되기를 바랍니다.</p>';
    html += '<div style="margin-top:auto;font-size:11pt;color:#7a6a4e;">天命堂 · cheonmyeongdang.com<br>'+todayStr+' 생성</div>';
    html += '</div>';

    html += '</div>'; // /pdf-root
    return html;
  }

  // PDF 생성 메인 ───────────────────────────────────────────
  function generateSajuPDF(sajuResult, userInfo) {
    if (!sajuResult) {
      alert('사주 결과가 없습니다. 먼저 사주 풀이를 받아주세요.');
      return Promise.reject(new Error('no result'));
    }
    userInfo = userInfo || {};

    // UI 피드백
    var btn = document.querySelector('.btn-pdf');
    var originalLabel = btn ? btn.innerHTML : '';
    if (btn) { btn.disabled = true; btn.innerHTML = '⏳ PDF 생성 중...(20~40초)'; }

    return ensureLibs().then(function(){
      var jsPDFCtor = getJsPDF();
      if (!jsPDFCtor) throw new Error('jsPDF not loaded');

      // 오프스크린 컨테이너에 PDF용 HTML 삽입
      var off = document.createElement('div');
      off.style.cssText = 'position:fixed;left:-99999px;top:0;width:210mm;background:#fff;z-index:-1;';
      off.innerHTML = buildPdfHTML(sajuResult, userInfo);
      document.body.appendChild(off);

      var pages = off.querySelectorAll('#pdf-root > div');
      var pdf = new jsPDFCtor({ unit:'mm', format:'a4', orientation:'portrait' });

      function renderPage(idx) {
        if (idx >= pages.length) return Promise.resolve();
        var pageEl = pages[idx];
        return window.html2canvas(pageEl, { scale:2, useCORS:true, backgroundColor:'#ffffff' }).then(function(canvas){
          var imgData = canvas.toDataURL('image/jpeg', 0.85);
          var pageW = 210, pageH = 297;
          if (idx > 0) pdf.addPage();
          pdf.addImage(imgData, 'JPEG', 0, 0, pageW, pageH);
          if (btn) btn.innerHTML = '⏳ PDF 생성 중... ('+(idx+1)+'/'+pages.length+')';
          return renderPage(idx+1);
        });
      }

      return renderPage(0).then(function(){
        var fname = '천명당_사주_'+(userInfo.name||'결과')+'_'+ (new Date()).getTime() +'.pdf';
        pdf.save(fname);
        document.body.removeChild(off);
        if (btn) { btn.disabled = false; btn.innerHTML = originalLabel || '📄 PDF 30페이지 다운로드'; }
        // 분석 이벤트
        try { if (window.cmEvent) window.cmEvent('pdf_download', { name: userInfo.name || '' }); } catch(e) {}
      });
    }).catch(function(err){
      console.error('[PDFGen]', err);
      alert('PDF 생성 중 오류가 발생했습니다. 새로고침 후 다시 시도해주세요.\n('+(err.message||err)+')');
      if (btn) { btn.disabled = false; btn.innerHTML = originalLabel || '📄 PDF 30페이지 다운로드'; }
      throw err;
    });
  }

  // 결과 데이터/사용자 정보 자동 수집 + 다운로드 트리거
  function downloadSajuPDF() {
    try {
      var r = window._lastSajuResult;
      if (!r) { alert('사주 결과가 없습니다. 먼저 사주 풀이를 받아주세요.'); return; }
      // 사용자 정보 수집 (localStorage / form)
      var ui = {};
      try { ui = JSON.parse(localStorage.getItem('cm_user_info') || '{}'); } catch(e) {}
      var userInfo = {
        name: ui.name || (document.getElementById('saju-name') && document.getElementById('saju-name').value) || '',
        birth: (r['기본정보'] && r['기본정보']['입력'] && r['기본정보']['입력']['양력']) || '',
        hour: r['기본정보'] && r['기본정보']['입력'] && r['기본정보']['입력']['시'],
        gender: (r._userContext && r._userContext.gender) || 'M'
      };
      // entitlement 가드
      var hasPremium = !!window._cmEntitlementVerified;
      if (!hasPremium) {
        // localStorage 보조 체크 (UI만 — 실제 다운로드 막지는 않음, 가벼운 체크)
        try {
          var skus = JSON.parse(localStorage.getItem('cm_purchases') || '[]');
          if (skus.indexOf('comprehensive_29900') >= 0 || skus.indexOf('saju_premium_9900') >= 0 || skus.indexOf('subscribe_monthly_29900') >= 0) {
            hasPremium = true;
          }
        } catch(e) {}
      }
      if (!hasPremium) {
        if (!confirm('PDF 30페이지 다운로드는 프리미엄 전용 기능입니다. 결제 페이지로 이동하시겠습니까?')) return;
        var p = document.getElementById('premium');
        if (p) p.scrollIntoView({behavior:'smooth'});
        return;
      }
      generateSajuPDF(r, userInfo);
    } catch(err) {
      console.error('[downloadSajuPDF]', err);
      alert('오류: '+(err.message||err));
    }
  }

  window.PDFGen = { generate: generateSajuPDF, build: buildPdfHTML };
  window.downloadSajuPDF = downloadSajuPDF;
})();
