import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'

interface Item {
  label: string
  value: number
  valueLabel: string
  color?: string
}

/** Horizontal bar list — used for Student Detail score components. */
export function HBars({ items, max = 1 }: { items: Item[]; max?: number }) {
  const m = Number(max)
  const safeMax = isFinite(m) && m > 0 ? m : 1
  const replayKey = useMemo(
    () => items.map((it) => `${it.label}:${it.value}`).join('|'),
    [items],
  )
  return (
    <motion.div
      key={replayKey}
      style={{ display: 'flex', flexDirection: 'column', gap: 8 }}
      initial="initial"
      animate="animate"
      variants={{
        initial: {},
        animate: { transition: { staggerChildren: 0.05 } },
      }}
    >
      {items.map((it, i) => {
        const v = Number(it.value)
        const pct = !isFinite(v) ? 0 : Math.max(0, Math.min(100, (v / safeMax) * 100))
        const isTiny = pct > 0 && pct < 0.5
        return (
          <motion.div
            key={i}
            variants={{
              initial: { opacity: 0, y: 4 },
              animate: { opacity: 1, y: 0 },
            }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            style={{ display: 'grid', gridTemplateColumns: '160px 1fr 48px', gap: 10, alignItems: 'center' }}
            aria-label={`${it.label}: ${it.valueLabel}`}
          >
            <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink2 }}>{it.label}</div>
            <div style={{ height: 6, background: T.line2, borderRadius: 1, overflow: 'hidden' }}>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: isTiny ? 2 : `${pct}%` }}
                transition={{ type: 'spring', stiffness: 120, damping: 22, mass: 0.6 }}
                style={{
                  height: '100%',
                  minWidth: isTiny ? 2 : undefined,
                  background: it.color ?? T.ink,
                }}
              />
            </div>
            <div style={{ fontFamily: T.fMono, fontSize: 12, textAlign: 'right', color: T.ink }}>
              {it.valueLabel}
            </div>
          </motion.div>
        )
      })}
    </motion.div>
  )
}
