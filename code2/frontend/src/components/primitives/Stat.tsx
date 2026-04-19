import type { CSSProperties } from 'react'
import { T } from '../../theme/tokens'

/**
 * Hero stat card — variant `primary` renders the inverted dark card used for
 * "Priority Now". Default variant is the bordered card.
 */
export function Stat({
  label,
  value,
  note,
  accent,
  variant = 'default',
}: {
  label: string
  value: string
  note?: string
  accent?: string
  variant?: 'default' | 'primary'
}) {
  const isPrimary = variant === 'primary'
  const base: CSSProperties = {
    padding: '20px 22px',
    background: isPrimary ? T.ink : T.card,
    color: isPrimary ? '#ffffff' : T.ink,
    border: isPrimary ? 'none' : `1px solid ${T.line}`,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    borderRadius: 2,
    minHeight: 128,
  }
  return (
    <div style={base}>
      <div
        style={{
          fontFamily: T.fMono,
          fontSize: 10.5,
          letterSpacing: 1.3,
          textTransform: 'uppercase',
          opacity: isPrimary ? 0.7 : 1,
          color: isPrimary ? '#ffffff' : T.ink3,
        }}
      >
        {label}
      </div>
      <div>
        <div
          style={{
            fontFamily: T.fSerif,
            fontSize: 46,
            lineHeight: 0.95,
            fontFeatureSettings: '"tnum"',
            color: accent ?? (isPrimary ? '#ffffff' : T.ink),
            marginTop: 16,
          }}
        >
          {value}
        </div>
        {note && (
          <div
            style={{
              fontFamily: T.fMono,
              fontSize: 11,
              marginTop: 8,
              opacity: isPrimary ? 0.75 : 1,
              color: isPrimary ? '#ffffff' : T.ink3,
            }}
          >
            {note}
          </div>
        )}
      </div>
    </div>
  )
}
