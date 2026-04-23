import { AnimatePresence, motion } from 'framer-motion'
import { T, LEVEL_STYLES } from '../../theme/tokens'
import type { StudentStruggle } from '../../types/api'
import { Pill } from '../../components/primitives/Pill'
import { AnimatedNumber } from '../../components/primitives/AnimatedNumber'
import { SessionStrip } from '../components/SessionStrip'
import { stagger, fadeUp } from '../../animation/motion'

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
    <motion.div variants={stagger} initial="initial" animate="animate">
      <motion.div
        variants={fadeUp}
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
      </motion.div>

      <div style={{ padding: 16 }}>
        <motion.div variants={fadeUp}>
          <SessionStrip assistantName={assistantName} sessionCode={sessionCode} onLeave={onLeave} />
        </motion.div>

        <motion.div
          variants={fadeUp}
          style={{
            marginTop: 18,
            padding: '18px 14px',
            background: T.card,
            border: `1px solid ${T.line}`,
            textAlign: 'center',
          }}
        >
          <div style={{ display: 'inline-flex', gap: 6, alignItems: 'center' }}>
            <motion.span
              animate={{ opacity: [1, 0.3, 1], scale: [1, 0.8, 1] }}
              transition={{ duration: 1.4, repeat: Infinity, ease: 'easeInOut' }}
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: T.accent,
                display: 'inline-block',
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
        </motion.div>

        <motion.div
          variants={fadeUp}
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
        </motion.div>
        <div style={{ height: 1, background: T.line, margin: '6px 0 10px' }} />

        {available.length === 0 ? (
          <motion.div
            variants={fadeUp}
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
          </motion.div>
        ) : (
          <motion.div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <AnimatePresence initial={false}>
              {available.map((s) => {
                const style = LEVEL_STYLES[s.level] ?? { fg: T.ink3, label: s.level }
                const isClaiming = claiming === s.id
                return (
                  <motion.div
                    key={s.id}
                    layout
                    initial={{ opacity: 0, y: 8, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, x: 20, scale: 0.96 }}
                    transition={{
                      type: 'spring',
                      stiffness: 360,
                      damping: 32,
                      opacity: { duration: 0.2 },
                    }}
                    style={{
                      padding: '12px 14px',
                      background: T.card,
                      border: `1px solid ${T.line}`,
                      borderLeft: `3px solid ${style.fg}`,
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'baseline',
                      }}
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
                      <AnimatedNumber
                        value={s.score.toFixed(2)}
                        duration={0.6}
                        style={{
                          fontFamily: T.fSerif,
                          fontSize: 26,
                          color: style.fg,
                          fontFeatureSettings: '"tnum"',
                          lineHeight: 1,
                          display: 'inline-block',
                        }}
                      />
                    </div>
                    {allowSelfAlloc && (
                      <motion.button
                        onClick={() => onClaim(s.id)}
                        disabled={isClaiming}
                        whileHover={isClaiming ? undefined : { background: T.accent, color: '#fff' }}
                        whileTap={isClaiming ? undefined : { scale: 0.97 }}
                        transition={{ duration: 0.15 }}
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
                      </motion.button>
                    )}
                  </motion.div>
                )
              })}
            </AnimatePresence>
          </motion.div>
        )}

        {!allowSelfAlloc && available.length > 0 && (
          <motion.div
            variants={fadeUp}
            style={{
              marginTop: 12,
              fontFamily: T.fMono,
              fontSize: 10,
              color: T.ink3,
              lineHeight: 1.5,
            }}
          >
            Self-allocation disabled — wait for the instructor to assign you.
          </motion.div>
        )}
        {hiddenCount > 0 && (
          <motion.div
            variants={fadeUp}
            style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 9.5, color: T.ink3 }}
          >
            {hiddenCount} student(s) not shown (Minor Issues or On Track).
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
