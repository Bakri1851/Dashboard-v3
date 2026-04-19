/**
 * Web Audio sound effects — mirrors `code/learning_dashboard/sound.py`.
 * All emit through a single lazily-created AudioContext. Callers should
 * gate on `settingsStore.sounds_enabled` (or `data.runtime.sounds_enabled`
 * from `/api/settings`) before invoking.
 */

let _ctx: AudioContext | null = null

function ctx(): AudioContext | null {
  if (_ctx) return _ctx
  const AC = (window.AudioContext || (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext)
  if (!AC) return null
  _ctx = new AC()
  return _ctx
}

type Tone = {
  freq: number
  start: number          // seconds from now
  duration: number
  type?: OscillatorType  // default sine
  gain?: number          // default 0.15
}

function play(tones: Tone[]) {
  const c = ctx()
  if (!c) return
  const now = c.currentTime
  for (const t of tones) {
    const osc = c.createOscillator()
    const g = c.createGain()
    osc.type = t.type ?? 'sine'
    osc.frequency.value = t.freq
    osc.connect(g).connect(c.destination)
    const vol = t.gain ?? 0.15
    g.gain.setValueAtTime(0, now + t.start)
    g.gain.linearRampToValueAtTime(vol, now + t.start + 0.02)
    g.gain.linearRampToValueAtTime(0, now + t.start + t.duration)
    osc.start(now + t.start)
    osc.stop(now + t.start + t.duration + 0.05)
  }
}

// --- 8 public functions matching sound.py ---

export const playSessionStart = () => play([
  { freq: 392, start: 0.00, duration: 0.12 },
  { freq: 523, start: 0.08, duration: 0.14 },
  { freq: 659, start: 0.16, duration: 0.20 },
])

export const playSessionEnd = () => play([
  { freq: 659, start: 0.00, duration: 0.14 },
  { freq: 523, start: 0.08, duration: 0.14 },
  { freq: 392, start: 0.16, duration: 0.20 },
])

export const playSelection = () => play([
  { freq: 660, start: 0.00, duration: 0.05, type: 'triangle', gain: 0.08 },
  { freq: 880, start: 0.05, duration: 0.05, type: 'triangle', gain: 0.08 },
])

export const playNavigation = () => play([
  { freq: 440, start: 0.00, duration: 0.04, type: 'triangle', gain: 0.06 },
  { freq: 600, start: 0.03, duration: 0.04, type: 'triangle', gain: 0.06 },
])

export const playRefresh = () => play([
  { freq: 220, start: 0.00, duration: 0.07, type: 'sine', gain: 0.05 },
])

export const playAssistantJoin = () => play([
  { freq: 523, start: 0.00, duration: 0.09 },
  { freq: 659, start: 0.08, duration: 0.09 },
  { freq: 784, start: 0.16, duration: 0.09 },
  { freq: 1046, start: 0.24, duration: 0.12 },
])

export const playAssignmentReceived = () => play([
  { freq: 880, start: 0.00, duration: 0.08, type: 'square', gain: 0.08 },
  { freq: 880, start: 0.14, duration: 0.08, type: 'square', gain: 0.08 },
])

export const playHighStruggle = () => play([
  { freq: 440, start: 0.00, duration: 0.18, type: 'sawtooth', gain: 0.10 },
  { freq: 330, start: 0.20, duration: 0.22, type: 'sawtooth', gain: 0.10 },
])
