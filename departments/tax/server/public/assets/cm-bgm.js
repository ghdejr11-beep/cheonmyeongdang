/**
 * 세금N혜택 BGM 컨트롤
 * - 자동재생 정책: 브라우저는 사용자 인터랙션 전 audio 자동재생 차단 → 작은 토글 버튼 노출
 * - 페이지 이동/새로고침 시 재생 상태 보존 (localStorage)
 * - 1회 활성화 후 다음 페이지에서도 자동 재생
 */
(function () {
  'use strict';
  if (window.__cmBgmInit) return;
  window.__cmBgmInit = true;

  // 2개 버전 — 접속 시 랜덤 선택 (사용자 매번 다른 분위기 경험)
  var SRCS = ['/assets/cm_jingle_v1.mp3', '/assets/cm_jingle_v2.mp3'];
  var SRC = SRCS[Math.floor(Math.random() * SRCS.length)];
  var KEY_ON = 'cm_bgm_on';
  var KEY_TIME = 'cm_bgm_time';

  var audio = document.createElement('audio');
  audio.id = 'cm-bgm';
  audio.src = SRC;
  audio.dataset.version = SRC.match(/v(\d+)/)[1];
  audio.loop = true;
  audio.preload = 'metadata';
  audio.volume = 0.35;
  document.body.appendChild(audio);

  var btn = document.createElement('button');
  btn.id = 'cm-bgm-toggle';
  btn.setAttribute('aria-label', 'BGM 재생/정지');
  btn.style.cssText = [
    'position:fixed', 'right:14px', 'bottom:14px', 'z-index:9999',
    'width:46px', 'height:46px', 'border-radius:50%',
    'border:none', 'cursor:pointer',
    'background:rgba(50,130,246,0.92)', 'color:#fff',
    'font-size:18px', 'box-shadow:0 4px 14px rgba(0,0,0,0.25)',
    'transition:transform 0.2s, opacity 0.2s', 'opacity:0.85'
  ].join(';');
  btn.innerHTML = '🎵';
  btn.title = 'BGM 재생';
  btn.onmouseenter = function () { btn.style.transform = 'scale(1.08)'; btn.style.opacity = '1'; };
  btn.onmouseleave = function () { btn.style.transform = 'scale(1)'; btn.style.opacity = '0.85'; };
  document.body.appendChild(btn);

  function persist() {
    try { localStorage.setItem(KEY_TIME, String(audio.currentTime || 0)); } catch (e) {}
  }

  function setOn(on) {
    try { localStorage.setItem(KEY_ON, on ? '1' : '0'); } catch (e) {}
    if (on) {
      var t = parseFloat(localStorage.getItem(KEY_TIME) || '0');
      if (!isNaN(t) && t > 0) { try { audio.currentTime = t; } catch (e) {} }
      var p = audio.play();
      if (p && p.catch) p.catch(function () {});
      btn.innerHTML = '⏸';
      btn.title = 'BGM 정지';
    } else {
      audio.pause();
      btn.innerHTML = '🎵';
      btn.title = 'BGM 재생';
    }
  }

  btn.addEventListener('click', function () {
    setOn(audio.paused);
  });

  audio.addEventListener('timeupdate', persist);
  window.addEventListener('beforeunload', persist);

  // 이전에 활성화된 경우 재생 시도 (사용자 인터랙션 후엔 가능)
  var prevOn = (function () { try { return localStorage.getItem(KEY_ON) === '1'; } catch (e) { return false; } })();
  if (prevOn) {
    var startOnInteraction = function () {
      setOn(true);
      window.removeEventListener('click', startOnInteraction);
      window.removeEventListener('touchstart', startOnInteraction);
      window.removeEventListener('keydown', startOnInteraction);
    };
    // 직접 시도
    audio.addEventListener('canplay', function () {
      var p = audio.play();
      if (p && p.catch) p.catch(function () {
        // autoplay blocked → wait for user interaction
        window.addEventListener('click', startOnInteraction, { once: true });
        window.addEventListener('touchstart', startOnInteraction, { once: true });
        window.addEventListener('keydown', startOnInteraction, { once: true });
      });
    }, { once: true });
    btn.innerHTML = '⏸';
    btn.title = 'BGM 정지';
  }
})();
