import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { LEVEL_STYLES, T } from '../theme/tokens'
import { stagger, fadeUp } from '../animation/motion'
import { AnimatedCard } from '../animation/AnimatedCard'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { Tooltip } from '../components/primitives/Tooltip'
import { ExpandableCard } from '../components/primitives/ExpandableCard'
import { Histogram } from '../components/charts/Histogram'
import { TimelineChart } from '../components/charts/TimelineChart'
import type { LiveDataResponse, QuestionDifficulty, StudentStruggle } from '../types/api'

type LevelBucket = LiveDataResponse['struggle_buckets'][number]

interface Props {
  struggle: StudentStruggle[]
  difficulty: QuestionDifficulty[]
  struggleBuckets: LevelBucket[]
  difficultyBuckets: LevelBucket[]
  timeline24h: number[]
  moduleOptions: string[]
  currentModule: string
  onSetModule: (m: string) => void
  onPickStudent: (id: string) => void
  onPickQuestion: (id: string) => void
  sessionActive: boolean
}

interface BasicRow {
  id: string
  level: string
  score: number
  widthPct: number
}

/**
 * Cohort min-max stretch with a small minimum fill so the lowest score is
 * still a visible nub. When all scores tie, every bar fills the row — colour
 * still distinguishes nothing, which is the truth of that situation.
 */
const MIN_FILL_PCT = 6

function scaleCohort<T extends { id: string; level: string; score: number }>(
  rows: T[]
): BasicRow[] {
  if (rows.length === 0) return []
  const scores = rows.map((r) => r.score)
  const min = Math.min(...scores)
  const max = Math.max(...scores)
  const span = max - min
  return rows.map((r) => {
    const pct = span > 0
      ? MIN_FILL_PCT + ((r.score - min) / span) * (100 - MIN_FILL_PCT)
      : 100
    return { id: r.id, level: r.level, score: r.score, widthPct: pct }
  })
}

const CARD_STYLE = {
  background: T.card,
  border: `1px solid ${T.line}`,
} as const

const PANEL_STYLE = {
  ...CARD_STYLE,
  padding: 16,
} as const

const LIST_CARD_STYLE = {
  ...CARD_STYLE,
  padding: 18,
  height: '100%',
  display: 'flex',
  flexDirection: 'column' as const,
  minHeight: 0,
}

export function InClassBasicView({
  struggle,
  difficulty,
  struggleBuckets,
  difficultyBuckets,
  timeline24h,
  moduleOptions,
  currentModule,
  onSetModule,
  onPickStudent,
  onPickQuestion,
  sessionActive,
}: Props) {
  const studentRows = useMemo(() => scaleCohort(struggle), [struggle])
  const questionRows = useMemo(() => scaleCohort(difficulty), [difficulty])

  return (
    <motion.div
      variants={stagger}
      initial="initial"
      animate="animate"
      style={{
        height: 'calc(100dvh - 110px)',
        padding: '16px 28px 20px',
        display: 'flex',
        flexDirection: 'column',
        gap: 14,
        minHeight: 0,
        boxSizing: 'border-box',
      }}
    >
      {/* Module filter — hidden while a session has locked the module to a specific one */}
      {!(sessionActive && currentModule !== 'All Modules') && (
        <AnimatedCard
          variants={fadeUp}
          style={{
            flex: '0 0 auto',
            display: 'flex',
            gap: 6,
            flexWrap: 'wrap',
            alignItems: 'center',
          }}
        >
          <span
            style={{
              fontFamily: T.fMono,
              fontSize: 10.5,
              color: T.ink3,
              letterSpacing: 1,
              textTransform: 'uppercase',
              marginRight: 8,
            }}
          >
            Module
          </span>
          {moduleOptions.map((m) => {
            const active = m === currentModule
            return (
              <motion.button
                key={m}
                onClick={() => onSetModule(m)}
                whileHover={{ y: -1 }}
                whileTap={{ scale: 0.95 }}
                style={{
                  padding: '5px 10px',
                  background: active ? T.priorityBg : 'transparent',
                  color: active ? T.priorityFg : T.ink2,
                  border: `1px solid ${active ? T.priorityBg : T.line2}`,
                  borderRadius: 999,
                  fontFamily: T.fSans,
                  fontSize: 12,
                  cursor: 'pointer',
                }}
              >
                {m}
              </motion.button>
            )
          })}
        </AnimatedCard>
      )}

      {/* Students | Questions — fills the remaining viewport height */}
      <AnimatedCard
        variants={fadeUp}
        style={{
          flex: '1 1 0',
          minHeight: 0,
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)',
          gap: 14,
        }}
      >
        <ExpandableCard label="Students" style={LIST_CARD_STYLE}>
          <SectionLabel n={1}>Students</SectionLabel>
          <div
            style={{
              flex: 1,
              minHeight: 0,
              overflowY: 'auto',
              marginTop: 6,
            }}
          >
            <BasicList
              rows={studentRows}
              emptyLabel="No student data yet"
              onClick={onPickStudent}
            />
          </div>
        </ExpandableCard>

        <ExpandableCard label="Questions" style={LIST_CARD_STYLE}>
          <SectionLabel n={2}>Questions</SectionLabel>
          <div
            style={{
              flex: 1,
              minHeight: 0,
              overflowY: 'auto',
              marginTop: 6,
            }}
          >
            <BasicList
              rows={questionRows}
              emptyLabel="No question data yet"
              onClick={onPickQuestion}
            />
          </div>
        </ExpandableCard>
      </AnimatedCard>

      {/* Distributions + 24h timeline */}
      <AnimatedCard
        variants={fadeUp}
        style={{
          flex: '0 0 auto',
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1.2fr)',
          gap: 14,
        }}
      >
        <ExpandableCard label="Struggle Distribution" style={PANEL_STYLE}>
          <Tooltip content="Count of students falling into each struggle band, using the composite struggle score (0–1).">
            <span style={{ cursor: 'help' }}>
              <SectionLabel n={3}>Struggle Distribution</SectionLabel>
            </span>
          </Tooltip>
          <Histogram
            data={struggleBuckets.map((b) => b.count)}
            labels={['On Track', 'Minor', 'Strug.', 'Needs']}
            bucketColors={[T.ok, T.ink3, T.warn, T.danger]}
            height={84}
          />
        </ExpandableCard>

        <ExpandableCard label="Difficulty Distribution" style={PANEL_STYLE}>
          <Tooltip content="Count of questions in each difficulty band, using the composite difficulty score (0–1).">
            <span style={{ cursor: 'help' }}>
              <SectionLabel n={4}>Difficulty Distribution</SectionLabel>
            </span>
          </Tooltip>
          <Histogram
            data={difficultyBuckets.map((b) => b.count)}
            labels={['Easy', 'Medium', 'Hard', 'V.Hard']}
            bucketColors={[T.ok, T.ink3, T.warn, T.danger]}
            height={84}
          />
        </ExpandableCard>

        <ExpandableCard label="Submissions, last 24h" style={PANEL_STYLE}>
          <Tooltip content="Wall-clock hourly submission counts for the past 24 hours. Always shows live activity, independent of the filter preset.">
            <span style={{ cursor: 'help' }}>
              <SectionLabel n={5}>Submissions, last 24h</SectionLabel>
            </span>
          </Tooltip>
          <TimelineChart data={timeline24h} semantic="hours_ago" highlightRange={[22, 23]} />
        </ExpandableCard>
      </AnimatedCard>
    </motion.div>
  )
}

function BasicList({
  rows,
  emptyLabel,
  onClick,
}: {
  rows: BasicRow[]
  emptyLabel: string
  onClick: (id: string) => void
}) {
  if (rows.length === 0) {
    return (
      <div style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink3, padding: '12px 0' }}>
        {emptyLabel}
      </div>
    )
  }
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {rows.map((r, i) => (
        <BasicRowView key={r.id} row={r} index={i} onClick={onClick} />
      ))}
    </div>
  )
}

function BasicRowView({
  row,
  index,
  onClick,
}: {
  row: BasicRow
  index: number
  onClick: (id: string) => void
}) {
  const colour = LEVEL_STYLES[row.level]?.fg ?? T.ink2
  return (
    <motion.button
      onClick={() => onClick(row.id)}
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22, delay: Math.min(index, 20) * 0.012, ease: 'easeOut' }}
      whileHover={{ background: T.bg2 }}
      style={{
        display: 'grid',
        gridTemplateColumns: '120px minmax(0, 1fr) 56px',
        alignItems: 'center',
        gap: 12,
        padding: '8px 10px',
        background: 'transparent',
        border: 'none',
        borderBottom: `1px solid ${T.line2}`,
        textAlign: 'left',
        cursor: 'pointer',
        width: '100%',
      }}
    >
      <span
        style={{
          fontFamily: T.fMono,
          fontSize: 13,
          color: T.ink,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
        title={row.id}
      >
        {row.id}
      </span>
      <div
        style={{
          height: 14,
          background: T.line2,
          borderRadius: 2,
          overflow: 'hidden',
          width: '100%',
        }}
      >
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${row.widthPct}%` }}
          transition={{ type: 'spring', stiffness: 220, damping: 30 }}
          style={{ height: '100%', background: colour }}
        />
      </div>
      <span
        style={{
          fontFamily: T.fMono,
          fontSize: 13,
          color: T.ink2,
          textAlign: 'right',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {row.score.toFixed(2)}
      </span>
    </motion.button>
  )
}
