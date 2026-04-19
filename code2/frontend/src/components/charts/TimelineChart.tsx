import { T } from '../../theme/tokens'

/** 24-hour submission volume — index 0 = earliest, index 23 = current hour. */
export function TimelineChart({ data, highlightRange }: { data: number[]; highlightRange?: [number, number] }) {
  const max = Math.max(...data, 1)
  const peakIdx = data.indexOf(max)
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height: 110 }}>
        {data.map((v, i) => {
          const inHighlight = highlightRange ? i >= highlightRange[0] && i <= highlightRange[1] : false
          return (
            <div
              key={i}
              style={{
                flex: 1,
                height: `${(v / max) * 100}%`,
                minHeight: v > 0 ? 1 : 0,
                background: inHighlight ? T.accent : T.ink2,
              }}
              title={`${String(i).padStart(2, '0')}:00 — ${v}`}
            />
          )
        })}
      </div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: 8,
          fontFamily: T.fMono,
          fontSize: 9.5,
          color: T.ink3,
        }}
      >
        <span>-24h</span><span>-18h</span><span>-12h</span><span>-6h</span><span>now</span>
      </div>
      <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
        Peak at {String(peakIdx).padStart(2, '0')}h ago · {max} submissions
      </div>
    </div>
  )
}
