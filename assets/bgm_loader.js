// 천명당 BGM 로더 — Suno 생성 곡 통합
// 파일 위치: assets/bgm/cheonmyeongdang_theme.mp3 (Suno에서 다운로드 후 이 경로에 저장)
//
// index.html 에 아래 1줄만 추가:
//   <script src="assets/bgm_loader.js" defer></script>
//
// 기능:
// - 첫 사용자 interaction 후 자동 재생 (브라우저 autoplay 정책 준수)
// - 볼륨 40%, 루프
// - 설정 화면에 음소거 버튼 자동 추가
// - localStorage 로 음소거 상태 기억

(function() {
  const BGM_URL = 'assets/bgm/cheonmyeongdang_theme.mp3';
  const STORAGE_KEY = 'cmd_bgm_muted';

  let audio = null;
  let isMuted = false;

  try {
    isMuted = localStorage.getItem(STORAGE_KEY) === '1';
  } catch (e) {}

  function createAudio() {
    if (audio) return audio;
    audio = document.createElement('audio');
    audio.src = BGM_URL;
    audio.loop = true;
    audio.volume = 0.35;
    audio.preload = 'auto';
    audio.muted = isMuted;
    audio.style.display = 'none';
    document.body.appendChild(audio);
    return audio;
  }

  function tryPlay() {
    const a = createAudio();
    a.play().catch((err) => {
      // Autoplay blocked — wait for first user interaction
      console.log('[bgm] autoplay blocked, waiting for interaction');
    });
  }

  function onFirstInteraction() {
    const a = createAudio();
    if (a.paused) a.play().catch(() => {});
    document.removeEventListener('click', onFirstInteraction);
    document.removeEventListener('touchstart', onFirstInteraction);
  }

  function toggleMute() {
    const a = createAudio();
    isMuted = !isMuted;
    a.muted = isMuted;
    try {
      localStorage.setItem(STORAGE_KEY, isMuted ? '1' : '0');
    } catch (e) {}
    updateButton();
  }

  function updateButton() {
    const btn = document.getElementById('cmd-bgm-toggle');
    if (btn) btn.textContent = isMuted ? '🔇 BGM 꺼짐' : '🔊 BGM 켜짐';
  }

  function injectSettingsButton() {
    // 설정 화면 또는 좌측 상단에 floating 버튼
    const btn = document.createElement('button');
    btn.id = 'cmd-bgm-toggle';
    btn.textContent = isMuted ? '🔇 BGM 꺼짐' : '🔊 BGM 켜짐';
    btn.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999;background:rgba(201,168,76,0.9);color:#1a1a2e;border:none;padding:10px 14px;border-radius:20px;font-size:12px;font-weight:700;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.2)';
    btn.onclick = toggleMute;
    document.body.appendChild(btn);
  }

  window.addEventListener('DOMContentLoaded', () => {
    tryPlay();
    injectSettingsButton();
    document.addEventListener('click', onFirstInteraction, { once: false });
    document.addEventListener('touchstart', onFirstInteraction, { once: false });
  });

  // Expose
  window.CMD_BGM = { toggleMute, get muted() { return isMuted; } };
})();
