import { useMemo } from 'react'
import { motion } from 'framer-motion'
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
  const maxRaw = Math.max(...data, 1)
  const max = isFinite(maxRaw) && maxRaw > 0 ? maxRaw : 1
  // Replay mount animation only when the underlying data actually changes.
  const replayKey = useMemo(() => data.join('|'), [data])
  return (
    <div>
      <motion.div
        key={replayKey}
        style={{ display: 'flex', alignItems: 'flex-end', gap: 6, height }}
        initial="initial"
        animate="animate"
        variants={{
          initial: {},
          animate: { transition: { staggerChildren: 0.04 } },
        }}
      >
        {data.map((v, i) => {
          const n = Number(v)
          const pct = !isFinite(n) ? 0 : Math.max(0, Math.min(100, (n / max) * 100))
          return (
            <motion.div
              key={i}
              variants={{
                initial: { scaleY: 0, opacity: 0 },
                animate: { scaleY: 1, opacity: 1 },
              }}
              transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
              style={{
                flex: 1,
                height: `${pct}%`,
                minHeight: n > 0 ? 2 : 0,
                background: bucketColors[i] ?? T.ink,
                transformOrigin: 'bottom',
                willChange: 'transform, opacity',
              }}
              title={`${labels[i]} — ${v}`}
            />
          )
        })}
      </motion.div>
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
