import { T } from '../../theme/tokens'

interface Item {
  label: string
  value: number
  valueLabel: string
  color?: string
}

/** Horizontal bar list — used for Student Detail score components. */
export function HBars({ items, max = 1 }: { items: Item[]; max?: number }) {
  const m = Number(max)
  const safeMax = isFinite(m) && m > 0 ? m : 1
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {items.map((it, i) => {
        const v = Number(it.value)
        const pct = !isFinite(v) ? 0 : Math.max(0, Math.min(100, (v / safeMax) * 100))
        const fillStyle: React.CSSProperties =
          pct > 0 && pct < 0.5
            ? { width: 2, minWidth: 2, height: '100%', background: it.color ?? T.ink }
            : { width: `${pct}%`, height: '100%', background: it.color ?? T.ink }
        return (
          <div
            key={i}
            style={{ display: 'grid', gridTemplateColumns: '160px 1fr 48px', gap: 10, alignItems: 'center' }}
            aria-label={`${it.label}: ${it.valueLabel}`}
          >
            <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink2 }}>{it.label}</div>
            <div style={{ height: 6, background: T.line2, borderRadius: 1, overflow: 'hidden' }}>
              <div style={fillStyle} />
            </div>
            <div style={{ fontFamily: T.fMono, fontSize: 12, textAlign: 'right', color: T.ink }}>
              {it.valueLabel}
            </div>
          </div>
        )
      })}
    </div>
  )
}
