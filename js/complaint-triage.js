/**
 * ============================================================================
 * 천명당 불만 자동 판독 엔진 (Complaint Auto-Triage Engine)
 * ============================================================================
 *
 * 공개된 불만 접수 폼에서 들어오는 텍스트를 순수 클라이언트 사이드에서
 * 판독·분류·응답 생성까지 수행한다. 서버 통신이나 LLM 호출은 일체 없다.
 *
 * 제공 기능:
 * - 스팸/욕설/광고성 자동 탐지 → 접수 거부
 * - 카테고리 자동 분류 (환불/버그/개선/불만족/기타)
 * - 심각도 점수 (1~5) 산출
 * - 타당성 점수 (0~5) — 구체성·명확성·실행가능성 기반
 * - 핵심 키워드 추출
 * - 카테고리별 맞춤 응답 생성
 *
 * ⚠️ 보안 원칙: 이 엔진은 절대 코드를 수정하지 않는다. 판독과 응답만 담당한다.
 *     실제 코드 수정이 필요한 항목은 관리자 대시보드에서 GitHub 이슈로
 *     전환되어 사람의 검토를 거쳐 반영된다.
 *
 * @version 1.0.0
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.ComplaintTriage = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ==========================================================================
  // 사전(辭典) 및 규칙
  // ==========================================================================

  /** 욕설·비방 키워드 (부분 일치) */
  const PROFANITY = [
    '씨발', '시발', '씨팔', '좆', '병신', '지랄', '개새', '개색',
    '꺼져', '엿먹', '니미', '느금', '쳐먹', '쓰레기같',
    'fuck', 'shit', 'bitch', 'asshole'
  ];

  /** 카테고리 정의 (우선순위 순) */
  const CATEGORIES = [
    {
      key: 'refund',
      label: '환불/결제 문의',
      icon: '💰',
      color: '#f4d06f',
      priority: 3,
      keywords: [
        '환불', '환급', '돌려', '결제', '취소', '돈', '카드', '송금', '입금',
        '토스', '카카오페이', '페이먼츠', '청구', '과금', '중복결제', '영수증'
      ]
    },
    {
      key: 'bug',
      label: '오류/버그 신고',
      icon: '🐛',
      color: '#e57373',
      priority: 2,
      keywords: [
        '오류', '에러', '버그', '안돼', '안됨', '안되', '먹통', '멈춤', '멈춰',
        '깨짐', '깨져', '안떠', '안뜨', '안나와', '표시안', '로딩', '로딩안',
        '작동안', '동작안', '먹히지', '먹히지않', '실행안', '클릭안', '반응없',
        '하얀화면', '빈화면', '에러메시지', '404', '500'
      ]
    },
    {
      key: 'dissatisfaction',
      label: '결과 불만족',
      icon: '😕',
      color: '#c75a6e',
      priority: 1,
      keywords: [
        '틀렸', '틀려', '맞지않', '맞지 않', '정확하지', '부정확', '엉터리',
        '이상해', '이상하', '별로', '실망', '소름', '엉성', '부실', '대충',
        '성의없', '만족못', '만족스럽'
      ]
    },
    {
      key: 'improvement',
      label: '개선 제안',
      icon: '💡',
      color: '#7bc4b5',
      priority: 1,
      keywords: [
        '추가', '개선', '제안', '건의', '됐으면', '좋겠', '바람', '요청',
        '있으면', '넣어', '만들어', '해주세요', '해주시', '부탁', '기능추가',
        '새로운', '업데이트', '보완'
      ]
    }
  ];

  /** 심각도 가중 키워드 */
  const SEVERITY_HIGH = ['환불', '사기', '긴급', '결제', '돈', '중복결제', '과금'];
  const SEVERITY_MID = ['오류', '에러', '안돼', '안됨', '작동', '멈춤', '먹통'];

  /** 타당성 판정용 마커 */
  const QUALITY_MARKERS = [
    '때', '언제', '어디', '어떻게', '왜', '그래서', '그런데',
    '했는데', '하는데', '하니', '까지', '부터', '이후', '이전',
    '클릭', '눌렀', '입력', '제출'
  ];

  /** 구체 명사 — 실제 서비스 용어 */
  const CONCRETE_NOUNS = [
    '버튼', '결과', '페이지', '분석', '결제', '화면', '사진', '카드',
    '사주', '관상', '손금', '타로', '운세', '궁합', '풍수', '꿈해몽',
    '별자리', '별점', '폼', '메뉴', '링크', '이미지', '생년월일'
  ];

  // ==========================================================================
  // 유틸리티
  // ==========================================================================

  function normalizeText(t) {
    return (t || '').toLowerCase().replace(/\s+/g, ' ').trim();
  }

  function includesAny(haystack, needles) {
    for (let i = 0; i < needles.length; i++) {
      if (haystack.indexOf(needles[i]) >= 0) return needles[i];
    }
    return null;
  }

  // ==========================================================================
  // 스팸/어뷰즈 탐지
  // ==========================================================================

  function detectSpam(detail) {
    const t = detail || '';
    const lower = t.toLowerCase();

    // 1) 욕설만 있는 짧은 텍스트 → 거부
    let profanityCount = 0;
    for (const w of PROFANITY) {
      if (lower.indexOf(w) >= 0) profanityCount++;
    }
    if (profanityCount > 0 && t.length < 40) {
      return { spam: true, reason: '욕설·비방 위주 내용은 접수가 어렵습니다' };
    }

    // 2) URL / 도메인 → 광고성 의심
    if (/https?:\/\//i.test(t) || /www\./i.test(t)) {
      return { spam: true, reason: '링크·URL이 포함된 내용은 광고성으로 분류되어 접수되지 않습니다' };
    }
    if (/\b\w+\.(com|net|kr|co\.kr|org|biz|shop|store)\b/i.test(t)) {
      return { spam: true, reason: '외부 도메인 언급은 광고성으로 분류되어 접수되지 않습니다' };
    }

    // 3) 같은 문자 6자 이상 반복 → 의미 없음
    if (/(.)\1{5,}/.test(t)) {
      return { spam: true, reason: '같은 문자 반복으로 의미 파악이 어렵습니다' };
    }

    // 4) 숫자·기호만 있는 내용
    if (/^[\d\s\-+().,!?~@#$%^&*]+$/.test(t)) {
      return { spam: true, reason: '구체적인 상황을 텍스트로 적어주세요' };
    }

    // 5) 의미 있는 문자 수 검사 (공백·숫자·기호 제외)
    const meaningful = t.replace(/[\s\d\-+().,!?~@#$%^&*]/g, '');
    if (meaningful.length < 6) {
      return { spam: true, reason: '의미 있는 텍스트가 너무 짧습니다' };
    }

    return { spam: false, reason: null };
  }

  // ==========================================================================
  // 카테고리 분류
  // ==========================================================================

  /** 폼에서 선택한 type 값 → 내부 카테고리 힌트 */
  const TYPE_HINT_MAP = {
    '서비스 이용 불편': 'bug',
    '분석 결과 불만족': 'dissatisfaction',
    '결제/환불 문의': 'refund',
    '오류/버그 신고': 'bug',
    '개선 제안': 'improvement',
    '기타': null
  };

  function detectCategory(detail, typeHint) {
    const t = normalizeText(detail);
    const scores = {};

    for (const cat of CATEGORIES) {
      let score = 0;
      for (const k of cat.keywords) {
        if (t.indexOf(k) >= 0) score += cat.priority;
      }
      scores[cat.key] = score;
    }

    // 사용자가 폼에서 직접 고른 유형에 가중치
    const hinted = TYPE_HINT_MAP[typeHint];
    if (hinted) scores[hinted] = (scores[hinted] || 0) + 3;

    let best = null, bestScore = 0;
    for (const cat of CATEGORIES) {
      if (scores[cat.key] > bestScore) {
        best = cat;
        bestScore = scores[cat.key];
      }
    }

    if (!best) {
      return { key: 'other', label: '기타', icon: '📋', color: '#9ba3b8', score: 0 };
    }
    return {
      key: best.key,
      label: best.label,
      icon: best.icon,
      color: best.color,
      score: bestScore
    };
  }

  // ==========================================================================
  // 심각도 점수 (1~5)
  // ==========================================================================

  function calcSeverity(detail, rating) {
    const t = normalizeText(detail);
    // 기본: 별점이 낮을수록 심각 (1성=5, 5성=1, 미설정=3)
    let base = 3;
    if (rating && rating > 0) base = 6 - rating;

    let boost = 0;
    for (const k of SEVERITY_HIGH) if (t.indexOf(k) >= 0) boost += 2;
    for (const k of SEVERITY_MID)  if (t.indexOf(k) >= 0) boost += 1;
    boost = Math.min(boost, 3);

    return Math.min(5, Math.max(1, base + boost));
  }

  // ==========================================================================
  // 타당성 점수 (0~5)
  // ==========================================================================

  function calcValidity(detail) {
    const t = detail || '';
    let score = 0;

    // 길이 기반 (구체성)
    if (t.length > 30) score += 1;
    if (t.length > 80) score += 1;

    // 상황 설명 마커
    let markers = 0;
    for (const m of QUALITY_MARKERS) {
      if (t.indexOf(m) >= 0) { markers++; if (markers >= 2) break; }
    }
    if (markers >= 1) score += 1;
    if (markers >= 2) score += 1;

    // 구체적 서비스 용어 언급
    for (const n of CONCRETE_NOUNS) {
      if (t.indexOf(n) >= 0) { score += 1; break; }
    }

    return Math.min(5, score);
  }

  // ==========================================================================
  // 키워드 추출
  // ==========================================================================

  function extractKeywords(detail) {
    const t = detail || '';
    const found = new Set();
    for (const cat of CATEGORIES) {
      for (const k of cat.keywords) {
        if (t.indexOf(k) >= 0) found.add(k);
      }
    }
    for (const n of CONCRETE_NOUNS) {
      if (t.indexOf(n) >= 0) found.add(n);
    }
    return Array.from(found).slice(0, 8);
  }

  // ==========================================================================
  // 카테고리별 응답 생성
  // ==========================================================================

  function buildResponse(analysis) {
    const cat = analysis.category.key;

    if (cat === 'refund') {
      return {
        tone: 'urgent',
        title: '환불·결제 문의로 접수되었습니다',
        body: '결제 후 24시간 이내 결과 미수령 시 전액 환불이 가능합니다. 아래 "환불 신청 메일 열기"를 누르면 제목·양식이 자동으로 채워진 이메일이 열립니다.',
        actions: [
          { label: '📧 환불 신청 메일 열기', type: 'mailto', data: {
            to: 'support@cheonmyeongdang.kr',
            subject: '[천명당] 환불 신청',
            body: '안녕하세요, 환불을 신청합니다.\n\n- 주문번호 / 결제 수단: \n- 결제 일시: \n- 환불 사유: \n\n감사합니다.'
          }},
          { label: '📖 환불 FAQ 보기', type: 'scroll', data: '.complaint-faq' }
        ]
      };
    }

    if (cat === 'bug') {
      return {
        tone: 'action',
        title: '오류·버그 신고로 분류되었습니다',
        body: '빠른 해결을 위해 다음 정보를 함께 알려주시면 크게 도움이 됩니다:\n① 어떤 페이지/기능에서 ② 어떤 동작을 하셨고 ③ 어떤 결과가 나왔는지.\n접수된 내용은 개발팀에 자동 전달되며 우선순위에 따라 처리됩니다.',
        actions: [
          { label: '✏️ 재현 정보 추가 작성', type: 'reopen', data: null }
        ]
      };
    }

    if (cat === 'improvement') {
      return {
        tone: 'thanks',
        title: '개선 제안으로 분류되었습니다',
        body: '소중한 제안 감사합니다. 유사 제안과 함께 검토 후 반영 여부를 결정하며, 반영 시 별도 공지드립니다.',
        actions: []
      };
    }

    if (cat === 'dissatisfaction') {
      return {
        tone: 'careful',
        title: '분석 결과 관련 의견으로 확인됩니다',
        body: '무료 사주·관상·손금 분석은 전통 명리학·관상학 공식 기반의 참고용 해석입니다. 더 정확한 상세 풀이를 원하시면 유료 사주 상세 풀이(29,900원) 이용을 고려해 주세요.',
        actions: [
          { label: '📜 유료 상세 풀이 보기', type: 'scroll', data: '#paid' }
        ]
      };
    }

    return {
      tone: 'neutral',
      title: '의견이 접수되었습니다',
      body: '소중한 의견 감사합니다. 내용은 담당 부서로 자동 전달되었으며, 필요 시 연락드리겠습니다.',
      actions: []
    };
  }

  // ==========================================================================
  // 메인: 전체 판독
  // ==========================================================================

  function analyze(complaint) {
    const detail = (complaint && complaint.detail) || '';
    const rating = (complaint && complaint.rating) || 0;
    const typeHint = (complaint && complaint.type) || '';

    // 1) 스팸 먼저 확인
    const spam = detectSpam(detail);
    if (spam.spam) {
      return {
        rejected: true,
        rejectionReason: spam.reason,
        valid: false,
        category: { key: 'spam', label: '스팸/미접수', icon: '🚫', color: '#9ba3b8' },
        severity: 0,
        validityScore: 0,
        keywords: [],
        response: {
          tone: 'reject',
          title: '접수되지 않았습니다',
          body: spam.reason + '. 구체적인 상황(언제 / 어디서 / 어떤 문제인지)을 적어주시면 빠르게 도와드릴 수 있습니다.',
          actions: [{ label: '✏️ 다시 작성하기', type: 'reopen', data: null }]
        },
        analyzedAt: new Date().toISOString(),
        engineVersion: '1.0.0'
      };
    }

    // 2) 분류·점수·키워드
    const category = detectCategory(detail, typeHint);
    const severity = calcSeverity(detail, rating);
    const validityScore = calcValidity(detail);
    const keywords = extractKeywords(detail);

    const analysis = {
      rejected: false,
      rejectionReason: null,
      valid: true,
      category: category,
      severity: severity,
      validityScore: validityScore,
      keywords: keywords,
      analyzedAt: new Date().toISOString(),
      engineVersion: '1.0.0'
    };

    // 3) 응답 생성
    analysis.response = buildResponse(analysis);
    return analysis;
  }

  // ==========================================================================
  // 공개 API
  // ==========================================================================

  return {
    analyze: analyze,
    detectSpam: detectSpam,
    detectCategory: detectCategory,
    calcSeverity: calcSeverity,
    calcValidity: calcValidity,
    extractKeywords: extractKeywords,
    CATEGORIES: CATEGORIES
  };
}));
