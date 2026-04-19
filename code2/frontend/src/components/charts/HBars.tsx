import { T } from '../../theme/tokens'

interface Item {
  label: string
  value: number
  valueLabel: string
  color?: string
}

/** Horizontal bar list — used for Student Detail score components. */
export function HBars({ items, max = 1 }: { items: Item[]; max?: number }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {items.map((it, i) => {
        const pct = Math.min(100, (it.value / max) * 100)
        return (
          <div key={i} style={{ display: 'grid', gridTemplateColumns: '160px 1fr 48px', gap: 10, alignItems: 'center' }}>
            <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink2 }}>{it.label}</div>
            <div style={{ height: 6, background: T.line2, borderRadius: 1, overflow: 'hidden' }}>
              <div style={{ width: `${pct}%`, height: '100%', background: it.color ?? T.ink }} />
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
