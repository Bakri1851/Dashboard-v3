import { useEffect, useState } from 'react'
import type { CSSProperties, ReactNode } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { T } from '../../theme/tokens'

interface Props {
  children: ReactNode
  /** Style applied to both the inline slot and the expanded overlay (background, border, padding…). */
  style?: CSSProperties
  /** Tooltip / aria-label suffix for the toggle button (e.g. "Students"). */
  label?: string
}

/**
 * Wraps any block of content with an expand/shrink button at the top-right.
 * When expanded, the content is mirrored into a fixed-positioned overlay with
 * a click-away backdrop. The inline slot stays in its layout position
 * (visibility: hidden) to avoid surrounding cards reflowing while expanded.
 */
export function ExpandableCard({ children, style, label }: Props) {
  const [expanded, setExpanded] = useState(false)

  // Esc closes the overlay — standard modal affordance.
  useEffect(() => {
    if (!expanded) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setExpanded(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [expanded])

  return (
    <>
      <div
        style={{
          ...style,
          position: 'relative',
          visibility: expanded ? 'hidden' : 'visible',
        }}
      >
        <ToggleButton expanded={false} label={label} onClick={() => setExpanded(true)} />
        {children}
      </div>

      <AnimatePresence>
        {expanded && (
          <>
            <motion.div
              key="bg"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.18 }}
              onClick={() => setExpanded(false)}
              style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(0,0,0,0.55)',
                zIndex: 99,
              }}
            />
            <motion.div
              key="ov"
              initial={{ scale: 0.96, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.96, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 280, damping: 32 }}
              style={{
                ...style,
                position: 'fixed',
                top: '4vh',
                left: '4vw',
                right: '4vw',
                bottom: '4vh',
                zIndex: 100,
                overflow: 'auto',
                boxShadow: '0 24px 80px rgba(0,0,0,0.5)',
              }}
            >
              <ToggleButton expanded={true} label={label} onClick={() => setExpanded(false)} />
              {children}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

function ToggleButton({
  expanded,
  label,
  onClick,
}: {
  expanded: boolean
  label?: string
  onClick: () => void
}) {
  const title = expanded
    ? label ? `Shrink ${label}` : 'Shrink'
    : label ? `Enlarge ${label}` : 'Enlarge'
  return (
    <button
      onClick={onClick}
      title={title}
      aria-label={title}
      style={{
        position: 'absolute',
        top: 10,
        right: 10,
        width: 28,
        height: 28,
        background: T.bg2,
        border: `1px solid ${T.line}`,
        color: T.ink2,
        cursor: 'pointer',
        zIndex: 3,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 0,
      }}
    >
      {expanded ? <ShrinkIcon /> : <ExpandIcon />}
    </button>
  )
}

function ExpandIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square">
      <polyline points="15 3 21 3 21 9" />
      <polyline points="9 21 3 21 3 15" />
      <line x1="21" y1="3" x2="14" y2="10" />
      <line x1="3" y1="21" x2="10" y2="14" />
    </svg>
  )
}

function ShrinkIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square">
      <polyline points="4 14 10 14 10 20" />
      <polyline points="20 10 14 10 14 4" />
      <line x1="14" y1="10" x2="21" y2="3" />
      <line x1="3" y1="21" x2="10" y2="14" />
    </svg>
  )
}
