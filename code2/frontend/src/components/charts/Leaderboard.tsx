import { useState } from 'react'
import { T, LEVEL_STYLES } from '../../theme/tokens'
import { Pill } from '../primitives/Pill'
import { ScoreBar } from '../primitives/ScoreBar'

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

export function Leaderboard({
  title,
  subtitle,
  cols,
  rows,
  onClick,
}: {
  title: string
  subtitle: string
  cols: LeaderboardColumn[]
  rows: LeaderboardRow[]
  onClick: (r: LeaderboardRow) => void
}) {
  const [hover, setHover] = useState<number | null>(null)

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
                  }}
                >
                  {HEADER[c]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr
                key={`${r.id}-${i}`}
                onClick={() => onClick(r)}
                onMouseEnter={() => setHover(i)}
                onMouseLeave={() => setHover(null)}
                style={{ cursor: 'pointer', background: hover === i ? T.bg2 : 'transparent' }}
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
              </tr>
            ))}
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
