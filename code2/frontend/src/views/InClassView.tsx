import { useEffect, useMemo, useRef } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { T } from '../theme/tokens'
import { prefetchApi, useApiData } from '../api/hooks'
import { AnimatedCard } from '../animation/AnimatedCard'
import { stagger, fadeUp } from '../animation/motion'
import { AnimatedNumber } from '../components/primitives/AnimatedNumber'
import { Skeleton, SkeletonStatCard } from '../components/primitives/Skeleton'
import { useAutoRefreshInterval } from '../api/useAutoRefreshInterval'
import { useFilterQuery } from '../api/filterQuery'
import { useFilterStore, presetNote } from '../state/filterStore'
import { useUiPrefsStore } from '../state/uiPrefsStore'
import { useSettings } from '../api/useSettings'
import { InClassBasicView } from './InClassBasicView'
import type {
  CFDiagnostics,
  LiveDataResponse,
  QuestionDifficulty,
  StudentStruggle,
} from '../types/api'
import { Pill } from '../components/primitives/Pill'
import { ScoreBar } from '../components/primitives/ScoreBar'
import { Stat } from '../components/primitives/Stat'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { LevelChips } from '../components/primitives/LevelChips'
import { Tooltip } from '../components/primitives/Tooltip'
import { ExpandableCard } from '../components/primitives/ExpandableCard'
import { Histogram } from '../components/charts/Histogram'
import { TimelineChart } from '../components/charts/TimelineChart'
import {
  Leaderboard,
  type LeaderboardColumn,
  type LeaderboardRow,
} from '../components/charts/Leaderboard'

interface Props {
  onPickStudent: (id: string) => void
  onPickQuestion: (id: string) => void
  onOpenLab: () => void
  sessionActive: boolean
}

const STRUGGLE_COLS: LeaderboardColumn[] = ['rank', 'id', 'level', 'score', 'submissions', 'recent', 'trend']
const DIFFICULTY_COLS: LeaderboardColumn[] = ['rank', 'id', 'level', 'score', 'students', 'avgAttempts', 'module']

const STRUGGLE_CHIP_HELP: Record<string, string> = {
  'On Track': 'Struggle score < 0.20. Performing well — low incorrectness and positive trends.',
  'Minor Issues': 'Struggle score 0.20–0.35. Some difficulty present. Monitor over upcoming submissions.',
  Struggling: 'Struggle score 0.35–0.50. Consistent difficulty signals. Consider checking in soon.',
  'Needs Help':
    'Struggle score ≥ 0.50. Highest combined incorrectness, retry rate, and recent difficulty. Immediate attention recommended.',
}

const DIFFICULTY_CHIP_HELP: Record<string, string> = {
  Easy: 'Difficulty score < 0.25. Most students answer correctly quickly and on the first attempt.',
  Medium: 'Difficulty score 0.25–0.50. Typical range — some retries, most get there.',
  Hard: 'Difficulty score 0.50–0.75. High retry rates or first-attempt failures. Worth reviewing.',
  'Very Hard':
    'Difficulty score ≥ 0.75. Most students struggle — high incorrectness, many attempts, poor first-fail rate.',
}

export function InClassView({ onPickStudent, onPickQuestion, onOpenLab, sessionActive }: Props) {
  const q = useFilterQuery()
  const filter = useFilterStore()
  const inClassViewMode = useUiPrefsStore((s) => s.inClassViewMode)
  const { data: settings } = useSettings()
  const cfEnabled = settings?.runtime.cf_enabled ?? false
  const liveInterval = useAutoRefreshInterval(10_000)
  const strugInterval = useAutoRefreshInterval(15_000)
  const diffInterval = useAutoRefreshInterval(15_000)
  const cfInterval = useAutoRefreshInterval(30_000)
  const { data: live, error: liveErr, loading: liveLoading } =
    useApiData<LiveDataResponse>('/live', liveInterval, q)
  const { data: struggle, error: strugErr, loading: strugLoading } =
    useApiData<StudentStruggle[]>('/struggle', strugInterval, q)
  const { data: difficulty, error: diffErr, loading: diffLoading } =
    useApiData<QuestionDifficulty[]>('/difficulty', diffInterval, q)
  const { data: cf } = useApiData<CFDiagnostics>(cfEnabled ? '/cf' : '', cfInterval, q)
  const anyError = liveErr || strugErr || diffErr
  const anyLoading = liveLoading || strugLoading || diffLoading

  const moduleFilter = filter.module
  const setModuleFilter = filter.setModule

  // Debounce hover-prefetch so sweeping the mouse across rows doesn't fan out
  // into a dozen concurrent /rag/ requests that saturate the backend threadpool.
  const hoverTimer = useRef<number | null>(null)
  const debouncedPrefetch = (path: string) => {
    if (hoverTimer.current) window.clearTimeout(hoverTimer.current)
    hoverTimer.current = window.setTimeout(() => prefetchApi(path), 150)
  }
  useEffect(() => () => {
    if (hoverTimer.current) window.clearTimeout(hoverTimer.current)
  }, [])

  // Pill options come from /live.modules (full unfiltered list) so that
  // picking a module doesn't collapse the pill row to a single entry.
  const moduleOptions = useMemo(() => {
    return ['All Modules', ...(live?.modules ?? [])]
  }, [live?.modules])

  const filteredDifficulty = useMemo<LeaderboardRow[]>(() => {
    if (!difficulty) return []
    return difficulty.slice(0, 15).map((q, i) => ({
      rank: i + 1,
      id: q.id,
      level: q.level,
      score: q.score,
      students: q.students,
      avgAttempts: q.avgAttempts,
      module: q.module,
      raw: q,
    }))
  }, [difficulty])

  const struggleRows = useMemo<LeaderboardRow[]>(() => {
    if (!struggle) return []
    return struggle.slice(0, 15).map((s, i) => ({
      rank: i + 1,
      id: s.id,
      level: s.level,
      score: s.score,
      submissions: s.submissions,
      recent: s.recent,
      trend: s.trend,
      raw: s,
    }))
  }, [struggle])

  // Hero stats
  const records = live?.records ?? 0
  const students = live?.unique_students ?? 0
  const questions = live?.unique_questions ?? 0
  const meanInc = live?.mean_incorrectness ?? 0
  const needsHelp = live?.struggle_buckets.find((b) => b.label === 'Needs Help')?.count ?? 0
  const strugCount = live?.struggle_buckets.find((b) => b.label === 'Struggling')?.count ?? 0

  const timeline = live?.timeline_24h ?? []
  const struggleBuckets = live?.struggle_buckets ?? []
  const difficultyBuckets = live?.difficulty_buckets ?? []

  // Auto-fallback: if preset is 'today' and today has no records, switch to 'all'
  // once. The flag prevents ping-pong between the two presets.
  useEffect(() => {
    if (!live) return
    if (filter.preset === 'today' && records === 0 && !filter.autoFallbackApplied) {
      filter.setAutoFallbackApplied(true)
      filter.setPreset('all')
    }
  }, [live, records, filter])

  const showFallbackBanner =
    filter.autoFallbackApplied && filter.preset === 'all' && records > 0

  const submissionsNote = presetNote(filter.preset)

  if (inClassViewMode === 'basic') {
    return (
      <InClassBasicView
        struggle={struggle ?? []}
        difficulty={difficulty ?? []}
        struggleBuckets={struggleBuckets}
        difficultyBuckets={difficultyBuckets}
        timeline24h={timeline}
        moduleOptions={moduleOptions}
        currentModule={moduleFilter}
        onSetModule={setModuleFilter}
        onPickStudent={onPickStudent}
        onPickQuestion={onPickQuestion}
        sessionActive={sessionActive}
      />
    )
  }

  return (
    <motion.div
      variants={stagger}
      initial="initial"
      animate="animate"
      style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 28 }}
    >
      <AnimatePresence initial={false}>
        {anyError && (
          <motion.div
            key="err-banner"
            layout
            initial={{ opacity: 0, height: 0, y: -6 }}
            animate={{ opacity: 1, height: 'auto', y: 0 }}
            exit={{ opacity: 0, height: 0, y: -6 }}
            transition={{ duration: 0.26, ease: [0.22, 1, 0.36, 1] }}
            style={{ overflow: 'hidden' }}
          >
            <div
              style={{
                padding: '12px 16px',
                border: `1px solid ${T.danger}`,
                background: T.card,
                color: T.danger,
                fontFamily: T.fMono,
                fontSize: 12,
                lineHeight: 1.5,
              }}
            >
              <div style={{ fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase', fontSize: 10 }}>
                Backend unreachable
              </div>
              <div style={{ color: T.ink2, marginTop: 4 }}>
                {liveErr ?? strugErr ?? diffErr}
              </div>
              <div style={{ color: T.ink3, marginTop: 6 }}>
                Start the FastAPI backend: <code style={{ background: T.bg2, padding: '1px 4px' }}>
                  uvicorn backend.main:app --app-dir code2 --port 8000 --reload
                </code>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      {anyLoading && !anyError && !live && (
        <AnimatedCard variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr)', gap: 12 }}>
          <SkeletonStatCard height={148} />
          <SkeletonStatCard />
          <SkeletonStatCard />
          <SkeletonStatCard />
          <SkeletonStatCard />
        </AnimatedCard>
      )}
      <AnimatePresence initial={false}>
        {showFallbackBanner && (
          <motion.div
            key="fallback-banner"
            layout
            initial={{ opacity: 0, height: 0, y: -6 }}
            animate={{ opacity: 1, height: 'auto', y: 0 }}
            exit={{ opacity: 0, height: 0, y: -6 }}
            transition={{ duration: 0.26, ease: [0.22, 1, 0.36, 1] }}
            style={{ overflow: 'hidden' }}
          >
            <div
              style={{
                padding: '10px 14px',
                border: `1px solid ${T.line2}`,
                background: T.card,
                color: T.ink2,
                fontFamily: T.fMono,
                fontSize: 11,
                display: 'flex',
                alignItems: 'center',
                gap: 12,
              }}
            >
              <span style={{ color: T.ink3, letterSpacing: 1, textTransform: 'uppercase', fontSize: 10 }}>
                No activity today
              </span>
              <span>— showing all time.</span>
              <motion.button
                onClick={() => {
                  filter.setAutoFallbackApplied(false)
                  filter.setPreset('today')
                }}
                whileHover={{ borderColor: T.ink2, color: T.ink }}
                whileTap={{ scale: 0.96 }}
                transition={{ duration: 0.15 }}
                style={{
                  marginLeft: 'auto',
                  padding: '4px 10px',
                  fontFamily: T.fMono,
                  fontSize: 10,
                  background: 'transparent',
                  color: T.ink2,
                  border: `1px solid ${T.line}`,
                  letterSpacing: 1,
                  textTransform: 'uppercase',
                  cursor: 'pointer',
                }}
              >
                Back to today
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      {/* Hero stats */}
      {live && (
      <AnimatedCard variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr)', gap: 12 }}>
        <div
          style={{
            padding: '20px 22px',
            background: T.priorityBg,
            color: T.priorityFg,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            borderRadius: 2,
          }}
        >
          <div
            style={{
              fontFamily: T.fMono,
              fontSize: 10.5,
              letterSpacing: 1.3,
              textTransform: 'uppercase',
              opacity: 0.75,
            }}
          >
            <Tooltip content="Students with composite struggle score ≥ 0.50 (Needs Help band). Click 'Dispatch Assistants' to push them out to lab assistants.">
              <span style={{ cursor: 'help', borderBottom: `1px dotted currentColor` }}>Priority Now</span>
            </Tooltip>
          </div>
          <div>
            <AnimatedNumber
              value={String(needsHelp)}
              style={{
                fontFamily: T.fSerif,
                fontSize: 56,
                lineHeight: 0.95,
                fontFeatureSettings: '"tnum"',
                color: T.priorityFg,
                display: 'inline-block',
              }}
            />
            <div style={{ fontFamily: T.fMono, fontSize: 11, marginTop: 8, opacity: 0.8 }}>
              students need help · {strugCount} struggling
            </div>
            <div style={{ marginTop: 14 }}>
              <motion.button
                onClick={onOpenLab}
                disabled={!sessionActive}
                whileHover={sessionActive ? { scale: 1.03 } : undefined}
                whileTap={sessionActive ? { scale: 0.97 } : undefined}
                style={{
                  padding: '6px 12px',
                  background: 'transparent',
                  color: T.priorityFg,
                  border: `1px solid ${T.priorityFg}`,
                  fontFamily: T.fMono,
                  fontSize: 10.5,
                  letterSpacing: 1.2,
                  textTransform: 'uppercase',
                  cursor: sessionActive ? 'pointer' : 'not-allowed',
                  opacity: sessionActive ? 0.9 : 0.4,
                }}
              >
                Dispatch Assistants →
              </motion.button>
            </div>
          </div>
        </div>
        <Stat
          label="Total Submissions"
          value={records.toLocaleString()}
          note={submissionsNote}
          help="Count of answer records in the current time window, after any active filters."
        />
        <Stat
          label="Unique Students"
          value={String(students)}
          note="loaded records"
          accent={T.accent}
          help="Distinct student IDs who submitted at least one answer in this window."
        />
        <Stat
          label="Questions Answered"
          value={String(questions)}
          note={`across ${live?.unique_modules ?? 0} modules`}
          help="Distinct question IDs attempted by any student in this window."
        />
        <Stat
          label="Mean Incorrectness"
          value={meanInc.toFixed(2)}
          note="class average"
          accent={T.warn}
          help="Class-average AI-scored incorrectness (0 = fully correct, 1 = fully incorrect). An answer counts as incorrect when its score ≥ 0.50."
        />
      </AnimatedCard>
      )}

      {/* Module filter — hidden while a session has locked the module to a specific one */}
      {!(sessionActive && moduleFilter !== 'All Modules') && (
        <AnimatedCard variants={fadeUp} style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
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
            const active = m === moduleFilter
            return (
              <motion.button
                key={m}
                onClick={() => setModuleFilter(m)}
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

      {/* Threshold-count chip rows — one per leaderboard */}
      {live && (struggleBuckets.length > 0 || difficultyBuckets.length > 0) && (
        <AnimatedCard
          variants={fadeUp}
          style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 24 }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <span
              style={{
                fontFamily: T.fMono,
                fontSize: 10,
                color: T.ink3,
                letterSpacing: 1.2,
                textTransform: 'uppercase',
              }}
            >
              <Tooltip content="Count of students in each struggle band — use to see at a glance how the class is distributed.">
                <span style={{ cursor: 'help', borderBottom: `1px dotted currentColor` }}>
                  Students per struggle level
                </span>
              </Tooltip>
            </span>
            <LevelChips buckets={struggleBuckets} tooltips={STRUGGLE_CHIP_HELP} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <span
              style={{
                fontFamily: T.fMono,
                fontSize: 10,
                color: T.ink3,
                letterSpacing: 1.2,
                textTransform: 'uppercase',
              }}
            >
              <Tooltip content="Count of questions in each difficulty band.">
                <span style={{ cursor: 'help', borderBottom: `1px dotted currentColor` }}>
                  Questions per difficulty level
                </span>
              </Tooltip>
            </span>
            <LevelChips buckets={difficultyBuckets} tooltips={DIFFICULTY_CHIP_HELP} />
          </div>
        </AnimatedCard>
      )}

      {/* Two leaderboards */}
      <AnimatedCard variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 24 }}>
        <ExpandableCard label="Student Struggle">
          <Leaderboard
            title="Student Struggle"
            subtitle="Ranked by composite struggle score · click to drill in"
            cols={STRUGGLE_COLS}
            rows={struggleRows}
            onClick={(r) => onPickStudent(r.id)}
            onHover={(r) => debouncedPrefetch(`/rag/student/${encodeURIComponent(r.id)}`)}
          />
        </ExpandableCard>
        <ExpandableCard label="Question Difficulty">
          <Leaderboard
            title="Question Difficulty"
            subtitle="Ranked by composite difficulty score · click for mistake clusters"
            cols={DIFFICULTY_COLS}
            rows={filteredDifficulty}
            onClick={(r) => onPickQuestion(r.id)}
            onHover={(r) => debouncedPrefetch(`/rag/question/${encodeURIComponent(r.id)}`)}
          />
        </ExpandableCard>
      </AnimatedCard>

      {strugLoading && !struggle && (
        <AnimatedCard variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 24 }}>
          <LeaderboardSkeleton />
          <LeaderboardSkeleton />
        </AnimatedCard>
      )}

      {/* CF panel (when enabled) */}
      {cfEnabled && cf && (
        <AnimatedCard variants={fadeUp}>
          <ExpandableCard
            label="Collaborative Filtering"
            style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}
          >
          <SectionLabel n={4}>Collaborative Filtering</SectionLabel>
          {cf.fallback ? (
            <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>
              CF skipped — {cf.reason ?? 'insufficient data'}
            </div>
          ) : (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 12, marginBottom: 16 }}>
                <Stat label="Parametric flagged" value={String(cf.n_flagged_parametric)} note={`τ = ${cf.threshold.toFixed(2)}`} />
                <Stat label="CF elevated" value={String(cf.n_elevated_cf)} note={`k = ${cf.k} neighbours`} accent={T.accent} />
                <Stat label="Agreement" value={cf.n_flagged_parametric > 0 ? `${Math.round((1 - cf.n_elevated_cf / Math.max(cf.n_flagged_parametric, 1)) * 100)}%` : '—'} note="lower = CF disagrees more" />
              </div>
              {cf.elevated_students.length > 0 && (
                <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
                  <thead>
                    <tr>
                      {['Student', 'Level', 'Baseline', 'CF score', 'Δ'].map((h) => (
                        <th key={h} style={{
                          textAlign: h === 'Student' || h === 'Level' ? 'left' : 'right',
                          padding: '8px 12px',
                          fontFamily: T.fMono,
                          fontSize: 10,
                          color: T.ink3,
                          letterSpacing: 1.2,
                          textTransform: 'uppercase',
                          fontWeight: 500,
                          borderBottom: `1px solid ${T.line}`,
                        }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <AnimatePresence initial={false}>
                      {cf.elevated_students.map((s) => (
                        <motion.tr
                          key={s.id}
                          layout
                          initial={{ opacity: 0, x: -8 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: 12 }}
                          transition={{
                            layout: { type: 'spring', stiffness: 400, damping: 38 },
                            opacity: { duration: 0.2 },
                          }}
                          onClick={() => onPickStudent(s.id)}
                          whileHover={{ background: T.bg2 }}
                          style={{ cursor: 'pointer' }}
                        >
                          <td style={{ padding: '8px 12px', fontFamily: T.fMono, fontSize: 12, color: T.ink, borderBottom: `1px solid ${T.line2}` }}>{s.id}</td>
                          <td style={{ padding: '8px 12px', borderBottom: `1px solid ${T.line2}` }}><Pill level={s.level} /></td>
                          <td style={{ padding: '8px 12px', textAlign: 'right', fontFamily: T.fMono, fontSize: 12, color: T.ink2, borderBottom: `1px solid ${T.line2}` }}>{s.baseline_score.toFixed(2)}</td>
                          <td style={{ padding: '8px 12px', textAlign: 'right', borderBottom: `1px solid ${T.line2}` }}>
                            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, justifyContent: 'flex-end', width: '100%' }}>
                              <ScoreBar value={s.cf_score} color={T.accent} width={44} height={3} />
                              <span style={{ fontFamily: T.fMono, fontSize: 12 }}>{s.cf_score.toFixed(2)}</span>
                            </div>
                          </td>
                          <td style={{ padding: '8px 12px', textAlign: 'right', fontFamily: T.fMono, fontSize: 12, color: s.delta >= 0 ? T.accent : T.ink3, borderBottom: `1px solid ${T.line2}` }}>
                            {s.delta >= 0 ? '+' : ''}{s.delta.toFixed(2)}
                          </td>
                        </motion.tr>
                      ))}
                    </AnimatePresence>
                  </tbody>
                </table>
              )}
            </div>
          )}
          </ExpandableCard>
        </AnimatedCard>
      )}

      {/* Distributions + timeline */}
      <AnimatedCard variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1.2fr)', gap: 24 }}>
        <ExpandableCard label="Struggle Distribution" style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <Tooltip content="Count of students falling into each struggle band, using the composite struggle score (0–1).">
            <span style={{ cursor: 'help' }}>
              <SectionLabel n={1}>Struggle Distribution</SectionLabel>
            </span>
          </Tooltip>
          <Histogram
            data={struggleBuckets.map((b) => b.count)}
            labels={['On Track', 'Minor', 'Strug.', 'Needs']}
            bucketColors={[T.ok, T.ink3, T.warn, T.danger]}
            height={100}
          />
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 14, lineHeight: 1.6 }}>
            Thresholds: on track &lt; 0.20 · minor &lt; 0.35 · struggling &lt; 0.50 · needs help ≥ 0.50
          </div>
        </ExpandableCard>
        <ExpandableCard label="Difficulty Distribution" style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <Tooltip content="Count of questions in each difficulty band, using the composite difficulty score (0–1).">
            <span style={{ cursor: 'help' }}>
              <SectionLabel n={2}>Difficulty Distribution</SectionLabel>
            </span>
          </Tooltip>
          <Histogram
            data={difficultyBuckets.map((b) => b.count)}
            labels={['Easy', 'Medium', 'Hard', 'V.Hard']}
            bucketColors={[T.ok, T.ink3, T.warn, T.danger]}
            height={100}
          />
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 14, lineHeight: 1.6 }}>
            D = 0.28·c + 0.12·t + 0.20·a + 0.20·f + 0.20·p &nbsp;·&nbsp; weighted
          </div>
        </ExpandableCard>
        <ExpandableCard label="Submissions, last 24h" style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <Tooltip content="Wall-clock hourly submission counts for the past 24 hours. Always shows live activity, independent of the filter preset.">
            <span style={{ cursor: 'help' }}>
              <SectionLabel n={3}>Submissions, last 24h</SectionLabel>
            </span>
          </Tooltip>
          <TimelineChart data={timeline} semantic="hours_ago" highlightRange={[22, 23]} />
        </ExpandableCard>
      </AnimatedCard>
    </motion.div>
  )
}

function LeaderboardSkeleton() {
  return (
    <div style={{ background: T.card, border: `1px solid ${T.line}`, padding: 20 }}>
      <Skeleton variant="text" width="40%" height={14} />
      <div style={{ height: 8 }} />
      <Skeleton variant="text" width="60%" height={10} />
      <div style={{ height: 18 }} />
      <Skeleton variant="text" rows={6} />
    </div>
  )
}
