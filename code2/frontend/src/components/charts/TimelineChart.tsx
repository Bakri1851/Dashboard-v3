import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'

/** 24-hour submission volume — index 0 = earliest, index 23 = current hour. */
export function TimelineChart({
  data,
  highlightRange,
}: {
  data: number[]
  highlightRange?: [number, number]
}) {
  const max = Math.max(...data, 1)
  const peakIdx = data.indexOf(max)
  const replayKey = useMemo(() => data.join('|'), [data])
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
              title={`${String(i).padStart(2, '0')}:00 — ${v}`}
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
        <span>-24h</span><span>-18h</span><span>-12h</span><span>-6h</span><span>now</span>
      </div>
      <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
        Peak at {String(peakIdx).padStart(2, '0')}h ago · {max} submissions
      </div>
    </div>
  )
}
