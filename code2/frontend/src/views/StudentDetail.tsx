import { useMemo } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { T, LEVEL_STYLES } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import { useFilterQuery } from '../api/filterQuery'
import { useFilterStore, presetNote } from '../state/filterStore'
import type { SimilarStudent, StudentDetail as StudentDetailData } from '../types/api'
import { useSettings } from '../api/useSettings'
import { useViewStore } from '../state/viewStore'
import { Pill } from '../components/primitives/Pill'
import { ScoreBar } from '../components/primitives/ScoreBar'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { AnimatedNumber } from '../components/primitives/AnimatedNumber'
import { Skeleton, SkeletonStatCard } from '../components/primitives/Skeleton'
import { Spark } from '../components/charts/Spark'
import { HBars } from '../components/charts/HBars'
import { TimelineChart } from '../components/charts/TimelineChart'
import { RagPanel } from '../components/RagPanel'
import { AnimatedCard } from '../animation/AnimatedCard'
import { stagger, fadeUp } from '../animation/motion'

function colorForComponent(key: string, value: number): string {
  if (value >= 0.7) return T.danger
  if (value >= 0.5) return T.warn
  if (key === 'n_hat' || key === 't_hat' || key === 'rep_hat') return T.ink3
  return T.ink3
}

export function StudentDetailView({ studentId }: { studentId: string }) {
  const q = useFilterQuery()
  const preset = useFilterStore((s) => s.preset)
  const scopeNote = presetNote(preset)
  const { data: settings } = useSettings()
  const cfEnabled = settings?.runtime.cf_enabled ?? false
  const pickStudent = useViewStore((s) => s.pickStudent)
  const { data, error, loading } = useApiData<StudentDetailData>(
    `/student/${encodeURIComponent(studentId)}`,
    undefined,
    q
  )
  const { data: similar } = useApiData<SimilarStudent[]>(
    cfEnabled ? `/student/${encodeURIComponent(studentId)}/similar` : '',
    0,
    q
  )
  const lvl = useMemo(() => (data ? LEVEL_STYLES[data.level] ?? { fg: T.ink, label: data.level } : null), [data])

  if (loading && !data) {
    return (
      <motion.div
        variants={stagger}
        initial="initial"
        animate="animate"
        style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}
      >
        <AnimatedCard variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1fr)', gap: 20 }}>
          <div style={{ padding: '28px 32px', background: T.card, border: `1px solid ${T.line}` }}>
            <Skeleton variant="text" width="30%" height={10} />
            <div style={{ height: 14 }} />
            <Skeleton variant="block" width={220} height={64} />
            <div style={{ height: 16 }} />
            <Skeleton variant="text" rows={3} />
          </div>
          <div style={{ display: 'grid', gridTemplateRows: 'repeat(4, 1fr)', gap: 8 }}>
            <SkeletonStatCard height={72} />
            <SkeletonStatCard height={72} />
            <SkeletonStatCard height={72} />
            <SkeletonStatCard height={72} />
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
      style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}
    >
      {/* Header card + metric strip */}
      <AnimatedCard variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1fr)', gap: 20 }}>
        <div style={{ padding: '28px 32px', background: T.card, border: `1px solid ${T.line}` }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 20 }}>
            <div>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.3, textTransform: 'uppercase' }}>
                Student · {data.id}
              </div>
              <AnimatedNumber
                value={data.score.toFixed(2)}
                duration={0.8}
                style={{
                  fontFamily: T.fSerif,
                  fontSize: 72,
                  lineHeight: 0.95,
                  color: lvl?.fg ?? T.ink,
                  marginTop: 10,
                  fontFeatureSettings: '"tnum"',
                  display: 'inline-block',
                }}
              />
              <div style={{ marginTop: 10 }}>
                <Pill level={data.level} />
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.3, textTransform: 'uppercase' }}>
                Trajectory, last {data.trajectory.length}
              </div>
              <div style={{ marginTop: 12 }}>
                <Spark data={data.trajectory} width={240} height={70} color={lvl?.fg ?? T.ink} fill domain={[0, 1]} />
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
          <MetricRow label="Submissions" value={data.submissions.toLocaleString()} note={scopeNote} />
          <MetricRow label="Time active" value={`${data.time_active_min.toFixed(0)} min`} note={scopeNote} />
          <MetricRow label="Retry rate" value={`${(data.retry_rate * 100).toFixed(0)}%`} note="vs class median" />
          <MetricRow
            label="Recent incorrectness"
            value={data.recent.toFixed(2)}
            note={`trend ${data.trend >= 0 ? '+' : ''}${data.trend.toFixed(2)}`}
          />
        </div>
      </AnimatedCard>

      {/* Score components + Top Questions */}
      <AnimatedCard variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1.2fr)', gap: 20 }}>
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
              <AnimatePresence initial={false}>
              {data.top_questions.map((r, i) => (
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
                >
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
                </motion.tr>
              ))}
              </AnimatePresence>
            </tbody>
          </table>
        </div>
      </AnimatedCard>

      {/* CF similar students */}
      {cfEnabled && similar && similar.length > 0 && (
        <AnimatedCard variants={fadeUp} style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={6}>Similar Students · Collaborative Filtering</SectionLabel>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 12 }}>
            {similar.map((s, i) => (
              <motion.button
                key={s.id}
                onClick={() => pickStudent(s.id)}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: i * 0.04, ease: 'easeOut' }}
                whileHover={{ y: -2, borderColor: T.accent }}
                whileTap={{ scale: 0.97 }}
                style={{ padding: 14, border: `1px solid ${T.line}`, background: T.bg2, textAlign: 'left', cursor: 'pointer' }}
              >
                <div style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink, marginBottom: 6 }}>{s.id}</div>
                <Pill level={s.level} />
                <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1, textTransform: 'uppercase' }}>
                  COS SIM
                </div>
                <div style={{ fontFamily: T.fMono, fontSize: 18, color: T.accent, marginTop: 2 }}>
                  {s.similarity.toFixed(2)}
                </div>
                <div style={{ marginTop: 6, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
                  struggle {s.struggle_score.toFixed(2)}
                </div>
              </motion.button>
            ))}
          </div>
          <div style={{ marginTop: 14, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, lineHeight: 1.6 }}>
            Ranked by cosine similarity across 5 behavioural features (n̂, t̂, ī, Â, d̂). High similarity = comparable submission patterns.
          </div>
        </AnimatedCard>
      )}

      {/* RAG coaching suggestions */}
      <AnimatedCard variants={fadeUp}>
        <RagPanel audience="student" subjectId={data.id} sectionNumber={7} />
      </AnimatedCard>

      {/* Recent submissions */}
      <AnimatedCard variants={fadeUp} style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={8}>Recent Submissions</SectionLabel>
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
            <AnimatePresence initial={false}>
            {data.recent_submissions.map((r, i) => (
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
              </motion.tr>
            ))}
            </AnimatePresence>
          </tbody>
        </table>
      </AnimatedCard>

      {/* Submission timeline — hour-of-day distribution for this student */}
      <AnimatedCard variants={fadeUp} style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={9}>Submission Timeline</SectionLabel>
        <TimelineChart data={data.timeline_24h} semantic="hour_of_day" />
      </AnimatedCard>
    </motion.div>
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
      <AnimatedNumber
        value={value}
        style={{
          fontFamily: T.fSerif,
          fontSize: 28,
          color: T.ink,
          fontFeatureSettings: '"tnum"',
          whiteSpace: 'nowrap',
          display: 'inline-block',
        }}
      />
    </div>
  )
}

function formatTimestamp(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')} · ${d.toLocaleDateString()}`
}
