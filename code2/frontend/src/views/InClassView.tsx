import { useMemo, useState } from 'react'
import { T } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import type {
  LiveDataResponse,
  QuestionDifficulty,
  StudentStruggle,
} from '../types/api'
import { Stat } from '../components/primitives/Stat'
import { SectionLabel } from '../components/primitives/SectionLabel'
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

export function InClassView({ onPickStudent, onPickQuestion, onOpenLab, sessionActive }: Props) {
  const { data: live, error: liveErr, loading: liveLoading } = useApiData<LiveDataResponse>('/live', 10_000)
  const { data: struggle, error: strugErr, loading: strugLoading } =
    useApiData<StudentStruggle[]>('/struggle', 15_000)
  const { data: difficulty, error: diffErr, loading: diffLoading } =
    useApiData<QuestionDifficulty[]>('/difficulty', 15_000)
  const anyError = liveErr || strugErr || diffErr
  const anyLoading = liveLoading || strugLoading || diffLoading

  const [moduleFilter, setModuleFilter] = useState<string>('All Modules')

  const moduleOptions = useMemo(() => {
    const mods = new Set<string>()
    difficulty?.forEach((q) => q.module && mods.add(q.module))
    return ['All Modules', ...Array.from(mods).sort()]
  }, [difficulty])

  const filteredDifficulty = useMemo(() => {
    if (!difficulty) return []
    const rows = moduleFilter === 'All Modules' ? difficulty : difficulty.filter((q) => q.module === moduleFilter)
    return rows.slice(0, 15).map<LeaderboardRow>((q, i) => ({
      rank: i + 1,
      id: q.id,
      level: q.level,
      score: q.score,
      students: q.students,
      avgAttempts: q.avgAttempts,
      module: q.module,
      raw: q,
    }))
  }, [difficulty, moduleFilter])

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

  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 28 }}>
      {anyError && (
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
      )}
      {anyLoading && !anyError && (
        <div
          style={{
            padding: '10px 14px',
            border: `1px dashed ${T.line2}`,
            color: T.ink3,
            fontFamily: T.fMono,
            fontSize: 11,
            letterSpacing: 1,
            textTransform: 'uppercase',
          }}
        >
          Loading live data…
        </div>
      )}
      {/* Hero stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr)', gap: 12 }}>
        <div
          style={{
            padding: '20px 22px',
            background: T.ink,
            color: '#ffffff',
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
              opacity: 0.7,
            }}
          >
            Priority Now
          </div>
          <div>
            <div
              style={{
                fontFamily: T.fSerif,
                fontSize: 56,
                lineHeight: 0.95,
                fontFeatureSettings: '"tnum"',
              }}
            >
              {needsHelp}
            </div>
            <div style={{ fontFamily: T.fMono, fontSize: 11, marginTop: 8, opacity: 0.75 }}>
              students need help · {strugCount} struggling
            </div>
            <div style={{ marginTop: 14 }}>
              <button
                onClick={onOpenLab}
                disabled={!sessionActive}
                style={{
                  padding: '6px 12px',
                  background: 'transparent',
                  color: '#ffffff',
                  border: '1px solid rgba(255,255,255,0.4)',
                  fontFamily: T.fMono,
                  fontSize: 10.5,
                  letterSpacing: 1.2,
                  textTransform: 'uppercase',
                  cursor: sessionActive ? 'pointer' : 'not-allowed',
                  opacity: sessionActive ? 1 : 0.4,
                }}
              >
                Dispatch Assistants →
              </button>
            </div>
          </div>
        </div>
        <Stat label="Total Submissions" value={records.toLocaleString()} note="all-time" />
        <Stat label="Unique Students" value={String(students)} note="loaded records" accent={T.accent} />
        <Stat label="Questions Answered" value={String(questions)} note={`across ${live?.unique_modules ?? 0} modules`} />
        <Stat label="Mean Incorrectness" value={meanInc.toFixed(2)} note="class average" accent={T.warn} />
      </div>

      {/* Module filter */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
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
            <button
              key={m}
              onClick={() => setModuleFilter(m)}
              style={{
                padding: '5px 10px',
                background: active ? T.ink : 'transparent',
                color: active ? '#ffffff' : T.ink2,
                border: `1px solid ${active ? T.ink : T.line2}`,
                borderRadius: 999,
                fontFamily: T.fSans,
                fontSize: 12,
              }}
            >
              {m}
            </button>
          )
        })}
      </div>

      {/* Two leaderboards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 24 }}>
        <Leaderboard
          title="Student Struggle"
          subtitle="Ranked by composite struggle score · click to drill in"
          cols={STRUGGLE_COLS}
          rows={struggleRows}
          onClick={(r) => onPickStudent(r.id)}
        />
        <Leaderboard
          title="Question Difficulty"
          subtitle="Ranked by composite difficulty score · click for mistake clusters"
          cols={DIFFICULTY_COLS}
          rows={filteredDifficulty}
          onClick={(r) => onPickQuestion(r.id)}
        />
      </div>

      {/* Distributions + timeline */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1.2fr)', gap: 24 }}>
        <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={1}>Struggle Distribution</SectionLabel>
          <Histogram
            data={struggleBuckets.map((b) => b.count)}
            labels={['On Track', 'Minor', 'Strug.', 'Needs']}
            bucketColors={[T.ok, T.ink3, T.warn, T.danger]}
            height={100}
          />
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 14, lineHeight: 1.6 }}>
            Thresholds: on track &lt; 0.20 · minor &lt; 0.35 · struggling &lt; 0.50 · needs help ≥ 0.50
          </div>
        </div>
        <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={2}>Difficulty Distribution</SectionLabel>
          <Histogram
            data={difficultyBuckets.map((b) => b.count)}
            labels={['Easy', 'Medium', 'Hard', 'V.Hard']}
            bucketColors={[T.ok, T.ink3, T.warn, T.danger]}
            height={100}
          />
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 14, lineHeight: 1.6 }}>
            D = 0.28·c + 0.12·t + 0.20·a + 0.20·f + 0.20·p &nbsp;·&nbsp; weighted
          </div>
        </div>
        <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={3}>Submissions, last 24h</SectionLabel>
          <TimelineChart data={timeline} highlightRange={[22, 23]} />
        </div>
      </div>
    </div>
  )
}
