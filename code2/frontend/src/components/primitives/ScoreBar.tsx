import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'
import { scoreBarSpring } from '../../animation/motion'

/** Inline horizontal progress bar — used in leaderboard "score" cell. */
export function ScoreBar({
  value,
  color = T.ink,
  width = 44,
  height = 3,
}: {
  /** 0..1 */
  value: number
  color?: string
  width?: number
  height?: number
}) {
  const clamped = Math.min(1, Math.max(0, value))
  return (
    <div
      style={{
        width,
        height,
        background: T.line2,
        borderRadius: 1,
        overflow: 'hidden',
        flexShrink: 0,
      }}
    >
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${clamped * 100}%` }}
        transition={scoreBarSpring}
        style={{ height: '100%', background: color }}
      />
    </div>
  )
}
