import type { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'

export function TopBar({
  breadcrumbs,
  title,
  right,
}: {
  breadcrumbs: string
  title: string
  right?: ReactNode
}) {
  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'flex-end',
        justifyContent: 'space-between',
        padding: '26px 36px 18px',
        borderBottom: `1px solid ${T.border}`,
        background: T.bg,
        gap: 24,
      }}
    >
      <div>
        <motion.div
          key={breadcrumbs}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          style={{ fontFamily: T.fMono, fontSize: 10.5, letterSpacing: 1.4, color: T.ink3, textTransform: 'uppercase' }}
        >
          {breadcrumbs}
        </motion.div>
        <motion.h2
          key={title}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          style={{ fontSize: 28, fontWeight: 600, margin: '4px 0 0' }}
        >
          {title}
        </motion.h2>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {right}
      </div>
    </header>
  )
}
