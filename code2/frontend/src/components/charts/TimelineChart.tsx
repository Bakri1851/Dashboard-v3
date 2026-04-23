import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'

type Semantic = 'hours_ago' | 'hour_of_day'

/**
 * 24-bar submission volume chart.
 *
 * semantic="hours_ago"    → index 0 = 24h ago, index 23 = now   (live heartbeat)
 * semantic="hour_of_day"  → index 0 = 00:00,   index 23 = 23:00 (filtered aggregate)
 */
export function TimelineChart({
  data,
  highlightRange,
  semantic = 'hours_ago',
}: {
  data: number[]
  highlightRange?: [number, number]
  semantic?: Semantic
}) {
  const max = Math.max(...data, 1)
  const peakIdx = data.indexOf(max)
  const replayKey = useMemo(() => data.join('|'), [data])

  const tileTitle = (i: number, v: number) =>
    semantic === 'hour_of_day'
      ? `${String(i).padStart(2, '0')}:00 — ${v}`
      : `${23 - i}h ago — ${v}`

  const peakCaption =
    semantic === 'hour_of_day'
      ? `Peak at ${String(peakIdx).padStart(2, '0')}:00 · ${max} submissions`
      : `Peak ${23 - peakIdx}h ago · ${max} submissions`

  const axisLabels =
    semantic === 'hour_of_day'
      ? ['00:00', '06:00', '12:00', '18:00', '23:00']
      : ['-24h', '-18h', '-12h', '-6h', 'now']

  return (
    <div>
      <motion.div
        key={replayKey}
        style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height: 110 }}
        initial="initial"
        animate="animate"
        variants={{
          initial: {},
          animate: { transition: { staggerChildren: 0.018 } },
        }}
      >
        {data.map((v, i) => {
          const inHighlight = highlightRange ? i >= highlightRange[0] && i <= highlightRange[1] : false
          return (
            <motion.div
              key={i}
              variants={{
                initial: { scaleY: 0, opacity: 0 },
                animate: { scaleY: 1, opacity: 1 },
              }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              style={{
                flex: 1,
                height: `${(v / max) * 100}%`,
                minHeight: v > 0 ? 1 : 0,
                background: inHighlight ? T.accent : T.ink2,
                transformOrigin: 'bottom',
              }}
              title={tileTitle(i, v)}
            />
          )
        })}
      </motion.div>
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
        {axisLabels.map((l) => <span key={l}>{l}</span>)}
      </div>
      <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
        {peakCaption}
      </div>
    </div>
  )
}
