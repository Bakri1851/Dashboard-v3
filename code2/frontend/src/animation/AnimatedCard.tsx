import type { ComponentProps, ReactNode } from 'react'
import { motion } from 'framer-motion'
import { fadeUp } from './motion'

type Props = ComponentProps<typeof motion.div> & {
  children: ReactNode
}

/** Section-level card wrapper — fades/slides in with the parent stagger. */
export function AnimatedCard({ children, variants, ...rest }: Props) {
  return (
    <motion.div variants={variants ?? fadeUp} {...rest}>
      {children}
    </motion.div>
  )
}
