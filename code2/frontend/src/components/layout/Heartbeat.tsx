import { AnimatePresence, motion } from 'framer-motion'
import { T } from '../../theme/tokens'

interface Props {
  /** True while any tracked `useApiData` hook is in-flight. */
  active: boolean
}

/**
 * 2px indeterminate progress bar pinned to the top of the viewport. Signals
 * that an API request is in flight so users can tell fresh-vs-stale data at
 * a glance.
 */
export function Heartbeat({ active }: Props) {
  return (
    <AnimatePresence>
      {active && (
        <motion.div
          key="heartbeat"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            height: 2,
            zIndex: 10_000,
            pointerEvents: 'none',
            background: 'transparent',
            overflow: 'hidden',
          }}
        >
          <motion.div
            animate={{ x: ['-40%', '110%'] }}
            transition={{
              duration: 1.1,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            style={{
              width: '40%',
              height: '100%',
              background: `linear-gradient(90deg, transparent, ${T.accent} 50%, transparent)`,
              boxShadow: `0 0 6px ${T.accent}`,
            }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  )
}
