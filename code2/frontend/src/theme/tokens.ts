/**
 * Design tokens — harvested verbatim from
 *   C:\Users\Bakri\Downloads\Alternative Dashboard _standalone_.html
 *
 * Seven themes swap via an `html.theme-<name>` class. All per-theme values
 * are CSS variables; this module just exposes a typed facade over them so
 * components can `style={{ color: T.ink }}` instead of using var() strings.
 */

export type ThemeName =
  | 'paper'
  | 'newsprint'
  | 'solar'
  | 'scifi'
  | 'blueprint'
  | 'matrix'
  | 'cyberpunk'

export const THEMES: { id: ThemeName; label: string; preview: string }[] = [
  { id: 'paper', label: 'Paper', preview: 'oklch(0.985 0.005 80)' },
  { id: 'newsprint', label: 'Newsprint', preview: 'oklch(0.96 0.012 75)' },
  { id: 'solar', label: 'Solar', preview: 'oklch(0.95 0.03 85)' },
  { id: 'scifi', label: 'Sci-fi', preview: 'oklch(0.14 0.02 240)' },
  { id: 'blueprint', label: 'Blueprint', preview: 'oklch(0.28 0.08 245)' },
  { id: 'matrix', label: 'Matrix', preview: 'oklch(0.08 0 0)' },
  { id: 'cyberpunk', label: 'Cyberpunk', preview: 'oklch(0.12 0.05 310)' },
]

/** Runtime-swappable tokens. Values are var() strings so themes take effect live. */
export const T = {
  /** Font stacks — resolve to per-theme CSS variables defined in global.css. */
  fMono: 'var(--font-mono)',
  fSerif: 'var(--font-serif)',
  fSans: 'var(--font-sans)',

  // --- surfaces -----------------------------------------------------------
  bg: 'var(--bg)',
  bg2: 'var(--bg2)',
  card: 'var(--card)',

  // --- ink (text) ramp ----------------------------------------------------
  /** Strongest text — headlines, body copy. */
  ink: 'var(--ink)',
  ink2: 'var(--ink2)',
  ink3: 'var(--ink3)',
  /** Alias kept for code that still says ink0. */
  ink0: 'var(--ink)',
  ink1: 'var(--ink2)',

  // --- lines --------------------------------------------------------------
  line: 'var(--line)',
  line2: 'var(--line2)',
  /** Alias. */
  border: 'var(--line)',
  panel: 'var(--bg2)',

  // --- accent (swappable hue) --------------------------------------------
  accent: 'var(--accent)',
  accentSoft: 'var(--accent-soft)',

  // --- status colours ----------------------------------------------------
  ok: 'var(--ok)',
  warn: 'var(--warn)',
  danger: 'var(--danger)',

  // --- priority card (theme-safe dark background + high-contrast fg) -----
  priorityBg: 'var(--priority-bg)',
  priorityFg: 'var(--priority-fg)',
} as const

export const ACCENT_HUES: { id: string; h: number }[] = [
  { id: 'indigo', h: 265 },
  { id: 'teal', h: 195 },
  { id: 'terracotta', h: 25 },
  { id: 'forest', h: 150 },
  { id: 'crimson', h: 10 },
]

/** Struggle / difficulty level → palette entry. */
export const LEVEL_STYLES: Record<string, { fg: string; label: string }> = {
  // Student struggle thresholds
  'On Track': { fg: 'var(--ok)', label: 'On Track' },
  'Minor Issues': { fg: 'var(--ink3)', label: 'Minor' },
  'Struggling': { fg: 'var(--warn)', label: 'Struggling' },
  'Needs Help': { fg: 'var(--danger)', label: 'Needs Help' },
  // Question difficulty thresholds
  'Easy': { fg: 'var(--ok)', label: 'Easy' },
  'Medium': { fg: 'var(--ink3)', label: 'Medium' },
  'Hard': { fg: 'var(--warn)', label: 'Hard' },
  'Very Hard': { fg: 'var(--danger)', label: 'Very Hard' },
}

export const DEFAULT_THEME: ThemeName = 'paper'
export const DEFAULT_ACCENT = ACCENT_HUES[0]
export const STORAGE_KEY_THEME = 'dash-theme'
export const STORAGE_KEY_ACCENT = 'dash-accent'
