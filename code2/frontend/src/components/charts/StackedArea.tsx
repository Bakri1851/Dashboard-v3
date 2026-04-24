import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'

export interface StackedSeries {
  label: string
  color: string
  /** Values per bucket. All series must share the same length. */
  values: number[]
}

/**
 * Thin SVG stacked-area chart — one polygon per series, stacked bottom-up.
 * Used by the Session Progression view to show the evolving count of
 * students in each struggle band across the session.
 *
 * All series must share the same `values.length` (the bucket count).
 */
export function StackedArea({
  series,
  height = 180,
  xLabels,
  onHoverBucket,
  activeIndex,
}: {
  series: StackedSeries[]
  height?: number
  /** Optional labels drawn under 5 evenly-spaced tick marks. */
  xLabels?: string[]
  /** Called when the pointer moves over a bucket index. */
  onHoverBucket?: (idx: number | null) => void
  /** Highlights a specific bucket with a vertical line (for scrub-sync). */
  activeIndex?: number | null
}) {
  const n = series[0]?.values.length ?? 0
  const totals = useMemo(() => {
    const out: number[] = Array(n).fill(0)
    for (const s of series) for (let i = 0; i < n; i++) out[i] += s.values[i] ?? 0
    return out
  }, [series, n])
  const maxTotal = Math.max(1, ...totals)

  const W = 1000 // virtual viewBox width — scales with container
  const H = height
  const stepX = n > 1 ? W / (n - 1) : W
  const yFor = (v: number) => H - (v / maxTotal) * H

  // Build running-bottom offsets per bucket so each series draws on top of previous ones.
  const runningBottom: number[] = Array(n).fill(0)

  const paths = series.map((s) => {
    const top: [number, number][] = []
    const bottom: [number, number][] = []
    for (let i = 0; i < n; i++) {
      const bot = runningBottom[i]
      const topVal = bot + (s.values[i] ?? 0)
      const x = i * stepX
      top.push([x, yFor(topVal)])
      bottom.push([x, yFor(bot)])
      runningBottom[i] = topVal
    }
    const fwd = top.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' L')
    const back = bottom.reverse().map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' L')
    return {
      label: s.label,
      color: s.color,
      d: `M${fwd} L${back} Z`,
    }
  })

  return (
    <div style={{ width: '100%' }}>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="none"
        style={{ width: '100%', height, display: 'block' }}
        onMouseLeave={() => onHoverBucket?.(null)}
        onMouseMove={(e) => {
          if (!onHoverBucket) return
          const rect = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
          const ratio = (e.clientX - rect.left) / rect.width
          const idx = Math.max(0, Math.min(n - 1, Math.round(ratio * (n - 1))))
          onHoverBucket(idx)
        }}
      >
        {paths.map((p, i) => (
          <motion.path
            key={p.label}
            d={p.d}
            fill={p.color}
            fillOpacity={0.75}
            stroke={p.color}
            strokeOpacity={0.95}
            strokeWidth={1}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: i * 0.05, ease: 'easeOut' }}
          />
        ))}
        {activeIndex != null && activeIndex >= 0 && activeIndex < n && (
          <line
            x1={activeIndex * stepX}
            x2={activeIndex * stepX}
            y1={0}
            y2={H}
            stroke={T.ink}
            strokeOpacity={0.65}
            strokeDasharray="3 3"
          />
        )}
      </svg>
      {xLabels && xLabels.length > 0 && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: 6,
            fontFamily: T.fMono,
            fontSize: 9.5,
            color: T.ink3,
          }}
        >
          {xLabels.map((l, i) => (
            <span key={i}>{l}</span>
          ))}
        </div>
      )}
      <div
        style={{
          marginTop: 10,
          display: 'flex',
          gap: 12,
          flexWrap: 'wrap',
          fontFamily: T.fMono,
          fontSize: 10.5,
          color: T.ink3,
        }}
      >
        {series.map((s) => (
          <span key={s.label} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <span
              aria-hidden
              style={{
                width: 10,
                height: 10,
                background: s.color,
                display: 'inline-block',
                borderRadius: 2,
              }}
            />
            {s.label}
          </span>
        ))}
      </div>
    </div>
  )
}
