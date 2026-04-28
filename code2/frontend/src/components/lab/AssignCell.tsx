import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { T } from '../../theme/tokens'

export interface AssignCellAssistant {
  id: string
  name: string
  joinedAt: string
  busy: boolean
}

export interface AssignCellAssignment {
  assistantId: string
  assistantName: string
}

interface Props {
  studentId: string
  assignment: AssignCellAssignment | null
  assistants: AssignCellAssistant[]
  onAssign: (studentId: string, assistantId: string) => void
  onUnassign: (studentId: string) => void
}

function initialsOf(name: string): string {
  return name
    .split(/\s+/)
    .map((n) => n[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

function formatJoined(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const POPOVER_WIDTH = 280

export function AssignCell({ studentId, assignment, assistants, onAssign, onUnassign }: Props) {
  const [open, setOpen] = useState(false)
  const [anchor, setAnchor] = useState<{ top: number; right: number } | null>(null)
  const wrapRef = useRef<HTMLSpanElement | null>(null)
  const popRef = useRef<HTMLDivElement | null>(null)
  const buttonRef = useRef<HTMLButtonElement | null>(null)

  useEffect(() => {
    if (!open) return
    const onDown = (e: MouseEvent) => {
      const t = e.target as Node
      if (wrapRef.current?.contains(t)) return
      if (popRef.current?.contains(t)) return
      setOpen(false)
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    const reposition = () => {
      if (!buttonRef.current) return
      const r = buttonRef.current.getBoundingClientRect()
      setAnchor({ top: r.bottom + 6, right: window.innerWidth - r.right })
    }
    reposition()
    window.addEventListener('mousedown', onDown)
    window.addEventListener('keydown', onKey)
    window.addEventListener('resize', reposition)
    window.addEventListener('scroll', reposition, true)
    return () => {
      window.removeEventListener('mousedown', onDown)
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('resize', reposition)
      window.removeEventListener('scroll', reposition, true)
    }
  }, [open])

  if (assignment) {
    const firstName = assignment.assistantName.split(/\s+/)[0] ?? assignment.assistantName
    return (
      <span
        onClick={(e) => e.stopPropagation()}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '3px 4px 3px 6px',
          border: `1px solid ${T.warn}`,
          background: 'transparent',
          fontFamily: T.fSans,
          fontSize: 12,
          color: T.warn,
          letterSpacing: 0.2,
        }}
      >
        <span
          style={{
            width: 18,
            height: 18,
            borderRadius: '50%',
            background: T.bg2,
            border: `1px solid ${T.warn}`,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: T.fMono,
            fontSize: 9,
            color: T.warn,
          }}
        >
          {initialsOf(assignment.assistantName) || '—'}
        </span>
        <span>{firstName}</span>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onUnassign(studentId)
          }}
          title="Unassign"
          style={{
            marginLeft: 2,
            padding: '0 4px',
            background: 'transparent',
            border: 'none',
            color: T.warn,
            fontFamily: T.fMono,
            fontSize: 12,
            cursor: 'pointer',
            lineHeight: 1,
          }}
        >
          ×
        </button>
      </span>
    )
  }

  return (
    <span
      ref={wrapRef}
      style={{ display: 'inline-block' }}
      onClick={(e) => e.stopPropagation()}
    >
      <button
        ref={buttonRef}
        onClick={(e) => {
          e.stopPropagation()
          setOpen((v) => !v)
        }}
        style={{
          padding: '4px 9px',
          background: 'transparent',
          color: T.accent,
          border: `1px solid ${T.accent}`,
          fontFamily: T.fMono,
          fontSize: 10,
          letterSpacing: 1.2,
          textTransform: 'uppercase',
          cursor: 'pointer',
        }}
      >
        Assign ▾
      </button>
      <AnimatePresence>
        {open && anchor && (
          <motion.div
            key="popover"
            ref={popRef}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.14, ease: 'easeOut' }}
            style={{
              position: 'fixed',
              top: anchor.top,
              right: anchor.right,
              width: POPOVER_WIDTH,
              background: T.card,
              border: `1px solid ${T.accent}`,
              boxShadow: '0 10px 24px rgba(0,0,0,0.35)',
              zIndex: 1000,
              textAlign: 'left',
            }}
          >
            <div
              style={{
                padding: '10px 14px',
                borderBottom: `1px solid ${T.line2}`,
                fontFamily: T.fMono,
                fontSize: 9.5,
                letterSpacing: 1.4,
                textTransform: 'uppercase',
                color: T.ink3,
              }}
            >
              Available Assistants
            </div>
            {assistants.length === 0 ? (
              <div style={{ padding: 14, fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>
                No assistants have joined yet.
              </div>
            ) : (
              assistants.map((a) => (
                <div
                  key={a.id}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'auto minmax(0, 1fr) auto',
                    alignItems: 'center',
                    gap: 10,
                    padding: '10px 14px',
                    borderBottom: `1px solid ${T.line2}`,
                  }}
                >
                  <span
                    style={{
                      width: 26,
                      height: 26,
                      borderRadius: '50%',
                      background: T.bg2,
                      border: `1px solid ${T.line2}`,
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontFamily: T.fMono,
                      fontSize: 10,
                      color: T.ink2,
                    }}
                  >
                    {initialsOf(a.name) || '—'}
                  </span>
                  <span style={{ minWidth: 0 }}>
                    <div
                      style={{
                        fontFamily: T.fSans,
                        fontSize: 12.5,
                        color: T.ink,
                        fontWeight: 500,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {a.name}
                    </div>
                    <div style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, marginTop: 2 }}>
                      <span style={{ color: a.busy ? T.warn : T.ok }}>
                        {a.busy ? 'helping' : 'free'}
                      </span>
                      {' · joined '}
                      {formatJoined(a.joinedAt)}
                    </div>
                  </span>
                  <button
                    disabled={a.busy}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (a.busy) return
                      onAssign(studentId, a.id)
                      setOpen(false)
                    }}
                    style={{
                      padding: '4px 9px',
                      background: 'transparent',
                      color: a.busy ? T.ink3 : T.accent,
                      border: `1px solid ${a.busy ? T.line2 : T.accent}`,
                      fontFamily: T.fMono,
                      fontSize: 10,
                      letterSpacing: 1.2,
                      textTransform: 'uppercase',
                      cursor: a.busy ? 'not-allowed' : 'pointer',
                      opacity: a.busy ? 0.55 : 1,
                    }}
                  >
                    Dispatch →
                  </button>
                </div>
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </span>
  )
}
