import { T } from '../../theme/tokens'

/** 4-bucket (or N-bucket) histogram used on the In-Class distribution panels. */
export function Histogram({
  data,
  labels,
  bucketColors,
  height = 100,
}: {
  data: number[]
  labels: string[]
  bucketColors: string[]
  height?: number
}) {
  const max = Math.max(...data, 1)
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, height }}>
        {data.map((v, i) => {
          const pct = (v / max) * 100
          return (
            <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
              <div
                style={{
                  width: '100%',
                  height: `${pct}%`,
                  background: bucketColors[i] ?? T.ink,
                  minHeight: v > 0 ? 2 : 0,
                  transition: 'height 200ms ease-out',
                }}
                title={`${labels[i]} — ${v}`}
              />
            </div>
          )
        })}
      </div>
      <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
        {labels.map((l, i) => (
          <div
            key={i}
            style={{ flex: 1, textAlign: 'center', fontFamily: T.fMono, fontSize: 10, color: T.ink3 }}
          >
            {l} · {data[i]}
          </div>
        ))}
      </div>
    </div>
  )
}
