import { useState } from 'react'
import { T } from '../../theme/tokens'

interface Props {
  name: string
  code: string
  error: string | null
  notice: string | null
  busy: boolean
  onNameChange: (v: string) => void
  onCodeChange: (v: string) => void
  onJoin: () => void
}

export function MobileJoin({
  name,
  code,
  error,
  notice,
  busy,
  onNameChange,
  onCodeChange,
  onJoin,
}: Props) {
  const [focus, setFocus] = useState<'name' | 'code' | null>(null)

  return (
    <div style={{ padding: '30px 22px' }}>
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontFamily: T.fMono,
            fontSize: 10,
            color: T.ink3,
            letterSpacing: 2,
            textTransform: 'uppercase',
          }}
        >
          Lab Assistant
        </div>
        <div
          style={{
            fontFamily: T.fSerif,
            fontSize: 30,
            color: T.ink,
            marginTop: 6,
            lineHeight: 1,
            letterSpacing: 0.2,
          }}
        >
          Join Session
        </div>
      </div>

      <div style={{ marginTop: 24, height: 1, background: T.line }} />

      {notice && (
        <div
          style={{
            marginTop: 16,
            padding: '10px 12px',
            background: T.accentSoft,
            border: `1px solid ${T.accent}`,
            fontFamily: T.fMono,
            fontSize: 10.5,
            color: T.ink2,
            lineHeight: 1.5,
          }}
        >
          {notice}
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        <label
          style={{
            fontFamily: T.fMono,
            fontSize: 10,
            color: T.ink3,
            letterSpacing: 1.3,
            textTransform: 'uppercase',
          }}
        >
          Your Name
        </label>
        <input
          value={name}
          onChange={(e) => onNameChange(e.target.value)}
          onFocus={() => setFocus('name')}
          onBlur={() => setFocus(null)}
          placeholder="e.g. Alice"
          maxLength={40}
          style={{
            marginTop: 6,
            width: '100%',
            padding: '11px 12px',
            background: T.card,
            color: T.ink,
            border: `1px solid ${focus === 'name' ? T.accent : T.line2}`,
            fontFamily: T.fSans,
            fontSize: 14,
            borderRadius: 0,
            outline: 'none',
          }}
        />
      </div>

      <div style={{ marginTop: 16 }}>
        <label
          style={{
            fontFamily: T.fMono,
            fontSize: 10,
            color: T.ink3,
            letterSpacing: 1.3,
            textTransform: 'uppercase',
          }}
        >
          Session Code
        </label>
        <input
          value={code}
          onChange={(e) => onCodeChange(e.target.value.toUpperCase().slice(0, 6))}
          onFocus={() => setFocus('code')}
          onBlur={() => setFocus(null)}
          placeholder="A3X7K2"
          maxLength={6}
          autoCapitalize="characters"
          autoCorrect="off"
          spellCheck={false}
          style={{
            marginTop: 6,
            width: '100%',
            padding: '11px 12px',
            background: T.card,
            color: T.ink,
            border: `1px solid ${focus === 'code' ? T.accent : T.line2}`,
            fontFamily: T.fMono,
            fontSize: 22,
            letterSpacing: 8,
            borderRadius: 0,
            outline: 'none',
            textAlign: 'center',
          }}
        />
        <div
          style={{
            marginTop: 6,
            fontFamily: T.fMono,
            fontSize: 9.5,
            color: T.ink3,
            letterSpacing: 0.5,
          }}
        >
          6 characters · provided by instructor
        </div>
      </div>

      {error && (
        <div
          style={{
            marginTop: 14,
            padding: '8px 10px',
            background: T.bg2,
            border: `1px solid ${T.danger}`,
            fontFamily: T.fMono,
            fontSize: 10.5,
            color: T.danger,
          }}
        >
          ⚠ {error}
        </div>
      )}

      <button
        onClick={onJoin}
        disabled={busy}
        style={{
          marginTop: 22,
          width: '100%',
          padding: '12px 0',
          background: T.ink,
          color: T.bg,
          border: 'none',
          fontFamily: T.fMono,
          fontSize: 12,
          letterSpacing: 2,
          textTransform: 'uppercase',
          cursor: busy ? 'wait' : 'pointer',
          fontWeight: 500,
          opacity: busy ? 0.6 : 1,
        }}
      >
        {busy ? 'Joining…' : 'Join Session →'}
      </button>

      <div
        style={{
          marginTop: 28,
          padding: '12px 14px',
          background: T.bg2,
          border: `1px dashed ${T.line2}`,
          fontFamily: T.fMono,
          fontSize: 10,
          color: T.ink3,
          lineHeight: 1.55,
        }}
      >
        Your session persists across refresh via{' '}
        <span style={{ color: T.ink2 }}>?aid=…</span> in the URL.
      </div>
    </div>
  )
}
