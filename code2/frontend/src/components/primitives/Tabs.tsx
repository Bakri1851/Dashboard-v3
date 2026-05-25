import { useRef } from 'react'
import type { CSSProperties, KeyboardEvent, ReactNode } from 'react'
import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'

export interface TabDef {
  id: string
  label: string
}

interface Props {
  tabs: TabDef[]
  activeId: string
  onChange: (id: string) => void
  children: ReactNode
  style?: CSSProperties
}

/**
 * Horizontal pill-strip tab navigator. Caller renders the active panel via
 * the `children` prop and decides which panel to mount based on `activeId`.
 * Left/right arrow keys cycle focus + selection across the tab strip.
 */
export function Tabs({ tabs, activeId, onChange, children, style }: Props) {
  const buttonRefs = useRef<(HTMLButtonElement | null)[]>([])

  const moveFocus = (fromIdx: number, delta: number) => {
    if (!tabs.length) return
    const next = (fromIdx + delta + tabs.length) % tabs.length
    onChange(tabs[next].id)
    requestAnimationFrame(() => buttonRefs.current[next]?.focus())
  }

  const onKeyDown = (e: KeyboardEvent<HTMLButtonElement>, idx: number) => {
    if (e.key === 'ArrowRight') {
      e.preventDefault()
      moveFocus(idx, 1)
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault()
      moveFocus(idx, -1)
    } else if (e.key === 'Home') {
      e.preventDefault()
      moveFocus(-1, 1)
    } else if (e.key === 'End') {
      e.preventDefault()
      moveFocus(0, -1)
    }
  }

  return (
    <div style={style}>
      <div
        role="tablist"
        aria-label="Settings sections"
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 6,
          padding: '8px 0 14px',
          borderBottom: `1px solid ${T.line}`,
          marginBottom: 18,
        }}
      >
        {tabs.map((t, i) => {
          const active = t.id === activeId
          return (
            <motion.button
              key={t.id}
              ref={(el) => {
                buttonRefs.current[i] = el
              }}
              role="tab"
              aria-selected={active}
              aria-controls={`tabpanel-${t.id}`}
              id={`tab-${t.id}`}
              tabIndex={active ? 0 : -1}
              onClick={() => onChange(t.id)}
              onKeyDown={(e) => onKeyDown(e, i)}
              whileHover={active ? undefined : { y: -1 }}
              whileTap={{ scale: 0.97 }}
              style={{
                padding: '7px 16px',
                background: active ? T.accent : 'transparent',
                color: active ? '#fff' : T.ink2,
                border: `1px solid ${active ? T.accent : T.line}`,
                borderRadius: 999,
                fontFamily: T.fMono,
                fontSize: 11,
                letterSpacing: 1.2,
                textTransform: 'uppercase',
                cursor: 'pointer',
              }}
            >
              {t.label}
            </motion.button>
          )
        })}
      </div>
      <div
        role="tabpanel"
        id={`tabpanel-${activeId}`}
        aria-labelledby={`tab-${activeId}`}
      >
        {children}
      </div>
    </div>
  )
}
