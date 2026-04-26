import { useMemo } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { T, LEVEL_STYLES } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import { useFilterQuery } from '../api/filterQuery'
import type { QuestionDetail as QuestionDetailData } from '../types/api'
import { Pill } from '../components/primitives/Pill'
import { ScoreBar } from '../components/primitives/ScoreBar'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { AnimatedNumber } from '../components/primitives/AnimatedNumber'
import { Tooltip } from '../components/primitives/Tooltip'
import { Skeleton } from '../components/primitives/Skeleton'
import { Collapsible } from '../components/primitives/Collapsible'
import { RagPanel } from '../components/RagPanel'
import { TimelineChart } from '../components/charts/TimelineChart'
import { useViewStore } from '../state/viewStore'
import { AnimatedCard } from '../animation/AnimatedCard'
import { stagger, fadeUp } from '../animation/motion'

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

  if (loading && !data) {
    return (
      <motion.div
        variants={stagger}
        initial="initial"
        animate="animate"
        style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}
      >
        <AnimatedCard variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1fr)', gap: 20 }}>
          <div style={{ padding: '32px 36px', background: T.card, border: `1px solid ${T.line}` }}>
            <Skeleton variant="text" width="40%" height={10} />
            <div style={{ height: 18 }} />
            <Skeleton variant="block" width={240} height={68} />
            <div style={{ height: 18 }} />
            <Skeleton variant="text" width="30%" height={14} />
          </div>
          <div style={{ padding: '28px 28px', background: T.bg2, border: `1px solid ${T.line}` }}>
            <Skeleton variant="text" rows={4} />
          </div>
        </AnimatedCard>
        <AnimatedCard variants={fadeUp}><Skeleton variant="block" height={220} /></AnimatedCard>
      </motion.div>
    )
  }
  if (error || !data) {
    return (
      <div style={{ padding: 36, color: T.danger, fontFamily: T.fMono, fontSize: 12 }}>
        {error ?? 'no data'}
      </div>
    )
  }

  return (
    <motion.div
      variants={stagger}
      initial="initial"
      animate="animate"
      style={{ padding: '18px 28px', display: 'flex', flexDirection: 'column', gap: 14 }}
    >
      {/* Header + measurement card */}
      <AnimatedCard variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1fr)', gap: 16 }}>
        <div style={{ padding: '20px 26px', background: T.card, border: `1px solid ${T.line}` }}>
          <div
            style={{
              fontFamily: T.fMono,
              fontSize: 10.5,
              color: T.ink3,
              letterSpacing: 1.3,
              textTransform: 'uppercase',
              marginBottom: 10,
            }}
          >
            Question · {data.id} · {data.module}
          </div>
          <div style={{ marginBottom: 10 }}>
            <AnimatedNumber
              value={data.score.toFixed(2)}
              duration={0.8}
              style={{
                fontFamily: T.fSerif,
                fontSize: 52,
                lineHeight: 0.95,
                color: lvl?.fg ?? T.ink,
                fontFeatureSettings: '"tnum"',
                display: 'inline-block',
              }}
            />
          </div>
          <div style={{ marginBottom: 14 }}>
            <Pill level={data.level} />
          </div>

          <div
            style={{
              paddingTop: 12,
              borderTop: `1px solid ${T.line}`,
              display: 'grid',
              gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
              gap: 14,
            }}
          >
            {[
              {
                l: 'Incorrect rate',
                v: `${(data.incorrect_rate * 100).toFixed(0)}%`,
                help: 'Share of attempts scored as incorrect (AI incorrectness ≥ 0.50).',
              },
              {
                l: 'Avg attempts',
                v: data.avg_attempts.toFixed(1),
                help: 'Mean submission attempts per student for this question. High values indicate repeated retries.',
              },
              {
                l: 'Students',
                v: String(data.students),
                help: 'Distinct students who attempted this question in the active window.',
              },
              {
                l: 'First-fail',
                v: `${(data.first_fail_rate * 100).toFixed(0)}%`,
                help: "Share of students whose first attempt was scored incorrect — a clean proxy for 'how hard is this on sight'.",
              },
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
                    marginBottom: 4,
                  }}
                >
                  <Tooltip content={m.help}>
                    <span style={{ cursor: 'help', borderBottom: `1px dotted currentColor` }}>{m.l}</span>
                  </Tooltip>
                </div>
                <AnimatedNumber
                  value={m.v}
                  style={{
                    fontFamily: T.fSerif,
                    fontSize: 20,
                    color: T.ink,
                    fontFeatureSettings: '"tnum"',
                    display: 'inline-block',
                  }}
                />
              </div>
            ))}
          </div>
        </div>

        <div style={{ padding: '18px 22px', background: T.priorityBg, color: T.priorityFg, borderRadius: 2 }}>
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
            <Tooltip content="Sample size behind this question's difficulty estimate — more students and submissions mean a more reliable score.">
              <span style={{ cursor: 'help', borderBottom: `1px dotted currentColor` }}>Measurement</span>
            </Tooltip>
          </div>
          <div style={{ marginBottom: 8 }}>
            <AnimatedNumber
              value={String(data.students)}
              style={{
                fontFamily: T.fSerif,
                fontSize: 42,
                lineHeight: 0.95,
                display: 'inline-block',
              }}
            />
          </div>
          <div style={{ fontFamily: T.fMono, fontSize: 11, opacity: 0.75 }}>
            students · {Math.round(data.students * data.avg_attempts)} submissions
          </div>
          <div style={{ marginTop: 14, borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: 12 }}>
            <div
              style={{
                fontFamily: T.fMono,
                fontSize: 10.5,
                opacity: 0.7,
                letterSpacing: 1.3,
                textTransform: 'uppercase',
                marginBottom: 4,
              }}
            >
              <Tooltip content="Composite 0–1 question difficulty. D = 0.28·incorrect_rate + 0.12·avg_time + 0.20·avg_attempts + 0.20·first_fail + 0.20·mean_incorrectness.">
                <span style={{ cursor: 'help', borderBottom: `1px dotted currentColor` }}>Composite score</span>
              </Tooltip>
            </div>
            <div style={{ fontFamily: T.fMono, fontSize: 18, marginBottom: 4 }}>D = {data.score.toFixed(2)}</div>
            <div style={{ fontFamily: T.fMono, fontSize: 11, opacity: 0.7 }}>
              0.28·c + 0.12·t + 0.20·a + 0.20·f + 0.20·p
            </div>
          </div>
        </div>
      </AnimatedCard>

      {/* Top strugglers on this question */}
      <AnimatedCard variants={fadeUp} style={{ padding: 14, background: T.card, border: `1px solid ${T.line}` }}>
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
              <AnimatePresence initial={false}>
              {data.top_strugglers.slice(0, 8).map((s) => (
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
                  onClick={() => pickStudent(s.id)}
                  whileHover={{ background: T.bg2 }}
                  style={{ cursor: 'pointer' }}
                >
                  <td
                    style={{
                      padding: '7px 0',
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
                      padding: '7px 0',
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
                      padding: '7px 0',
                      fontFamily: T.fMono,
                      fontSize: 12,
                      color: s.mean_incorrectness > 0.5 ? T.danger : T.ink2,
                      borderBottom: `1px solid ${T.line2}`,
                    }}
                  >
                    {s.mean_incorrectness.toFixed(2)}
                  </td>
                  <td style={{ padding: '7px 0', borderBottom: `1px solid ${T.line2}` }}>
                    {s.struggle_level ? <Pill level={s.struggle_level} /> : <span style={{ color: T.ink3 }}>—</span>}
                  </td>
                  <td style={{ padding: '7px 0', borderBottom: `1px solid ${T.line2}`, width: 160 }}>
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
                      padding: '7px 0',
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
                </motion.tr>
              ))}
              </AnimatePresence>
            </tbody>
          </table>
        )}
      </AnimatedCard>

      {/* RAG teaching feedback */}
      <AnimatedCard variants={fadeUp}>
        <RagPanel audience="question" subjectId={data.id} sectionNumber={2} />
      </AnimatedCard>

      {/* Mistake clusters — collapsed by default, sits below RAG */}
      <AnimatedCard variants={fadeUp}>
        <Collapsible
          n={3}
          title="Mistake Clusters"
          count={data.mistake_clusters.length}
          defaultOpen={false}
        >
          {data.mistake_clusters.length === 0 ? (
            <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>
              Not enough incorrect submissions for clustering (min 3 wrong answers required).
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
              {data.mistake_clusters.map((c, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.05, ease: 'easeOut' }}
                  whileHover={{ y: -2, borderColor: T.accent }}
                  style={{ padding: '12px 14px', border: `1px solid ${T.line}`, background: T.bg2 }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12 }}>
                    <div style={{ fontFamily: T.fSans, fontSize: 13, fontWeight: 500, color: T.ink, lineHeight: 1.3 }}>
                      {c.label}
                    </div>
                    <div style={{ fontFamily: T.fSerif, fontSize: 18, color: T.accent, fontFeatureSettings: '"tnum"' }}>
                      <AnimatedNumber
                        value={String(Math.round(c.percent_of_wrong * 100))}
                        style={{ display: 'inline-block' }}
                      />
                      <span style={{ fontSize: 12, color: T.ink3 }}>%</span>
                    </div>
                  </div>
                  <div style={{ marginTop: 6 }}>
                    <ScoreBar value={c.percent_of_wrong} color={T.accent} width={240} height={2} />
                  </div>
                  <div style={{ marginTop: 8 }}>
                    {c.example_answers.map((ex, j) => (
                      <div
                        key={j}
                        style={{
                          fontFamily: T.fMono,
                          fontSize: 11.5,
                          color: T.ink2,
                          padding: '4px 0',
                          borderTop: j === 0 ? 'none' : `1px dashed ${T.line2}`,
                        }}
                      >
                        {ex}
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </Collapsible>
      </AnimatedCard>

      {/* Recent attempts */}
      <AnimatedCard variants={fadeUp} style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
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
            <AnimatePresence initial={false}>
            {data.recent_attempts.map((r, i) => (
              <motion.tr
                key={i}
                layout
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 12 }}
                transition={{
                  layout: { type: 'spring', stiffness: 400, damping: 38 },
                  opacity: { duration: 0.2 },
                }}
                onClick={() => pickStudent(r.user)}
                whileHover={{ background: T.bg2 }}
                style={{ cursor: 'pointer' }}
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
              </motion.tr>
            ))}
            </AnimatePresence>
          </tbody>
        </table>
      </AnimatedCard>

      {/* Attempt timeline — hour-of-day distribution for this question */}
      <AnimatedCard variants={fadeUp}>
        <Collapsible n={5} title="Attempt Timeline" defaultOpen={false}>
          <TimelineChart data={data.timeline_24h} semantic="hour_of_day" />
        </Collapsible>
      </AnimatedCard>
    </motion.div>
  )
}

function formatTimestamp(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')} · ${d.toLocaleDateString()}`
}
