import { useEffect, useRef } from 'react'
import type { CSSProperties } from 'react'
import { AnimatePresence, animate, motion, useReducedMotion } from 'framer-motion'

const NUMERIC_RE = /^-?\d+(\.\d+)?$/

function countFractionDigits(s: string): number {
  const idx = s.indexOf('.')
  return idx === -1 ? 0 : s.length - idx - 1
}

/**
 * Renders a string value. If the value parses as a number, it tweens from the
 * previous display number to the new target on every change by writing to a
 * ref — avoiding setState-in-effect churn. Non-numeric values ("Very Hard",
 * "CS101-Q7") crossfade instead. Reduced-motion users get the final value
 * immediately.
 */
export function AnimatedNumber({
  value,
  duration = 0.6,
  style,
  className,
}: {
  value: string
  duration?: number
  style?: CSSProperties
  className?: string
}) {
  const reduce = useReducedMotion()
  const trimmed = value.trim()
  const isNumeric = NUMERIC_RE.test(trimmed)
  const fractionDigits = isNumeric ? countFractionDigits(trimmed) : 0
  const target = isNumeric ? Number(trimmed) : 0

  const spanRef = useRef<HTMLSpanElement | null>(null)
  const latestRef = useRef<number>(isNumeric ? target : 0)

  useEffect(() => {
    if (!isNumeric || !spanRef.current) return
    if (reduce) {
      latestRef.current = target
      spanRef.current.textContent = target.toFixed(fractionDigits)
      return
    }
    const controls = animate(latestRef.current, target, {
      duration,
      ease: 'easeOut',
      onUpdate: (v) => {
        latestRef.current = v
        if (spanRef.current) {
          spanRef.current.textContent = v.toFixed(fractionDigits)
        }
      },
    })
    return () => controls.stop()
  }, [value, isNumeric, target, fractionDigits, duration, reduce])

  if (isNumeric) {
    return (
      <span ref={spanRef} style={style} className={className}>
        {target.toFixed(fractionDigits)}
      </span>
    )
  }

  return (
    <span style={{ position: 'relative', display: 'inline-block', ...style }} className={className}>
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={value}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.15, ease: 'easeOut' }}
          style={{ display: 'inline-block' }}
        >
          {value}
        </motion.span>
      </AnimatePresence>
    </span>
  )
}
