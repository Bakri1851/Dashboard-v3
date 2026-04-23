import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'

/** Inline sparkline — given y-values in 0..1, draws a line (optionally filled). */
export function Spark({
  data,
  width = 240,
  height = 70,
  color = T.ink,
  fill = false,
  domain,
}: {
  data: number[]
  width?: number
  height?: number
  color?: string
  fill?: boolean
  domain?: [number, number]
}) {
  const replayKey = useMemo(() => data.join('|'), [data])
  if (data.length === 0) {
    return <div style={{ width, height, color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>no data</div>
  }
  const [lo, hi] = domain ?? [Math.min(...data), Math.max(...data)]
  const range = hi - lo
  const stepX = width / Math.max(data.length - 1, 1)
  const yOf =
    range === 0
      ? () => height / 2
      : (v: number) => height - ((v - lo) / range) * height

  let path = ''
  data.forEach((v, i) => {
    const x = i * stepX
    const y = yOf(v)
    path += (i === 0 ? 'M' : 'L') + x.toFixed(1) + ' ' + y.toFixed(1) + ' '
  })

  const fillPath = fill ? `${path} L ${width.toFixed(1)} ${height} L 0 ${height} Z` : ''

  return (
    <svg key={replayKey} width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {fill && (
        <motion.path
          d={fillPath}
          fill={color}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.12 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        />
      )}
      <motion.path
        d={path.trim()}
        stroke={color}
        strokeWidth={1.5}
        fill="none"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.7, ease: 'easeOut' }}
      />
      {data.map((v, i) => {
        const isLast = i === data.length - 1
        const cx = i * stepX
        const cy = yOf(v)
        return (
          <motion.circle
            key={i}
            cx={cx}
            cy={cy}
            r={isLast ? 3 : 1.5}
            fill={color}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              duration: 0.25,
              delay: 0.6 + Math.min(i * 0.01, 0.25),
              ease: 'easeOut',
            }}
            style={{ transformOrigin: `${cx}px ${cy}px` }}
          />
        )
      })}
      {/* "Now" pulse on the last data point — breathing halo that signals
          this is the current value. */}
      {data.length > 0 && (
        <motion.circle
          cx={(data.length - 1) * stepX}
          cy={yOf(data[data.length - 1])}
          r={3}
          fill="none"
          stroke={color}
          strokeWidth={1}
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 0.55, 0], scale: [1, 2.2, 2.4] }}
          transition={{
            duration: 1.8,
            repeat: Infinity,
            ease: 'easeOut',
            delay: 0.9,
          }}
          style={{
            transformOrigin: `${(data.length - 1) * stepX}px ${yOf(data[data.length - 1])}px`,
          }}
        />
      )}
    </svg>
  )
}
