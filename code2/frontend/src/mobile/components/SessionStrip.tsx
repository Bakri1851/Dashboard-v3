import { T } from '../../theme/tokens'

interface Props {
  assistantName: string
  sessionCode: string | null
  onLeave: () => void
}

/** Pinned status strip shown on unassigned + assigned views. */
export function SessionStrip({ assistantName, sessionCode, onLeave }: Props) {
  return (
    <div
      style={{
        padding: '10px 14px',
        background: T.bg2,
        border: `1px solid ${T.line}`,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: 10,
      }}
    >
      <div style={{ minWidth: 0, overflow: 'hidden' }}>
        <div
          style={{
            fontFamily: T.fMono,
            fontSize: 9,
            color: T.ink3,
            letterSpacing: 1.3,
            textTransform: 'uppercase',
          }}
        >
          Current Session
        </div>
        <div
          style={{
            fontFamily: T.fMono,
            fontSize: 11,
            color: T.ink,
            marginTop: 2,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {assistantName} ·{' '}
          <span style={{ color: T.accent, letterSpacing: 1.8 }}>{sessionCode ?? '------'}</span>
        </div>
      </div>
      <button
        onClick={onLeave}
        style={{
          background: 'transparent',
          color: T.danger,
          border: `1px solid ${T.danger}`,
          padding: '4px 9px',
          fontFamily: T.fMono,
          fontSize: 9.5,
          letterSpacing: 1,
          textTransform: 'uppercase',
          cursor: 'pointer',
          flexShrink: 0,
        }}
      >
        Leave
      </button>
    </div>
  )
}
