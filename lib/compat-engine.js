/**
 * 천명당 궁합(宮合) 분석 엔진 — 서버측 공식 명리학 기반 SKU compat_detail_9900
 *
 * 입력: 두 사람의 양력 생년월일+시 (year, month, day, hour, gender)
 * 출력: 합/충/오행균형/일간궁합 점수 + 한국어 결과 텍스트
 *
 * 명리학 데이터 (사용자 명시 + 검증):
 *   - 12지지 6합: 子丑(土) / 寅亥(木) / 卯戌(火) / 辰酉(金) / 巳申(水) / 午未(火·土)
 *   - 12지지 6충: 子午 / 丑未 / 寅申 / 卯酉 / 辰戌 / 巳亥
 *   - 천간 5합: 甲己(土) / 乙庚(金) / 丙辛(水) / 丁壬(木) / 戊癸(火)
 *   - 천간 7충: 甲庚 / 乙辛 / 丙壬 / 丁癸 / 戊壬(반흉) / 己癸(반흉)
 *   - 오행 상생: 木→火→土→金→水→木
 *   - 오행 상극: 木→土→水→火→金→木
 *
 * 이 모듈은 saju-engine.js (브라우저 IIFE)를 commonjs 환경에서 require하여 재사용한다.
 * 천명당 코드 스타일: 한국어 주석 + var 우선 + commonjs.
 */

// saju-engine.js는 UMD 패턴이라 commonjs require 가능 (module.exports = factory())
const SajuEngine = require('../js/saju-engine.js');

// ─── 천간/지지 인덱스 매핑 ────────────────────────────────────
// 천간: 0=갑(甲) 1=을(乙) 2=병(丙) 3=정(丁) 4=무(戊) 5=기(己) 6=경(庚) 7=신(辛) 8=임(壬) 9=계(癸)
// 지지: 0=자(子) 1=축(丑) 2=인(寅) 3=묘(卯) 4=진(辰) 5=사(巳) 6=오(午) 7=미(未) 8=신(申) 9=유(酉) 10=술(戌) 11=해(亥)
const STEM_HANJA = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'];
const BRANCH_HANJA = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'];
const STEM_KR = ['갑','을','병','정','무','기','경','신','임','계'];
const BRANCH_KR = ['자','축','인','묘','진','사','오','미','신','유','술','해'];
const ELEMENT_KR = ['목','화','토','금','수'];
const ELEMENT_HANJA = ['木','火','土','金','水'];

// ─── 12지지 6합: [a, b, 변화오행idx] ─────────────────────────
// 子(0)+丑(1)→土(2), 寅(2)+亥(11)→木(0), 卯(3)+戌(10)→火(1)
// 辰(4)+酉(9)→金(3),  巳(5)+申(8)→水(4),  午(6)+未(7)→火/土(여기선 화 채택)
const BRANCH_6HAP = [
  [0, 1, 2,  '자축합토'],
  [2, 11, 0, '인해합목'],
  [3, 10, 1, '묘술합화'],
  [4, 9, 3,  '진유합금'],
  [5, 8, 4,  '사신합수'],
  [6, 7, 1,  '오미합화'],
];

// ─── 12지지 6충 ───────────────────────────────────────────────
const BRANCH_6CHUNG = [
  [0, 6,  '자오충'], [1, 7,  '축미충'], [2, 8,  '인신충'],
  [3, 9,  '묘유충'], [4, 10, '진술충'], [5, 11, '사해충'],
];

// ─── 천간 5합: [a, b, 변화오행idx] ───────────────────────────
// 甲(0)+己(5)→土(2), 乙(1)+庚(6)→金(3), 丙(2)+辛(7)→水(4), 丁(3)+壬(8)→木(0), 戊(4)+癸(9)→火(1)
const STEM_5HAP = [
  [0, 5, 2, '갑기합토'],
  [1, 6, 3, '을경합금'],
  [2, 7, 4, '병신합수'],
  [3, 8, 0, '정임합목'],
  [4, 9, 1, '무계합화'],
];

// ─── 천간 7충 (정충 + 반흉) ──────────────────────────────────
// 정충(흉도 강): 甲庚, 乙辛, 丙壬, 丁癸
// 반흉(주의):    戊壬, 己癸
const STEM_CHUNG = [
  [0, 6, 'full', '갑경충'],
  [1, 7, 'full', '을신충'],
  [2, 8, 'full', '병임충'],
  [3, 9, 'full', '정계충'],
  [4, 8, 'half', '무임반충'],
  [5, 9, 'half', '기계반충'],
];

// 천간/지지 → 오행 인덱스 (saju-engine과 동일)
const STEM_TO_ELEMENT = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]; // 갑을=목, 병정=화, 무기=토, 경신=금, 임계=수
const BRANCH_TO_ELEMENT = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4]; // 자=수,축=토,인=목,묘=목,진=토,사=화,오=화,미=토,신=금,유=금,술=토,해=수

// 상생: src→tgt이 i→(i+1)%5 이면 상생
function isSheng(srcEl, tgtEl) { return (srcEl + 1) % 5 === tgtEl; }
// 상극: src→tgt이 i→(i+2)%5 이면 상극 (목→토, 화→금, 토→수, 금→목, 수→화)
function isKe(srcEl, tgtEl) { return (srcEl + 2) % 5 === tgtEl; }

// ─── 사주 4기둥 → stem/branch 인덱스 배열 4쌍 ──────────────
function extractPillars(sajuObj) {
  // sajuObj: result.사주 (analyzeSaju 결과)
  var p = ['년주', '월주', '일주', '시주'];
  var stems = [];
  var branches = [];
  p.forEach(function (key) {
    var pillar = sajuObj[key];
    if (pillar) {
      stems.push(pillar.stem);
      branches.push(pillar.branch);
    }
  });
  return { stems: stems, branches: branches };
}

// ─── 두 사람의 천간 합/충 분석 ─────────────────────────────
function analyzeStemInteractions(stemsA, stemsB) {
  var hap = [];
  var chung = [];
  stemsA.forEach(function (a, ai) {
    stemsB.forEach(function (b, bi) {
      // 5합
      STEM_5HAP.forEach(function (rule) {
        if ((rule[0] === a && rule[1] === b) || (rule[1] === a && rule[0] === b)) {
          hap.push({
            from: STEM_HANJA[a],
            to: STEM_HANJA[b],
            element: ELEMENT_KR[rule[2]],
            elementHanja: ELEMENT_HANJA[rule[2]],
            name: rule[3],
            posA: ai,
            posB: bi,
          });
        }
      });
      // 7충
      STEM_CHUNG.forEach(function (rule) {
        if ((rule[0] === a && rule[1] === b) || (rule[1] === a && rule[0] === b)) {
          chung.push({
            from: STEM_HANJA[a],
            to: STEM_HANJA[b],
            severity: rule[2], // 'full' | 'half'
            name: rule[3],
            posA: ai,
            posB: bi,
          });
        }
      });
    });
  });
  return { hap: hap, chung: chung };
}

// ─── 두 사람의 지지 합/충 분석 ─────────────────────────────
function analyzeBranchInteractions(branchesA, branchesB) {
  var hap = [];
  var chung = [];
  branchesA.forEach(function (a, ai) {
    branchesB.forEach(function (b, bi) {
      BRANCH_6HAP.forEach(function (rule) {
        if ((rule[0] === a && rule[1] === b) || (rule[1] === a && rule[0] === b)) {
          hap.push({
            from: BRANCH_HANJA[a],
            to: BRANCH_HANJA[b],
            element: ELEMENT_KR[rule[2]],
            elementHanja: ELEMENT_HANJA[rule[2]],
            name: rule[3],
            posA: ai,
            posB: bi,
          });
        }
      });
      BRANCH_6CHUNG.forEach(function (rule) {
        if ((rule[0] === a && rule[1] === b) || (rule[1] === a && rule[0] === b)) {
          chung.push({
            from: BRANCH_HANJA[a],
            to: BRANCH_HANJA[b],
            name: rule[2],
            posA: ai,
            posB: bi,
          });
        }
      });
    });
  });
  return { hap: hap, chung: chung };
}

// ─── 두 사람의 오행 합산 분포 + 균형 평가 ────────────────────
function analyzeElementBalance(stemsA, branchesA, stemsB, branchesB) {
  var counts = [0, 0, 0, 0, 0]; // 목 화 토 금 수
  stemsA.forEach(function (s) { counts[STEM_TO_ELEMENT[s]]++; });
  branchesA.forEach(function (b) { counts[BRANCH_TO_ELEMENT[b]]++; });
  stemsB.forEach(function (s) { counts[STEM_TO_ELEMENT[s]]++; });
  branchesB.forEach(function (b) { counts[BRANCH_TO_ELEMENT[b]]++; });

  var total = counts.reduce(function (a, b) { return a + b; }, 0) || 1;
  var pct = counts.map(function (c) { return Math.round(c / total * 100); });

  // 한 사람 단독 분포도 함께 (보완 효과 시각화용)
  var aOnly = [0, 0, 0, 0, 0];
  stemsA.forEach(function (s) { aOnly[STEM_TO_ELEMENT[s]]++; });
  branchesA.forEach(function (b) { aOnly[BRANCH_TO_ELEMENT[b]]++; });

  var bOnly = [0, 0, 0, 0, 0];
  stemsB.forEach(function (s) { bOnly[STEM_TO_ELEMENT[s]]++; });
  branchesB.forEach(function (b) { bOnly[BRANCH_TO_ELEMENT[b]]++; });

  // 보완 효과: A의 부족분(0~1)을 B가 채워주는 갯수
  var complementAByB = 0;
  var complementBByA = 0;
  for (var i = 0; i < 5; i++) {
    if (aOnly[i] <= 1 && bOnly[i] >= 2) complementAByB++;
    if (bOnly[i] <= 1 && aOnly[i] >= 2) complementBByA++;
  }

  // 표준편차 (낮을수록 균형 잡힘)
  var mean = total / 5;
  var variance = counts.reduce(function (acc, c) { return acc + Math.pow(c - mean, 2); }, 0) / 5;
  var stddev = Math.sqrt(variance);
  // 균형 점수: stddev 0 = 100점, stddev 5 = 0점 (선형, clamp)
  var balanceScore = Math.max(0, Math.min(100, Math.round(100 - stddev * 20)));

  return {
    counts: {
      목: counts[0], 화: counts[1], 토: counts[2], 금: counts[3], 수: counts[4],
    },
    percentage: {
      목: pct[0], 화: pct[1], 토: pct[2], 금: pct[3], 수: pct[4],
    },
    aOnly: { 목: aOnly[0], 화: aOnly[1], 토: aOnly[2], 금: aOnly[3], 수: aOnly[4] },
    bOnly: { 목: bOnly[0], 화: bOnly[1], 토: bOnly[2], 금: bOnly[3], 수: bOnly[4] },
    complementAByB: complementAByB,
    complementBByA: complementBByA,
    balanceScore: balanceScore,
    stddev: Math.round(stddev * 100) / 100,
    dominantElement: ELEMENT_KR[counts.indexOf(Math.max.apply(null, counts))],
    weakestElement: ELEMENT_KR[counts.indexOf(Math.min.apply(null, counts))],
  };
}

// ─── 일간(日干) 궁합 0~100점 ───────────────────────────────
// 핵심 명리학: 두 사람의 일간 오행 관계 + 음양 + 일지(日支) 합/충
function analyzeIlganCompat(sajuA, sajuB) {
  var ilganA = sajuA.일주.stem;
  var ilganB = sajuB.일주.stem;
  var iljiA = sajuA.일주.branch;
  var iljiB = sajuB.일주.branch;

  var elA = STEM_TO_ELEMENT[ilganA];
  var elB = STEM_TO_ELEMENT[ilganB];
  var yangA = ilganA % 2 === 0; // 양=짝수
  var yangB = ilganB % 2 === 0;

  var score = 50; // 기준점
  var notes = [];

  // 1. 오행 관계 (가중치 30점)
  if (elA === elB) {
    score += 12;
    notes.push('두 분의 일간이 같은 ' + ELEMENT_KR[elA] + '(' + ELEMENT_HANJA[elA] + ') 오행으로 비견(比肩) 관계, 동질감과 공감대가 깊습니다.');
  } else if (isSheng(elA, elB)) {
    score += 22;
    notes.push(STEM_HANJA[ilganA] + '→' + STEM_HANJA[ilganB] + ' 상생(' + ELEMENT_KR[elA] + '生' + ELEMENT_KR[elB] + '), 본인이 상대를 도와주고 키워주는 관계입니다.');
  } else if (isSheng(elB, elA)) {
    score += 25;
    notes.push(STEM_HANJA[ilganB] + '→' + STEM_HANJA[ilganA] + ' 상생(' + ELEMENT_KR[elB] + '生' + ELEMENT_KR[elA] + '), 상대가 본인을 든든히 받쳐주는 관계입니다.');
  } else if (isKe(elA, elB)) {
    score -= 12;
    notes.push(STEM_HANJA[ilganA] + '→' + STEM_HANJA[ilganB] + ' 상극(' + ELEMENT_KR[elA] + '克' + ELEMENT_KR[elB] + '), 본인의 의지가 상대에게 부담될 수 있어 부드러운 소통이 필요합니다.');
  } else if (isKe(elB, elA)) {
    score -= 15;
    notes.push(STEM_HANJA[ilganB] + '→' + STEM_HANJA[ilganA] + ' 상극(' + ELEMENT_KR[elB] + '克' + ELEMENT_KR[elA] + '), 상대의 영향력이 강해 본인의 중심을 잘 지켜야 합니다.');
  }

  // 2. 천간 합 (가중치 +15점)
  var ganHapMatch = STEM_5HAP.find(function (r) {
    return (r[0] === ilganA && r[1] === ilganB) || (r[1] === ilganA && r[0] === ilganB);
  });
  if (ganHapMatch) {
    score += 15;
    notes.push('일간끼리 ' + ganHapMatch[3] + '(천간 5합)이 성립되어 운명적 끌림이 있는 천생연분 관계입니다.');
  }

  // 3. 천간 충 (가중치 -15점)
  var ganChungMatch = STEM_CHUNG.find(function (r) {
    return (r[0] === ilganA && r[1] === ilganB) || (r[1] === ilganA && r[0] === ilganB);
  });
  if (ganChungMatch) {
    var chungPenalty = ganChungMatch[2] === 'full' ? -15 : -8;
    score += chungPenalty;
    notes.push('일간끼리 ' + ganChungMatch[3] + '(천간 충)이 성립되어 가치관 충돌 가능성이 있으니 서로의 차이를 인정해야 합니다.');
  }

  // 4. 음양 조화 (가중치 ±5점)
  if (yangA !== yangB) {
    score += 5;
    notes.push('일간 음양(陰陽)이 서로 달라 자연스러운 균형이 이루어집니다.');
  } else {
    score -= 3;
    notes.push('일간 음양이 같아(' + (yangA ? '양·양' : '음·음') + ') 같은 방향성이지만 보완성은 약할 수 있습니다.');
  }

  // 5. 일지(日支) 6합 (가중치 +12점) — 부부궁이라 가중치 큼
  var iljiHapMatch = BRANCH_6HAP.find(function (r) {
    return (r[0] === iljiA && r[1] === iljiB) || (r[1] === iljiA && r[0] === iljiB);
  });
  if (iljiHapMatch) {
    score += 12;
    notes.push('일지(부부궁)에서 ' + iljiHapMatch[3] + '이 성립되어 가정의 화목과 깊은 정이 약속됩니다.');
  }

  // 6. 일지 6충 (가중치 -12점)
  var iljiChungMatch = BRANCH_6CHUNG.find(function (r) {
    return (r[0] === iljiA && r[1] === iljiB) || (r[1] === iljiA && r[0] === iljiB);
  });
  if (iljiChungMatch) {
    score -= 12;
    notes.push('일지에서 ' + iljiChungMatch[2] + '(부부궁 충)이 발생, 동거·결혼 시 마찰이 잦을 수 있어 별도 공간 확보를 권장합니다.');
  }

  // clamp
  score = Math.max(15, Math.min(98, score));

  return {
    score: score,
    ilganA: { kr: STEM_KR[ilganA], hanja: STEM_HANJA[ilganA], element: ELEMENT_KR[elA], yinyang: yangA ? '양' : '음' },
    ilganB: { kr: STEM_KR[ilganB], hanja: STEM_HANJA[ilganB], element: ELEMENT_KR[elB], yinyang: yangB ? '양' : '음' },
    iljiA: { kr: BRANCH_KR[iljiA], hanja: BRANCH_HANJA[iljiA] },
    iljiB: { kr: BRANCH_KR[iljiB], hanja: BRANCH_HANJA[iljiB] },
    notes: notes,
  };
}

// ─── 종합 점수 가중 합산 ──────────────────────────────────
// 일간궁합 60% + 합/충 카운트 25% + 오행균형 15%
function calcOverallScore(ilganResult, stemInter, branchInter, balance) {
  var ilganScore = ilganResult.score;

  // 합/충 점수 (전체 8자 vs 8자 카운트)
  var hapCount = stemInter.hap.length + branchInter.hap.length;
  var fullChungCount = stemInter.chung.filter(function (c) { return c.severity === 'full'; }).length
                      + branchInter.chung.length;
  var halfChungCount = stemInter.chung.filter(function (c) { return c.severity === 'half'; }).length;

  // hap 1개 = +6점, fullChung 1개 = -8점, halfChung 1개 = -4점, 기준 65점에서 시작
  var interactionScore = 65 + hapCount * 6 - fullChungCount * 8 - halfChungCount * 4;
  interactionScore = Math.max(15, Math.min(100, interactionScore));

  // 가중 평균
  var overall = Math.round(
    ilganScore * 0.60 + interactionScore * 0.25 + balance.balanceScore * 0.15
  );
  overall = Math.max(20, Math.min(98, overall));

  return {
    overall: overall,
    ilgan: ilganScore,
    interaction: interactionScore,
    balance: balance.balanceScore,
  };
}

// ─── 종합 코멘트 + 주의사항 텍스트 생성 ──────────────────────
function buildSummaryText(scores, ilganResult, stemInter, branchInter, balance) {
  var s = scores.overall;
  var headline;
  if (s >= 90) headline = '천생연분 — 명리학적으로 매우 드문 최상의 궁합입니다.';
  else if (s >= 80) headline = '아주 좋은 궁합 — 평생 동반자로 권할 만한 관계입니다.';
  else if (s >= 70) headline = '좋은 궁합 — 노력하면 안정적이고 화목한 관계를 이룹니다.';
  else if (s >= 60) headline = '보통 궁합 — 서로의 차이를 인정하면 충분히 행복할 수 있습니다.';
  else if (s >= 45) headline = '주의가 필요한 궁합 — 갈등 요소가 있으니 의식적인 노력이 필요합니다.';
  else headline = '도전적 궁합 — 깊은 이해와 배려가 필수적입니다. 충(冲) 작용이 강합니다.';

  var advice = [];

  // 합 기반 추천
  if (stemInter.hap.length > 0) {
    advice.push('천간에서 ' + stemInter.hap.length + '개의 합(合)이 성립되어, 가치관·생각이 자연스럽게 통합니다. 깊은 대화를 자주 나누세요.');
  }
  if (branchInter.hap.length > 0) {
    advice.push('지지에서 ' + branchInter.hap.length + '개의 합이 성립되어 일상의 호흡이 잘 맞습니다. 함께하는 시간을 늘릴수록 관계가 깊어집니다.');
  }
  if (balance.complementAByB > 0 || balance.complementBByA > 0) {
    advice.push('두 분의 오행이 서로 부족한 부분을 ' + (balance.complementAByB + balance.complementBByA) + '곳에서 채워주는 보완 관계입니다. 함께 있을 때 운기(運氣)가 강해집니다.');
  }
  if (balance.balanceScore >= 75) {
    advice.push('두 사람의 오행 합산 분포가 균형 잡혀(' + balance.balanceScore + '점) 함께할 때 행운의 흐름이 안정적입니다.');
  }

  var cautions = [];
  // 충 기반 주의
  var fullChungs = stemInter.chung.filter(function (c) { return c.severity === 'full'; });
  if (fullChungs.length > 0) {
    cautions.push('천간 정충(正冲) ' + fullChungs.length + '건: 핵심 가치관 충돌 가능성. 큰 결정 전 충분한 의논이 필요합니다.');
  }
  if (branchInter.chung.length > 0) {
    cautions.push('지지 충 ' + branchInter.chung.length + '건: 생활 패턴·습관 차이가 자주 부딪힐 수 있습니다. 각자의 영역을 존중하세요.');
  }
  if (balance.balanceScore < 50) {
    cautions.push('두 사람의 오행 분포가 한쪽으로 치우쳐(' + balance.dominantElement + ' 과다) 있어 ' + balance.weakestElement + ' 기운을 보완하는 활동(음식·색상·방위)을 권장합니다.');
  }
  if (cautions.length === 0) {
    cautions.push('명리학적으로 큰 충(冲)이 없어 안정적인 관계입니다. 다만 대운(大運) 변동기에는 서로의 변화를 세심히 살피세요.');
  }

  return {
    headline: headline,
    advice: advice,
    cautions: cautions,
  };
}

// ─── 메인 분석 함수 ───────────────────────────────────────
/**
 * @param {Object} personA - { year, month, day, hour, gender }
 * @param {Object} personB - { year, month, day, hour, gender }
 * @returns {Object} 궁합 분석 결과 (JSON)
 */
function analyzeCompat(personA, personB) {
  if (!personA || !personB) throw new Error('두 사람의 정보가 필요합니다');

  var resultA = SajuEngine.analyzeSaju(
    personA.year, personA.month, personA.day,
    personA.hour != null ? personA.hour : -1,
    personA.gender || 'M'
  );
  var resultB = SajuEngine.analyzeSaju(
    personB.year, personB.month, personB.day,
    personB.hour != null ? personB.hour : -1,
    personB.gender || 'F'
  );

  var pA = extractPillars(resultA.사주);
  var pB = extractPillars(resultB.사주);

  var stemInter = analyzeStemInteractions(pA.stems, pB.stems);
  var branchInter = analyzeBranchInteractions(pA.branches, pB.branches);
  var balance = analyzeElementBalance(pA.stems, pA.branches, pB.stems, pB.branches);
  var ilgan = analyzeIlganCompat(resultA.사주, resultB.사주);
  var scores = calcOverallScore(ilgan, stemInter, branchInter, balance);
  var summary = buildSummaryText(scores, ilgan, stemInter, branchInter, balance);

  return {
    personA: {
      birth: personA.year + '-' + String(personA.month).padStart(2, '0') + '-' + String(personA.day).padStart(2, '0'),
      hour: personA.hour,
      gender: personA.gender,
      saju: resultA.사주.summary,
      sajuHanja: resultA.사주.summary_한자,
      ilgan: ilgan.ilganA,
      ttiName: resultA.기본정보.띠,
    },
    personB: {
      birth: personB.year + '-' + String(personB.month).padStart(2, '0') + '-' + String(personB.day).padStart(2, '0'),
      hour: personB.hour,
      gender: personB.gender,
      saju: resultB.사주.summary,
      sajuHanja: resultB.사주.summary_한자,
      ilgan: ilgan.ilganB,
      ttiName: resultB.기본정보.띠,
    },
    scores: scores,
    ilganAnalysis: {
      score: ilgan.score,
      notes: ilgan.notes,
    },
    stemInteractions: stemInter,
    branchInteractions: branchInter,
    elementBalance: balance,
    summary: summary,
    generatedAt: new Date().toISOString(),
    engineVersion: '1.0.0',
  };
}

module.exports = {
  analyzeCompat,
  // 내부 함수도 노출 (테스트/디버깅용)
  analyzeStemInteractions,
  analyzeBranchInteractions,
  analyzeElementBalance,
  analyzeIlganCompat,
  calcOverallScore,
  buildSummaryText,
  // 상수도 export
  STEM_HANJA, BRANCH_HANJA, STEM_KR, BRANCH_KR,
  ELEMENT_KR, ELEMENT_HANJA,
  BRANCH_6HAP, BRANCH_6CHUNG, STEM_5HAP, STEM_CHUNG,
};
