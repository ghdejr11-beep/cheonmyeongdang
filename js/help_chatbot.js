/* 천명당 도움말 챗봇 (FAQ 매칭, AI 호출 X, 비용 0)
   사용자 헷갈림 해결 → 결제 conversion ↑ */

(function() {
  if (window._cmHelpBotLoaded) return;
  window._cmHelpBotLoaded = true;

  // FAQ 30개 — 키워드 매칭 기반
  var FAQ = [
    {
      q: '쿠폰', kw: ['쿠폰', 'coupon', 'KSAJU', '코드', '활성화'],
      a: '<b>쿠폰 사용 방법</b><br>1. 사이트 우상단 "쿠폰 입력" 버튼 클릭<br>2. 코드 (예: KSAJU-XXXXX-XXXXXX) + 본인 이메일 입력<br>3. 매직링크 메일 발송 → 메일에서 "쿠폰 등록" 1클릭<br>4. 30일 무료 구독 즉시 활성화<br><br>안내: 메일 안 오면 스팸함 확인 + 30분 안에 클릭 (만료 30분)'
    },
    {
      q: '결제 후 결과', kw: ['결제 후', '결제했는데', '풀이 보기', '결과', '안 보여', '안보여', '못 봐', '못봐'],
      a: '<b>결제 후 결과 보는 방법</b><br>결제 완료 페이지에서 "사주 풀이 보기" 또는 "결과 보기" 클릭하면 자동 이동.<br><br>이미 닫으셨다면:<br>1. <a href="/?view_saju=1#saju-result" style="color:var(--gold2);">여기 클릭</a> → 자동 채움 + 잠금 해제<br>2. 또는 메인에서 사주 분석 다시 → 같은 이메일 입력 시 자동 권한 인식'
    },
    {
      q: 'PDF 다운', kw: ['pdf', '다운', 'download', '30페이지', '30p'],
      a: '<b>PDF 30페이지 다운로드</b><br>1. 사주 분석 결과 페이지 맨 아래 스크롤<br>2. <b>"PDF 30페이지 다운로드"</b> 황금색 버튼 클릭<br>3. 10-30초 소요 → 다운로드 폴더에 자동 저장<br>파일명: <code>천명당_사주풀이_{이름}_{날짜}.pdf</code><br><br>안내: 프리미엄 결제자만 가능 (₩9,900~)'
    },
    {
      q: '광고', kw: ['광고', 'ad', '광고 보기', '결제했는데 광고'],
      a: '<b>광고 뜨는 이유</b><br>유료 결제자에게는 광고 안 뜸. 만약 결제했는데도 광고가 뜨면:<br>1. <b>같은 이메일</b>로 사주 분석 다시 (다른 이메일 사용 시 권한 인식 X)<br>2. 페이지 새로고침 (Ctrl+Shift+R)<br>3. 그래도 뜨면 챗봇에 "환불" 입력 → 자동 환불 안내'
    },
    {
      q: '매직링크', kw: ['매직링크', 'magic', '메일 안', '이메일 안', '링크 안'],
      a: '<b>매직링크 안 올 때</b><br>1. <b>스팸함 확인</b> (가장 흔한 원인)<br>2. 발송 메일 주소 = <code>noreply@cheonmyeongdang.com</code> (스팸 해제 후 추가)<br>3. 5분 기다려도 안 오면 → 챗봇에 "재발송" 입력<br>4. <b>30분 이내</b> 클릭 (이후 만료, 다시 발급)'
    },
    {
      q: '환불', kw: ['환불', 'refund', '취소'],
      a: '<b>환불 정책</b><br>• 디지털 콘텐츠 특성상 <b>결제 즉시 사용 가능</b>해서 단순 변심 환불 X<br>• 시스템 오류 / 중복결제 / 결과 미수신: <b>100% 환불</b><br><br>환불 신청: support@cheonmyeongdang.com 또는 챗봇에 "환불 요청" + 주문번호 (CMD-XXXX) 입력<br>(처리 1-3 영업일)'
    },
    {
      q: '다른 기기', kw: ['다른 기기', '다른 폰', '다른 컴퓨터', '컴퓨터에서', '폰에서'],
      a: '<b>다른 기기에서 사주 보기</b><br>이미 결제했으면 다른 기기에서도 무료 OK!<br>1. <a href="/restore.html" style="color:var(--gold2);">이전 구매 복원 페이지</a> 접속<br>2. 결제 시 사용한 <b>이메일 입력</b><br>3. 권한 자동 적용 (비밀번호 X)'
    },
    {
      q: '월회원', kw: ['월회원', '구독', '종합풀이', '차이', 'subscription'],
      a: '<b>월회원 vs 종합풀이</b><br><b>월회원 (₩29,900/월)</b>: 매월 자동 결제, 매월 새 운세 PDF, 무제한 AI Q&A<br><b>종합풀이 (₩29,900 1회)</b>: 평생 한 번 결제, 사주+궁합+심층 가이드 묶음 PDF<br><b>사주 정밀 풀이 (₩9,900 1회)</b>: 직업·재물·건강·인연 상세 PDF<br><br>처음이라면 <b>사주 정밀 풀이 ₩9,900</b> 추천'
    },
    {
      q: '결제 안전', kw: ['결제 안전', '안전한가', '카드정보', '보안'],
      a: '<b>결제 안전성</b><br>• <b>토스페이먼츠</b> + <b>PayPal Smart Buttons</b> (글로벌 PCI-DSS Level 1)<br>• 카드정보 천명당 서버에 X (PG사가 직접 처리)<br>• HTTPS + 매직링크 비밀번호리스 인증<br>• 사업자 552-59-00848 (쿤스튜디오)'
    },
    {
      q: '사용 방법', kw: ['어떻게', '사용 방법', '시작', '처음', '뭐부터'],
      a: '<b>천명당 시작하기</b><br>1. 메인 화면 "사주 분석" 폼에 생년월일·시간·성별 입력<br>2. "사주 분석하기" 클릭 → 무료 기본 풀이 (잠금 부분 있음)<br>3. 정밀 분석 보려면 <b>₩9,900 결제</b> 또는 30일 무료 쿠폰 사용<br>4. 결제 후 PDF 30페이지 다운로드 가능<br><br>추천: <b>FLASH507 50% 할인 코드</b> 적용해서 절반 가격으로!'
    },
    {
      q: '연락처', kw: ['연락', '문의', '고객센터', '이메일', 'support'],
      a: '<b>고객 지원</b><br>• 이메일: <code>support@cheonmyeongdang.com</code><br>• 평일 9~18시 응답 (1-3 영업일)<br>• 결제 / 환불 / 권한 문제는 <b>주문번호 (CMD-XXXX) 포함</b>해서 메일'
    },
    {
      q: '회원가입', kw: ['회원가입', '가입', '계정', '비밀번호', 'password'],
      a: '<b>회원가입 X — 비밀번호 없음</b><br>천명당은 <b>매직링크</b> 방식이라 가입 X.<br>이메일만 입력 → 메일에서 1클릭 인증.<br>다른 기기에서 보려면 같은 이메일만 입력하면 자동 권한 인식.'
    },
  ];

  function findAnswer(query) {
    var q = query.trim().toLowerCase().replace(/[?.,!]/g, '');
    if (!q) return null;
    var bestMatch = null;
    var bestScore = 0;
    FAQ.forEach(function(item) {
      var score = 0;
      item.kw.forEach(function(k) {
        if (q.indexOf(k.toLowerCase()) >= 0) score += k.length;
      });
      if (score > bestScore) {
        bestScore = score;
        bestMatch = item;
      }
    });
    return bestMatch;
  }

  // CSS
  var style = document.createElement('style');
  style.textContent = ''
    + '#cm-helpbot-toggle{position:fixed;bottom:24px;right:24px;width:60px;height:60px;border-radius:30px;background:linear-gradient(135deg,var(--gold,#c9a84c),var(--gold2,#e0c060));border:none;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,0.3);z-index:9998;font-family:"Noto Serif KR",serif;font-size:24px;font-weight:800;display:flex;align-items:center;justify-content:center;color:#0a0d18;transition:transform 0.2s;}'
    + '#cm-helpbot-toggle:hover{transform:scale(1.08);}'
    + '#cm-helpbot-panel{position:fixed;bottom:96px;right:24px;width:360px;max-width:calc(100vw - 32px);max-height:540px;background:var(--card,#0d1020);border:1px solid var(--gold,#c9a84c);border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,0.5);z-index:9999;display:none;flex-direction:column;overflow:hidden;font-family:"Noto Sans KR",sans-serif;}'
    + '#cm-helpbot-panel.open{display:flex;}'
    + '.cmhb-header{background:linear-gradient(135deg,var(--gold,#c9a84c),var(--gold2,#e0c060));color:#0a0d18;padding:14px 16px;font-weight:700;display:flex;align-items:center;justify-content:space-between;}'
    + '.cmhb-close{background:none;border:none;color:#0a0d18;font-size:22px;cursor:pointer;padding:0;line-height:1;}'
    + '.cmhb-messages{flex:1;overflow-y:auto;padding:14px;color:var(--text,#e0d4a8);font-size:0.88rem;line-height:1.55;}'
    + '.cmhb-msg{margin-bottom:12px;padding:10px 12px;border-radius:10px;}'
    + '.cmhb-msg.bot{background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);}'
    + '.cmhb-msg.user{background:rgba(74,158,142,0.08);border:1px solid rgba(74,158,142,0.2);text-align:right;}'
    + '.cmhb-msg a{color:var(--gold2,#e0c060);text-decoration:underline;}'
    + '.cmhb-suggest{display:flex;flex-wrap:wrap;gap:6px;padding:10px 14px;border-top:1px solid var(--border,#2a2e3e);}'
    + '.cmhb-suggest button{background:rgba(255,255,255,0.05);border:1px solid var(--border,#2a2e3e);color:var(--text,#e0d4a8);padding:6px 10px;font-size:0.78rem;border-radius:14px;cursor:pointer;font-family:inherit;}'
    + '.cmhb-suggest button:hover{background:rgba(201,168,76,0.15);border-color:var(--gold,#c9a84c);}'
    + '.cmhb-input{display:flex;gap:8px;padding:12px;border-top:1px solid var(--border,#2a2e3e);}'
    + '.cmhb-input input{flex:1;background:rgba(255,255,255,0.05);border:1px solid var(--border,#2a2e3e);color:var(--text,#e0d4a8);padding:8px 12px;border-radius:8px;font-family:inherit;font-size:0.88rem;}'
    + '.cmhb-input button{background:var(--gold,#c9a84c);color:#0a0d18;border:none;padding:8px 16px;border-radius:8px;cursor:pointer;font-weight:700;font-family:inherit;font-size:0.88rem;}';
  document.head.appendChild(style);

  // Toggle button
  var toggle = document.createElement('button');
  toggle.id = 'cm-helpbot-toggle';
  toggle.innerHTML = '問';
  toggle.title = '도움말 (자주 묻는 질문)';
  toggle.setAttribute('aria-label', '도움말 챗봇');
  document.body.appendChild(toggle);

  // Panel
  var panel = document.createElement('div');
  panel.id = 'cm-helpbot-panel';
  panel.innerHTML = ''
    + '<div class="cmhb-header"><span>천명당 도움말</span><button class="cmhb-close" aria-label="닫기">&times;</button></div>'
    + '<div class="cmhb-messages" id="cmhb-msgs"></div>'
    + '<div class="cmhb-suggest">'
    +   '<button data-q="쿠폰 사용 방법">쿠폰</button>'
    +   '<button data-q="결제 후 결과">결과 보기</button>'
    +   '<button data-q="PDF 다운로드">PDF</button>'
    +   '<button data-q="광고 뜸">광고</button>'
    +   '<button data-q="매직링크 안와">매직링크</button>'
    +   '<button data-q="환불">환불</button>'
    +   '<button data-q="다른 기기">다른 기기</button>'
    +   '<button data-q="월회원 vs 종합풀이">가격 차이</button>'
    + '</div>'
    + '<div class="cmhb-input"><input id="cmhb-q" placeholder="궁금한 거 입력해 주세요"><button id="cmhb-send">전송</button></div>';
  document.body.appendChild(panel);

  var msgsEl = document.getElementById('cmhb-msgs');
  var inputEl = document.getElementById('cmhb-q');
  var sendBtn = document.getElementById('cmhb-send');

  function appendMsg(text, who) {
    var div = document.createElement('div');
    div.className = 'cmhb-msg ' + who;
    div.innerHTML = text;
    msgsEl.appendChild(div);
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  function ask(q) {
    if (!q || !q.trim()) return;
    appendMsg(q, 'user');
    var match = findAnswer(q);
    if (match) {
      appendMsg(match.a, 'bot');
    } else {
      appendMsg('궁금하신 내용을 잘 못 찾았어요.<br><br>아래 자주 묻는 질문 버튼을 눌러보시거나, <code>support@cheonmyeongdang.com</code> 으로 문의해 주세요.<br><br>또는 더 구체적으로 입력해 주세요 (예: "쿠폰 사용법", "PDF 다운로드", "환불")', 'bot');
    }
  }

  // Initial bot greeting
  appendMsg('안녕하세요 사장님.<br>천명당 도움말 챗봇입니다. 자주 묻는 질문은 아래 버튼, 그 외는 직접 입력해 주세요.', 'bot');

  // Event handlers
  toggle.addEventListener('click', function() { panel.classList.toggle('open'); inputEl.focus(); });
  panel.querySelector('.cmhb-close').addEventListener('click', function() { panel.classList.remove('open'); });
  sendBtn.addEventListener('click', function() {
    var q = inputEl.value;
    inputEl.value = '';
    ask(q);
  });
  inputEl.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') { sendBtn.click(); }
  });
  panel.querySelectorAll('.cmhb-suggest button').forEach(function(b) {
    b.addEventListener('click', function() { ask(b.getAttribute('data-q')); });
  });
})();
