import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { T, LEVEL_STYLES } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import type { SessionProgression } from '../types/api'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { Skeleton } from '../components/primitives/Skeleton'
import { Tooltip } from '../components/primitives/Tooltip'
import { LevelChips } from '../components/primitives/LevelChips'
import { Pill } from '../components/primitives/Pill'
import { AnimatedNumber } from '../components/primitives/AnimatedNumber'
import { StackedArea } from '../components/charts/StackedArea'
import { AnimatedCard } from '../animation/AnimatedCard'
import { stagger, fadeUp } from '../animation/motion'
import { useViewStore } from '../state/viewStore'

const STRUGGLE_ORDER = ['On Track', 'Minor Issues', 'Struggling', 'Needs Help']

function fmtTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function fmtClock(iso: string): string {
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

export function SessionProgressionView({ sessionId }: { sessionId: string }) {
  const { data, error, loading } = useApiData<SessionProgression>(
    `/sessions/${encodeURIComponent(sessionId)}/progression?buckets=20`
  )
  const pickStudent = useViewStore((s) => s.pickStudent)
  const setView = useViewStore((s) => s.setView)

  const [scrubIdx, setScrubIdx] = useState<number | null>(null)
  const activePoint = useMemo(() => {
    if (!data || data.points.length === 0) return null
    const idx = scrubIdx ?? data.points.length - 1
    return data.points[Math.max(0, Math.min(idx, data.points.length - 1))]
  }, [data, scrubIdx])

  if (loading && !data) {
    return (
      <motion.div
        variants={stagger}
        initial="initial"
        animate="animate"
        style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}
      >
        <AnimatedCard variants={fadeUp}>
          <Skeleton variant="text" width="40%" height={14} />
          <div style={{ height: 12 }} />
          <Skeleton variant="block" height={200} />
        </AnimatedCard>
      </motion.div>
    )
  }
  if (error) {
    return (
      <div style={{ padding: 36, color: T.danger, fontFamily: T.fMono, fontSize: 12 }}>{error}</div>
    )
  }
  if (!data) return null

  const sess = data.session
  const points = data.points
  const struggleSeries = STRUGGLE_ORDER.map((label) => ({
    label,
    color: LEVEL_STYLES[label]?.fg ?? T.ink2,
    values: points.map((p) => p.struggle_buckets.find((b) => b.label === label)?.count ?? 0),
  }))
  const cumulativeSubs = points.map((p) => p.cumulative_submissions)
  const meanInc = points.map((p) => p.mean_incorrectness)

  // 5 evenly spaced x-axis labels
  const xLabels = points.length
    ? [0, 0.25, 0.5, 0.75, 1]
        .map((r) => Math.round(r * (points.length - 1)))
        .map((i) => fmtClock(points[i].t_end))
    : []

  return (
    <motion.div
      variants={stagger}
      initial="initial"
      animate="animate"
      style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}
    >
      {/* Header bar */}
      <AnimatedCard
        variants={fadeUp}
        style={{ padding: '22px 26px', background: T.card, border: `1px solid ${T.line}` }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div
              style={{
                fontFamily: T.fMono,
                fontSize: 10.5,
                color: T.ink3,
                letterSpacing: 1.3,
                textTransform: 'uppercase',
              }}
            >
              Session Progression
            </div>
            <div style={{ fontFamily: T.fSerif, fontSize: 24, color: T.ink, marginTop: 6 }}>
              {sess.name}
            </div>
            <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3, marginTop: 6 }}>
              {fmtTime(sess.start_time)} → {fmtTime(sess.end_time)}
              {sess.duration_minutes != null && (
                <>
                  {' · '}
                  {Math.floor(sess.duration_minutes / 60) > 0
                    ? `${Math.floor(sess.duration_minutes / 60)}h ${Math.round(sess.duration_minutes % 60)}m`
                    : `${Math.round(sess.duration_minutes)}m`}
                </>
              )}
              {data.bucket_minutes > 0 && <> · bucket ≈ {data.bucket_minutes.toFixed(1)} min</>}
            </div>
          </div>
          <motion.button
            onClick={() => setView('previous')}
            whileHover={{ borderColor: T.ink2, color: T.ink }}
            whileTap={{ scale: 0.96 }}
            style={{
              padding: '6px 14px',
              background: 'transparent',
              color: T.ink2,
              border: `1px solid ${T.line}`,
              fontFamily: T.fMono,
              fontSize: 11,
              letterSpacing: 1.2,
              textTransform: 'uppercase',
              cursor: 'pointer',
              alignSelf: 'flex-start',
            }}
          >
            ← Back to sessions
          </motion.button>
        </div>
      </AnimatedCard>

      {points.length === 0 ? (
        <AnimatedCard variants={fadeUp} style={{ padding: 28, background: T.card, border: `1px solid ${T.line}` }}>
          <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>
            No submissions fell inside this session's time window — nothing to replay.
          </div>
        </AnimatedCard>
      ) : (
        <>
          {/* Stacked-area: struggle levels over time */}
          <AnimatedCard
            variants={fadeUp}
            style={{ padding: 22, background: T.card, border: `1px solid ${T.line}` }}
          >
            <Tooltip content="Count of students in each struggle band at each bucket end. Watch the Needs Help (red) region rise or fall across the session — that's how the struggle picture evolved.">
              <span style={{ cursor: 'help' }}>
                <SectionLabel n={1}>Struggle Levels Over Time</SectionLabel>
              </span>
            </Tooltip>
            <StackedArea
              series={struggleSeries}
              height={200}
              xLabels={xLabels}
              onHoverBucket={(idx) => setScrubIdx(idx)}
              activeIndex={scrubIdx}
            />
          </AnimatedCard>

          {/* Scrub snapshot + line charts */}
          <AnimatedCard
            variants={fadeUp}
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 1fr)',
              gap: 20,
            }}
          >
            {/* Cumulative submissions + mean incorrectness sparkline */}
            <div style={{ padding: 22, background: T.card, border: `1px solid ${T.line}` }}>
              <Tooltip content="Left axis: cumulative submissions (class-total, monotonically rises). Right axis: mean AI incorrectness across all submissions up to this bucket.">
                <span style={{ cursor: 'help' }}>
                  <SectionLabel n={2}>Submissions & Mean Incorrectness</SectionLabel>
                </span>
              </Tooltip>
              <DualLineChart
                cumulative={cumulativeSubs}
                mean={meanInc}
                xLabels={xLabels}
                activeIndex={scrubIdx}
              />
            </div>

            {/* Scrub snapshot panel */}
            <div style={{ padding: 22, background: T.card, border: `1px solid ${T.line}` }}>
              <Tooltip content="The class state at the selected point in time. Hover the chart above to scrub — release to see the final snapshot.">
                <span style={{ cursor: 'help' }}>
                  <SectionLabel n={3}>Snapshot</SectionLabel>
                </span>
              </Tooltip>
              {activePoint && (
                <>
                  <div
                    style={{
                      fontFamily: T.fMono,
                      fontSize: 11,
                      color: T.ink3,
                      letterSpacing: 0.5,
                      marginBottom: 12,
                    }}
                  >
                    at {fmtClock(activePoint.t_end)}{' '}
                    {scrubIdx == null && (
                      <span style={{ color: T.ink3, opacity: 0.7 }}>· end of session</span>
                    )}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 12 }}>
                    <SnapshotStat
                      label="Submissions"
                      value={activePoint.cumulative_submissions.toLocaleString()}
                    />
                    <SnapshotStat
                      label="Students"
                      value={String(activePoint.cumulative_students)}
                    />
                    <SnapshotStat
                      label="Mean inc."
                      value={activePoint.mean_incorrectness.toFixed(2)}
                    />
                  </div>
                  <div style={{ marginTop: 14 }}>
                    <LevelChips buckets={activePoint.struggle_buckets} />
                  </div>

                  {activePoint.needs_help_ids.length > 0 && (
                    <div style={{ marginTop: 18 }}>
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
                        Needs Help at this point
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                        {activePoint.needs_help_ids.slice(0, 16).map((id) => (
                          <motion.button
                            key={id}
                            onClick={() => pickStudent(id)}
                            whileHover={{ borderColor: T.danger, color: T.ink }}
                            whileTap={{ scale: 0.96 }}
                            style={{
                              padding: '4px 9px',
                              background: 'transparent',
                              border: `1px solid ${T.line2}`,
                              color: T.ink2,
                              fontFamily: T.fMono,
                              fontSize: 11,
                              cursor: 'pointer',
                            }}
                          >
                            {id}
                          </motion.button>
                        ))}
                        {activePoint.needs_help_ids.length > 16 && (
                          <span style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, alignSelf: 'center' }}>
                            +{activePoint.needs_help_ids.length - 16} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </AnimatedCard>

          {/* Bucket scrubber */}
          <AnimatedCard
            variants={fadeUp}
            style={{ padding: '18px 22px', background: T.card, border: `1px solid ${T.line}` }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                fontFamily: T.fMono,
                fontSize: 10.5,
                color: T.ink3,
                letterSpacing: 1.1,
                textTransform: 'uppercase',
                marginBottom: 8,
              }}
            >
              <span>Scrub</span>
              <span>
                {scrubIdx != null ? `bucket ${scrubIdx + 1} / ${points.length}` : `end of session`}
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={points.length - 1}
              value={scrubIdx ?? points.length - 1}
              onChange={(e) => setScrubIdx(Number(e.target.value))}
              onMouseUp={() => {
                /* keep scrub position until user moves off */
              }}
              style={{ width: '100%', accentColor: T.accent }}
            />
            <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between' }}>
              <button
                onClick={() => setScrubIdx(null)}
                style={{
                  padding: '4px 10px',
                  background: 'transparent',
                  color: T.ink2,
                  border: `1px solid ${T.line}`,
                  fontFamily: T.fMono,
                  fontSize: 10,
                  letterSpacing: 1,
                  textTransform: 'uppercase',
                  cursor: 'pointer',
                }}
              >
                Jump to end
              </button>
              {activePoint?.struggle_buckets && (
                <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>
                  {activePoint.struggle_buckets
                    .find((b) => b.label === 'Needs Help')
                    ?.count ?? 0}{' '}
                  needs help · {activePoint.cumulative_submissions.toLocaleString()} total subs
                </div>
              )}
            </div>
          </AnimatedCard>

          {/* Final state — level pills + badge */}
          <AnimatedCard
            variants={fadeUp}
            style={{ padding: 22, background: T.card, border: `1px solid ${T.line}` }}
          >
            <SectionLabel n={4}>End of Session</SectionLabel>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginTop: 8 }}>
              <Pill level="Needs Help" />
              <span style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink }}>
                {points[points.length - 1].struggle_buckets.find((b) => b.label === 'Needs Help')?.count ?? 0}{' '}
                students flagged at the end
              </span>
              <span style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginLeft: 10 }}>
                peak during session:{' '}
                {Math.max(
                  ...points.map(
                    (p) => p.struggle_buckets.find((b) => b.label === 'Needs Help')?.count ?? 0
                  )
                )}
              </span>
            </div>
          </AnimatedCard>
        </>
      )}
    </motion.div>
  )
}

function SnapshotStat({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ padding: '10px 12px', background: T.bg2, border: `1px solid ${T.line2}` }}>
      <div
        style={{
          fontFamily: T.fMono,
          fontSize: 9.5,
          color: T.ink3,
          letterSpacing: 1.1,
          textTransform: 'uppercase',
        }}
      >
        {label}
      </div>
      <AnimatedNumber
        value={value}
        style={{
          fontFamily: T.fSerif,
          fontSize: 22,
          color: T.ink,
          fontFeatureSettings: '"tnum"',
          marginTop: 4,
          display: 'inline-block',
        }}
      />
    </div>
  )
}

/**
 * Dual-axis sparkline — cumulative submissions (left, accent) and mean
 * incorrectness (right, warn). Independent normalization so both curves fit
 * within the same height.
 */
function DualLineChart({
  cumulative,
  mean,
  xLabels,
  activeIndex,
}: {
  cumulative: number[]
  mean: number[]
  xLabels: string[]
  activeIndex: number | null
}) {
  const n = cumulative.length
  const W = 1000
  const H = 160
  const maxC = Math.max(1, ...cumulative)
  const stepX = n > 1 ? W / (n - 1) : W
  const yCum = (v: number) => H - (v / maxC) * H
  const yMean = (v: number) => H - Math.min(1, v) * H
  const cumPath = cumulative
    .map((v, i) => `${i === 0 ? 'M' : 'L'}${(i * stepX).toFixed(1)},${yCum(v).toFixed(1)}`)
    .join(' ')
  const meanPath = mean
    .map((v, i) => `${i === 0 ? 'M' : 'L'}${(i * stepX).toFixed(1)},${yMean(v).toFixed(1)}`)
    .join(' ')
  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" style={{ width: '100%', height: H }}>
        <path d={cumPath} fill="none" stroke={T.accent} strokeWidth={2} />
        <path d={meanPath} fill="none" stroke={T.warn} strokeWidth={1.5} strokeDasharray="4 3" />
        {activeIndex != null && activeIndex >= 0 && activeIndex < n && (
          <line
            x1={activeIndex * stepX}
            x2={activeIndex * stepX}
            y1={0}
            y2={H}
            stroke={T.ink}
            strokeOpacity={0.5}
            strokeDasharray="3 3"
          />
        )}
      </svg>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: 6,
          fontFamily: T.fMono,
          fontSize: 9.5,
          color: T.ink3,
        }}
      >
        {xLabels.map((l, i) => (
          <span key={i}>{l}</span>
        ))}
      </div>
      <div
        style={{
          display: 'flex',
          gap: 14,
          marginTop: 10,
          fontFamily: T.fMono,
          fontSize: 10.5,
          color: T.ink3,
          flexWrap: 'wrap',
        }}
      >
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 14, height: 2, background: T.accent, display: 'inline-block' }} /> cumulative submissions (max {maxC})
        </span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <span
            style={{
              width: 14,
              height: 2,
              background: T.warn,
              display: 'inline-block',
              borderTop: `1.5px dashed ${T.warn}`,
            }}
          />{' '}
          mean incorrectness (0–1)
        </span>
      </div>
    </div>
  )
}
