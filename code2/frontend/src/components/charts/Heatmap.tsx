import { T } from '../../theme/tokens'

export interface HeatmapRow {
  rowLabel: string
  cells: { colLabel: string; value: number }[]
}

/**
 * Generic 2D heatmap used by the Data Analysis "Activity by Academic Week"
 * view (rows = week labels, cols = day of week) and could be reused for
 * hour-of-day × day-of-week if needed.
 */
export function Heatmap({
  rows,
  colLabels,
  maxValue,
  cellSize = 28,
}: {
  rows: HeatmapRow[]
  colLabels: string[]
  maxValue?: number
  cellSize?: number
}) {
  const max = maxValue ?? Math.max(1, ...rows.flatMap((r) => r.cells.map((c) => c.value)))

  return (
    <div style={{ overflow: 'auto', fontFamily: T.fMono, fontSize: 10.5 }}>
      <table style={{ borderCollapse: 'separate', borderSpacing: 2, color: T.ink2 }}>
        <thead>
          <tr>
            <th style={{ padding: '2px 8px', textAlign: 'left', color: T.ink3, fontWeight: 400 }}></th>
            {colLabels.map((c) => (
              <th
                key={c}
                style={{
                  padding: '2px 4px',
                  textAlign: 'center',
                  fontWeight: 400,
                  color: T.ink3,
                  letterSpacing: 1,
                  textTransform: 'uppercase',
                  minWidth: cellSize,
                }}
              >
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.rowLabel}>
              <th
                style={{
                  padding: '2px 10px 2px 0',
                  textAlign: 'right',
                  fontWeight: 400,
                  color: T.ink2,
                  whiteSpace: 'nowrap',
                }}
              >
                {r.rowLabel}
              </th>
              {colLabels.map((col) => {
                const cell = r.cells.find((c) => c.colLabel === col)
                const v = cell?.value ?? 0
                const opacity = max > 0 ? v / max : 0
                return (
                  <td
                    key={col}
                    title={`${r.rowLabel} · ${col} · ${v}`}
                    style={{
                      width: cellSize,
                      height: cellSize,
                      background: v === 0
                        ? T.bg2
                        : `color-mix(in oklch, var(--accent) ${Math.round(opacity * 80 + 20)}%, transparent)`,
                      border: `1px solid ${T.line2}`,
                      textAlign: 'center',
                      color: opacity > 0.55 ? '#fff' : T.ink2,
                      fontVariantNumeric: 'tabular-nums',
                      fontSize: 10,
                    }}
                  >
                    {v > 0 ? v : ''}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
