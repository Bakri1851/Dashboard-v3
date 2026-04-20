import { T, LEVEL_STYLES } from '../../theme/tokens'
import type { StrugglingQuestionRow, StudentDetail, RagSuggestions } from '../../types/api'
import { Pill } from '../../components/primitives/Pill'
import { SessionStrip } from '../components/SessionStrip'
import { CornerMarks } from '../components/CornerMarks'

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
    <div>
      <div
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
          ● Active Assignment
        </div>
        <div style={{ fontFamily: T.fSerif, fontSize: 20, color: T.ink, marginTop: 4, lineHeight: 1.1 }}>
          Hello, {firstName}
        </div>
      </div>

      <div style={{ padding: 14 }}>
        <SessionStrip assistantName={assistantName} sessionCode={sessionCode} onLeave={onLeave} />

        {/* Hero student card */}
        <div
          style={{
            position: 'relative',
            marginTop: 14,
            padding: '18px 16px',
            background: T.card,
            border: `2px solid ${style.fg}`,
          }}
        >
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
          <div
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
          </div>
          <div
            style={{
              fontFamily: T.fSerif,
              fontSize: 54,
              color: style.fg,
              marginTop: 4,
              lineHeight: 0.95,
              fontFeatureSettings: '"tnum"',
            }}
          >
            {detail ? score.toFixed(3) : '—'}
          </div>
          {detail && (
            <div style={{ marginTop: 8 }}>
              <Pill level={level} />
            </div>
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
            ].map((m) => (
              <div key={m.l}>
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
                <div style={{ fontFamily: T.fMono, fontSize: 13, color: T.ink, marginTop: 2 }}>{m.v}</div>
              </div>
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
        </div>

        {/* RAG suggestions */}
        <div style={{ marginTop: 18 }}>
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
          {suggestions && suggestions.bullets.length > 0 ? (
            <div
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
              <ul style={{ margin: 0, paddingLeft: 16 }}>
                {suggestions.bullets.map((b, i) => (
                  <li key={i} style={{ marginBottom: i < suggestions.bullets.length - 1 ? 6 : 0 }}>
                    {b}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <div
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
              {suggestions == null ? 'Loading suggestions…' : 'Not enough data yet.'}
            </div>
          )}
        </div>

        {/* Top-3 struggling questions */}
        <div style={{ marginTop: 18 }}>
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
              No submission data for this student yet.
            </div>
          ) : (
            topQuestions.map((q, i) => {
              const pct = Math.round(q.avg_incorrectness * 100)
              const isLast = i === topQuestions.length - 1
              return (
                <div
                  key={`${q.question}-${i}`}
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
                      <div
                        style={{
                          width: `${Math.max(0, Math.min(100, q.avg_incorrectness * 100))}%`,
                          height: '100%',
                          background: q.avg_incorrectness > 0.5 ? T.danger : T.warn,
                        }}
                      />
                    </div>
                    <span style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
                      Avg incorrect · {pct}%
                    </span>
                  </div>
                </div>
              )
            })
          )}
        </div>

        {showHelpedBanner && (
          <div
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
          </div>
        )}

        <div
          style={{
            marginTop: 18,
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 8,
          }}
        >
          <button
            onClick={onMarkHelped}
            disabled={busy}
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
          </button>
          <button
            onClick={onRelease}
            disabled={busy}
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
          </button>
        </div>
      </div>
    </div>
  )
}
