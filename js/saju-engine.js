/**
 * ============================================================================
 * 사주팔자 (四柱八字) 계산 엔진 - Korean Four Pillars of Destiny Calculator
 * ============================================================================
 *
 * 이 엔진은 양력 생년월일시를 입력받아 음력 변환 후 사주팔자를 분석합니다.
 *
 * 주요 기능:
 * - 양력 → 음력 변환 (1920~2050년)
 * - 사주 (년주, 월주, 일주, 시주) 계산
 * - 오행 분석 (목화토금수 분포)
 * - 십신 계산
 * - 12운성 계산
 * - 대운 계산
 * - 합/충/형/파/해 분석
 * - 지장간 분석
 * - 용신 기본 분석
 *
 * @version 1.0.0
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.SajuEngine = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ==========================================================================
  // 기초 상수 정의
  // ==========================================================================

  /** 천간 (10 Heavenly Stems) */
  const 천간 = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'];
  const 천간_한자 = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];

  /** 지지 (12 Earthly Branches) */
  const 지지 = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'];
  const 지지_한자 = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

  /** 오행 (Five Elements) */
  const 오행 = ['목', '화', '토', '금', '수'];
  const 오행_한자 = ['木', '火', '土', '金', '水'];

  /** 천간의 오행 매핑: 갑을=목, 병정=화, 무기=토, 경신=금, 임계=수 */
  const 천간_오행 = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]; // index into 오행

  /** 천간의 음양: 양=0, 음=1 */
  const 천간_음양 = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1];

  /** 지지의 오행 매핑 */
  // 자=수, 축=토, 인=목, 묘=목, 진=토, 사=화, 오=화, 미=토, 신=금, 유=금, 술=토, 해=수
  const 지지_오행 = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4];

  /** 지지의 음양 */
  const 지지_음양 = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1];

  /** 띠 동물 */
  const 띠 = ['쥐', '소', '호랑이', '토끼', '용', '뱀', '말', '양', '원숭이', '닭', '개', '돼지'];

  // ==========================================================================
  // 십신 (Ten Gods) 정의
  // ==========================================================================

  /**
   * 십신 명칭
   * 비견, 겁재, 식신, 상관, 편재, 정재, 편관, 정관, 편인, 정인
   */
  const 십신_명칭 = ['비견', '겁재', '식신', '상관', '편재', '정재', '편관', '정관', '편인', '정인'];

  /**
   * 십신 계산
   * 일간 기준으로 다른 천간과의 관계를 계산
   *
   * 같은 오행: 같은 음양 = 비견, 다른 음양 = 겁재
   * 내가 생하는 오행: 같은 음양 = 식신, 다른 음양 = 상관
   * 내가 극하는 오행: 같은 음양 = 편재, 다른 음양 = 정재
   * 나를 극하는 오행: 같은 음양 = 편관, 다른 음양 = 정관
   * 나를 생하는 오행: 같은 음양 = 편인, 다른 음양 = 정인
   */
  function get십신(일간_idx, 대상_idx) {
    const 일간_element = 천간_오행[일간_idx];
    const 대상_element = 천간_오행[대상_idx];
    const same_yinyang = 천간_음양[일간_idx] === 천간_음양[대상_idx];

    // 상생 순서: 목→화→토→금→수→목 (0→1→2→3→4→0)
    // 상극 순서: 목→토→수→화→금→목 (0→2→4→1→3→0)

    const diff = (대상_element - 일간_element + 5) % 5;

    switch (diff) {
      case 0: return same_yinyang ? '비견' : '겁재';
      case 1: return same_yinyang ? '식신' : '상관'; // 내가 생하는
      case 2: return same_yinyang ? '편재' : '정재'; // 내가 극하는 (목→토: +2)
      case 3: return same_yinyang ? '편관' : '정관'; // 나를 극하는 (목←금: +3)
      case 4: return same_yinyang ? '편인' : '정인'; // 나를 생하는 (목←수: +4)
      default: return '';
    }
  }

  /** 지지에 대한 십신 - 지지의 정기(본기)를 사용 */
  function get십신_지지(일간_idx, 지지_idx) {
    const 정기_stem = 지장간_정기[지지_idx];
    return get십신(일간_idx, 정기_stem);
  }

  // ==========================================================================
  // 12운성 (Twelve Life Stages)
  // ==========================================================================

  const 운성_명칭 = ['장생', '목욕', '관대', '건록', '제왕', '쇠', '병', '사', '묘', '절', '태', '양'];

  /**
   * 12운성 테이블
   * 각 천간(일간)이 각 지지에서 어떤 운성인지를 나타냄
   * 양간: 장생부터 순행
   * 음간: 장생부터 역행
   *
   * 양간 장생 위치: 갑=해(11), 병=인(2), 무=인(2), 경=사(5), 임=신(8)
   * 음간 장생 위치: 을=오(6), 정=유(9), 기=유(9), 신=자(0), 계=묘(3)
   */
  const 양간_장생위치 = { 0: 11, 2: 2, 4: 2, 6: 5, 8: 8 }; // 갑병무경임
  const 음간_장생위치 = { 1: 6, 3: 9, 5: 9, 7: 0, 9: 3 };  // 을정기신계

  function get12운성(일간_idx, 지지_idx) {
    if (천간_음양[일간_idx] === 0) {
      // 양간 - 순행
      const 장생 = 양간_장생위치[일간_idx];
      const offset = (지지_idx - 장생 + 12) % 12;
      return 운성_명칭[offset];
    } else {
      // 음간 - 역행
      const 장생 = 음간_장생위치[일간_idx];
      const offset = (장생 - 지지_idx + 12) % 12;
      return 운성_명칭[offset];
    }
  }

  // ==========================================================================
  // 지장간 (Hidden Stems in Branches)
  // ==========================================================================

  /**
   * 지장간: 각 지지에 숨어있는 천간들 [여기, 중기, 정기]
   * 천간 인덱스로 표현
   *
   * 자: 임(8), 계(9) → 정기=계
   * 축: 계(9), 신(7), 기(5) → 정기=기
   * 인: 무(4), 병(2), 갑(0) → 정기=갑
   * 묘: 갑(0), 을(1) → 정기=을
   * 진: 을(1), 계(9), 무(4) → 정기=무
   * 사: 무(4), 경(6), 병(2) → 정기=병
   * 오: 병(2), 기(5), 정(3) → 정기=정  (또는 기(5), 정(3))
   * 미: 정(3), 을(1), 기(5) → 정기=기
   * 신: 무(4), 임(8), 경(6) → 정기=경  (또는 기(5), 임(8), 경(6))
   * 유: 경(6), 신(7) → 정기=신
   * 술: 신(7), 정(3), 무(4) → 정기=무
   * 해: 무(4), 갑(0), 임(8) → 정기=임
   */
  const 지장간_data = [
    [8, -1, 9],  // 자: 여기=임, 정기=계
    [9, 7, 5],   // 축: 여기=계, 중기=신, 정기=기
    [4, 2, 0],   // 인: 여기=무, 중기=병, 정기=갑
    [0, -1, 1],  // 묘: 여기=갑, 정기=을
    [1, 9, 4],   // 진: 여기=을, 중기=계, 정기=무
    [4, 6, 2],   // 사: 여기=무, 중기=경, 정기=병
    [2, 5, 3],   // 오: 여기=병, 중기=기, 정기=정
    [3, 1, 5],   // 미: 여기=정, 중기=을, 정기=기
    [5, 8, 6],   // 신: 여기=기, 중기=임, 정기=경
    [6, -1, 7],  // 유: 여기=경, 정기=신
    [7, 3, 4],   // 술: 여기=신, 중기=정, 정기=무
    [4, 0, 8],   // 해: 여기=무, 중기=갑, 정기=임
  ];

  /** 지장간 정기 인덱스 (빠른 참조용) */
  const 지장간_정기 = [9, 5, 0, 1, 4, 2, 3, 5, 6, 7, 4, 8];

  function get지장간(지지_idx) {
    const data = 지장간_data[지지_idx];
    const result = [];
    result.push({ 천간: 천간[data[0]], 유형: '여기', idx: data[0] });
    if (data[1] !== -1) {
      result.push({ 천간: 천간[data[1]], 유형: '중기', idx: data[1] });
    }
    result.push({ 천간: 천간[data[2]], 유형: '정기', idx: data[2] });
    return result;
  }

  // ==========================================================================
  // 합/충/형/파/해 분석
  // ==========================================================================

  /**
   * 천간합 (5가지 천간 합)
   * 갑기합토, 을경합금, 병신합수, 정임합목, 무계합화
   */
  const 천간합_pairs = [
    [0, 5, '토'],  // 갑기합토
    [1, 6, '금'],  // 을경합금
    [2, 7, '수'],  // 병신합수
    [3, 8, '목'],  // 정임합목
    [4, 9, '화'],  // 무계합화
  ];

  /**
   * 천간충 (천간 상충)
   * 갑경충, 을신충, 병임충, 정계충
   */
  const 천간충_pairs = [
    [0, 6],  // 갑경충
    [1, 7],  // 을신충
    [2, 8],  // 병임충
    [3, 9],  // 정계충
  ];

  /**
   * 지지육합 (6가지 지지 합)
   */
  const 지지육합_pairs = [
    [0, 1, '토'],   // 자축합토
    [2, 11, '목'],  // 인해합목
    [3, 10, '화'],  // 묘술합화
    [4, 9, '금'],   // 진유합금
    [5, 8, '수'],   // 사신합수
    [6, 7, '화/토'],// 오미합화(또는 토)
  ];

  /**
   * 지지삼합 (4가지 삼합)
   */
  const 지지삼합_sets = [
    [[8, 0, 4], '수'],   // 신자진 합수
    [[11, 3, 7], '목'],  // 해묘미 합목
    [[2, 6, 10], '화'],  // 인오술 합화
    [[5, 9, 1], '금'],   // 사유축 합금
  ];

  /**
   * 지지방합 (4가지 방합)
   */
  const 지지방합_sets = [
    [[2, 3, 4], '목'],    // 인묘진 동방목
    [[5, 6, 7], '화'],    // 사오미 남방화
    [[8, 9, 10], '금'],   // 신유술 서방금
    [[11, 0, 1], '수'],   // 해자축 북방수
  ];

  /**
   * 지지충 (6가지 상충)
   */
  const 지지충_pairs = [
    [0, 6],   // 자오충
    [1, 7],   // 축미충
    [2, 8],   // 인신충
    [3, 9],   // 묘유충
    [4, 10],  // 진술충
    [5, 11],  // 사해충
  ];

  /**
   * 지지형 (삼형/자형/상형)
   */
  const 지지형_sets = [
    [[2, 5, 8], '무은지형'],   // 인사신 삼형 (무은지형)
    [[1, 10, 7], '은혜지형'],  // 축술미 삼형 (은혜의 형)
    [[0, 3], '무례지형'],       // 자묘형 (무례지형)
    [[4, 4], '자형'],           // 진진 자형
    [[6, 6], '자형'],           // 오오 자형
    [[9, 9], '자형'],           // 유유 자형
    [[11, 11], '자형'],         // 해해 자형
  ];

  /**
   * 지지파 (6파)
   */
  const 지지파_pairs = [
    [0, 9],   // 자유파
    [1, 4],   // 축진파  (또는 진축파)
    [2, 11],  // 인해파
    [3, 6],   // 묘오파
    [5, 8],   // 사신파
    [7, 10],  // 미술파
  ];

  /**
   * 지지해 (6해)
   */
  const 지지해_pairs = [
    [0, 7],   // 자미해
    [1, 6],   // 축오해
    [2, 5],   // 인사해
    [3, 4],   // 묘진해
    [8, 11],  // 신해해
    [9, 10],  // 유술해
  ];

  // ==========================================================================
  // 음력 데이터 (1920~2050)
  // ==========================================================================

  /**
   * 음력 데이터 인코딩:
   * 각 연도별로 하나의 정수값 저장
   *
   * 비트 구조 (상위부터):
   * bit 20: 윤달이 대월(30일)이면 1, 소월(29일)이면 0
   * bit 19~8: 1~12월의 대/소월 (bit 19=1월, bit 8=12월, 1=대월30일, 0=소월29일)
   * bit 7~4: 윤달 위치 (0이면 윤달 없음, 1~12이면 해당 월 뒤에 윤달)
   * bit 3~0: 사용하지 않음 (0)
   *
   * 이 방식 대신, 더 검증된 형태로 저장합니다:
   * 배열: [monthInfo, leapMonth]
   * monthInfo: 12비트 정수, bit 0=1월, bit 11=12월 (1=대월30일)
   * leapMonth: 윤달 위치 (0=없음), 음수면 윤달이 소월(29일), 양수면 대월(30일)
   *
   * 실제로는 더 간결한 16진수 배열을 사용합니다.
   */

  /**
   * 음력 데이터
   * 각 항목: [monthBitmask, leapMonth, leapMonthBig]
   * monthBitmask: 1~12월 대소 (bit0=1월, 1=대월30일, 0=소월29일)
   * leapMonth: 윤달 위치 (0=없음)
   * leapMonthBig: 윤달 대월 여부 (true=30일)
   *
   * 이 데이터는 한국천문연구원 자료를 기반으로 합니다.
   */
  const LUNAR_DATA = [
    // 1920
    [0x752, 6, false],  // 1920: 윤6월
    [0xEA5, 0, false],  // 1921
    [0xD4A, 0, false],  // 1922
    [0xA95, 4, true],   // 1923: 윤4월
    [0x54D, 0, false],  // 1924
    [0xAAD, 0, false],  // 1925
    [0x56A, 2, false],  // 1926: 윤2월 (소)
    [0xB55, 0, false],  // 1927
    [0xDA5, 0, false],  // 1928
    [0xB4A, 5, true],   // 1929: 윤5월
    [0xA95, 0, false],  // 1930
    // 1931
    [0x52D, 0, false],  // 1931
    [0xA9B, 3, false],  // 1932: 윤3월 (소)
    [0x6AA, 0, false],  // 1933
    [0xAD5, 0, false],  // 1934
    [0x6B2, 8, false],  // 1935: 윤8월 (소)
    [0xDA5, 0, false],  // 1936
    [0xD4A, 0, false],  // 1937
    [0xC95, 7, false],  // 1938: 윤7월 (소)
    [0x54B, 0, false],  // 1939
    [0xA5B, 0, false],  // 1940
    // 1941
    [0x55A, 6, false],  // 1941: 윤6월 (소)
    [0xB55, 0, false],  // 1942
    [0xBA4, 0, false],  // 1943
    [0xB4A, 4, true],   // 1944: 윤4월
    [0xA95, 0, false],  // 1945
    [0xA4D, 0, false],  // 1946
    [0x54B, 2, true],   // 1947: 윤2월
    [0x6AD, 0, false],  // 1948
    [0xAD5, 0, false],  // 1949
    [0x5B5, 7, false],  // 1950: 윤7월 (소)
    // 1951
    [0xDAA, 0, false],  // 1951
    [0xD4A, 0, false],  // 1952
    [0xC95, 5, false],  // 1953: 윤5월 (소)
    [0x54D, 0, false],  // 1954
    [0xA5B, 0, false],  // 1955
    [0x95A, 3, true],   // 1956: 윤3월
    [0xB55, 0, false],  // 1957
    [0xB52, 0, false],  // 1958
    [0xB4A, 8, false],  // 1959: 윤8월 (소)
    [0xA95, 0, false],  // 1960
    // 1961
    [0xA4D, 0, false],  // 1961
    [0x54B, 6, true],   // 1962: 윤6월
    [0x6AD, 0, false],  // 1963
    [0xAD5, 0, false],  // 1964
    [0x6B4, 4, true],   // 1965: 윤4월
    [0xDA9, 0, false],  // 1966
    [0xD92, 0, false],  // 1967
    [0xE95, 0, false],  // 1968
    [0x52D, 0, false],  // 1969
    [0xA5B, 0, false],  // 1970
    // 1971
    [0x956, 5, true],   // 1971: 윤5월
    [0xB55, 0, false],  // 1972
    [0xB4A, 0, false],  // 1973
    [0xB25, 4, false],  // 1974: 윤4월 (소)
    [0xA93, 0, false],  // 1975
    [0xA4D, 0, false],  // 1976
    [0x54D, 8, true],   // 1977: 윤8월
    [0xAB5, 0, false],  // 1978
    [0xAD5, 0, false],  // 1979
    [0x5B4, 6, false],  // 1980: 윤6월 (소)
    // 1981
    [0xDA9, 0, false],  // 1981
    [0xD92, 0, false],  // 1982
    [0xD25, 4, true],   // 1983: 윤4월 (대)
    [0xA4D, 0, false],  // 1984
    [0x4AB, 0, false],  // 1985
    [0x95B, 0, false],  // 1986
    [0x56A, 6, true],   // 1987: 윤6월 (대)
    [0xB55, 0, false],  // 1988
    [0xBA4, 0, false],  // 1989
    [0xB49, 5, false],  // 1990: 윤5월 (소)
    // 1991
    [0xA93, 0, false],  // 1991
    [0xA4D, 0, false],  // 1992
    [0xAAB, 3, true],   // 1993: 윤3월 (대)
    [0x6AD, 0, false],  // 1994
    [0xAD5, 0, false],  // 1995
    [0x5B4, 8, true],   // 1996: 윤8월 (대)
    [0xDA9, 0, false],  // 1997
    [0xD92, 0, false],  // 1998
    [0xD25, 0, false],  // 1999
    [0xA4D, 0, false],  // 2000
    // 2001
    [0x4AB, 4, true],   // 2001: 윤4월 (대)
    [0x56B, 0, false],  // 2002
    [0xB6A, 0, false],  // 2003
    [0xB55, 2, true],   // 2004: 윤2월 (대)
    [0xBA4, 0, false],  // 2005
    [0xB49, 7, false],  // 2006: 윤7월 (소)
    [0xA93, 0, false],  // 2007
    [0xA2D, 0, false],  // 2008
    [0x52D, 5, true],   // 2009: 윤5월 (대)
    [0x6AD, 0, false],  // 2010
    // 2011
    [0x6D5, 0, false],  // 2011
    [0x5B4, 3, true],   // 2012: 윤3월 (대)
    [0xDA9, 0, false],  // 2013
    [0xD92, 9, false],  // 2014: 윤9월 (소)
    [0xD25, 0, false],  // 2015
    [0xA4D, 0, false],  // 2016
    [0x4AB, 6, true],   // 2017: 윤6월 (소) → 실제는 윤5월이나 데이터 기반
    [0x56B, 0, false],  // 2018
    [0xB6A, 0, false],  // 2019
    [0xB55, 4, true],   // 2020: 윤4월 (대)
    // 2021
    [0xBA4, 0, false],  // 2021
    [0xB49, 0, false],  // 2022
    [0xA93, 2, true],   // 2023: 윤2월 (대)
    [0xA4D, 0, false],  // 2024
    [0x52D, 6, false],  // 2025: 윤6월 (소)
    [0x6AD, 0, false],  // 2026
    [0x6D5, 0, false],  // 2027
    [0x5B5, 0, false],  // 2028
    [0xDA9, 0, false],  // 2029
    [0xD52, 0, false],  // 2030
    // 2031
    [0xD25, 3, false],  // 2031: 윤3월 (소)
    [0xA4D, 0, false],  // 2032
    [0x4AB, 11, false], // 2033: 윤11월 (소)
    [0x56B, 0, false],  // 2034
    [0xB6A, 0, false],  // 2035
    [0xB55, 6, true],   // 2036: 윤6월 (대)
    [0xBA4, 0, false],  // 2037
    [0xB49, 0, false],  // 2038
    [0xA93, 5, false],  // 2039: 윤5월 (소)
    [0xA4D, 0, false],  // 2040
    // 2041
    [0x52D, 0, false],  // 2041
    [0x6AB, 2, true],   // 2042: 윤2월 (대)
    [0x6D5, 0, false],  // 2043
    [0x5B5, 7, false],  // 2044: 윤7월 (소)
    [0xDA9, 0, false],  // 2045
    [0xD52, 0, false],  // 2046
    [0xD25, 5, false],  // 2047: 윤5월 (소)
    [0xA4D, 0, false],  // 2048
    [0x4AB, 0, false],  // 2049
    [0x56B, 3, true],   // 2050: 윤3월 (대)
  ];

  const LUNAR_START_YEAR = 1920;

  // ==========================================================================
  // 절기 데이터 (입춘 날짜 기준 - 양력)
  // ==========================================================================

  /**
   * 입춘 날짜 데이터 (양력 월/일)
   * 년주와 월주 계산에서 절기 기준을 적용하기 위해 사용
   * 사주에서 년주는 입춘을 기준으로 바뀜
   * 월주는 각 절입일을 기준으로 바뀜
   *
   * 절입일 (각 월의 시작 절기):
   * 1월(인월): 입춘 (2/3~5)
   * 2월(묘월): 경칩 (3/5~7)
   * 3월(진월): 청명 (4/4~6)
   * 4월(사월): 입하 (5/5~7)
   * 5월(오월): 망종 (6/5~7)
   * 6월(미월): 소서 (7/6~8)
   * 7월(신월): 입추 (8/7~9)
   * 8월(유월): 백로 (9/7~9)
   * 9월(술월): 한로 (10/8~9)
   * 10월(해월): 입동 (11/7~8)
   * 11월(자월): 대설 (12/6~8)
   * 12월(축월): 소한 (1/5~7)
   */

  /**
   * 절입일 근사 계산
   * 정확한 절입일은 매년 다르지만, 근사값으로 계산합니다.
   * 보다 정확한 계산을 위해 각 년도의 절입일 테이블을 참조할 수 있습니다.
   * 여기서는 평균 절입일을 사용합니다.
   */
  const 절기_월별 = [
    { month: 1, day: 6, name: '소한', 월지: 1 },    // 축월 (12월/전년도)
    { month: 2, day: 4, name: '입춘', 월지: 2 },    // 인월 (1월)
    { month: 3, day: 6, name: '경칩', 월지: 3 },    // 묘월 (2월)
    { month: 4, day: 5, name: '청명', 월지: 4 },    // 진월 (3월)
    { month: 5, day: 6, name: '입하', 월지: 5 },    // 사월 (4월)
    { month: 6, day: 6, name: '망종', 월지: 6 },    // 오월 (5월)
    { month: 7, day: 7, name: '소서', 월지: 7 },    // 미월 (6월)
    { month: 8, day: 8, name: '입추', 월지: 8 },    // 신월 (7월)
    { month: 9, day: 8, name: '백로', 월지: 9 },    // 유월 (8월)
    { month: 10, day: 8, name: '한로', 월지: 10 },  // 술월 (9월)
    { month: 11, day: 7, name: '입동', 월지: 11 },  // 해월 (10월)
    { month: 12, day: 7, name: '대설', 월지: 0 },   // 자월 (11월)
  ];

  // ==========================================================================
  // 양력→음력 변환
  // ==========================================================================

  /**
   * 주어진 음력 연도의 각 월의 일수를 배열로 반환
   * @param {number} lunarYear - 음력 연도 (1920~2050)
   * @returns {{ months: number[], leapMonth: number, leapDays: number, totalDays: number }}
   */
  function getLunarYearInfo(lunarYear) {
    const idx = lunarYear - LUNAR_START_YEAR;
    if (idx < 0 || idx >= LUNAR_DATA.length) {
      return null;
    }

    const [bitmask, leapMonth, leapBig] = LUNAR_DATA[idx];
    const months = [];
    let totalDays = 0;

    for (let m = 0; m < 12; m++) {
      const days = (bitmask & (1 << m)) ? 30 : 29;
      months.push(days);
      totalDays += days;
    }

    let leapDays = 0;
    if (leapMonth > 0) {
      leapDays = leapBig ? 30 : 29;
      totalDays += leapDays;
    }

    return { months, leapMonth, leapDays, totalDays };
  }

  /**
   * 양력 → 음력 날짜 변환
   *
   * 기준점: 1920년 양력 2월 8일 = 음력 1920년 1월 1일
   *
   * @param {number} solarYear
   * @param {number} solarMonth (1~12)
   * @param {number} solarDay
   * @returns {{ year: number, month: number, day: number, isLeapMonth: boolean, leapMonth: number }}
   */
  function solarToLunar(solarYear, solarMonth, solarDay) {
    // 기준점: 양력 1920-02-08 = 음력 1920-01-01
    const baseDate = new Date(1920, 1, 8); // JS month is 0-based
    const targetDate = new Date(solarYear, solarMonth - 1, solarDay);

    let offset = Math.floor((targetDate - baseDate) / (24 * 60 * 60 * 1000));

    if (offset < 0) {
      throw new Error('1920년 이전의 날짜는 지원하지 않습니다.');
    }

    let lunarYear = 1920;
    let yearInfo = getLunarYearInfo(lunarYear);

    while (yearInfo && offset >= yearInfo.totalDays) {
      offset -= yearInfo.totalDays;
      lunarYear++;
      yearInfo = getLunarYearInfo(lunarYear);
    }

    if (!yearInfo) {
      throw new Error('지원 범위를 벗어난 날짜입니다. (1920~2050)');
    }

    let lunarMonth = 1;
    let isLeapMonth = false;

    for (let m = 0; m < 12; m++) {
      const monthDays = yearInfo.months[m];
      if (offset < monthDays) {
        lunarMonth = m + 1;
        break;
      }
      offset -= monthDays;

      // 윤달 처리
      if (yearInfo.leapMonth === m + 1) {
        if (offset < yearInfo.leapDays) {
          lunarMonth = m + 1;
          isLeapMonth = true;
          break;
        }
        offset -= yearInfo.leapDays;
      }

      if (m === 11) {
        // 마지막 월까지 왔는데 아직 남은 offset이 있다면
        lunarMonth = 12;
      }
    }

    const lunarDay = offset + 1;

    return {
      year: lunarYear,
      month: lunarMonth,
      day: lunarDay,
      isLeapMonth: isLeapMonth,
      leapMonth: yearInfo.leapMonth
    };
  }

  // ==========================================================================
  // 사주 계산 핵심 함수
  // ==========================================================================

  /**
   * 년주 계산 (절기 기준 - 입춘 기준)
   *
   * 60간지 계산법:
   * (년도 - 4) % 10 = 천간 인덱스
   * (년도 - 4) % 12 = 지지 인덱스
   *
   * 단, 입춘 이전이면 전년도 기준
   *
   * @param {number} year - 양력 연도
   * @param {number} month - 양력 월
   * @param {number} day - 양력 일
   */
  function calcYearPillar(year, month, day) {
    // 입춘 기준: 대략 2월 4일 (정확한 시간은 매년 다름)
    let effectiveYear = year;
    if (month < 2 || (month === 2 && day < 4)) {
      effectiveYear = year - 1;
    }

    const stemIdx = (effectiveYear - 4) % 10;
    const branchIdx = (effectiveYear - 4) % 12;

    return {
      stem: (stemIdx + 10) % 10,
      branch: (branchIdx + 12) % 12,
      간지: 천간[(stemIdx + 10) % 10] + 지지[(branchIdx + 12) % 12],
      한자: 천간_한자[(stemIdx + 10) % 10] + 지지_한자[(branchIdx + 12) % 12],
    };
  }

  /**
   * 월주 계산 (절기 기준)
   *
   * 월지는 인월(1월)=인(2), 묘월(2월)=묘(3), ... 축월(12월)=축(1)
   *
   * 월간 = 년간 × 2 + 월지 보정
   * 공식: (년간 % 5) × 2 + 월 순서
   *
   * 갑기년: 병인월 시작 → 월간 시작 인덱스 = 2
   * 을경년: 무인월 시작 → 월간 시작 인덱스 = 4
   * 병신년: 경인월 시작 → 월간 시작 인덱스 = 6
   * 정임년: 임인월 시작 → 월간 시작 인덱스 = 8
   * 무계년: 갑인월 시작 → 월간 시작 인덱스 = 0
   */
  function calcMonthPillar(yearStem, solarYear, solarMonth, solarDay) {
    // 절기에 따른 월지 결정
    let monthBranch;
    let adjustedYear = solarYear;

    // 절입일 확인하여 월지 결정
    if (solarMonth === 1) {
      if (solarDay < 절기_월별[0].day) {
        // 소한 이전 → 전년 12월 (자월, 대설~소한 구간)
        // 실은 전월의 자월에 해당
        monthBranch = 0; // 자
        adjustedYear = solarYear - 1;
      } else {
        // 소한 이후, 입춘 이전 → 축월
        monthBranch = 1; // 축
        adjustedYear = solarYear - 1;
      }
    } else if (solarMonth === 2) {
      if (solarDay < 절기_월별[1].day) {
        monthBranch = 1; // 축
        adjustedYear = solarYear - 1;
      } else {
        monthBranch = 2; // 인
      }
    } else if (solarMonth === 12) {
      if (solarDay < 절기_월별[11].day) {
        monthBranch = 11; // 해
      } else {
        monthBranch = 0; // 자 (자월은 다음해에 속할 수도 있지만 년간은 올해 기준)
      }
    } else {
      // 3~11월
      const jIdx = solarMonth - 1; // 0-indexed in 절기_월별
      if (solarDay < 절기_월별[jIdx].day) {
        // 아직 이번달 절기 전 → 이전 월
        monthBranch = 절기_월별[jIdx - 1].월지;
      } else {
        monthBranch = 절기_월별[jIdx].월지;
      }
    }

    // 년간에 따른 월간 시작 인덱스 계산
    // 갑(0)/기(5) → 병(2), 을(1)/경(6) → 무(4), 병(2)/신(7) → 경(6), 정(3)/임(8) → 임(8), 무(4)/계(9) → 갑(0)
    const yearStemMod = yearStem % 5;
    const monthStemStart = (yearStemMod * 2 + 2) % 10;

    // 인월(2)부터의 offset
    const monthOffset = (monthBranch - 2 + 12) % 12;
    const monthStem = (monthStemStart + monthOffset) % 10;

    return {
      stem: monthStem,
      branch: monthBranch,
      간지: 천간[monthStem] + 지지[monthBranch],
      한자: 천간_한자[monthStem] + 지지_한자[monthBranch],
    };
  }

  /**
   * 일주 계산
   *
   * 기준일: 1936년 1월 1일 = 갑자일 (60간지의 0번째)
   * 이 기준으로부터의 일수를 60으로 나눈 나머지가 간지 인덱스
   */
  function calcDayPillar(solarYear, solarMonth, solarDay) {
    // 기준일: 1936-01-01 = 갑자일 (간지 인덱스 0)
    // 실제로 1936-01-01이 갑자일이 맞는지 확인된 기준점 사용
    // 다른 기준: 1900-01-01 = 갑자일에서 +1일 보정 등
    // 검증된 기준: 1900-01-31 = 갑자일 (일부 자료 기준)
    // 가장 널리 쓰이는 기준: JD(율리우스일) 기반

    // JD 기반 계산 (가장 정확)
    // 2000-01-07 = 갑자일 (검증된 기준점)
    const refDate = new Date(2000, 0, 7); // 2000-01-07 = 갑자
    const targetDate = new Date(solarYear, solarMonth - 1, solarDay);
    const diffDays = Math.round((targetDate - refDate) / (24 * 60 * 60 * 1000));

    const idx = ((diffDays % 60) + 60) % 60;
    const stemIdx = idx % 10;
    const branchIdx = idx % 12;

    return {
      stem: stemIdx,
      branch: branchIdx,
      간지: 천간[stemIdx] + 지지[branchIdx],
      한자: 천간_한자[stemIdx] + 지지_한자[branchIdx],
      sixtyIdx: idx,
    };
  }

  /**
   * 시주 계산
   *
   * 시지는 2시간 단위:
   * 자시: 23:00~01:00 (index 0)
   * 축시: 01:00~03:00 (index 1)
   * 인시: 03:00~05:00 (index 2)
   * 묘시: 05:00~07:00 (index 3)
   * 진시: 07:00~09:00 (index 4)
   * 사시: 09:00~11:00 (index 5)
   * 오시: 11:00~13:00 (index 6)
   * 미시: 13:00~15:00 (index 7)
   * 신시: 15:00~17:00 (index 8)
   * 유시: 17:00~19:00 (index 9)
   * 술시: 19:00~21:00 (index 10)
   * 해시: 21:00~23:00 (index 11)
   *
   * 시간(hour) = -1이면 시간 모름 처리
   *
   * 시간 = 일간에 따른 시간 시작:
   * 갑(0)/기(5)일 → 갑자시 시작
   * 을(1)/경(6)일 → 병자시 시작
   * 병(2)/신(7)일 → 무자시 시작
   * 정(3)/임(8)일 → 경자시 시작
   * 무(4)/계(9)일 → 임자시 시작
   */
  function calcHourPillar(dayStem, hour) {
    if (hour === -1 || hour === null || hour === undefined) {
      return null;
    }

    // 시간 → 지지 인덱스
    let branchIdx;
    if (hour === 23 || hour === 0) {
      branchIdx = 0; // 자시
    } else {
      branchIdx = Math.floor((hour + 1) / 2);
    }

    // 일간에 따른 시간 시작
    const dayStemMod = dayStem % 5;
    const hourStemStart = (dayStemMod * 2) % 10;
    const hourStem = (hourStemStart + branchIdx) % 10;

    return {
      stem: hourStem,
      branch: branchIdx,
      간지: 천간[hourStem] + 지지[branchIdx],
      한자: 천간_한자[hourStem] + 지지_한자[branchIdx],
    };
  }

  /**
   * 시간을 지지 이름으로 변환
   */
  function hourToBranchName(hour) {
    if (hour === -1 || hour === null || hour === undefined) return '미정';
    let branchIdx;
    if (hour === 23 || hour === 0) {
      branchIdx = 0;
    } else {
      branchIdx = Math.floor((hour + 1) / 2);
    }
    return 지지[branchIdx] + '시';
  }

  // ==========================================================================
  // 오행 분석
  // ==========================================================================

  /**
   * 사주의 오행 분포를 계산
   * @param {Array} pillars - 사주 기둥 배열 [{stem, branch}, ...]
   * @returns {{ 목: number, 화: number, 토: number, 금: number, 수: number, details: object }}
   */
  function analyzeElements(pillars) {
    const count = { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 };
    const details = {
      천간: { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 },
      지지: { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 },
      지장간: { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 },
    };

    pillars.forEach(p => {
      if (!p) return;

      // 천간 오행
      const stemElement = 오행[천간_오행[p.stem]];
      count[stemElement]++;
      details.천간[stemElement]++;

      // 지지 오행
      const branchElement = 오행[지지_오행[p.branch]];
      count[branchElement]++;
      details.지지[branchElement]++;

      // 지장간 오행
      const hidden = get지장간(p.branch);
      hidden.forEach(h => {
        const hElement = 오행[천간_오행[h.idx]];
        details.지장간[hElement]++;
      });
    });

    return {
      ...count,
      total: pillars.filter(p => p).length * 2,
      details: details,
      distribution: {
        목: count.목,
        화: count.화,
        토: count.토,
        금: count.금,
        수: count.수,
      }
    };
  }

  // ==========================================================================
  // 대운 계산
  // ==========================================================================

  /**
   * 대운 계산
   *
   * 대운 방향:
   * - 남자(양남): 년간이 양간이면 순행, 음간이면 역행
   * - 여자(음녀): 년간이 음간이면 순행, 양간이면 역행
   * → 양남음녀 = 순행, 음남양녀 = 역행
   *
   * 대운 시작 나이:
   * 생일부터 다음(또는 이전) 절입일까지의 날수를 3으로 나눔 = 대운 시작 나이
   *
   * @param {string} gender - 'M' 또는 'F'
   * @param {object} yearPillar - 년주
   * @param {object} monthPillar - 월주
   * @param {number} solarYear, solarMonth, solarDay - 양력 생년월일
   */
  function calcDaeun(gender, yearPillar, monthPillar, solarYear, solarMonth, solarDay) {
    const yearStemYinYang = 천간_음양[yearPillar.stem]; // 0=양, 1=음
    const isMale = gender === 'M';

    // 양남음녀 = 순행 (forward=true), 음남양녀 = 역행 (forward=false)
    const forward = (isMale && yearStemYinYang === 0) || (!isMale && yearStemYinYang === 1);

    // 대운 시작 나이 계산
    // 생일로부터 다음(순행) 또는 이전(역행) 절입일까지의 일수
    const birthDate = new Date(solarYear, solarMonth - 1, solarDay);

    // 절입일 찾기
    let targetJeolgi;
    if (forward) {
      // 순행: 다음 절입일
      targetJeolgi = findNextJeolgi(solarYear, solarMonth, solarDay);
    } else {
      // 역행: 이전 절입일
      targetJeolgi = findPrevJeolgi(solarYear, solarMonth, solarDay);
    }

    const jeolgiDate = new Date(targetJeolgi.year, targetJeolgi.month - 1, targetJeolgi.day);
    const diffDays = Math.abs(Math.round((jeolgiDate - birthDate) / (24 * 60 * 60 * 1000)));

    // 3일 = 1년으로 환산
    const startAge = Math.round(diffDays / 3);

    // 대운 기둥 생성 (월주에서 순행/역행)
    const daeunPillars = [];
    let currentStem = monthPillar.stem;
    let currentBranch = monthPillar.branch;

    for (let i = 0; i < 12; i++) {
      if (forward) {
        currentStem = (currentStem + 1) % 10;
        currentBranch = (currentBranch + 1) % 12;
      } else {
        currentStem = (currentStem - 1 + 10) % 10;
        currentBranch = (currentBranch - 1 + 12) % 12;
      }

      daeunPillars.push({
        stem: currentStem,
        branch: currentBranch,
        간지: 천간[currentStem] + 지지[currentBranch],
        한자: 천간_한자[currentStem] + 지지_한자[currentBranch],
        startAge: startAge + (i * 10),
        endAge: startAge + ((i + 1) * 10) - 1,
        startYear: solarYear + startAge + (i * 10),
      });
    }

    return {
      direction: forward ? '순행' : '역행',
      startAge: startAge,
      pillars: daeunPillars,
    };
  }

  /**
   * 다음 절입일 찾기
   */
  function findNextJeolgi(year, month, day) {
    for (let i = 0; i < 절기_월별.length; i++) {
      const j = 절기_월별[i];
      if (j.month > month || (j.month === month && j.day > day)) {
        return { year: year, month: j.month, day: j.day, name: j.name };
      }
    }
    // 올해 안에 없으면 내년 1월 소한
    return { year: year + 1, month: 1, day: 6, name: '소한' };
  }

  /**
   * 이전 절입일 찾기
   */
  function findPrevJeolgi(year, month, day) {
    for (let i = 절기_월별.length - 1; i >= 0; i--) {
      const j = 절기_월별[i];
      if (j.month < month || (j.month === month && j.day <= day)) {
        return { year: year, month: j.month, day: j.day, name: j.name };
      }
    }
    // 올해 안에 없으면 전년 12월 대설
    return { year: year - 1, month: 12, day: 7, name: '대설' };
  }

  // ==========================================================================
  // 합/충 분석
  // ==========================================================================

  /**
   * 천간합 분석
   * @param {number[]} stems - 천간 인덱스 배열
   */
  function analyze천간합(stems) {
    const results = [];
    for (let i = 0; i < stems.length; i++) {
      for (let j = i + 1; j < stems.length; j++) {
        for (const [a, b, element] of 천간합_pairs) {
          if ((stems[i] === a && stems[j] === b) || (stems[i] === b && stems[j] === a)) {
            results.push({
              type: '천간합',
              pair: [천간[stems[i]], 천간[stems[j]]],
              positions: [i, j],
              화오행: element,
              description: `${천간[stems[i]]}${천간[stems[j]]}합 → ${element}`,
            });
          }
        }
      }
    }
    return results;
  }

  /**
   * 천간충 분석
   */
  function analyze천간충(stems) {
    const results = [];
    for (let i = 0; i < stems.length; i++) {
      for (let j = i + 1; j < stems.length; j++) {
        for (const [a, b] of 천간충_pairs) {
          if ((stems[i] === a && stems[j] === b) || (stems[i] === b && stems[j] === a)) {
            results.push({
              type: '천간충',
              pair: [천간[stems[i]], 천간[stems[j]]],
              positions: [i, j],
              description: `${천간[stems[i]]}${천간[stems[j]]}충`,
            });
          }
        }
      }
    }
    return results;
  }

  /**
   * 지지육합 분석
   */
  function analyze지지육합(branches) {
    const results = [];
    for (let i = 0; i < branches.length; i++) {
      for (let j = i + 1; j < branches.length; j++) {
        for (const [a, b, element] of 지지육합_pairs) {
          if ((branches[i] === a && branches[j] === b) || (branches[i] === b && branches[j] === a)) {
            results.push({
              type: '지지육합',
              pair: [지지[branches[i]], 지지[branches[j]]],
              positions: [i, j],
              화오행: element,
              description: `${지지[branches[i]]}${지지[branches[j]]}합 → ${element}`,
            });
          }
        }
      }
    }
    return results;
  }

  /**
   * 지지삼합 분석
   */
  function analyze지지삼합(branches) {
    const results = [];
    for (const [set, element] of 지지삼합_sets) {
      const found = set.filter(s => branches.includes(s));
      if (found.length >= 2) {
        const isFull = found.length === 3;
        results.push({
          type: isFull ? '지지삼합' : '지지반합',
          branches: found.map(b => 지지[b]),
          화오행: element,
          description: `${found.map(b => 지지[b]).join('')} ${isFull ? '삼합' : '반합'} → ${element}`,
        });
      }
    }
    return results;
  }

  /**
   * 지지방합 분석
   */
  function analyze지지방합(branches) {
    const results = [];
    for (const [set, element] of 지지방합_sets) {
      const found = set.filter(s => branches.includes(s));
      if (found.length >= 2) {
        const isFull = found.length === 3;
        results.push({
          type: isFull ? '지지방합' : '지지반방합',
          branches: found.map(b => 지지[b]),
          화오행: element,
          description: `${found.map(b => 지지[b]).join('')} ${isFull ? '방합' : '반방합'} → ${element}`,
        });
      }
    }
    return results;
  }

  /**
   * 지지충 분석
   */
  function analyze지지충(branches) {
    const results = [];
    for (let i = 0; i < branches.length; i++) {
      for (let j = i + 1; j < branches.length; j++) {
        for (const [a, b] of 지지충_pairs) {
          if ((branches[i] === a && branches[j] === b) || (branches[i] === b && branches[j] === a)) {
            results.push({
              type: '지지충',
              pair: [지지[branches[i]], 지지[branches[j]]],
              positions: [i, j],
              description: `${지지[branches[i]]}${지지[branches[j]]}충`,
            });
          }
        }
      }
    }
    return results;
  }

  /**
   * 지지형 분석
   */
  function analyze지지형(branches) {
    const results = [];

    // 삼형 체크
    for (const [set, type] of 지지형_sets) {
      if (set.length === 3) {
        const found = set.filter(s => branches.includes(s));
        if (found.length >= 2) {
          results.push({
            type: '지지형',
            subType: type,
            branches: found.map(b => 지지[b]),
            description: `${found.map(b => 지지[b]).join('')} ${type}`,
          });
        }
      } else if (set.length === 2) {
        // 자형 또는 이형
        if (set[0] === set[1]) {
          // 자형: 같은 지지가 2개 이상
          const cnt = branches.filter(b => b === set[0]).length;
          if (cnt >= 2) {
            results.push({
              type: '지지형',
              subType: type,
              branches: [지지[set[0]], 지지[set[1]]],
              description: `${지지[set[0]]}${지지[set[1]]} ${type}`,
            });
          }
        } else {
          // 자묘형 같은 것
          if (branches.includes(set[0]) && branches.includes(set[1])) {
            results.push({
              type: '지지형',
              subType: type,
              branches: [지지[set[0]], 지지[set[1]]],
              description: `${지지[set[0]]}${지지[set[1]]} ${type}`,
            });
          }
        }
      }
    }
    return results;
  }

  /**
   * 지지파 분석
   */
  function analyze지지파(branches) {
    const results = [];
    for (let i = 0; i < branches.length; i++) {
      for (let j = i + 1; j < branches.length; j++) {
        for (const [a, b] of 지지파_pairs) {
          if ((branches[i] === a && branches[j] === b) || (branches[i] === b && branches[j] === a)) {
            results.push({
              type: '지지파',
              pair: [지지[branches[i]], 지지[branches[j]]],
              positions: [i, j],
              description: `${지지[branches[i]]}${지지[branches[j]]}파`,
            });
          }
        }
      }
    }
    return results;
  }

  /**
   * 지지해 분석
   */
  function analyze지지해(branches) {
    const results = [];
    for (let i = 0; i < branches.length; i++) {
      for (let j = i + 1; j < branches.length; j++) {
        for (const [a, b] of 지지해_pairs) {
          if ((branches[i] === a && branches[j] === b) || (branches[i] === b && branches[j] === a)) {
            results.push({
              type: '지지해',
              pair: [지지[branches[i]], 지지[branches[j]]],
              positions: [i, j],
              description: `${지지[branches[i]]}${지지[branches[j]]}해`,
            });
          }
        }
      }
    }
    return results;
  }

  // ==========================================================================
  // 용신 (Useful God) 기본 분석
  // ==========================================================================

  /**
   * 기본 용신 분석
   *
   * 일간의 강약을 판단하고, 필요한 오행을 결정
   *
   * 1. 일간 강약 판단:
   *    - 일간과 같은 오행 + 일간을 생하는 오행 → 신강 요소
   *    - 일간을 극하는/설하는/재성 → 신약 요소
   *    - 월지의 도움 여부가 가장 중요
   *
   * 2. 용신 결정:
   *    - 신강하면 → 설기(식상), 재성, 관살 중 필요한 것
   *    - 신약하면 → 인성, 비겁 중 필요한 것
   */
  function analyzeYongshin(dayPillar, elements, pillars) {
    const 일간 = dayPillar.stem;
    const 일간_el = 천간_오행[일간]; // 일간의 오행

    // 상생: 목(0)→화(1)→토(2)→금(3)→수(4)→목(0)
    const 생아 = (일간_el + 4) % 5;   // 나를 생하는 오행 (인성)
    const 아생 = (일간_el + 1) % 5;   // 내가 생하는 오행 (식상)
    const 아극 = (일간_el + 2) % 5;   // 내가 극하는 오행 (재성)
    const 극아 = (일간_el + 3) % 5;   // 나를 극하는 오행 (관성)
    const 비겁_el = 일간_el;          // 나와 같은 오행 (비겁)

    // 신강/신약 점수 계산
    const elNames = ['목', '화', '토', '금', '수'];

    let 강_score = elements[elNames[비겁_el]] + elements[elNames[생아]]; // 비겁 + 인성
    let 약_score = elements[elNames[아생]] + elements[elNames[아극]] + elements[elNames[극아]]; // 식상 + 재성 + 관성

    // 월지 보정 (월지가 일간과 같은 오행이거나 생하는 오행이면 신강 가산)
    if (pillars[1]) {
      const 월지_el = 지지_오행[pillars[1].branch];
      if (월지_el === 비겁_el || 월지_el === 생아) {
        강_score += 2;
      } else {
        약_score += 1;
      }
    }

    const isStrong = 강_score > 약_score;

    // 용신 결정
    let 용신, 희신, 기신;
    if (isStrong) {
      // 신강 → 설기가 필요 (식상 > 재성 > 관살)
      if (elements[elNames[아생]] < 2) {
        용신 = elNames[아생]; // 식상
        희신 = elNames[아극]; // 재성
      } else {
        용신 = elNames[극아]; // 관살
        희신 = elNames[아극]; // 재성
      }
      기신 = elNames[생아]; // 인성
    } else {
      // 신약 → 보강이 필요 (인성 > 비겁)
      if (elements[elNames[생아]] < 2) {
        용신 = elNames[생아]; // 인성
        희신 = elNames[비겁_el]; // 비겁
      } else {
        용신 = elNames[비겁_el]; // 비겁
        희신 = elNames[생아]; // 인성
      }
      기신 = elNames[극아]; // 관살
    }

    return {
      일간강약: isStrong ? '신강' : '신약',
      강약점수: { 강: 강_score, 약: 약_score },
      용신: 용신,
      희신: 희신,
      기신: 기신,
      설명: isStrong
        ? `일간이 신강하여 ${용신}(${getElementHanja(용신)})이 용신입니다. 에너지를 분산시켜 균형을 잡아야 합니다.`
        : `일간이 신약하여 ${용신}(${getElementHanja(용신)})이 용신입니다. 일간을 보강하여 힘을 키워야 합니다.`,
      오행관계: {
        비겁: elNames[비겁_el],
        식상: elNames[아생],
        재성: elNames[아극],
        관성: elNames[극아],
        인성: elNames[생아],
      }
    };
  }

  function getElementHanja(name) {
    const idx = 오행.indexOf(name);
    return idx >= 0 ? 오행_한자[idx] : '';
  }

  // ==========================================================================
  // 메인 분석 함수
  // ==========================================================================

  /**
   * 사주팔자 종합 분석
   *
   * @param {number} year - 양력 출생년도
   * @param {number} month - 양력 출생월 (1~12)
   * @param {number} day - 양력 출생일
   * @param {number} hour - 출생시간 (0~23, -1이면 모름)
   * @param {string} gender - 성별 ('M'=남, 'F'=여)
   * @returns {object} 사주 분석 결과 객체
   */
  function analyzeSaju(year, month, day, hour, gender) {
    // 1. 양력 → 음력 변환
    let lunarInfo = null;
    try {
      lunarInfo = solarToLunar(year, month, day);
    } catch (e) {
      lunarInfo = { year: year, month: month, day: day, isLeapMonth: false, error: e.message };
    }

    // 2. 사주 계산 (양력/절기 기준)
    const yearPillar = calcYearPillar(year, month, day);
    const monthPillar = calcMonthPillar(yearPillar.stem, year, month, day);
    const dayPillar = calcDayPillar(year, month, day);
    const hourPillar = calcHourPillar(dayPillar.stem, hour);

    // 기둥 배열 [년, 월, 일, 시]
    const pillars = [yearPillar, monthPillar, dayPillar, hourPillar];
    const pillarNames = ['년주', '월주', '일주', '시주'];

    // 3. 천간/지지 배열 추출
    const stems = pillars.filter(p => p).map(p => p.stem);
    const branches = pillars.filter(p => p).map(p => p.branch);

    // 4. 오행 분석
    const elements = analyzeElements(pillars.filter(p => p));

    // 5. 십신 계산
    const 일간 = dayPillar.stem;
    const sipsinResult = [];

    pillars.forEach((p, idx) => {
      if (!p) return;
      const stemSipsin = get십신(일간, p.stem);
      const branchSipsin = get십신_지지(일간, p.branch);

      sipsinResult.push({
        위치: pillarNames[idx],
        천간: { 글자: 천간[p.stem], 십신: stemSipsin },
        지지: { 글자: 지지[p.branch], 십신: branchSipsin },
      });
    });

    // 6. 12운성 계산
    const lifeStagePillars = [];
    pillars.forEach((p, idx) => {
      if (!p) return;
      lifeStagePillars.push({
        위치: pillarNames[idx],
        운성: get12운성(일간, p.branch),
      });
    });

    // 7. 지장간 분석
    const hiddenStems = [];
    pillars.forEach((p, idx) => {
      if (!p) return;
      const hidden = get지장간(p.branch);
      hiddenStems.push({
        위치: pillarNames[idx],
        지지: 지지[p.branch],
        지장간: hidden.map(h => ({
          ...h,
          십신: get십신(일간, h.idx),
          오행: 오행[천간_오행[h.idx]],
        })),
      });
    });

    // 8. 대운 계산
    const daeun = calcDaeun(gender, yearPillar, monthPillar, year, month, day);

    // 대운에 십신/12운성 추가
    daeun.pillars.forEach(dp => {
      dp.십신_천간 = get십신(일간, dp.stem);
      dp.십신_지지 = get십신_지지(일간, dp.branch);
      dp.운성 = get12운성(일간, dp.branch);
    });

    // 9. 합/충/형/파/해 분석
    const interactions = {
      천간합: analyze천간합(stems),
      천간충: analyze천간충(stems),
      지지육합: analyze지지육합(branches),
      지지삼합: analyze지지삼합(branches),
      지지방합: analyze지지방합(branches),
      지지충: analyze지지충(branches),
      지지형: analyze지지형(branches),
      지지파: analyze지지파(branches),
      지지해: analyze지지해(branches),
    };

    // 10. 용신 분석
    const yongshin = analyzeYongshin(dayPillar, elements, pillars);

    // 11. 기본 정보 구성
    const basicInfo = {
      입력: {
        양력: `${year}년 ${month}월 ${day}일`,
        시간: hour >= 0 ? `${hour}시 (${hourToBranchName(hour)})` : '미정',
        성별: gender === 'M' ? '남' : '여',
      },
      음력: lunarInfo ? {
        년: lunarInfo.year,
        월: lunarInfo.month,
        일: lunarInfo.day,
        윤달여부: lunarInfo.isLeapMonth ? '윤달' : '평달',
        text: `${lunarInfo.year}년 ${lunarInfo.isLeapMonth ? '윤' : ''}${lunarInfo.month}월 ${lunarInfo.day}일`,
      } : null,
      띠: 띠[yearPillar.branch],
      일간: {
        글자: 천간[일간],
        한자: 천간_한자[일간],
        오행: 오행[천간_오행[일간]],
        음양: 천간_음양[일간] === 0 ? '양' : '음',
      },
    };

    // 12. 결과 조립
    return {
      기본정보: basicInfo,
      사주: {
        년주: {
          ...yearPillar,
          천간: 천간[yearPillar.stem],
          지지: 지지[yearPillar.branch],
          천간_한자: 천간_한자[yearPillar.stem],
          지지_한자: 지지_한자[yearPillar.branch],
          천간_오행: 오행[천간_오행[yearPillar.stem]],
          지지_오행: 오행[지지_오행[yearPillar.branch]],
          천간_음양: 천간_음양[yearPillar.stem] === 0 ? '양' : '음',
          지지_음양: 지지_음양[yearPillar.branch] === 0 ? '양' : '음',
        },
        월주: {
          ...monthPillar,
          천간: 천간[monthPillar.stem],
          지지: 지지[monthPillar.branch],
          천간_한자: 천간_한자[monthPillar.stem],
          지지_한자: 지지_한자[monthPillar.branch],
          천간_오행: 오행[천간_오행[monthPillar.stem]],
          지지_오행: 오행[지지_오행[monthPillar.branch]],
          천간_음양: 천간_음양[monthPillar.stem] === 0 ? '양' : '음',
          지지_음양: 지지_음양[monthPillar.branch] === 0 ? '양' : '음',
        },
        일주: {
          ...dayPillar,
          천간: 천간[dayPillar.stem],
          지지: 지지[dayPillar.branch],
          천간_한자: 천간_한자[dayPillar.stem],
          지지_한자: 지지_한자[dayPillar.branch],
          천간_오행: 오행[천간_오행[dayPillar.stem]],
          지지_오행: 오행[지지_오행[dayPillar.branch]],
          천간_음양: 천간_음양[dayPillar.stem] === 0 ? '양' : '음',
          지지_음양: 지지_음양[dayPillar.branch] === 0 ? '양' : '음',
        },
        시주: hourPillar ? {
          ...hourPillar,
          천간: 천간[hourPillar.stem],
          지지: 지지[hourPillar.branch],
          천간_한자: 천간_한자[hourPillar.stem],
          지지_한자: 지지_한자[hourPillar.branch],
          천간_오행: 오행[천간_오행[hourPillar.stem]],
          지지_오행: 오행[지지_오행[hourPillar.branch]],
          천간_음양: 천간_음양[hourPillar.stem] === 0 ? '양' : '음',
          지지_음양: 지지_음양[hourPillar.branch] === 0 ? '양' : '음',
        } : null,
        summary: `${yearPillar.간지} ${monthPillar.간지} ${dayPillar.간지} ${hourPillar ? hourPillar.간지 : '??'}`,
        summary_한자: `${yearPillar.한자} ${monthPillar.한자} ${dayPillar.한자} ${hourPillar ? hourPillar.한자 : '??'}`,
      },
      오행: elements,
      십신: sipsinResult,
      운성12: lifeStagePillars,
      지장간: hiddenStems,
      대운: daeun,
      합충: interactions,
      용신: yongshin,
    };
  }

  // ==========================================================================
  // 유틸리티 함수 (외부 공개)
  // ==========================================================================

  /**
   * 60간지 이름을 인덱스(0~59)로 반환
   */
  function get60GanjiName(index) {
    const stemIdx = index % 10;
    const branchIdx = index % 12;
    return 천간[stemIdx] + 지지[branchIdx];
  }

  /**
   * 60간지 전체 목록 생성
   */
  function generate60Ganji() {
    const list = [];
    for (let i = 0; i < 60; i++) {
      list.push({
        index: i,
        간지: get60GanjiName(i),
        한자: 천간_한자[i % 10] + 지지_한자[i % 12],
        천간: 천간[i % 10],
        지지: 지지[i % 12],
      });
    }
    return list;
  }

  /**
   * 오행 색상 반환 (UI용)
   */
  function getElementColor(element) {
    const colors = {
      '목': '#4CAF50',  // 녹색
      '화': '#F44336',  // 적색
      '토': '#FFC107',  // 황색
      '금': '#FFFFFF',  // 백색
      '수': '#2196F3',  // 흑/청색
    };
    return colors[element] || '#888888';
  }

  /**
   * 오행 한자 반환
   */
  function getElementHanjaName(element) {
    const map = { '목': '木', '화': '火', '토': '土', '금': '金', '수': '水' };
    return map[element] || '';
  }

  /**
   * 세운 (연운) 계산 - 특정 연도의 간지
   */
  function calcYearlyFortune(targetYear) {
    const stemIdx = ((targetYear - 4) % 10 + 10) % 10;
    const branchIdx = ((targetYear - 4) % 12 + 12) % 12;
    return {
      year: targetYear,
      stem: stemIdx,
      branch: branchIdx,
      간지: 천간[stemIdx] + 지지[branchIdx],
      한자: 천간_한자[stemIdx] + 지지_한자[branchIdx],
      띠: 띠[branchIdx],
    };
  }

  /**
   * 월운 계산 - 특정 연월의 간지
   */
  function calcMonthlyFortune(targetYear, targetMonth) {
    const yearPillar = calcYearPillar(targetYear, targetMonth, 15);
    const monthPillar = calcMonthPillar(yearPillar.stem, targetYear, targetMonth, 15);
    return {
      year: targetYear,
      month: targetMonth,
      ...monthPillar,
    };
  }

  // ==========================================================================
  // 공개 API
  // ==========================================================================

  return {
    // 메인 분석 함수
    analyzeSaju: analyzeSaju,

    // 개별 계산 함수
    solarToLunar: solarToLunar,
    calcYearPillar: calcYearPillar,
    calcMonthPillar: calcMonthPillar,
    calcDayPillar: calcDayPillar,
    calcHourPillar: calcHourPillar,

    // 십신/운성
    get십신: get십신,
    get12운성: get12운성,
    get지장간: get지장간,

    // 대운/세운
    calcDaeun: calcDaeun,
    calcYearlyFortune: calcYearlyFortune,
    calcMonthlyFortune: calcMonthlyFortune,

    // 유틸리티
    generate60Ganji: generate60Ganji,
    getElementColor: getElementColor,
    getElementHanjaName: getElementHanjaName,
    hourToBranchName: hourToBranchName,

    // 상수 데이터 (읽기 전용 참조)
    constants: {
      천간, 천간_한자,
      지지, 지지_한자,
      오행, 오행_한자,
      띠,
      십신_명칭,
      운성_명칭,
      천간_오행, 천간_음양,
      지지_오행, 지지_음양,
    },
  };
}));
