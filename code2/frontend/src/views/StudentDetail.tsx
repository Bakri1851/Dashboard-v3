import { useMemo } from 'react'
import { T, LEVEL_STYLES } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import type { StudentDetail as StudentDetailData } from '../types/api'
import { Pill } from '../components/primitives/Pill'
import { ScoreBar } from '../components/primitives/ScoreBar'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { Spark } from '../components/charts/Spark'
import { HBars } from '../components/charts/HBars'
import { RagPanel } from '../components/RagPanel'

function colorForComponent(key: string, value: number): string {
  if (value >= 0.7) return T.danger
  if (value >= 0.5) return T.warn
  if (key === 'n_hat' || key === 't_hat' || key === 'rep_hat') return T.ink3
  return T.ink3
}

export function StudentDetailView({ studentId }: { studentId: string }) {
  const { data, error, loading } = useApiData<StudentDetailData>(`/student/${encodeURIComponent(studentId)}`)
  const lvl = useMemo(() => (data ? LEVEL_STYLES[data.level] ?? { fg: T.ink, label: data.level } : null), [data])

  if (loading) {
    return <div style={{ padding: 36, color: T.ink2, fontFamily: T.fMono, fontSize: 12 }}>loading student…</div>
  }
  if (error || !data) {
    return (
      <div style={{ padding: 36, color: T.danger, fontFamily: T.fMono, fontSize: 12 }}>
        {error ?? 'no data'}
      </div>
    )
  }

  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header card + metric strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1fr)', gap: 20 }}>
        <div style={{ padding: '28px 32px', background: T.card, border: `1px solid ${T.line}` }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 20 }}>
            <div>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.3, textTransform: 'uppercase' }}>
                Student · {data.id}
              </div>
              <div
                style={{
                  fontFamily: T.fSerif,
                  fontSize: 72,
                  lineHeight: 0.95,
                  color: lvl?.fg ?? T.ink,
                  marginTop: 10,
                  fontFeatureSettings: '"tnum"',
                }}
              >
                {data.score.toFixed(2)}
              </div>
              <div style={{ marginTop: 10 }}>
                <Pill level={data.level} />
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.3, textTransform: 'uppercase' }}>
                Trajectory, last {data.trajectory.length}
              </div>
              <div style={{ marginTop: 12 }}>
                <Spark data={data.trajectory} width={240} height={70} color={lvl?.fg ?? T.ink} fill />
              </div>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 8 }}>
                {data.trend >= 0 ? '+' : ''}
                {data.trend.toFixed(2)} recent slope
              </div>
            </div>
          </div>
          <div
            style={{
              marginTop: 24,
              paddingTop: 20,
              borderTop: `1px solid ${T.line}`,
              fontFamily: T.fSans,
              fontSize: 13,
              color: T.ink2,
              lineHeight: 1.55,
            }}
          >
            <strong style={{ color: T.ink, fontWeight: 500 }}>Why flagged.</strong> Recent
            incorrectness {data.recent.toFixed(2)} vs mean {(data.mean_incorrectness).toFixed(2)}. Retry rate{' '}
            {(data.retry_rate * 100).toFixed(0)}%. Bayesian shrinkage (K=5) applied to the raw struggle
            score to land at <strong>{data.score.toFixed(2)}</strong>.
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateRows: 'repeat(4, 1fr)', gap: 8 }}>
          <MetricRow label="Submissions" value={data.submissions.toLocaleString()} note="all time" />
          <MetricRow label="Time active" value={`${data.time_active_min.toFixed(0)} min`} note="cumulative" />
          <MetricRow label="Retry rate" value={`${(data.retry_rate * 100).toFixed(0)}%`} note="vs class median" />
          <MetricRow
            label="Recent incorrectness"
            value={data.recent.toFixed(2)}
            note={`trend ${data.trend >= 0 ? '+' : ''}${data.trend.toFixed(2)}`}
          />
        </div>
      </div>

      {/* Score components + Top Questions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1.2fr)', gap: 20 }}>
        <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={4}>Score Components</SectionLabel>
          <HBars
            items={data.components.map((c) => ({
              label: c.label,
              value: c.value,
              valueLabel: c.value.toFixed(2),
              color: colorForComponent(c.key, c.value),
            }))}
            max={1}
          />
          <div
            style={{
              marginTop: 16,
              padding: 12,
              background: T.bg2,
              fontFamily: T.fMono,
              fontSize: 11,
              color: T.ink2,
              lineHeight: 1.6,
            }}
          >
            S_raw = {data.components.map((c) => `${c.weight.toFixed(2)}·${c.key}`).join(' + ')}
          </div>
        </div>

        <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={5}>Top Questions Attempted</SectionLabel>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
            <thead>
              <tr>
                {['Question', 'Attempts', 'Difficulty', 'Last'].map((h) => (
                  <th
                    key={h}
                    style={{
                      textAlign: 'left',
                      padding: '8px 0',
                      fontFamily: T.fMono,
                      fontSize: 10,
                      letterSpacing: 1,
                      color: T.ink3,
                      textTransform: 'uppercase',
                      fontWeight: 500,
                      borderBottom: `1px solid ${T.line}`,
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.top_questions.map((r, i) => (
                <tr key={i}>
                  <td
                    style={{
                      padding: '9px 0',
                      fontFamily: T.fMono,
                      fontSize: 12,
                      borderBottom: `1px solid ${T.line2}`,
                      color: T.ink,
                      maxWidth: 360,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                    title={r.question}
                  >
                    {r.question}
                  </td>
                  <td style={{ padding: '9px 0', fontVariantNumeric: 'tabular-nums', borderBottom: `1px solid ${T.line2}` }}>
                    {r.attempts}
                  </td>
                  <td style={{ padding: '9px 0', borderBottom: `1px solid ${T.line2}` }}>
                    {r.difficulty ? <Pill level={r.difficulty} /> : '—'}
                  </td>
                  <td
                    style={{
                      padding: '9px 0',
                      fontFamily: T.fMono,
                      fontSize: 12,
                      borderBottom: `1px solid ${T.line2}`,
                      color:
                        r.last_incorrectness == null
                          ? T.ink3
                          : r.last_incorrectness > 0.5
                          ? T.danger
                          : T.ok,
                    }}
                  >
                    {r.last_incorrectness == null ? '—' : r.last_incorrectness.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* RAG coaching suggestions */}
      <RagPanel audience="student" subjectId={data.id} sectionNumber={6} />

      {/* Recent submissions */}
      <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={7}>Recent Submissions</SectionLabel>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
          <thead>
            <tr>
              {['Time', 'Question', 'Answer', 'Incorrectness'].map((h) => (
                <th
                  key={h}
                  style={{
                    textAlign: 'left',
                    padding: '8px 0',
                    fontFamily: T.fMono,
                    fontSize: 10,
                    letterSpacing: 1,
                    color: T.ink3,
                    textTransform: 'uppercase',
                    fontWeight: 500,
                    borderBottom: `1px solid ${T.line}`,
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.recent_submissions.map((r, i) => (
              <tr key={i}>
                <td
                  style={{
                    padding: '10px 0',
                    fontFamily: T.fMono,
                    fontSize: 11.5,
                    color: T.ink2,
                    borderBottom: `1px solid ${T.line2}`,
                    whiteSpace: 'nowrap',
                  }}
                >
                  {formatTimestamp(r.timestamp)}
                </td>
                <td
                  style={{
                    padding: '10px 0',
                    fontFamily: T.fMono,
                    fontSize: 12,
                    color: T.ink,
                    borderBottom: `1px solid ${T.line2}`,
                    maxWidth: 260,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                  title={r.question}
                >
                  {r.question}
                </td>
                <td
                  style={{
                    padding: '10px 0',
                    fontFamily: T.fMono,
                    fontSize: 12,
                    color: T.ink2,
                    borderBottom: `1px solid ${T.line2}`,
                    maxWidth: 400,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                  title={r.answer}
                >
                  {r.answer}
                </td>
                <td style={{ padding: '10px 0', borderBottom: `1px solid ${T.line2}`, width: 180 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <ScoreBar value={r.incorrectness} color={r.incorrectness > 0.5 ? T.danger : T.ok} width={80} height={3} />
                    <span
                      style={{
                        fontFamily: T.fMono,
                        fontSize: 12,
                        color: r.incorrectness > 0.5 ? T.danger : T.ok,
                      }}
                    >
                      {r.incorrectness.toFixed(2)}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function MetricRow({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr auto',
        padding: '14px 18px',
        background: T.card,
        border: `1px solid ${T.line}`,
        alignItems: 'center',
      }}
    >
      <div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase' }}>
          {label}
        </div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>{note}</div>
      </div>
      <div
        style={{
          fontFamily: T.fSerif,
          fontSize: 28,
          color: T.ink,
          fontFeatureSettings: '"tnum"',
          whiteSpace: 'nowrap',
        }}
      >
        {value}
      </div>
    </div>
  )
}

function formatTimestamp(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')} · ${d.toLocaleDateString()}`
}
