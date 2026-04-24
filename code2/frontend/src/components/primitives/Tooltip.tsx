import { useId, useState, type ReactNode, type CSSProperties } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { T } from '../../theme/tokens'

/**
 * Themed hover/focus tooltip. Wraps its child and renders a positioned popover
 * on hover or keyboard focus. Use for metric labels, column headers, and any
 * compact UI where the meaning isn't self-evident.
 *
 * Accessible: triggers on focusin/focusout as well as hover, uses role="tooltip"
 * and ties the trigger to the popover via aria-describedby.
 */
export function Tooltip({
  content,
  children,
  placement = 'top',
  maxWidth = 240,
  inline = true,
}: {
  content: ReactNode
  children: ReactNode
  placement?: 'top' | 'bottom'
  maxWidth?: number
  /** When true, wrap in an inline-flex span; when false, a block div. */
  inline?: boolean
}) {
  const [open, setOpen] = useState(false)
  const id = useId()
  const hasContent = content !== undefined && content !== null && content !== ''

  const wrapStyle: CSSProperties = {
    position: 'relative',
    display: inline ? 'inline-flex' : 'block',
    alignItems: inline ? 'center' : undefined,
  }

  if (!hasContent) {
    return <span style={wrapStyle}>{children}</span>
  }

  const show = () => setOpen(true)
  const hide = () => setOpen(false)

  const bubbleStyle: CSSProperties = {
    position: 'absolute',
    left: '50%',
    transform: 'translateX(-50%)',
    zIndex: 9999,
    background: T.card,
    color: T.ink,
    border: `1px solid ${T.line2}`,
    padding: '8px 11px',
    fontFamily: T.fMono,
    fontSize: 11,
    lineHeight: 1.5,
    letterSpacing: 0.2,
    textTransform: 'none',
    width: 'max-content',
    maxWidth,
    whiteSpace: 'normal',
    textAlign: 'left',
    pointerEvents: 'none',
    boxShadow: `0 8px 24px rgba(0,0,0,0.35)`,
    ...(placement === 'top'
      ? { bottom: 'calc(100% + 8px)' }
      : { top: 'calc(100% + 8px)' }),
  }

  return (
    <span
      style={wrapStyle}
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
      aria-describedby={open ? id : undefined}
    >
      {children}
      <AnimatePresence>
        {open && (
          <motion.span
            key="tip"
            id={id}
            role="tooltip"
            initial={{ opacity: 0, y: placement === 'top' ? 4 : -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: placement === 'top' ? 4 : -4 }}
            transition={{ duration: 0.14, ease: 'easeOut' }}
            style={bubbleStyle}
          >
            {content}
          </motion.span>
        )}
      </AnimatePresence>
    </span>
  )
}
