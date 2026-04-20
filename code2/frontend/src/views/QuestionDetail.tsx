import { useMemo } from 'react'
import { T, LEVEL_STYLES } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import { useFilterQuery } from '../api/filterQuery'
import type { QuestionDetail as QuestionDetailData } from '../types/api'
import { Pill } from '../components/primitives/Pill'
import { ScoreBar } from '../components/primitives/ScoreBar'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { RagPanel } from '../components/RagPanel'
import { useViewStore } from '../state/viewStore'

export function QuestionDetailView({ questionId }: { questionId: string }) {
  const q = useFilterQuery()
  const { data, error, loading } = useApiData<QuestionDetailData>(
    `/question/${encodeURIComponent(questionId)}`,
    undefined,
    q
  )
  const pickStudent = useViewStore((s) => s.pickStudent)
  const lvl = useMemo(
    () => (data ? LEVEL_STYLES[data.level] ?? { fg: T.ink, label: data.level } : null),
    [data]
  )

  if (loading) {
    return <div style={{ padding: 36, color: T.ink2, fontFamily: T.fMono, fontSize: 12 }}>loading question…</div>
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
      {/* Header + measurement card */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1fr)', gap: 20 }}>
        <div style={{ padding: '32px 36px', background: T.card, border: `1px solid ${T.line}` }}>
          <div
            style={{
              fontFamily: T.fMono,
              fontSize: 10.5,
              color: T.ink3,
              letterSpacing: 1.3,
              textTransform: 'uppercase',
              marginBottom: 18,
            }}
          >
            Question · {data.id} · {data.module}
          </div>
          <div
            style={{
              fontFamily: T.fSerif,
              fontSize: 72,
              lineHeight: 0.95,
              color: lvl?.fg ?? T.ink,
              marginBottom: 18,
              fontFeatureSettings: '"tnum"',
            }}
          >
            {data.score.toFixed(2)}
          </div>
          <div style={{ marginBottom: 28 }}>
            <Pill level={data.level} />
          </div>

          <div
            style={{
              paddingTop: 22,
              borderTop: `1px solid ${T.line}`,
              display: 'grid',
              gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
              gap: 20,
            }}
          >
            {[
              { l: 'Incorrect rate', v: `${(data.incorrect_rate * 100).toFixed(0)}%` },
              { l: 'Avg attempts', v: data.avg_attempts.toFixed(1) },
              { l: 'Students', v: String(data.students) },
              { l: 'First-fail', v: `${(data.first_fail_rate * 100).toFixed(0)}%` },
            ].map((m, i, arr) => (
              <div
                key={i}
                style={{
                  borderRight: i < arr.length - 1 ? `1px solid ${T.line}` : 'none',
                  paddingRight: i < arr.length - 1 ? 16 : 0,
                }}
              >
                <div
                  style={{
                    fontFamily: T.fMono,
                    fontSize: 10,
                    color: T.ink3,
                    letterSpacing: 1.1,
                    textTransform: 'uppercase',
                    marginBottom: 8,
                  }}
                >
                  {m.l}
                </div>
                <div
                  style={{
                    fontFamily: T.fSerif,
                    fontSize: 24,
                    color: T.ink,
                    fontFeatureSettings: '"tnum"',
                  }}
                >
                  {m.v}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ padding: '28px 28px', background: T.priorityBg, color: T.priorityFg, borderRadius: 2 }}>
          <div
            style={{
              fontFamily: T.fMono,
              fontSize: 10.5,
              opacity: 0.7,
              letterSpacing: 1.3,
              textTransform: 'uppercase',
              marginBottom: 16,
            }}
          >
            Measurement
          </div>
          <div
            style={{
              fontFamily: T.fSerif,
              fontSize: 56,
              lineHeight: 0.95,
              marginBottom: 14,
            }}
          >
            {data.students}
          </div>
          <div style={{ fontFamily: T.fMono, fontSize: 11, opacity: 0.75 }}>
            students · {Math.round(data.students * data.avg_attempts)} submissions
          </div>
          <div style={{ marginTop: 24, borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: 18 }}>
            <div
              style={{
                fontFamily: T.fMono,
                fontSize: 10.5,
                opacity: 0.7,
                letterSpacing: 1.3,
                textTransform: 'uppercase',
                marginBottom: 8,
              }}
            >
              Composite score
            </div>
            <div style={{ fontFamily: T.fMono, fontSize: 22, marginBottom: 8 }}>D = {data.score.toFixed(2)}</div>
            <div style={{ fontFamily: T.fMono, fontSize: 11, opacity: 0.7 }}>
              0.28·c + 0.12·t + 0.20·a + 0.20·f + 0.20·p
            </div>
          </div>
        </div>
      </div>

      {/* Top strugglers on this question */}
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={1}>Top Strugglers on this Question</SectionLabel>
        {data.top_strugglers.length === 0 ? (
          <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>
            No per-student data yet — waiting for attempts.
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
            <thead>
              <tr>
                {['Student', 'Attempts', 'Mean inc.', 'Struggle level', 'Global score', ''].map((h) => (
                  <th
                    key={h}
                    style={{
                      textAlign: 'left',
                      padding: '10px 0',
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
              {data.top_strugglers.map((s) => (
                <tr
                  key={s.id}
                  onClick={() => pickStudent(s.id)}
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = T.bg2)}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  <td
                    style={{
                      padding: '10px 0',
                      fontFamily: T.fMono,
                      fontSize: 12,
                      color: T.ink,
                      borderBottom: `1px solid ${T.line2}`,
                    }}
                  >
                    {s.id}
                  </td>
                  <td
                    style={{
                      padding: '10px 0',
                      fontFamily: T.fMono,
                      fontSize: 12,
                      color: T.ink2,
                      borderBottom: `1px solid ${T.line2}`,
                    }}
                  >
                    {s.attempts}
                  </td>
                  <td
                    style={{
                      padding: '10px 0',
                      fontFamily: T.fMono,
                      fontSize: 12,
                      color: s.mean_incorrectness > 0.5 ? T.danger : T.ink2,
                      borderBottom: `1px solid ${T.line2}`,
                    }}
                  >
                    {s.mean_incorrectness.toFixed(2)}
                  </td>
                  <td style={{ padding: '10px 0', borderBottom: `1px solid ${T.line2}` }}>
                    {s.struggle_level ? <Pill level={s.struggle_level} /> : <span style={{ color: T.ink3 }}>—</span>}
                  </td>
                  <td style={{ padding: '10px 0', borderBottom: `1px solid ${T.line2}`, width: 160 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <ScoreBar
                        value={s.struggle_score}
                        color={LEVEL_STYLES[s.struggle_level]?.fg ?? T.ink}
                        height={3}
                        width={80}
                      />
                      <span style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink }}>
                        {s.struggle_score.toFixed(2)}
                      </span>
                    </div>
                  </td>
                  <td
                    style={{
                      padding: '10px 0',
                      borderBottom: `1px solid ${T.line2}`,
                      textAlign: 'right',
                      fontFamily: T.fMono,
                      fontSize: 10.5,
                      color: T.ink3,
                      letterSpacing: 1,
                    }}
                  >
                    click →
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Mistake clusters */}
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={2}>Mistake Clusters</SectionLabel>
        {data.mistake_clusters.length === 0 ? (
          <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>
            Not enough incorrect submissions for clustering (min 3 wrong answers required).
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 16 }}>
            {data.mistake_clusters.map((c, i) => (
              <div key={i} style={{ padding: '18px 20px', border: `1px solid ${T.line}`, background: T.bg2 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 16 }}>
                  <div style={{ fontFamily: T.fSans, fontSize: 14, fontWeight: 500, color: T.ink, lineHeight: 1.3 }}>
                    {c.label}
                  </div>
                  <div style={{ fontFamily: T.fSerif, fontSize: 22, color: T.accent, fontFeatureSettings: '"tnum"' }}>
                    {Math.round(c.percent_of_wrong * 100)}
                    <span style={{ fontSize: 13, color: T.ink3 }}>%</span>
                  </div>
                </div>
                <div style={{ marginTop: 10 }}>
                  <ScoreBar value={c.percent_of_wrong} color={T.accent} width={280} height={2} />
                </div>
                <div style={{ marginTop: 14 }}>
                  {c.example_answers.map((ex, j) => (
                    <div
                      key={j}
                      style={{
                        fontFamily: T.fMono,
                        fontSize: 11.5,
                        color: T.ink2,
                        padding: '5px 0',
                        borderTop: j === 0 ? 'none' : `1px dashed ${T.line2}`,
                      }}
                    >
                      {ex}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* RAG teaching feedback */}
      <RagPanel audience="question" subjectId={data.id} sectionNumber={3} />

      {/* Recent attempts */}
      <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={4}>Recent Attempts</SectionLabel>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
          <thead>
            <tr>
              {['Time', 'Student', 'Answer', 'Incorrectness'].map((h) => (
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
            {data.recent_attempts.map((r, i) => (
              <tr
                key={i}
                onClick={() => pickStudent(r.user)}
                style={{ cursor: 'pointer' }}
                onMouseEnter={(e) => (e.currentTarget.style.background = T.bg2)}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
              >
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
                  }}
                >
                  {r.user}
                </td>
                <td
                  style={{
                    padding: '10px 0',
                    fontFamily: T.fMono,
                    fontSize: 12,
                    color: T.ink2,
                    borderBottom: `1px solid ${T.line2}`,
                    maxWidth: 420,
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
                    <ScoreBar
                      value={r.incorrectness}
                      color={r.incorrectness > 0.5 ? T.danger : T.ok}
                      width={80}
                      height={3}
                    />
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

function formatTimestamp(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')} · ${d.toLocaleDateString()}`
}
