import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'

export interface ScatterPoint {
  x: number
  y: number
  id: string
}

/**
 * Minimal SVG scatter for comparing two model scores per entity.
 * Both axes are normalised to [0, 1] (matches struggle/difficulty score domain).
 * A dashed y=x diagonal anchors the "agreement" reading.
 */
export function ScatterChart({
  points,
  width = 520,
  height = 340,
  xLabel,
  yLabel,
  color,
  maxWidth = 520,
}: {
  points: ScatterPoint[]
  width?: number
  height?: number
  xLabel: string
  yLabel: string
  color?: string
  maxWidth?: number
}) {
  const pad = { top: 16, right: 16, bottom: 36, left: 44 }
  const innerW = width - pad.left - pad.right
  const innerH = height - pad.top - pad.bottom
  const dot = color ?? T.accent

  const xMin = 0, xMax = 1, yMin = 0, yMax = 1
  const sx = (v: number) => pad.left + ((v - xMin) / (xMax - xMin || 1)) * innerW
  const sy = (v: number) => pad.top + (1 - (v - yMin) / (yMax - yMin || 1)) * innerH

  const ticks = [0, 0.25, 0.5, 0.75, 1]
  const replayKey = useMemo(
    () => `${points.length}:${points[0]?.id ?? ''}:${points[points.length - 1]?.id ?? ''}`,
    [points],
  )

  return (
    <svg
      key={replayKey}
      width="100%"
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="xMidYMid meet"
      style={{ display: 'block', maxWidth, margin: '0 auto' }}
    >
      {/* Gridlines */}
      {ticks.map((t, i) => (
        <g key={`g${i}`}>
          <line
            x1={sx(t)}
            x2={sx(t)}
            y1={pad.top}
            y2={pad.top + innerH}
            stroke={T.line2}
            strokeDasharray="2 3"
            strokeWidth={0.5}
          />
          <line
            x1={pad.left}
            x2={pad.left + innerW}
            y1={sy(t)}
            y2={sy(t)}
            stroke={T.line2}
            strokeDasharray="2 3"
            strokeWidth={0.5}
          />
        </g>
      ))}

      {/* y = x diagonal — draws in alongside points */}
      <motion.line
        x1={sx(0)}
        y1={sy(0)}
        x2={sx(1)}
        y2={sy(1)}
        stroke={T.ink3}
        strokeDasharray="4 4"
        strokeWidth={1}
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      />

      {/* Axes */}
      <line x1={pad.left} y1={pad.top + innerH} x2={pad.left + innerW} y2={pad.top + innerH} stroke={T.line} />
      <line x1={pad.left} y1={pad.top} x2={pad.left} y2={pad.top + innerH} stroke={T.line} />

      {/* Tick labels */}
      {ticks.map((t, i) => (
        <g key={`t${i}`}>
          <text
            x={sx(t)}
            y={pad.top + innerH + 14}
            textAnchor="middle"
            fontSize={9.5}
            fontFamily={T.fMono}
            fill={T.ink3}
          >
            {t.toFixed(2)}
          </text>
          <text
            x={pad.left - 6}
            y={sy(t) + 3}
            textAnchor="end"
            fontSize={9.5}
            fontFamily={T.fMono}
            fill={T.ink3}
          >
            {t.toFixed(2)}
          </text>
        </g>
      ))}

      {/* Axis labels */}
      <text
        x={pad.left + innerW / 2}
        y={height - 4}
        textAnchor="middle"
        fontSize={10}
        fontFamily={T.fMono}
        fill={T.ink3}
        letterSpacing={1.2}
      >
        {xLabel.toUpperCase()}
      </text>
      <text
        transform={`translate(12 ${pad.top + innerH / 2}) rotate(-90)`}
        textAnchor="middle"
        fontSize={10}
        fontFamily={T.fMono}
        fill={T.ink3}
        letterSpacing={1.2}
      >
        {yLabel.toUpperCase()}
      </text>

      {/* Points — staggered entrance, delay cap so large N stays snappy */}
      {points.map((p, i) => {
        const cx = sx(p.x)
        const cy = sy(p.y)
        const delay = Math.min(i * 0.008, 0.4)
        return (
          <motion.circle
            key={`${p.id}-${i}`}
            cx={cx}
            cy={cy}
            r={3}
            fill={dot}
            fillOpacity={0.65}
            stroke={dot}
            strokeWidth={0.5}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay, ease: 'easeOut' }}
            style={{ transformOrigin: `${cx}px ${cy}px` }}
          >
            <title>{`${p.id} · baseline ${p.x.toFixed(3)} · improved ${p.y.toFixed(3)}`}</title>
          </motion.circle>
        )
      })}
    </svg>
  )
}
