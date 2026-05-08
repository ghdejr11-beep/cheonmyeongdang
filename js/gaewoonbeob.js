/* ============================================================
   gaewoonbeob.js — 개운법 (Lucky/Fortune-improving practices)
   ============================================================
   일간(日干) 10개 + 용신(用神) 오행 5개 기반 개운법 데이터.
   - 행운 색상 (RGB hex × 3)
   - 행운 방향 (동서남북중)
   - 행운 숫자 (×5)
   - 행운 요일
   - 추천 직업 키워드
   - 음식·음료 (오행 보강)
   - 휴대폰 배경화면 추천
   - 보석/액세서리 추천
   ──────────────────────────────────────────────────────────────
   참고: 정통 명리학(滴天髓·窮通寶鑑) + 五行歸類 — 오행과 색·
        방향·숫자·요일·식재의 대응표를 따른다. (천간 음양 차등 반영)
   외부 의존: window 전용. window.Gaewoonbeob.build(r) 노출.
   ============================================================ */
(function(){
  'use strict';

  // 오행별 기본 매핑
  var elementMap = {
    '木': {
      colors:  ['#2E7D32', '#43A047', '#66BB6A'], // 짙은 초록·연두
      direction: '동(東)',
      numbers: [3, 8, 13, 28, 38],
      day:     '목요일',
      job:     ['교육', '출판', '디자인', '스타트업', '환경', '의류·섬유', '한방·약초', '예술'],
      food:    '제철 채소·녹차·신맛(레몬/매실)·청포도',
      drink:   '녹차·매실차·민트·청량 음료',
      wallpaper: '대나무 숲, 푸른 소나무, 새벽 산림, 잎사귀 매크로',
      gem:     '에메랄드·말라카이트·아벤츄린·옥(玉)'
    },
    '火': {
      colors:  ['#D32F2F', '#E53935', '#EF5350'],
      direction: '남(南)',
      numbers: [2, 7, 12, 27, 37],
      day:     '화요일',
      job:     ['방송·미디어', '홍보·마케팅', '연예·엔터', '뷰티', '요식업', 'IT 프론트엔드', '전기·전자'],
      food:    '쓴맛(커피/다크초콜릿)·붉은 채소(토마토/파프리카)·딸기',
      drink:   '아메리카노·카카오·홍차·생강차',
      wallpaper: '일출, 노을, 모닥불, 빨간 단풍, 도심 야경',
      gem:     '루비·가넷·오팔(파이어)·산호'
    },
    '土': {
      colors:  ['#FBC02D', '#F9A825', '#A1887F'],
      direction: '중앙(中)',
      numbers: [5, 10, 15, 25, 50],
      day:     '토요일',
      job:     ['부동산', '건설·건축', '농업·식품', '중개·플랫폼', '교육 행정', '도자기·공예', '신탁·자산'],
      food:    '단맛(꿀/대추)·곡물(쌀/조)·뿌리채소(고구마/감자)·황색 콩',
      drink:   '대추차·옥수수수염차·우롱차·꿀물',
      wallpaper: '황금 들판, 사막, 토기·자기, 베이지 모래사장, 안정된 벽돌 건축',
      gem:     '시트린·타이거 아이·황수정·호박(琥珀)'
    },
    '金': {
      colors:  ['#FAFAFA', '#E0E0E0', '#FFD700'],
      direction: '서(西)',
      numbers: [4, 9, 14, 24, 49],
      day:     '금요일',
      job:     ['금융·증권', '법률·법무', '의료·외과', '귀금속', '기계·금속', '정밀공학', '군·경찰', '회계'],
      food:    '매운맛(고추/마늘/생강)·견과류·배·도라지·무',
      drink:   '도라지차·생강차·페퍼민트·스파클링 워터',
      wallpaper: '눈 덮인 산, 백자, 은빛 바위, 금속 텍스처, 미니멀 화이트',
      gem:     '다이아몬드·플래티넘·실버·문스톤·헤마타이트'
    },
    '水': {
      colors:  ['#0D47A1', '#1565C0', '#37474F'],
      direction: '북(北)',
      numbers: [1, 6, 11, 26, 36],
      day:     '수요일',
      job:     ['IT·SW·AI', '연구·학술', '유통·물류', '해운·수산', '주류·음료', '관광·여행', '컨설팅', '심리·상담'],
      food:    '짠맛(된장/간장 적절)·검은콩/검은깨·해조류·수산물',
      drink:   '검정콩차·우엉차·다시마차·생수(미네랄)',
      wallpaper: '바다, 폭포, 호수 윤슬, 빗방울, 심해 청색, 우주',
      gem:     '사파이어·아쿠아마린·블랙 오닉스·진주(흑·백)'
    }
  };

  // 일간 10간 → 오행 + 음양 + 미세 조정
  var dayStemMap = {
    '갑': { el:'木', yy:'양', desc:'갑목(甲木)·큰 나무' },
    '을': { el:'木', yy:'음', desc:'을목(乙木)·꽃나무·풀' },
    '병': { el:'火', yy:'양', desc:'병화(丙火)·태양' },
    '정': { el:'火', yy:'음', desc:'정화(丁火)·촛불·등불' },
    '무': { el:'土', yy:'양', desc:'무토(戊土)·큰 산' },
    '기': { el:'土', yy:'음', desc:'기토(己土)·논밭' },
    '경': { el:'金', yy:'양', desc:'경금(庚金)·큰 쇠·도끼' },
    '신': { el:'金', yy:'음', desc:'신금(辛金)·보석·정밀 금속' },
    '임': { el:'水', yy:'양', desc:'임수(壬水)·바다·강' },
    '계': { el:'水', yy:'음', desc:'계수(癸水)·이슬·시냇물' }
  };

  // 용신 오행 추정 (간단 규칙: 신강 → 식상/재성/관성, 신약 → 인성/비겁)
  function pickYongshin(r) {
    try {
      var saju = r['사주'] || {};
      var pillars = ['년주','월주','일주','시주'];
      var elCount = {木:0,火:0,土:0,金:0,水:0};
      var stemEl = {갑:'木',을:'木',병:'火',정:'火',무:'土',기:'土',경:'金',신:'金',임:'水',계:'水'};
      var branchEl = {자:'水',축:'土',인:'木',묘:'木',진:'土',사:'火',오:'火',미:'土',신:'金',유:'金',술:'土',해:'水'};
      pillars.forEach(function(p){
        if (!saju[p]) return;
        var s = saju[p].stem || saju[p].천간 || '';
        var b = saju[p].branch || saju[p].지지 || '';
        if (stemEl[s]) elCount[stemEl[s]]++;
        if (branchEl[b]) elCount[branchEl[b]]++;
      });
      // 가장 적은 오행을 용신 후보로 (균형 보강)
      var min = 999, candidate = '木';
      Object.keys(elCount).forEach(function(k){ if (elCount[k] < min) { min = elCount[k]; candidate = k; } });
      return candidate;
    } catch(e) { return '木'; }
  }

  // 메인: 카드 HTML 생성
  function buildGaewoonbeobCard(r) {
    try {
      var dayStem = (r['기본정보'] && r['기본정보']['일간'] && r['기본정보']['일간']['글자']) || '';
      var dInfo = dayStemMap[dayStem] || dayStemMap['갑'];
      var dayEl = elementMap[dInfo.el];
      var yongshinEl = pickYongshin(r);
      var ysEl = elementMap[yongshinEl];

      // 일간 기준 1차 + 용신 보강 2차 = 종합 추천
      var combinedColors = [].concat(dayEl.colors.slice(0,2), ysEl.colors.slice(0,1));
      var combinedNumbers = [dayEl.numbers[0], dayEl.numbers[1], ysEl.numbers[0], ysEl.numbers[1], dayEl.numbers[2]];

      // 색상 이름 매핑 (한국어 + 한자 음역, 정통 오행 색명 기준)
      var COLOR_NAMES = {
        '#2E7D32': '진초록', '#43A047': '에메랄드', '#66BB6A': '연두',
        '#D32F2F': '진홍', '#E53935': '주홍', '#EF5350': '산호색',
        '#FBC02D': '황금색', '#F9A825': '호박색', '#A1887F': '갈색',
        '#FAFAFA': '백색', '#E0E0E0': '은회색', '#FFD700': '황금',
        '#0D47A1': '감청색', '#1565C0': '청옥색', '#37474F': '먹청색'
      };

      var swatch = combinedColors.map(function(c){
        var name = COLOR_NAMES[c] || '';
        return '<span style="display:inline-flex;align-items:center;gap:6px;margin:0 14px 8px 0;vertical-align:middle;">'+
               '<span style="display:inline-block;width:36px;height:36px;border-radius:8px;background:'+c+';border:1px solid rgba(255,255,255,0.2);" title="'+(name?name+' ':'')+c+'"></span>'+
               '<span style="display:inline-flex;flex-direction:column;line-height:1.2;">'+
                 (name ? '<span style="font-size:0.85rem;color:var(--text);font-weight:600;">'+name+'</span>' : '')+
                 '<span style="font-size:0.7rem;color:var(--text2);font-family:\'Playfair Display\',monospace;">'+c+'</span>'+
               '</span>'+
               '</span>';
      }).join('');

      var html = '';
      html += '<div class="result-card" style="border-color:var(--gold);background:linear-gradient(135deg,rgba(201,168,76,0.08),rgba(74,158,142,0.05));">';
      html += '<h4>🍀 개운법 — 일간('+dInfo.desc+') + 용신('+yongshinEl+') 보강</h4>';
      html += '<p style="color:var(--text2);font-size:0.85rem;line-height:1.7;margin-bottom:14px;">'+
              '본 사주의 일간('+dayStem+'·'+dInfo.el+') 에너지에 부족한 <strong style="color:var(--gold2)">용신 '+yongshinEl+'</strong>을 보강하는 개운법입니다. 색·방향·숫자·요일·음식을 일상에 녹여 운기를 끌어올리세요.</p>';

      // 1) 행운 색상
      html += '<div style="margin-bottom:14px;"><strong style="color:var(--gold2);font-size:0.88rem;">🎨 행운 색상</strong><div style="margin-top:8px;">'+swatch+'</div></div>';

      // 2) 행운 방향 + 숫자 + 요일
      html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px;">';
      html += '<div><strong style="color:var(--gold2);font-size:0.85rem;">🧭 행운 방향</strong><p style="margin-top:4px;font-size:0.95rem;">일간: '+dayEl.direction+'<br>용신: '+ysEl.direction+'</p></div>';
      html += '<div><strong style="color:var(--gold2);font-size:0.85rem;">📅 행운 요일</strong><p style="margin-top:4px;font-size:0.95rem;">'+dayEl.day+' / '+ysEl.day+'</p></div>';
      html += '</div>';

      html += '<div style="margin-bottom:14px;"><strong style="color:var(--gold2);font-size:0.88rem;">🔢 행운 숫자</strong><p style="margin-top:6px;font-size:1.05rem;letter-spacing:0.4em;color:var(--gold);font-weight:600;">'+combinedNumbers.join(' · ')+'</p></div>';

      // 3) 추천 직업
      var jobs = (dayEl.job.slice(0,4)).concat(ysEl.job.slice(0,3));
      html += '<div style="margin-bottom:14px;"><strong style="color:var(--gold2);font-size:0.88rem;">💼 추천 직업·분야</strong><p style="margin-top:6px;font-size:0.88rem;line-height:1.7;">'+jobs.join(' · ')+'</p></div>';

      // 4) 음식·음료
      html += '<div style="margin-bottom:14px;"><strong style="color:var(--gold2);font-size:0.88rem;">🍽️ 음식 & 음료 (오행 보강)</strong>'+
              '<p style="margin-top:6px;font-size:0.85rem;line-height:1.7;"><strong>음식:</strong> '+dayEl.food+' / <em style="color:var(--text2);">용신 보강:</em> '+ysEl.food+'</p>'+
              '<p style="font-size:0.85rem;line-height:1.7;"><strong>음료:</strong> '+dayEl.drink+' / <em style="color:var(--text2);">용신 보강:</em> '+ysEl.drink+'</p></div>';

      // 5) 휴대폰 배경화면
      html += '<div style="margin-bottom:14px;"><strong style="color:var(--gold2);font-size:0.88rem;">📱 휴대폰 배경화면 추천</strong>'+
              '<p style="margin-top:6px;font-size:0.85rem;line-height:1.7;">'+dayEl.wallpaper+' (메인) / '+ysEl.wallpaper+' (용신 보강)</p></div>';

      // 6) 보석/액세서리
      html += '<div style="margin-bottom:8px;"><strong style="color:var(--gold2);font-size:0.88rem;">💎 보석·액세서리</strong>'+
              '<p style="margin-top:6px;font-size:0.85rem;line-height:1.7;">'+dayEl.gem+' (일간) / '+ysEl.gem+' (용신)</p></div>';

      html += '<p style="color:var(--text2);font-size:0.72rem;margin-top:12px;border-top:1px solid var(--border);padding-top:10px;">※ 정통 명리학 오행귀류(五行歸類) 대응표 기반. 매일 한 가지씩만 반영해도 충분합니다.</p>';
      html += '</div>';
      return html;
    } catch(e) {
      console.warn('[gaewoonbeob] build failed:', e);
      return '';
    }
  }

  // 노출
  window.Gaewoonbeob = {
    build: buildGaewoonbeobCard,
    pickYongshin: pickYongshin,
    elementMap: elementMap,
    dayStemMap: dayStemMap
  };
  // 함수 직접 호출 가능 별칭
  window.buildGaewoonbeobCard = buildGaewoonbeobCard;
})();
