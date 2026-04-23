import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { T, LEVEL_STYLES } from '../../theme/tokens'
import { Pill } from '../primitives/Pill'
import { ScoreBar } from '../primitives/ScoreBar'
import { rowEnter, rowLayoutSpring } from '../../animation/motion'

export type LeaderboardColumn =
  | 'rank'
  | 'id'
  | 'level'
  | 'score'
  | 'submissions'
  | 'recent'
  | 'trend'
  | 'students'
  | 'avgAttempts'
  | 'module'

export interface LeaderboardRow {
  rank: number
  id: string
  level: string
  score: number
  // union of optional fields per flavour
  submissions?: number
  recent?: number
  trend?: number
  students?: number
  avgAttempts?: number
  module?: string
  raw: unknown
}

const HEADER: Record<LeaderboardColumn, string> = {
  rank: '#',
  id: 'ID',
  level: 'Level',
  score: 'Score',
  submissions: 'Subs',
  recent: 'Recent',
  trend: 'Trend',
  students: 'Students',
  avgAttempts: 'Avg att.',
  module: 'Module',
}

function alignFor(col: LeaderboardColumn): 'left' | 'right' {
  return col === 'id' || col === 'level' || col === 'module' ? 'left' : 'right'
}

const FLASH_LEVELS: ReadonlySet<string> = new Set(['Needs Help', 'Very Hard'])

export function Leaderboard({
  title,
  subtitle,
  cols,
  rows,
  onClick,
  onHover,
}: {
  title: string
  subtitle: string
  cols: LeaderboardColumn[]
  rows: LeaderboardRow[]
  onClick: (r: LeaderboardRow) => void
  onHover?: (r: LeaderboardRow) => void
}) {
  const [hover, setHover] = useState<string | null>(null)
  const seenRef = useRef<Set<string>>(new Set())
  const [flashIds, setFlashIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    const current = new Set(rows.map((r) => r.id))
    const isFirstPaint = seenRef.current.size === 0
    const nextFlash = new Set<string>()
    if (!isFirstPaint) {
      for (const r of rows) {
        if (!seenRef.current.has(r.id) && FLASH_LEVELS.has(r.level)) {
          nextFlash.add(r.id)
        }
      }
    }
    seenRef.current = current
    if (nextFlash.size === 0) return
    // Defer the setState out of the effect body so React doesn't cascade
    // a synchronous re-render (see react-hooks/set-state-in-effect).
    const mount = window.setTimeout(() => setFlashIds(nextFlash), 0)
    const clear = window.setTimeout(() => setFlashIds(new Set()), 1400)
    return () => {
      window.clearTimeout(mount)
      window.clearTimeout(clear)
    }
  }, [rows])

  return (
    <div style={{ background: T.card, border: `1px solid ${T.line}`, minWidth: 0, overflow: 'hidden' }}>
      <div style={{ padding: '18px 22px 12px', borderBottom: `1px solid ${T.line}` }}>
        <div style={{ fontFamily: T.fSerif, fontSize: 18, color: T.ink }}>{title}</div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>{subtitle}</div>
      </div>

      <div style={{ maxHeight: 440, overflow: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
          <thead>
            <tr>
              {cols.map((c) => (
                <th
                  key={c}
                  style={{
                    textAlign: alignFor(c),
                    padding: '10px 18px',
                    fontFamily: T.fMono,
                    fontSize: 10,
                    color: T.ink3,
                    letterSpacing: 1.2,
                    textTransform: 'uppercase',
                    fontWeight: 500,
                    borderBottom: `1px solid ${T.line}`,
                    background: T.card,
                    position: 'sticky',
                    top: 0,
                    zIndex: 2,
                  }}
                >
                  {HEADER[c]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <AnimatePresence initial={false}>
              {rows.map((r) => {
                const isHover = hover === r.id
                const shouldFlash = flashIds.has(r.id)
                const flashBg = T.warn
                return (
                  <motion.tr
                    key={r.id}
                    layout
                    layoutId={`row-${r.id}`}
                    variants={rowEnter}
                    initial="initial"
                    animate={
                      shouldFlash
                        ? {
                            opacity: 1,
                            x: 0,
                            backgroundColor: [`${flashBg}44`, `${flashBg}22`, 'rgba(0,0,0,0)'],
                          }
                        : 'animate'
                    }
                    exit="exit"
                    transition={{
                      layout: rowLayoutSpring,
                      backgroundColor: { duration: 1.4, ease: 'easeOut' },
                    }}
                    onClick={() => onClick(r)}
                    onMouseEnter={() => {
                      setHover(r.id)
                      onHover?.(r)
                    }}
                    onMouseLeave={() => setHover(null)}
                    style={{
                      cursor: 'pointer',
                      background: isHover ? T.bg2 : 'transparent',
                    }}
                  >
                    {cols.map((c) => (
                      <td
                        key={c}
                        style={{
                          padding: '9px 18px',
                          borderBottom: `1px solid ${T.line2}`,
                          fontVariantNumeric: 'tabular-nums',
                          fontFamily: c === 'id' ? T.fMono : T.fSans,
                          fontSize: c === 'id' ? 12 : 13,
                          color: T.ink,
                          textAlign: alignFor(c),
                        }}
                      >
                        {renderCell(c, r)}
                      </td>
                    ))}
                  </motion.tr>
                )
              })}
            </AnimatePresence>
            {rows.length === 0 && (
              <tr>
                <td
                  colSpan={cols.length}
                  style={{ padding: 32, textAlign: 'center', color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}
                >
                  No rows yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function renderCell(col: LeaderboardColumn, r: LeaderboardRow) {
  const val = (r as unknown as Record<string, unknown>)[col]
  switch (col) {
    case 'rank':
      return (
        <span style={{ color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>
          {String(r.rank).padStart(2, '0')}
        </span>
      )
    case 'level':
      return <Pill level={r.level} />
    case 'score': {
      const color = LEVEL_STYLES[r.level]?.fg ?? T.ink
      return (
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, justifyContent: 'flex-end', width: '100%' }}>
          <ScoreBar value={r.score} color={color} width={44} height={3} />
          <span style={{ fontFamily: T.fMono, fontSize: 12 }}>{r.score.toFixed(2)}</span>
        </div>
      )
    }
    case 'trend': {
      const t = r.trend ?? 0
      return (
        <span style={{ color: t >= 0 ? T.ok : T.danger, fontFamily: T.fMono, fontSize: 12 }}>
          {t >= 0 ? '↑' : '↓'} {Math.abs(t).toFixed(2)}
        </span>
      )
    }
    case 'recent':
      return (r.recent ?? 0).toFixed(2)
    case 'avgAttempts':
      return (r.avgAttempts ?? 0).toFixed(1)
    case 'id':
    case 'module':
      return String(val ?? '')
    case 'submissions':
    case 'students':
      return typeof val === 'number' ? val.toLocaleString() : String(val ?? '')
    default:
      return String(val ?? '')
  }
}
