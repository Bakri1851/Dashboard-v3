// Persistent settings store with event bus.
// Every setting is persisted to localStorage under 'dash-<key>' and broadcasts
// a 'dash-settings-change' CustomEvent so subscribing components re-render.

(function() {
  const PREFIX = 'dash-';
  const DEFAULTS = {
    theme: 'paper',
    struggleModel: 'Baseline',           // 'Baseline' | 'Improved'
    difficultyModel: 'Baseline',         // 'Baseline' | 'IRT'
    cfEnabled: true,
    cfThreshold: 0.5,
    smoothing: true,
    sounds: false,
    autoRefresh: true,
    refreshInterval: 30,                 // seconds
    bkt_p_init: 0.30,
    bkt_p_learn: 0.15,
    bkt_p_guess: 0.20,
    bkt_p_slip: 0.10,
    density: 'comfy',                    // 'compact' | 'comfy' | 'roomy'
  };

  const cache = {};
  for (const [k, v] of Object.entries(DEFAULTS)) {
    const raw = localStorage.getItem(PREFIX + k);
    if (raw == null) { cache[k] = v; continue; }
    try {
      const parsed = JSON.parse(raw);
      cache[k] = parsed;
    } catch { cache[k] = v; }
  }

  const bus = new EventTarget();

  function get(k) { return cache[k]; }
  function getAll() { return { ...cache }; }
  function set(k, v) {
    if (cache[k] === v) return;
    cache[k] = v;
    try { localStorage.setItem(PREFIX + k, JSON.stringify(v)); } catch {}
    bus.dispatchEvent(new CustomEvent('change', { detail: { key: k, value: v } }));
    // Theme change requires full reload so T tokens rebuild
    if (k === 'theme') {
      setTimeout(() => location.reload(), 50);
    }
  }
  function subscribe(cb) {
    const handler = (e) => cb(e.detail.key, e.detail.value);
    bus.addEventListener('change', handler);
    return () => bus.removeEventListener('change', handler);
  }

  // Tiny React hook binding to useState
  function useSetting(key) {
    const [val, setVal] = React.useState(cache[key]);
    React.useEffect(() => {
      const unsub = subscribe((k, v) => { if (k === key) setVal(v); });
      return unsub;
    }, [key]);
    return [val, (v) => set(key, v)];
  }

  // Synth sounds (Web Audio)
  const audioCtx = (() => {
    try { return new (window.AudioContext || window.webkitAudioContext)(); }
    catch { return null; }
  })();
  function beep(freq = 440, dur = 0.08, type = 'sine', vol = 0.08) {
    if (!audioCtx || !cache.sounds) return;
    try {
      if (audioCtx.state === 'suspended') audioCtx.resume();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type; osc.frequency.value = freq;
      gain.gain.setValueAtTime(vol, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + dur);
      osc.connect(gain); gain.connect(audioCtx.destination);
      osc.start(); osc.stop(audioCtx.currentTime + dur);
    } catch {}
  }
  function playSessionStart() { beep(660, 0.08); setTimeout(() => beep(880, 0.12), 90); }
  function playSessionEnd() { beep(440, 0.12); setTimeout(() => beep(330, 0.14), 100); }
  function playNav() { beep(520, 0.04, 'square', 0.04); }
  function playSelect() { beep(720, 0.05, 'triangle', 0.05); }
  function playRefresh() { beep(900, 0.03, 'sine', 0.03); }

  window.DashSettings = {
    get, getAll, set, subscribe, useSetting, DEFAULTS,
    playSessionStart, playSessionEnd, playNav, playSelect, playRefresh,
  };
})();
