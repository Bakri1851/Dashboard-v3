import { T } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import type { AnalysisStats } from '../types/api'
import { Stat } from '../components/primitives/Stat'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { HBars } from '../components/charts/HBars'
import { TimelineChart } from '../components/charts/TimelineChart'

export function DataAnalysisView() {
  const { data, error, loading } = useApiData<AnalysisStats>('/analysis', 60_000)

  if (loading && !data) {
    return <div style={{ padding: 36, color: T.ink2, fontFamily: T.fMono, fontSize: 12 }}>loading analysis…</div>
  }
  if (error) {
    return <div style={{ padding: 36, color: T.danger, fontFamily: T.fMono, fontSize: 12 }}>{error}</div>
  }
  if (!data) return null

  const maxModule = Math.max(...data.module_breakdown.map((m) => m.submissions), 1)

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

      {/* Module breakdown */}
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={1}>Module Breakdown</SectionLabel>
        {data.module_breakdown.length === 0 ? (
          <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>No module data loaded.</div>
        ) : (
          <HBars
            items={data.module_breakdown.map((m, i) => ({
              label: m.module,
              value: m.submissions,
              valueLabel: `${m.submissions.toLocaleString()} subs · ${m.unique_students} students`,
              color:
                i === 0
                  ? T.danger
                  : i === 1
                  ? T.warn
                  : i === 2
                  ? T.ink2
                  : i === 3
                  ? T.ink3
                  : T.ok,
            }))}
            max={maxModule}
          />
        )}
      </div>

      {/* Timeline */}
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={2}>Hourly Submissions · last 24h</SectionLabel>
        <TimelineChart data={data.timeline_24h} highlightRange={[22, 23]} />
      </div>
    </div>
  )
}
