import { T, LEVEL_STYLES } from '../../theme/tokens'
import type { StudentStruggle } from '../../types/api'
import { Pill } from '../../components/primitives/Pill'
import { SessionStrip } from '../components/SessionStrip'

interface Props {
  assistantName: string
  sessionCode: string | null
  available: StudentStruggle[]
  hiddenCount: number
  allowSelfAlloc: boolean
  claiming: string | null
  onClaim: (studentId: string) => void
  onLeave: () => void
}

const pulseKeyframes = `@keyframes mobilePulseDot { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.3; transform: scale(0.8); } }`

export function MobileUnassigned({
  assistantName,
  sessionCode,
  available,
  hiddenCount,
  allowSelfAlloc,
  claiming,
  onClaim,
  onLeave,
}: Props) {
  const firstName = assistantName.split(/\s+/)[0] || assistantName
  return (
    <div>
      <style>{pulseKeyframes}</style>
      <div
        style={{
          padding: '22px 22px 14px',
          textAlign: 'center',
          borderBottom: `1px solid ${T.line}`,
        }}
      >
        <div
          style={{
            fontFamily: T.fMono,
            fontSize: 10,
            color: T.ink3,
            letterSpacing: 2,
            textTransform: 'uppercase',
          }}
        >
          Waiting for Assignment
        </div>
        <div style={{ fontFamily: T.fSerif, fontSize: 22, color: T.ink, marginTop: 4, lineHeight: 1.1 }}>
          Hello, {firstName}
        </div>
      </div>

      <div style={{ padding: 16 }}>
        <SessionStrip assistantName={assistantName} sessionCode={sessionCode} onLeave={onLeave} />

        <div
          style={{
            marginTop: 18,
            padding: '18px 14px',
            background: T.card,
            border: `1px solid ${T.line}`,
            textAlign: 'center',
          }}
        >
          <div style={{ display: 'inline-flex', gap: 6, alignItems: 'center' }}>
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: T.accent,
                animation: 'mobilePulseDot 1.4s infinite',
              }}
            />
            <span
              style={{
                fontFamily: T.fMono,
                fontSize: 10.5,
                color: T.accent,
                letterSpacing: 1.4,
                textTransform: 'uppercase',
              }}
            >
              Standby
            </span>
          </div>
          <div
            style={{
              marginTop: 10,
              fontFamily: T.fSans,
              fontSize: 12.5,
              color: T.ink2,
              lineHeight: 1.5,
            }}
          >
            Instructor will assign you a student.
            <br />
            This screen updates automatically.
          </div>
        </div>

        <div
          style={{
            marginTop: 20,
            fontFamily: T.fMono,
            fontSize: 10,
            color: T.ink3,
            letterSpacing: 1.4,
            textTransform: 'uppercase',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'baseline',
          }}
        >
          <span>§01 Available Students</span>
          <span style={{ color: allowSelfAlloc ? T.ok : T.ink3 }}>
            {allowSelfAlloc ? 'SELF-CLAIM ON' : 'SELF-CLAIM OFF'}
          </span>
        </div>
        <div style={{ height: 1, background: T.line, margin: '6px 0 10px' }} />

        {available.length === 0 ? (
          <div
            style={{
              padding: '16px 14px',
              background: T.bg2,
              border: `1px solid ${T.ok}`,
              fontFamily: T.fMono,
              fontSize: 11,
              color: T.ok,
              letterSpacing: 0.4,
              lineHeight: 1.5,
            }}
          >
            ✓ All struggling students are covered — great work!
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {available.map((s) => {
              const style = LEVEL_STYLES[s.level] ?? { fg: T.ink3, label: s.level }
              const isClaiming = claiming === s.id
              return (
                <div
                  key={s.id}
                  style={{
                    padding: '12px 14px',
                    background: T.card,
                    border: `1px solid ${T.line}`,
                    borderLeft: `3px solid ${style.fg}`,
                  }}
                >
                  <div
                    style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}
                  >
                    <div style={{ minWidth: 0 }}>
                      <div
                        style={{
                          fontFamily: T.fMono,
                          fontSize: 13,
                          color: T.ink,
                          letterSpacing: 0.8,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {s.id}
                      </div>
                      <div style={{ marginTop: 6 }}>
                        <Pill level={s.level} />
                      </div>
                    </div>
                    <div
                      style={{
                        fontFamily: T.fSerif,
                        fontSize: 26,
                        color: style.fg,
                        fontFeatureSettings: '"tnum"',
                        lineHeight: 1,
                      }}
                    >
                      {s.score.toFixed(2)}
                    </div>
                  </div>
                  {allowSelfAlloc && (
                    <button
                      onClick={() => onClaim(s.id)}
                      disabled={isClaiming}
                      style={{
                        marginTop: 10,
                        width: '100%',
                        padding: '8px 0',
                        background: 'transparent',
                        color: T.accent,
                        border: `1px solid ${T.accent}`,
                        fontFamily: T.fMono,
                        fontSize: 10.5,
                        letterSpacing: 1.3,
                        textTransform: 'uppercase',
                        cursor: isClaiming ? 'wait' : 'pointer',
                        opacity: isClaiming ? 0.6 : 1,
                      }}
                    >
                      {isClaiming ? 'Claiming…' : `Help ${s.id} →`}
                    </button>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {!allowSelfAlloc && available.length > 0 && (
          <div
            style={{
              marginTop: 12,
              fontFamily: T.fMono,
              fontSize: 10,
              color: T.ink3,
              lineHeight: 1.5,
            }}
          >
            Self-allocation disabled — wait for the instructor to assign you.
          </div>
        )}
        {hiddenCount > 0 && (
          <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 9.5, color: T.ink3 }}>
            {hiddenCount} student(s) not shown (Minor Issues or On Track).
          </div>
        )}
      </div>
    </div>
  )
}
