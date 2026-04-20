import { T } from '../../theme/tokens'

/** Shown when the instructor has not started a lab session. */
export function MobileSessionEnded() {
  return (
    <div style={{ padding: '40px 22px', textAlign: 'center' }}>
      <div
        style={{
          fontFamily: T.fMono,
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 2,
          textTransform: 'uppercase',
        }}
      >
        Lab Assistant Portal
      </div>

      <div
        style={{
          margin: '44px auto 0',
          width: 74,
          height: 74,
          border: `1.5px solid ${T.danger}`,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 6,
            border: `1px dashed ${T.danger}`,
            borderRadius: '50%',
            opacity: 0.55,
          }}
        />
        <span style={{ fontFamily: T.fMono, fontSize: 26, color: T.danger }}>✕</span>
      </div>

      <div
        style={{
          marginTop: 22,
          fontFamily: T.fSerif,
          fontSize: 22,
          color: T.danger,
          letterSpacing: 1,
          textTransform: 'uppercase',
          lineHeight: 1.15,
        }}
      >
        No Active Session
      </div>

      <div
        style={{
          marginTop: 14,
          maxWidth: 260,
          margin: '14px auto 0',
          fontFamily: T.fSans,
          fontSize: 13,
          color: T.ink2,
          lineHeight: 1.55,
        }}
      >
        Ask your instructor to start a lab session — this portal will refresh automatically.
      </div>

      <div
        style={{
          marginTop: 32,
          padding: '12px 14px',
          background: T.bg2,
          border: `1px dashed ${T.line2}`,
          fontFamily: T.fMono,
          fontSize: 10.5,
          color: T.ink3,
          textAlign: 'left',
          lineHeight: 1.55,
        }}
      >
        <span style={{ color: T.ink2 }}>polling</span> · every 5s
      </div>
    </div>
  )
}
