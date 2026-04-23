import type { CSSProperties, ReactNode } from 'react'
import { motion } from 'framer-motion'
import { viewTransition } from './motion'

/** Wraps a view screen with an entrance/exit animation + child stagger. */
export function ViewTransition({
  children,
  style,
}: {
  children: ReactNode
  style?: CSSProperties
}) {
  return (
    <motion.div
      variants={viewTransition}
      initial="initial"
      animate="animate"
      exit="exit"
      style={{ width: '100%', ...style }}
    >
      {children}
    </motion.div>
  )
}
