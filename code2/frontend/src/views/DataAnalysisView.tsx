import { useMemo, useState } from 'react'
import { T } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import { useFilterQuery } from '../api/filterQuery'
import type { AnalysisStats } from '../types/api'
import { Stat } from '../components/primitives/Stat'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { HBars } from '../components/charts/HBars'
import { TimelineChart } from '../components/charts/TimelineChart'
import { Heatmap, type HeatmapRow } from '../components/charts/Heatmap'

type ChartMode =
  | 'module_usage'
  | 'top_questions'
  | 'user_activity'
  | 'timeline'
  | 'week_heatmap'
  | 'students_per_module'

const MODES: { id: ChartMode; label: string; hint: string }[] = [
  { id: 'module_usage',        label: 'Module Usage',         hint: 'submissions per module' },
  { id: 'top_questions',       label: 'Top Questions',        hint: 'most attempted' },
  { id: 'user_activity',       label: 'User Activity',        hint: 'top submitters' },
  { id: 'timeline',            label: 'Activity Timeline',    hint: '24-hour heartbeat' },
  { id: 'week_heatmap',        label: 'Activity by Week',     hint: 'academic week × day' },
  { id: 'students_per_module', label: 'Students by Module',   hint: 'unique students per module' },
]

const DAY_COLS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export function DataAnalysisView() {
  const q = useFilterQuery()
  const { data, error, loading } = useApiData<AnalysisStats>('/analysis', 60_000, q)
  const [mode, setMode] = useState<ChartMode>('module_usage')

  if (loading && !data) {
    return <div style={{ padding: 36, color: T.ink2, fontFamily: T.fMono, fontSize: 12 }}>loading analysis…</div>
  }
  if (error) {
    return <div style={{ padding: 36, color: T.danger, fontFamily: T.fMono, fontSize: 12 }}>{error}</div>
  }
  if (!data) return null

  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Hero stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12 }}>
        <Stat label="Modules" value={String(data.modules)} note={`${data.unique_students} active students`} />
        <Stat
          label="Peak hour"
          value={`${String(data.peak_hour).padStart(2, '0')}:00`}
          note={`${data.peak_hour_count} submissions`}
          accent={T.accent}
        />
        <Stat label="Avg attempts / Q" value={data.avg_attempts_per_question.toFixed(1)} note="class median" />
        <Stat
          label="Avg session"
          value={`${data.avg_session_minutes.toFixed(0)}m`}
          note="min → max per student"
        />
      </div>

      {/* Chart-mode picker */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        <span
          style={{
            fontFamily: T.fMono,
            fontSize: 10.5,
            color: T.ink3,
            letterSpacing: 1,
            textTransform: 'uppercase',
            alignSelf: 'center',
            marginRight: 8,
          }}
        >
          Chart
        </span>
        {MODES.map((m) => {
          const active = mode === m.id
          return (
            <button
              key={m.id}
              onClick={() => setMode(m.id)}
              title={m.hint}
              style={{
                padding: '6px 12px',
                background: active ? T.priorityBg : 'transparent',
                color: active ? T.priorityFg : T.ink2,
                border: `1px solid ${active ? T.priorityBg : T.line2}`,
                borderRadius: 999,
                fontFamily: T.fSans,
                fontSize: 12,
                cursor: 'pointer',
              }}
            >
              {m.label}
            </button>
          )
        })}
      </div>

      {/* Chart body */}
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={MODES.findIndex((m) => m.id === mode) + 1}>
          {MODES.find((m) => m.id === mode)?.label}
        </SectionLabel>
        <ChartBody mode={mode} data={data} />
      </div>
    </div>
  )
}

function ChartBody({ mode, data }: { mode: ChartMode; data: AnalysisStats }) {
  switch (mode) {
    case 'module_usage': {
      const max = Math.max(...data.module_breakdown.map((m) => m.submissions), 1)
      if (!data.module_breakdown.length) return <Empty>No module data in the current window.</Empty>
      return (
        <HBars
          items={data.module_breakdown.map((m, i) => ({
            label: m.module,
            value: m.submissions,
            valueLabel: `${m.submissions.toLocaleString()} subs`,
            color: i === 0 ? T.danger : i === 1 ? T.warn : i === 2 ? T.ink2 : i === 3 ? T.ink3 : T.ok,
          }))}
          max={max}
        />
      )
    }
    case 'students_per_module': {
      const max = Math.max(...data.module_breakdown.map((m) => m.unique_students), 1)
      if (!data.module_breakdown.length) return <Empty>No module data in the current window.</Empty>
      return (
        <HBars
          items={data.module_breakdown.map((m, i) => ({
            label: m.module,
            value: m.unique_students,
            valueLabel: `${m.unique_students} students`,
            color: i === 0 ? T.accent : i === 1 ? T.warn : T.ink2,
          }))}
          max={max}
        />
      )
    }
    case 'top_questions':
      if (!data.top_questions.length) return <Empty>No questions attempted in the current window.</Empty>
      return (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
          <thead>
            <tr>
              {['Question', 'Module', 'Attempts', 'Students', 'Avg / student'].map((h) => (
                <th key={h} style={thStyle(h === 'Question' || h === 'Module')}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.top_questions.map((r, i) => (
              <tr key={`${r.question}-${i}`}>
                <td style={tdStyle(true, { maxWidth: 380, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} title={r.question}>
                  {r.question}
                </td>
                <td style={tdStyle(true)}>{r.module}</td>
                <td style={tdStyle(false)}>{r.attempts.toLocaleString()}</td>
                <td style={tdStyle(false)}>{r.unique_students}</td>
                <td style={tdStyle(false)}>{r.avg_attempts.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )
    case 'user_activity':
      if (!data.user_activity.length) return <Empty>No student activity in the current window.</Empty>
      return (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
          <thead>
            <tr>
              {['Student', 'Submissions', 'Questions', 'First', 'Last'].map((h) => (
                <th key={h} style={thStyle(h === 'Student')}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.user_activity.map((r) => (
              <tr key={r.user}>
                <td style={tdStyle(true)}>{r.user}</td>
                <td style={tdStyle(false)}>{r.submissions.toLocaleString()}</td>
                <td style={tdStyle(false)}>{r.unique_questions}</td>
                <td style={tdStyle(true)}>{formatTimestamp(r.first_submission)}</td>
                <td style={tdStyle(true)}>{formatTimestamp(r.last_submission)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )
    case 'timeline':
      return <TimelineChart data={data.timeline_24h} highlightRange={[22, 23]} />
    case 'week_heatmap':
      return <WeekHeatmap data={data} />
  }
}

function WeekHeatmap({ data }: { data: AnalysisStats }) {
  const rows = useMemo<HeatmapRow[]>(() => {
    if (!data.activity_by_week.length) return []
    // Group cells by week_label, preserving incoming order.
    const grouped: Record<string, HeatmapRow> = {}
    const order: string[] = []
    for (const c of data.activity_by_week) {
      if (!grouped[c.week_label]) {
        grouped[c.week_label] = { rowLabel: c.week_label, cells: [] }
        order.push(c.week_label)
      }
      grouped[c.week_label].cells.push({ colLabel: c.day_label, value: c.count })
    }
    return order.map((k) => grouped[k])
  }, [data.activity_by_week])

  if (!rows.length) {
    return <Empty>No activity falls within a mapped academic week.</Empty>
  }
  return (
    <div>
      <Heatmap rows={rows} colLabels={DAY_COLS} />
      <div style={{ marginTop: 14, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
        Academic periods from <code>academic_calendar.py</code> · filtered by the sidebar time window.
      </div>
    </div>
  )
}

function Empty({ children }: { children: React.ReactNode }) {
  return <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>{children}</div>
}

function thStyle(leftAlign: boolean): React.CSSProperties {
  return {
    textAlign: leftAlign ? 'left' : 'right',
    padding: '10px 14px',
    fontFamily: T.fMono,
    fontSize: 10,
    color: T.ink3,
    letterSpacing: 1.2,
    textTransform: 'uppercase',
    fontWeight: 500,
    borderBottom: `1px solid ${T.line}`,
  }
}

function tdStyle(leftAlign: boolean, extra: React.CSSProperties = {}): React.CSSProperties {
  return {
    textAlign: leftAlign ? 'left' : 'right',
    padding: '9px 14px',
    borderBottom: `1px solid ${T.line2}`,
    fontFamily: leftAlign ? T.fMono : T.fSans,
    fontSize: 12,
    color: T.ink,
    fontVariantNumeric: 'tabular-nums',
    ...extra,
  }
}

function formatTimestamp(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
