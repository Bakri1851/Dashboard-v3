import { AnimatePresence, motion } from 'framer-motion'
import { T, LEVEL_STYLES } from '../../theme/tokens'
import type { StrugglingQuestionRow, StudentDetail, RagSuggestions } from '../../types/api'
import { Pill } from '../../components/primitives/Pill'
import { AnimatedNumber } from '../../components/primitives/AnimatedNumber'
import { SessionStrip } from '../components/SessionStrip'
import { CornerMarks } from '../components/CornerMarks'
import { stagger, fadeUp } from '../../animation/motion'

interface Props {
  assistantName: string
  sessionCode: string | null
  studentId: string
  detail: StudentDetail | null
  detailLoading: boolean
  suggestions: RagSuggestions | null
  topQuestions: StrugglingQuestionRow[] | null
  helpedFlash: boolean
  assignmentStatus: string
  busy: boolean
  onMarkHelped: () => void
  onRelease: () => void
  onLeave: () => void
}

function formatTime(minutes: number | null | undefined): string {
  if (minutes == null || !isFinite(minutes) || minutes <= 0) return '—'
  const total = Math.round(minutes)
  const h = Math.floor(total / 60)
  const m = total % 60
  if (h > 0) return `${h}h ${String(m).padStart(2, '0')}m`
  return `${m}m`
}

function truncate(q: string, max = 50): string {
  if (q.length <= max) return q
  return q.slice(0, max - 3) + '…'
}

export function MobileAssigned({
  assistantName,
  sessionCode,
  studentId,
  detail,
  detailLoading,
  suggestions,
  topQuestions,
  helpedFlash,
  assignmentStatus,
  busy,
  onMarkHelped,
  onRelease,
  onLeave,
}: Props) {
  const isHelped = assignmentStatus === 'helped'
  const showHelpedBanner = isHelped || helpedFlash
  const firstName = assistantName.split(/\s+/)[0] || assistantName
  const level = detail?.level ?? ''
  const style = LEVEL_STYLES[level] ?? { fg: T.ink, label: level }
  const score = detail?.score ?? 0
  const subs = detail?.submissions ?? 0
  const timeLabel = formatTime(detail?.time_active_min ?? null)
  const retryLabel = detail ? `${Math.round(detail.retry_rate * 100)}%` : '—'

  return (
    <motion.div variants={stagger} initial="initial" animate="animate">
      <motion.div
        variants={fadeUp}
        style={{
          padding: '18px 22px 14px',
          textAlign: 'center',
          borderBottom: `1px solid ${T.line}`,
        }}
      >
        <div
          style={{
            fontFamily: T.fMono,
            fontSize: 10,
            color: T.accent,
            letterSpacing: 2,
            textTransform: 'uppercase',
          }}
        >
          <motion.span
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1.4, repeat: Infinity, ease: 'easeInOut' }}
            style={{ display: 'inline-block', marginRight: 4 }}
          >
            ●
          </motion.span>
          Active Assignment
        </div>
        <div style={{ fontFamily: T.fSerif, fontSize: 20, color: T.ink, marginTop: 4, lineHeight: 1.1 }}>
          Hello, {firstName}
        </div>
      </motion.div>

      <div style={{ padding: 14 }}>
        <motion.div variants={fadeUp}>
          <SessionStrip assistantName={assistantName} sessionCode={sessionCode} onLeave={onLeave} />
        </motion.div>

        {/* Hero student card — celebratory entrance */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{
            type: 'spring',
            stiffness: 320,
            damping: 22,
            mass: 0.8,
            delay: 0.1,
          }}
          style={{
            position: 'relative',
            marginTop: 14,
            padding: '18px 16px',
            background: T.card,
            border: `2px solid ${style.fg}`,
          }}
        >
          {/* Arrival glow — fades out after celebratory pulse */}
          <motion.div
            aria-hidden
            initial={{ opacity: 0.55, scale: 1 }}
            animate={{ opacity: 0, scale: 1.05 }}
            transition={{ duration: 1.2, ease: 'easeOut', delay: 0.1 }}
            style={{
              position: 'absolute',
              inset: -2,
              border: `2px solid ${style.fg}`,
              pointerEvents: 'none',
              boxShadow: `0 0 24px ${style.fg}`,
            }}
          />
          <CornerMarks color={style.fg} />
          <div
            style={{
              fontFamily: T.fMono,
              fontSize: 9.5,
              color: T.ink3,
              letterSpacing: 1.4,
              textTransform: 'uppercase',
            }}
          >
            Your Student
          </div>
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.3 }}
            style={{
              fontFamily: T.fMono,
              fontSize: 20,
              color: T.ink,
              marginTop: 6,
              letterSpacing: 2,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {studentId}
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              type: 'spring',
              stiffness: 380,
              damping: 20,
              delay: 0.4,
            }}
            style={{
              fontFamily: T.fSerif,
              fontSize: 54,
              color: style.fg,
              marginTop: 4,
              lineHeight: 0.95,
              fontFeatureSettings: '"tnum"',
              textShadow: `0 0 18px ${style.fg}55`,
            }}
          >
            {detail ? (
              <AnimatedNumber
                value={score.toFixed(3)}
                duration={0.9}
                style={{ display: 'inline-block' }}
              />
            ) : (
              '—'
            )}
          </motion.div>
          {detail && (
            <motion.div
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.55 }}
              style={{ marginTop: 8 }}
            >
              <Pill level={level} />
            </motion.div>
          )}

          <div
            style={{
              marginTop: 12,
              paddingTop: 12,
              borderTop: `1px dashed ${T.line}`,
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: 8,
            }}
          >
            {[
              { l: 'Subs', v: detail ? String(subs) : '—' },
              { l: 'Time', v: timeLabel },
              { l: 'Retry', v: retryLabel },
            ].map((m, i) => (
              <motion.div
                key={m.l}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.55 + i * 0.06 }}
              >
                <div
                  style={{
                    fontFamily: T.fMono,
                    fontSize: 9,
                    color: T.ink3,
                    letterSpacing: 1.1,
                    textTransform: 'uppercase',
                  }}
                >
                  {m.l}
                </div>
                <div style={{ fontFamily: T.fMono, fontSize: 13, color: T.ink, marginTop: 2 }}>
                  <AnimatedNumber value={m.v} style={{ display: 'inline-block' }} />
                </div>
              </motion.div>
            ))}
          </div>
          {detailLoading && !detail && (
            <div
              style={{
                marginTop: 12,
                fontFamily: T.fMono,
                fontSize: 10,
                color: T.ink3,
                letterSpacing: 1,
              }}
            >
              loading student metrics…
            </div>
          )}
        </motion.div>

        {/* RAG suggestions */}
        <motion.div variants={fadeUp} style={{ marginTop: 18 }}>
          <div
            style={{
              fontFamily: T.fMono,
              fontSize: 10,
              color: T.ink3,
              letterSpacing: 1.4,
              textTransform: 'uppercase',
              display: 'flex',
              justifyContent: 'space-between',
            }}
          >
            <span>§02 Suggested Focus Areas</span>
            <span style={{ color: T.accent }}>RAG</span>
          </div>
          <div style={{ height: 1, background: T.line, margin: '6px 0 10px' }} />
          <AnimatePresence mode="wait" initial={false}>
            {suggestions && suggestions.bullets.length > 0 ? (
              <motion.div
                key="bullets"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                style={{
                  padding: 12,
                  background: T.accentSoft,
                  border: `1px solid ${T.accent}`,
                  fontFamily: T.fSans,
                  fontSize: 12.5,
                  color: T.ink,
                  lineHeight: 1.55,
                }}
              >
                <motion.ul
                  initial="initial"
                  animate="animate"
                  variants={{
                    initial: {},
                    animate: { transition: { staggerChildren: 0.07 } },
                  }}
                  style={{ margin: 0, paddingLeft: 16 }}
                >
                  {suggestions.bullets.map((b, i) => (
                    <motion.li
                      key={i}
                      variants={{
                        initial: { opacity: 0, x: -6 },
                        animate: { opacity: 1, x: 0 },
                      }}
                      transition={{ duration: 0.3 }}
                      style={{ marginBottom: i < suggestions.bullets.length - 1 ? 6 : 0 }}
                    >
                      {b}
                    </motion.li>
                  ))}
                </motion.ul>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                style={{
                  padding: 12,
                  background: T.bg2,
                  border: `1px dashed ${T.line2}`,
                  fontFamily: T.fMono,
                  fontSize: 10.5,
                  color: T.ink3,
                  textAlign: 'center',
                }}
              >
                {suggestions == null
                  ? 'Loading suggestions…'
                  : 'No recent context — ask the student what they were working on.'}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Top-3 struggling questions */}
        <motion.div variants={fadeUp} style={{ marginTop: 18 }}>
          <div
            style={{
              fontFamily: T.fMono,
              fontSize: 10,
              color: T.ink3,
              letterSpacing: 1.4,
              textTransform: 'uppercase',
            }}
          >
            §03 Top Struggling Questions
          </div>
          <div style={{ height: 1, background: T.line, margin: '6px 0 10px' }} />
          {topQuestions == null ? (
            <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>loading…</div>
          ) : topQuestions.length === 0 ? (
            <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
              No struggling questions on record — check in with the student directly.
            </div>
          ) : (
            topQuestions.map((q, i) => {
              const pct = Math.round(q.avg_incorrectness * 100)
              const isLast = i === topQuestions.length - 1
              return (
                <motion.div
                  key={`${q.question}-${i}`}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.2 + i * 0.08 }}
                  style={{
                    padding: '10px 0',
                    borderBottom: isLast ? 'none' : `1px solid ${T.line}`,
                  }}
                >
                  <div
                    style={{
                      fontFamily: T.fMono,
                      fontSize: 11.5,
                      color: T.ink,
                      lineHeight: 1.4,
                      wordBreak: 'break-word',
                    }}
                  >
                    {truncate(q.question)}
                  </div>
                  <div
                    style={{
                      marginTop: 6,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                    }}
                  >
                    <div
                      style={{
                        flex: 1,
                        maxWidth: 160,
                        height: 3,
                        background: T.line,
                        overflow: 'hidden',
                      }}
                    >
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{
                          width: `${Math.max(0, Math.min(100, q.avg_incorrectness * 100))}%`,
                        }}
                        transition={{
                          type: 'spring',
                          stiffness: 100,
                          damping: 22,
                          delay: 0.3 + i * 0.08,
                        }}
                        style={{
                          height: '100%',
                          background: q.avg_incorrectness > 0.5 ? T.danger : T.warn,
                        }}
                      />
                    </div>
                    <span style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
                      Avg incorrect · {pct}%
                    </span>
                  </div>
                </motion.div>
              )
            })
          )}
        </motion.div>

        <AnimatePresence>
          {showHelpedBanner && (
            <motion.div
              key="helped"
              initial={{ opacity: 0, scale: 0.9, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -4 }}
              transition={{ type: 'spring', stiffness: 380, damping: 22 }}
              style={{
                marginTop: 16,
                padding: '10px 12px',
                background: T.bg2,
                border: `1px solid ${T.ok}`,
                fontFamily: T.fMono,
                fontSize: 11,
                color: T.ok,
                letterSpacing: 0.4,
                textAlign: 'center',
              }}
            >
              ✓ Marked as helped.
            </motion.div>
          )}
        </AnimatePresence>

        <motion.div
          variants={fadeUp}
          style={{
            marginTop: 18,
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 8,
          }}
        >
          <motion.button
            onClick={onMarkHelped}
            disabled={busy}
            whileHover={busy ? undefined : { filter: 'brightness(1.15)' }}
            whileTap={busy ? undefined : { scale: 0.96 }}
            style={{
              padding: '12px 0',
              background: T.ok,
              color: T.bg,
              border: 'none',
              fontFamily: T.fMono,
              fontSize: 11,
              letterSpacing: 1.3,
              textTransform: 'uppercase',
              cursor: busy ? 'wait' : 'pointer',
              fontWeight: 500,
              opacity: busy ? 0.6 : 1,
            }}
          >
            ✓ Mark Helped
          </motion.button>
          <motion.button
            onClick={onRelease}
            disabled={busy}
            whileHover={busy ? undefined : { borderColor: T.danger, color: T.danger }}
            whileTap={busy ? undefined : { scale: 0.96 }}
            transition={{ duration: 0.15 }}
            style={{
              padding: '12px 0',
              background: 'transparent',
              color: T.ink,
              border: `1px solid ${T.line2}`,
              fontFamily: T.fMono,
              fontSize: 11,
              letterSpacing: 1.3,
              textTransform: 'uppercase',
              cursor: busy ? 'wait' : 'pointer',
              opacity: busy ? 0.6 : 1,
            }}
          >
            ↩ Release
          </motion.button>
        </motion.div>
      </div>
    </motion.div>
  )
}
