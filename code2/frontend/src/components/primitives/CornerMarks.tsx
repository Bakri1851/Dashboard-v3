import { motion, useReducedMotion } from 'framer-motion'
import { T } from '../../theme/tokens'
import { useTheme } from '../../theme/ThemeContext'

/** Four corner ticks that frame a card. Pure decoration for sci-fi/dark themes. */
export function CornerMarks({ color }: { color?: string }) {
  const c = color ?? T.accent
  const sz = 8
  const { themeKind } = useTheme()
  const reduce = useReducedMotion()
  const breathe = themeKind === 'dark' && !reduce
  const base = {
    position: 'absolute' as const,
    width: sz,
    height: sz,
    borderColor: c,
    borderStyle: 'solid' as const,
  }
  const marks: {
    style: { borderWidth: string; top?: number; left?: number; right?: number; bottom?: number }
    delay: number
  }[] = [
    { style: { top: -1, left: -1, borderWidth: '1px 0 0 1px' }, delay: 0 },
    { style: { top: -1, right: -1, borderWidth: '1px 1px 0 0' }, delay: 0.35 },
    { style: { bottom: -1, left: -1, borderWidth: '0 0 1px 1px' }, delay: 0.7 },
    { style: { bottom: -1, right: -1, borderWidth: '0 1px 1px 0' }, delay: 1.05 },
  ]
  return (
    <>
      {marks.map((m, i) =>
        breathe ? (
          <motion.span
            key={i}
            style={{ ...base, ...m.style }}
            initial={{ opacity: 0.55 }}
            animate={{ opacity: [0.55, 1, 0.55] }}
            transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: m.delay }}
          />
        ) : (
          <span key={i} style={{ ...base, ...m.style }} />
        ),
      )}
    </>
  )
}
