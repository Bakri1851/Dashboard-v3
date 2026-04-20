import { useEffect, useMemo, useState } from 'react'
import { T } from '../theme/tokens'
import { prefetchApi, useApiData } from '../api/hooks'
import { useFilterQuery } from '../api/filterQuery'
import { useFilterStore, presetNote } from '../state/filterStore'
import { useSettings } from '../api/useSettings'
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
  const q = useFilterQuery()
  const filter = useFilterStore()
  const { data: settings } = useSettings()
  const cfEnabled = settings?.runtime.cf_enabled ?? false
  const { data: live, error: liveErr, loading: liveLoading } =
    useApiData<LiveDataResponse>('/live', 10_000, q)
  const { data: struggle, error: strugErr, loading: strugLoading } =
    useApiData<StudentStruggle[]>('/struggle', 15_000, q)
  const { data: difficulty, error: diffErr, loading: diffLoading } =
    useApiData<QuestionDifficulty[]>('/difficulty', 15_000, q)
  const { data: cf } = useApiData<CFDiagnostics>(cfEnabled ? '/cf' : '', 30_000, q)
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
      {showFallbackBanner && (
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
          <button
            onClick={() => {
              filter.setAutoFallbackApplied(false)
              filter.setPreset('today')
            }}
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
          </button>
        </div>
      )}
      {/* Hero stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr)', gap: 12 }}>
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
            Priority Now
          </div>
          <div>
            <div
              style={{
                fontFamily: T.fSerif,
                fontSize: 56,
                lineHeight: 0.95,
                fontFeatureSettings: '"tnum"',
                color: T.priorityFg,
              }}
            >
              {needsHelp}
            </div>
            <div style={{ fontFamily: T.fMono, fontSize: 11, marginTop: 8, opacity: 0.8 }}>
              students need help · {strugCount} struggling
            </div>
            <div style={{ marginTop: 14 }}>
              <button
                onClick={onOpenLab}
                disabled={!sessionActive}
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
              </button>
            </div>
          </div>
        </div>
        <Stat label="Total Submissions" value={records.toLocaleString()} note={submissionsNote} />
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
                background: active ? T.priorityBg : 'transparent',
                color: active ? T.priorityFg : T.ink2,
                border: `1px solid ${active ? T.priorityBg : T.line2}`,
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
          onHover={(r) => prefetchApi(`/rag/student/${encodeURIComponent(r.id)}`)}
        />
        <Leaderboard
          title="Question Difficulty"
          subtitle="Ranked by composite difficulty score · click for mistake clusters"
          cols={DIFFICULTY_COLS}
          rows={filteredDifficulty}
          onClick={(r) => onPickQuestion(r.id)}
          onHover={(r) => prefetchApi(`/rag/question/${encodeURIComponent(r.id)}`)}
        />
      </div>

      {/* CF panel (when enabled) */}
      {cfEnabled && cf && (
        <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
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
                    {cf.elevated_students.map((s) => (
                      <tr key={s.id} onClick={() => onPickStudent(s.id)} style={{ cursor: 'pointer' }}>
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
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </div>
      )}

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
