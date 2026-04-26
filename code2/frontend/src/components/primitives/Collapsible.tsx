import { useState } from 'react'
import type { CSSProperties, ReactNode } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { T } from '../../theme/tokens'
import { SectionLabel } from './SectionLabel'

interface Props {
  n: number
  title: string
  count?: number
  defaultOpen?: boolean
  children: ReactNode
  style?: CSSProperties
}

/**
 * Inline accordion: header bar always visible; body collapses by default and
 * opens with a height animation on click. Distinct from `ExpandableCard`,
 * which expands to a fullscreen overlay.
 */
export function Collapsible({
  n,
  title,
  count,
  defaultOpen = false,
  children,
  style,
}: Props) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div
      style={{
        background: T.card,
        border: `1px solid ${T.line}`,
        ...style,
      }}
    >
      <button
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          textAlign: 'left',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 12 }}>
          {/* SectionLabel includes its own marginBottom; neutralise it inside the button */}
          <div style={{ marginBottom: -14 }}>
            <SectionLabel n={n}>{title}</SectionLabel>
          </div>
          {typeof count === 'number' && (
            <span
              style={{
                fontFamily: T.fMono,
                fontSize: 11,
                color: T.ink3,
                letterSpacing: 1,
              }}
            >
              · {count} {count === 1 ? 'item' : 'items'}
            </span>
          )}
        </div>
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 24,
            height: 24,
            color: T.ink2,
          }}
          aria-hidden
        >
          <ChevronDown />
        </motion.span>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
            style={{ overflow: 'hidden' }}
          >
            <div style={{ padding: '4px 16px 16px' }}>{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function ChevronDown() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square">
      <polyline points="6 9 12 15 18 9" />
    </svg>
  )
}
