// Shared UI primitives for the redesign.
// Two themes: "paper" (editorial paper-white) and "scifi" (phosphor console).

const { useState, useMemo, useEffect, useRef } = React;

const THEMES = {
  paper: {
    bg: 'oklch(0.985 0.005 80)',
    bg2: 'oklch(0.97 0.006 80)',
    card: '#ffffff',
    ink: 'oklch(0.18 0.01 80)',
    ink2: 'oklch(0.38 0.01 80)',
    ink3: 'oklch(0.58 0.008 80)',
    line: 'oklch(0.90 0.006 80)',
    line2: 'oklch(0.82 0.006 80)',
    accent: 'oklch(0.42 0.12 265)',
    accentSoft: 'oklch(0.93 0.03 265)',
    warn: 'oklch(0.65 0.14 60)',
    warnSoft: 'oklch(0.95 0.04 60)',
    danger: 'oklch(0.52 0.17 25)',
    dangerSoft: 'oklch(0.94 0.04 25)',
    ok: 'oklch(0.55 0.10 155)',
    okSoft: 'oklch(0.94 0.04 155)',
    fSans: `'IBM Plex Sans', system-ui, sans-serif`,
    fMono: `'IBM Plex Mono', ui-monospace, monospace`,
    fSerif: `'IBM Plex Serif', Georgia, serif`,
    themeKind: 'paper',
  },
  scifi: {
    // Deep space ground, phosphor-cyan accent, amber warn, magenta danger, lime ok
    bg: 'oklch(0.14 0.02 240)',
    bg2: 'oklch(0.18 0.025 240)',
    card: 'oklch(0.17 0.025 240)',
    ink: 'oklch(0.95 0.03 190)',
    ink2: 'oklch(0.78 0.04 190)',
    ink3: 'oklch(0.58 0.05 210)',
    line: 'oklch(0.28 0.04 220)',
    line2: 'oklch(0.42 0.08 200)',
    accent: 'oklch(0.78 0.14 195)',
    accentSoft: 'oklch(0.28 0.06 200)',
    warn: 'oklch(0.82 0.15 85)',
    warnSoft: 'oklch(0.30 0.07 85)',
    danger: 'oklch(0.70 0.22 20)',
    dangerSoft: 'oklch(0.28 0.09 20)',
    ok: 'oklch(0.85 0.18 135)',
    okSoft: 'oklch(0.28 0.07 135)',
    fSans: `'Space Grotesk', 'IBM Plex Sans', system-ui, sans-serif`,
    fMono: `'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace`,
    fSerif: `'Space Grotesk', 'IBM Plex Sans', system-ui, sans-serif`,
    themeKind: 'scifi',
  },
  blueprint: {
    // Drafting paper — cool cyan-indigo ground, chalk white ink
    bg: 'oklch(0.28 0.08 245)',
    bg2: 'oklch(0.32 0.08 245)',
    card: 'oklch(0.30 0.09 245)',
    ink: 'oklch(0.97 0.015 240)',
    ink2: 'oklch(0.82 0.03 240)',
    ink3: 'oklch(0.68 0.05 240)',
    line: 'oklch(0.45 0.10 240)',
    line2: 'oklch(0.58 0.12 240)',
    accent: 'oklch(0.88 0.10 90)',
    accentSoft: 'oklch(0.40 0.08 90)',
    warn: 'oklch(0.82 0.13 70)',
    warnSoft: 'oklch(0.40 0.08 70)',
    danger: 'oklch(0.68 0.20 20)',
    dangerSoft: 'oklch(0.40 0.10 20)',
    ok: 'oklch(0.82 0.12 150)',
    okSoft: 'oklch(0.40 0.08 150)',
    fSans: `'Inconsolata', 'IBM Plex Mono', monospace`,
    fMono: `'Inconsolata', 'IBM Plex Mono', monospace`,
    fSerif: `'Inconsolata', 'IBM Plex Mono', monospace`,
    themeKind: 'blueprint',
  },
  matrix: {
    // Green phosphor on black — pure terminal
    bg: 'oklch(0.08 0 0)',
    bg2: 'oklch(0.12 0 0)',
    card: 'oklch(0.10 0.02 150)',
    ink: 'oklch(0.88 0.18 150)',
    ink2: 'oklch(0.72 0.18 150)',
    ink3: 'oklch(0.50 0.14 150)',
    line: 'oklch(0.25 0.06 150)',
    line2: 'oklch(0.38 0.10 150)',
    accent: 'oklch(0.92 0.22 145)',
    accentSoft: 'oklch(0.22 0.08 150)',
    warn: 'oklch(0.85 0.18 85)',
    warnSoft: 'oklch(0.22 0.07 85)',
    danger: 'oklch(0.72 0.24 25)',
    dangerSoft: 'oklch(0.22 0.09 25)',
    ok: 'oklch(0.90 0.22 145)',
    okSoft: 'oklch(0.22 0.08 145)',
    fSans: `'VT323', 'JetBrains Mono', monospace`,
    fMono: `'VT323', 'JetBrains Mono', monospace`,
    fSerif: `'VT323', 'JetBrains Mono', monospace`,
    themeKind: 'matrix',
  },
  cyberpunk: {
    // Hot magenta + electric cyan on deep purple-black
    bg: 'oklch(0.12 0.05 310)',
    bg2: 'oklch(0.16 0.06 310)',
    card: 'oklch(0.15 0.06 310)',
    ink: 'oklch(0.96 0.02 330)',
    ink2: 'oklch(0.78 0.08 320)',
    ink3: 'oklch(0.58 0.10 310)',
    line: 'oklch(0.30 0.10 310)',
    line2: 'oklch(0.48 0.15 315)',
    accent: 'oklch(0.72 0.26 335)',
    accentSoft: 'oklch(0.28 0.12 330)',
    warn: 'oklch(0.85 0.18 75)',
    warnSoft: 'oklch(0.28 0.08 75)',
    danger: 'oklch(0.70 0.26 18)',
    dangerSoft: 'oklch(0.28 0.12 20)',
    ok: 'oklch(0.82 0.18 190)',
    okSoft: 'oklch(0.28 0.10 190)',
    fSans: `'Rajdhani', 'Space Grotesk', sans-serif`,
    fMono: `'JetBrains Mono', monospace`,
    fSerif: `'Rajdhani', 'Space Grotesk', sans-serif`,
    themeKind: 'cyberpunk',
  },
  newsprint: {
    // High-contrast warm broadsheet
    bg: 'oklch(0.96 0.012 75)',
    bg2: 'oklch(0.93 0.015 75)',
    card: 'oklch(0.98 0.008 75)',
    ink: 'oklch(0.15 0.02 60)',
    ink2: 'oklch(0.32 0.02 60)',
    ink3: 'oklch(0.50 0.015 70)',
    line: 'oklch(0.82 0.015 75)',
    line2: 'oklch(0.68 0.02 70)',
    accent: 'oklch(0.42 0.18 25)',
    accentSoft: 'oklch(0.88 0.06 25)',
    warn: 'oklch(0.62 0.15 55)',
    warnSoft: 'oklch(0.92 0.05 55)',
    danger: 'oklch(0.45 0.20 25)',
    dangerSoft: 'oklch(0.90 0.05 25)',
    ok: 'oklch(0.42 0.12 145)',
    okSoft: 'oklch(0.90 0.04 145)',
    fSans: `'Playfair Display', Georgia, serif`,
    fMono: `'Courier Prime', 'IBM Plex Mono', monospace`,
    fSerif: `'Playfair Display', Georgia, serif`,
    themeKind: 'newsprint',
  },
  solar: {
    // Warm solarized — amber-cream ground, olive ink
    bg: 'oklch(0.95 0.03 85)',
    bg2: 'oklch(0.92 0.035 85)',
    card: 'oklch(0.97 0.025 85)',
    ink: 'oklch(0.30 0.04 55)',
    ink2: 'oklch(0.45 0.04 55)',
    ink3: 'oklch(0.60 0.035 55)',
    line: 'oklch(0.82 0.04 85)',
    line2: 'oklch(0.70 0.05 85)',
    accent: 'oklch(0.52 0.14 55)',
    accentSoft: 'oklch(0.90 0.05 55)',
    warn: 'oklch(0.62 0.15 50)',
    warnSoft: 'oklch(0.92 0.05 50)',
    danger: 'oklch(0.50 0.18 25)',
    dangerSoft: 'oklch(0.90 0.05 25)',
    ok: 'oklch(0.55 0.12 135)',
    okSoft: 'oklch(0.92 0.04 135)',
    fSans: `'Fraunces', Georgia, serif`,
    fMono: `'IBM Plex Mono', monospace`,
    fSerif: `'Fraunces', Georgia, serif`,
    themeKind: 'solar',
  },
};

const _themeName = (window.DashSettings && window.DashSettings.get('theme')) || 'paper';
const T = { ...THEMES[_themeName] || THEMES.paper };
window.THEMES = THEMES;
window.setDashTheme = function(name) {
  if (!THEMES[name]) return;
  if (window.DashSettings) window.DashSettings.set('theme', name);
};

const LEVEL_STYLES = {
  'Needs Help':   { fg: T.danger, bg: T.dangerSoft, dot: T.danger },
  'Struggling':   { fg: T.warn,   bg: T.warnSoft,   dot: T.warn },
  'Minor Issues': { fg: T.ink2,   bg: T.bg2,        dot: T.ink3 },
  'On Track':     { fg: T.ok,     bg: T.okSoft,     dot: T.ok },
  'Very Hard':    { fg: T.danger, bg: T.dangerSoft, dot: T.danger },
  'Hard':         { fg: T.warn,   bg: T.warnSoft,   dot: T.warn },
  'Medium':       { fg: T.ink2,   bg: T.bg2,        dot: T.ink3 },
  'Easy':         { fg: T.ok,     bg: T.okSoft,     dot: T.ok },
};

function Pill({ level, size = 11 }) {
  const s = LEVEL_STYLES[level] || LEVEL_STYLES['On Track'];
  const sf = T.themeKind === 'scifi';
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '2px 8px', borderRadius: 0,
      border: `1px solid ${s.fg}`, color: s.fg, background: s.bg,
      fontFamily: T.fMono, fontSize: size, letterSpacing: sf ? 0.6 : 0.2,
      textTransform: 'uppercase', fontWeight: 500,
      boxShadow: sf ? `0 0 8px ${s.fg}55, inset 0 0 8px ${s.fg}22` : 'none',
    }}>
      <span style={{
        width: 5, height: 5, borderRadius: '50%', background: s.dot,
        boxShadow: sf ? `0 0 6px ${s.dot}` : 'none',
      }} />
      {level}
    </span>
  );
}

function ScoreBar({ value, color, height = 3, width = '100%' }) {
  return (
    <div style={{ width, height, background: T.line, borderRadius: 0, overflow: 'hidden' }}>
      <div style={{ width: `${value * 100}%`, height: '100%', background: color }} />
    </div>
  );
}

function Stat({ label, value, note, accent = T.ink }) {
  const sf = T.themeKind === 'scifi';
  return (
    <div style={{
      position: 'relative', padding: '14px 18px', background: T.card,
      border: `1px solid ${T.line}`, borderRadius: 0,
    }}>
      {sf && <CornerMarks />}
      <div style={{
        fontFamily: T.fMono, fontSize: 10.5, color: T.ink3,
        textTransform: 'uppercase', letterSpacing: 1.3, marginBottom: 8,
      }}>{label}</div>
      <div style={{
        fontFamily: T.fSerif, fontSize: 32, color: accent, lineHeight: 1, fontWeight: sf ? 500 : 400,
        fontFeatureSettings: '"tnum"',
        textShadow: sf ? `0 0 12px ${accent}88` : 'none',
        letterSpacing: sf ? 0.5 : 0,
      }}>
        {value}
      </div>
      {note && <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 8 }}>{note}</div>}
    </div>
  );
}

function CornerMarks() {
  const c = T.accent;
  const sz = 8;
  const mk = (pos) => ({
    position: 'absolute', width: sz, height: sz,
    borderColor: c, borderStyle: 'solid', ...pos,
  });
  return (
    <>
      <span style={{ ...mk({ top: -1, left: -1, borderWidth: '1px 0 0 1px' }) }} />
      <span style={{ ...mk({ top: -1, right: -1, borderWidth: '1px 1px 0 0' }) }} />
      <span style={{ ...mk({ bottom: -1, left: -1, borderWidth: '0 0 1px 1px' }) }} />
      <span style={{ ...mk({ bottom: -1, right: -1, borderWidth: '0 1px 1px 0' }) }} />
    </>
  );
}

function SectionLabel({ children, n }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 16,
      borderBottom: `1px solid ${T.line}`, paddingBottom: 8,
    }}>
      {n != null && (
        <span style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1 }}>
          §{String(n).padStart(2, '0')}
        </span>
      )}
      <span style={{ fontFamily: T.fSans, fontSize: 13, color: T.ink, fontWeight: 500, letterSpacing: 0.3 }}>
        {children}
      </span>
    </div>
  );
}

function Button({ children, variant = 'ghost', onClick, ...rest }) {
  const v = {
    primary: { bg: T.ink, fg: T.themeKind === 'scifi' ? T.bg : '#fff', bd: T.ink },
    ghost:   { bg: 'transparent', fg: T.ink, bd: T.line2 },
    accent:  { bg: T.accent, fg: T.themeKind === 'scifi' ? T.bg : '#fff', bd: T.accent },
    danger:  { bg: 'transparent', fg: T.danger, bd: T.danger },
  }[variant];
  const sf = T.themeKind === 'scifi';
  return (
    <button onClick={onClick} {...rest} style={{
      padding: '6px 12px', background: v.bg, color: v.fg,
      border: `1px solid ${v.bd}`, borderRadius: 0,
      fontFamily: T.fMono, fontSize: 11, textTransform: 'uppercase',
      letterSpacing: sf ? 1.4 : 1, cursor: 'pointer', fontWeight: sf ? 500 : 400,
      boxShadow: sf && variant === 'accent' ? `0 0 10px ${T.accent}66` : 'none',
    }}>
      {children}
    </button>
  );
}

// Sparkline (tiny line chart)
function Spark({ data, width = 72, height = 20, color = T.ink2, fill = false }) {
  if (!data || !data.length) return null;
  const max = Math.max(...data, 1);
  const min = Math.min(...data, 0);
  const range = max - min || 1;
  const step = width / (data.length - 1 || 1);
  const pts = data.map((v, i) => `${i * step},${height - ((v - min) / range) * height}`).join(' ');
  return (
    <svg width={width} height={height} style={{ display: 'block' }}>
      {fill && (
        <polygon points={`0,${height} ${pts} ${width},${height}`} fill={color} fillOpacity="0.15" />
      )}
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// Simple bar chart (horizontal)
function HBars({ items, width = 100, height = 6, max }) {
  const m = max || Math.max(...items.map(i => i.value));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {items.map((it, i) => (
        <div key={i} style={{ display: 'grid', gridTemplateColumns: '88px 1fr 40px', gap: 10, alignItems: 'center' }}>
          <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink2 }}>{it.label}</span>
          <div style={{ height, background: T.line, position: 'relative' }}>
            <div style={{
              height: '100%', width: `${(it.value / m) * 100}%`,
              background: it.color || T.ink,
            }} />
          </div>
          <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink2, textAlign: 'right' }}>
            {it.valueLabel || it.value}
          </span>
        </div>
      ))}
    </div>
  );
}

// Histogram with 4 bucket colors
function Histogram({ data, bucketColors, labels, height = 60 }) {
  const max = Math.max(...data);
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height }}>
        {data.map((v, i) => (
          <div key={i} style={{
            flex: 1, height: `${(v / max) * 100}%`,
            background: bucketColors[i] || T.ink2, minHeight: v > 0 ? 2 : 0,
          }} />
        ))}
      </div>
      {labels && (
        <div style={{ display: 'flex', gap: 2, marginTop: 6 }}>
          {labels.map((l, i) => (
            <div key={i} style={{ flex: 1, fontFamily: T.fMono, fontSize: 9.5, color: T.ink3, textAlign: 'center' }}>{l}</div>
          ))}
        </div>
      )}
    </div>
  );
}

Object.assign(window, { T, LEVEL_STYLES, Pill, ScoreBar, Stat, SectionLabel, Button, Spark, HBars, Histogram, CornerMarks });
