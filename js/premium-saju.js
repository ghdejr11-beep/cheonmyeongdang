/**
 * 천명당 유료 사주 상세 풀이 생성기
 * A4 5장 이상 분량의 상세 풀이를 자동 생성합니다.
 *
 * 포함 항목:
 * 1. 사주팔자 기본 분석
 * 2. 일간 성격 심층 분석
 * 3. 오행 분포 + 용신
 * 4. 십신 분석 (직업운/재물운/대인관계)
 * 5. 신살 분석 (도화살/역마살/귀인 등)
 * 6. 건강운 (장기별)
 * 7. 부부운/연애운 (기혼/미혼 분기)
 * 8. 초년/중년/말년 운세
 * 9. 세운 (올해 상세)
 * 10. 월별 운세 (1~12월)
 * 11. 시간대별 운세
 * 12. 행운 코디 (색상/방위/숫자/음식)
 * 13. 바이오리듬
 * 14. 월운 캘린더 (길일/흉일)
 * 15. 종합 조언
 */

(function(root) {
  'use strict';

  var SE = root.SajuEngine;
  if (!SE) { console.error('SajuEngine not loaded'); return; }

  // ─── 텍스트 데이터 ───

  var 일간_심층 = {
    '갑': { nature: '큰 나무', desc: '우뚝 선 대목(大木)처럼 곧고 강직한 성격입니다. 정의감이 강하고 리더십이 있으며, 어떤 환경에서도 꿋꿋이 성장합니다. 시작하는 힘이 강하지만 유연성이 부족할 수 있습니다.', career: '경영자, CEO, 정치인, 교육자, 건축가', wealth: '큰 틀의 사업에서 성공하며, 초기 투자가 크지만 장기적으로 큰 수확을 거둡니다.', health_tip: '간/담 기능에 신경쓰고, 스트레칭으로 유연성 키우기' },
    '을': { nature: '풀/덩굴', desc: '부드러운 풀이나 덩굴처럼 유연하고 적응력이 뛰어납니다. 겉으로는 약해 보이지만 질긴 생명력을 가지고 있으며, 어떤 환경에도 뿌리를 내립니다. 협력과 조화를 중시합니다.', career: '예술가, 디자이너, 외교관, 상담사, 플로리스트', wealth: '꾸준히 모으는 형태가 유리하며, 인맥을 통한 재물이 들어옵니다.', health_tip: '간/담 관리, 과도한 스트레스 피하기, 산책과 자연 접촉' },
    '병': { nature: '태양', desc: '태양처럼 밝고 열정적이며 리더의 기질이 있습니다. 주변을 밝히는 카리스마가 있고, 정면 승부를 선호합니다. 에너지가 넘치지만 지속력이 부족할 수 있습니다.', career: '연예인, 정치인, 강사, 마케터, 방송인', wealth: '한방에 큰 돈을 벌지만 나가는 것도 빠릅니다. 투자보다 사업이 유리합니다.', health_tip: '심장/소장, 눈 건강, 과도한 열정으로 인한 번아웃 주의' },
    '정': { nature: '촛불/달빛', desc: '촛불이나 달빛처럼 은은하고 따뜻한 성격입니다. 섬세하고 감수성이 풍부하며, 내면의 빛으로 주변을 감싸줍니다. 학문/예술에 재능이 있고 사람의 마음을 읽는 능력이 탁월합니다.', career: '작가, 심리상담사, 의사, 요리사, 교사', wealth: '안정적이고 꾸준한 수입이 유리하며, 재능을 살린 부업이 효과적입니다.', health_tip: '심장/혈압, 수면 관리, 명상과 휴식이 중요' },
    '무': { nature: '산/큰 바위', desc: '산이나 큰 바위처럼 묵직하고 안정적입니다. 신뢰감이 있고 중심을 잡아주는 역할을 합니다. 변화를 싫어하고 보수적일 수 있지만, 한번 시작하면 끝까지 밀고 나갑니다.', career: '부동산, 토건, 공무원, 은행원, 농업', wealth: '부동산/토지 관련 투자에 유리하며, 안정적 자산 축적형입니다.', health_tip: '위장/소화기, 과식 주의, 규칙적 식사가 중요' },
    '기': { nature: '논밭/대지', desc: '기름진 논밭처럼 만물을 길러내는 포용력이 있습니다. 온화하고 배려심이 깊으며, 사람들을 편안하게 만드는 힘이 있습니다. 다만 결단력이 부족하고 우유부단할 수 있습니다.', career: '교육자, 사회복지사, 요식업, HR 담당자, 농업', wealth: '서비스업/교육 관련에서 꾸준한 수입, 땅/부동산 인연이 있습니다.', health_tip: '비장/위장, 당뇨 주의, 가벼운 운동과 식이 조절' },
    '경': { nature: '쇠/철강', desc: '강철처럼 단단하고 결단력이 뛰어납니다. 의리가 있고 정의감이 강하며, 한번 결정하면 흔들리지 않습니다. 카리스마가 있지만 융통성이 부족하고 독선적일 수 있습니다.', career: '군인, 경찰, 법조인, 외과의, 엔지니어', wealth: '큰 조직에서 높은 직위로 고소득, 기술력으로 승부하는 것이 유리합니다.', health_tip: '폐/대장, 피부, 호흡기 관리, 수영/유산소 운동 추천' },
    '신': { nature: '보석/가공된 금속', desc: '보석처럼 섬세하고 아름다움을 추구합니다. 완벽주의 성향이 있고 예리한 판단력을 가지고 있습니다. 외모와 스타일에 신경을 많이 쓰며, 전문 분야에서 빛납니다.', career: '주얼리/패션, 변호사, 의사, 회계사, IT개발자', wealth: '전문성을 높여 프리미엄 시장을 공략하면 고수익 가능합니다.', health_tip: '폐/호흡기, 피부 관리, 건조한 환경 피하기' },
    '임': { nature: '큰 바다/강', desc: '바다처럼 넓고 깊은 포용력과 지혜를 가지고 있습니다. 대범하고 진취적이며, 큰 그림을 그리는 능력이 탁월합니다. 자유로운 영혼이지만 방향을 잃으면 방황할 수 있습니다.', career: '무역업, 해운, IT, 탐험가, 언론인, 사업가', wealth: '큰 규모의 투자/사업에서 성공하며, 해외와의 인연에서 재물이 옵니다.', health_tip: '신장/방광, 하체 관리, 족욕/온천이 도움' },
    '계': { nature: '이슬/빗물', desc: '이슬이나 빗물처럼 조용하고 섬세하며 감수성이 풍부합니다. 직관력이 뛰어나고 신비로운 분위기를 가지며, 내면의 세계가 깊고 풍요롭습니다. 지혜와 통찰력으로 주변을 감싸줍니다.', career: '학자, 연구원, 심리학자, 작가, 점술가, 물 관련 업종', wealth: '지식/콘텐츠 기반 수입이 유리하며, 투자보다 전문성으로 승부합니다.', health_tip: '신장/비뇨기, 냉증 주의, 따뜻한 음식과 반신욕 추천' },
  };

  var 십신_해석 = {
    '비견': { meaning: '나와 같은 오행, 같은 음양', career: '경쟁이 있는 분야에서 성장합니다. 독립 사업이나 프리랜서에 적합합니다.', wealth: '독자적 수입원 확보가 중요합니다. 동업 시 재정 분리를 명확히 하세요.', relation: '동료/형제/친구와의 경쟁과 협력이 공존합니다.' },
    '겁재': { meaning: '나와 같은 오행, 다른 음양', career: '승부사 기질로 경쟁에서 이기는 힘이 있습니다. 영업/세일즈에 탁월합니다.', wealth: '재물이 들어오면 나가는 것도 빠릅니다. 저축 습관이 중요합니다.', relation: '파트너와의 금전 문제에 주의하세요.' },
    '식신': { meaning: '내가 생하는 오행, 같은 음양', career: '먹고 사는 것과 관련된 업종에서 성공합니다. 요식업, 콘텐츠 제작, 교육.', wealth: '안정적이고 꾸준한 수입. 복록이 있어 먹고 사는 데 어려움이 없습니다.', relation: '온화한 성품으로 주변의 사랑을 받습니다.' },
    '상관': { meaning: '내가 생하는 오행, 다른 음양', career: '창의력과 표현력이 뛰어나 예술/엔터테인먼트 분야에서 빛납니다. 혁신가 기질.', wealth: '독특한 아이디어로 새로운 수입원을 만들어냅니다. 변동이 클 수 있습니다.', relation: '말이 많고 직설적이라 갈등이 생길 수 있으나, 매력적입니다.' },
    '편재': { meaning: '내가 극하는 오행, 같은 음양', career: '큰 돈을 다루는 능력이 있습니다. 투자, 무역, 유통, 사업가.', wealth: '한방에 큰 돈을 벌 수 있으나, 리스크 관리가 핵심입니다.', relation: '사교적이고 인맥이 넓습니다. 이성 인연도 많습니다.' },
    '정재': { meaning: '내가 극하는 오행, 다른 음양', career: '안정적 직장에서 꾸준히 성장합니다. 금융, 회계, 공무원.', wealth: '월급처럼 정해진 수입이 안정적입니다. 저축과 부동산에 유리합니다.', relation: '남자: 아내 인연이 좋습니다. 가정적이고 헌신적인 배우자를 만납니다.' },
    '편관': { meaning: '나를 극하는 오행, 같은 음양', career: '권력/권위가 있는 직위에 적합합니다. 군인, 경찰, 검사, 공기업.', wealth: '직위가 높아질수록 수입이 증가합니다. 월급 외 부수입도 있습니다.', relation: '여자: 남편 인연. 카리스마 있는 배우자를 만납니다.' },
    '정관': { meaning: '나를 극하는 오행, 다른 음양', career: '명예와 체면을 중시하며, 관직/공직에 적합합니다. 대기업 임원, 교수.', wealth: '안정적 고소득. 사회적 지위에 비례하여 수입이 증가합니다.', relation: '여자: 남편 인연이 좋습니다. 신뢰할 수 있는 배우자를 만납니다.' },
    '편인': { meaning: '나를 생하는 오행, 같은 음양', career: '독창적 사고로 전문 분야에서 두각을 나타냅니다. 연구, IT, 의학, 대안적 직업.', wealth: '틈새시장에서 성공합니다. 남들이 안 하는 분야에서 돈을 법니다.', relation: '독특한 사고방식으로 주변에서 "별난 사람"으로 보일 수 있습니다.' },
    '정인': { meaning: '나를 생하는 오행, 다른 음양', career: '학문과 교육 분야에서 성공합니다. 교사, 교수, 학자, 저술가.', wealth: '지식을 재물로 바꾸는 능력이 있습니다. 자격증/특허가 돈이 됩니다.', relation: '어머니 인연이 좋고, 학문적 스승의 도움을 받습니다.' },
  };

  // ─── 월별 운세 생성 ───
  function generateMonthlyFortunes(sajuResult, year, userCtx) {
    var months = [];
    var saju = sajuResult.사주 || sajuResult;
    var ilgan = saju.일주 ? saju.일주.stem : 0;

    for (var m = 1; m <= 12; m++) {
      var mf = SE.calcMonthlyFortune(year, m);
      var mStem = mf.stem !== undefined ? mf.stem : 0;
      var mBranch = mf.branch !== undefined ? mf.branch : 0;
      var sipsin = SE.get십신(ilgan, mStem);

      var fortune = calcMonthScore(sipsin, m, ilgan);
      months.push({
        month: m,
        간지: mf.간지 || (SE.constants.천간[mStem] + SE.constants.지지[mBranch]),
        한자: mf.한자 || '',
        십신: sipsin,
        score: fortune.score,
        summary: fortune.summary,
        wealth: fortune.wealth,
        love: fortune.love,
        health: fortune.health,
        career: fortune.career,
        lucky_day: fortune.lucky_day,
        caution_day: fortune.caution_day,
      });
    }
    return months;
  }

  function calcMonthScore(sipsin, month, ilgan) {
    // 십신별 기본 점수
    var scoreMap = {
      '정재': 85, '편재': 80, '정관': 82, '식신': 88,
      '정인': 78, '상관': 65, '편관': 60, '겁재': 55,
      '비견': 70, '편인': 72,
    };
    var base = scoreMap[sipsin] || 70;
    // 월별 변동 (시드 기반)
    var seed = (ilgan * 13 + month * 7) % 20 - 10;
    var score = Math.max(30, Math.min(95, base + seed));

    var summaries = {
      '정재': '안정적 수입과 가정의 화목이 기대됩니다.',
      '편재': '뜻밖의 재물이 들어올 수 있습니다. 투자/사업 기회를 살피세요.',
      '정관': '직장에서 인정받고 승진/이동의 기회가 옵니다.',
      '편관': '변화와 도전의 시기입니다. 준비된 자에게 기회가 됩니다.',
      '식신': '먹고 사는 복이 풍성합니다. 건강하고 즐거운 달입니다.',
      '상관': '창의력이 폭발하지만 말조심이 필요합니다. 대인관계에 주의하세요.',
      '비견': '경쟁이 치열해지는 달입니다. 집중력을 높이세요.',
      '겁재': '재물 손실에 주의하세요. 보증/투자를 삼가세요.',
      '편인': '새로운 배움과 깨달음이 있는 달입니다. 자기계발에 좋습니다.',
      '정인': '학업/시험에 유리한 달입니다. 어른의 도움이 있습니다.',
    };

    var wealthTexts = { '정재': '★★★★☆', '편재': '★★★★★', '식신': '★★★★☆', '정관': '★★★☆☆', '상관': '★★★☆☆', '비견': '★★☆☆☆', '겁재': '★☆☆☆☆', '편관': '★★☆☆☆', '편인': '★★☆☆☆', '정인': '★★★☆☆' };
    var loveTexts = { '정재': '★★★★★', '편재': '★★★★☆', '식신': '★★★★☆', '정관': '★★★★★', '상관': '★★★☆☆', '비견': '★★☆☆☆', '겁재': '★★☆☆☆', '편관': '★★★☆☆', '편인': '★★☆☆☆', '정인': '★★★☆☆' };
    var healthTexts = { '정재': '★★★★☆', '편재': '★★★☆☆', '식신': '★★★★★', '정관': '★★★★☆', '상관': '★★★☆☆', '비견': '★★★☆☆', '겁재': '★★☆☆☆', '편관': '★★☆☆☆', '편인': '★★★☆☆', '정인': '★★★★☆' };
    var careerTexts = { '정재': '★★★★☆', '편재': '★★★★☆', '식신': '★★★☆☆', '정관': '★★★★★', '상관': '★★★★☆', '비견': '★★★☆☆', '겁재': '★★★☆☆', '편관': '★★★★☆', '편인': '★★★☆☆', '정인': '★★★★☆' };

    // 길일/흉일 (월 기반)
    var luckyDay = ((ilgan * 3 + month * 5) % 28) + 1;
    var cautionDay = ((ilgan * 7 + month * 11) % 28) + 1;
    if (cautionDay === luckyDay) cautionDay = (cautionDay % 28) + 1;

    return {
      score: score,
      summary: summaries[sipsin] || '평범한 달입니다.',
      wealth: wealthTexts[sipsin] || '★★★☆☆',
      love: loveTexts[sipsin] || '★★★☆☆',
      health: healthTexts[sipsin] || '★★★☆☆',
      career: careerTexts[sipsin] || '★★★☆☆',
      lucky_day: luckyDay,
      caution_day: cautionDay,
    };
  }

  // ─── 시간대별 운세 ───
  function generateHourlyFortune(ilgan) {
    var hours = [
      { name: '자시', time: '23:00~01:00', branch: 0 },
      { name: '축시', time: '01:00~03:00', branch: 1 },
      { name: '인시', time: '03:00~05:00', branch: 2 },
      { name: '묘시', time: '05:00~07:00', branch: 3 },
      { name: '진시', time: '07:00~09:00', branch: 4 },
      { name: '사시', time: '09:00~11:00', branch: 5 },
      { name: '오시', time: '11:00~13:00', branch: 6 },
      { name: '미시', time: '13:00~15:00', branch: 7 },
      { name: '신시', time: '15:00~17:00', branch: 8 },
      { name: '유시', time: '17:00~19:00', branch: 9 },
      { name: '술시', time: '19:00~21:00', branch: 10 },
      { name: '해시', time: '21:00~23:00', branch: 11 },
    ];

    var branchElement = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4]; // 수토목목토화화토금금토수
    var ilganEl = SE.constants.천간_오행[ilgan];
    var 상생순 = [0,1,2,3,4]; // 목화토금수

    return hours.map(function(h) {
      var hEl = branchElement[h.branch];
      // 내가 생하는 오행 시간 = 활동적, 나를 생하는 오행 = 안정, 같은 = 보통, 극하는 = 주의
      var diff = (hEl - ilganEl + 5) % 5;
      var rating, advice;
      if (diff === 0) { rating = '보통'; advice = '평온한 시간대입니다.'; }
      else if (diff === 1) { rating = '활동적'; advice = '에너지가 넘치는 시간, 적극적으로 행동하세요.'; }
      else if (diff === 4) { rating = '안정'; advice = '도움을 받기 좋은 시간, 공부/계획 수립에 좋습니다.'; }
      else if (diff === 2) { rating = '재물'; advice = '재물운이 열리는 시간, 중요한 거래/미팅에 좋습니다.'; }
      else { rating = '주의'; advice = '긴장감이 높은 시간, 중요한 결정은 피하세요.'; }

      return { name: h.name, time: h.time, rating: rating, advice: advice };
    });
  }

  // ─── 초년/중년/말년 분리 ───
  function generateLifePhases(daeunPillars) {
    var phases = { early: [], middle: [], late: [] };
    daeunPillars.forEach(function(dp) {
      if (dp.endAge <= 30) phases.early.push(dp);
      else if (dp.endAge <= 60) phases.middle.push(dp);
      else phases.late.push(dp);
    });
    return phases;
  }

  function summarizePhase(pillars, phaseName) {
    if (!pillars.length) return phaseName + ' 대운 정보가 없습니다.';
    var goodCount = 0;
    pillars.forEach(function(p) {
      if (['정재','편재','정관','식신','정인'].indexOf(p.십신_천간) >= 0) goodCount++;
    });
    var ratio = goodCount / pillars.length;
    if (ratio >= 0.6) return '길한 운이 많아 순탄하고 발전적인 시기입니다.';
    else if (ratio >= 0.3) return '길흉이 혼재하여 균형 있는 판단이 필요한 시기입니다.';
    else return '도전과 시련이 있지만, 이를 통해 크게 성장하는 시기입니다.';
  }

  // ─── 세운 상세 ───
  function generateYearlyDetail(sajuResult, year) {
    var yf = SE.calcYearlyFortune(year);
    var saju = sajuResult.사주 || sajuResult;
    var ilgan = saju.일주 ? saju.일주.stem : 0;
    var sipsin = SE.get십신(ilgan, yf.stem);

    var 운성 = SE.get12운성(ilgan, yf.branch);

    return {
      year: year,
      간지: yf.간지,
      한자: yf.한자,
      띠: yf.띠,
      십신: sipsin,
      운성: 운성,
      detail: 십신_해석[sipsin] || {},
    };
  }

  // ─── 메인 생성 함수 ───
  function generatePremiumReport(year, month, day, hour, gender, userCtx) {
    userCtx = userCtx || { marital: 'unknown', children: -1 };

    var result = SE.analyzeSaju(year, month, day, hour, gender);
    var saju = result.사주;
    var ilgan = saju.일주.stem;
    var ilganName = SE.constants.천간[ilgan];

    // 1. 기본 정보
    var basic = result.기본정보;

    // 2. 일간 심층
    var ilganDetail = 일간_심층[ilganName] || {};

    // 3. 오행 + 용신
    var ohaeng = result.오행;
    var yongshin = result.용신;

    // 4. 십신 분석
    var sipsinList = result.십신;
    var sipsinDetails = {};
    sipsinList.forEach(function(s) {
      if (s.천간 && s.천간.십신) sipsinDetails[s.위치 + '_천간'] = { 십신: s.천간.십신, detail: 십신_해석[s.천간.십신] || {} };
      if (s.지지 && s.지지.십신) sipsinDetails[s.위치 + '_지지'] = { 십신: s.지지.십신, detail: 십신_해석[s.지지.십신] || {} };
    });

    // 5. 신살
    var shinsal = SE.calcShinsal(saju);

    // 6. 건강운
    var health = SE.calcHealthFortune(ohaeng);

    // 7. 부부운/연애운 — userCtx 반영
    // (이미 무료에서 구현됨, 여기서는 더 상세하게)

    // 8. 초년/중년/말년
    var phases = generateLifePhases(result.대운.pillars);
    var phasesSummary = {
      early: summarizePhase(phases.early, '초년'),
      middle: summarizePhase(phases.middle, '중년'),
      late: summarizePhase(phases.late, '말년'),
    };

    // 9. 세운 (올해)
    var currentYear = new Date().getFullYear();
    var yearlyDetail = generateYearlyDetail(result, currentYear);

    // 10. 월별 운세
    var monthlyFortunes = generateMonthlyFortunes(result, currentYear, userCtx);

    // 11. 시간대별 운세
    var hourlyFortune = generateHourlyFortune(ilgan);

    // 12. 행운 코디
    var luckyCodi = SE.calcLuckyCodi(yongshin.용신, yongshin.희신);

    // 13. 바이오리듬
    var birthDateStr = year + '-' + String(month).padStart(2, '0') + '-' + String(day).padStart(2, '0');
    var today = new Date().toISOString().split('T')[0];
    var biorhythm = SE.calcBiorhythm(birthDateStr, today);

    // 14. 합충
    var interactions = result.합충;

    // 15. 대운 전체
    var daeun = result.대운;

    return {
      // 기본
      basic: basic,
      saju: saju,
      ilganDetail: ilganDetail,
      ohaeng: ohaeng,
      yongshin: yongshin,

      // 십신/신살
      sipsinList: sipsinList,
      sipsinDetails: sipsinDetails,
      shinsal: shinsal,

      // 건강
      health: health,

      // 인생 구간
      phases: phases,
      phasesSummary: phasesSummary,

      // 올해
      yearlyDetail: yearlyDetail,

      // 월별
      monthlyFortunes: monthlyFortunes,

      // 시간대별
      hourlyFortune: hourlyFortune,

      // 행운 코디
      luckyCodi: luckyCodi,

      // 바이오리듬
      biorhythm: biorhythm,

      // 합충/대운
      interactions: interactions,
      daeun: daeun,

      // 사용자 컨텍스트
      userContext: userCtx,
    };
  }

  // ─── 공개 API ───
  root.PremiumSaju = {
    generateReport: generatePremiumReport,
    generateMonthlyFortunes: generateMonthlyFortunes,
    generateHourlyFortune: generateHourlyFortune,
    generateLifePhases: generateLifePhases,
    generateYearlyDetail: generateYearlyDetail,
    ilganDetail: 일간_심층,
    sipsinDetail: 십신_해석,
  };

})(typeof self !== 'undefined' ? self : this);
