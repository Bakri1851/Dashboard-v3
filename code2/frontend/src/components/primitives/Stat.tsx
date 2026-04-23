import type { CSSProperties } from 'react'
import { T } from '../../theme/tokens'
import { useTheme } from '../../theme/ThemeContext'
import { CornerMarks } from './CornerMarks'
import { AnimatedNumber } from './AnimatedNumber'

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
  const { themeKind } = useTheme()
  const dark = themeKind === 'dark'
  const valueColor = accent ?? (isPrimary ? '#ffffff' : T.ink)
  const base: CSSProperties = {
    position: 'relative',
    padding: '20px 22px',
    background: isPrimary ? T.ink : T.card,
    color: isPrimary ? '#ffffff' : T.ink,
    border: isPrimary ? 'none' : `1px solid ${T.line}`,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    borderRadius: dark ? 0 : 2,
    minHeight: 128,
  }
  return (
    <div style={base}>
      {dark && !isPrimary && <CornerMarks color={T.line} />}
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
        <AnimatedNumber
          value={value}
          style={{
            fontFamily: T.fSerif,
            fontSize: 46,
            lineHeight: 0.95,
            fontFeatureSettings: '"tnum"',
            color: valueColor,
            marginTop: 16,
            letterSpacing: dark ? 0.5 : 0,
            textShadow: dark ? `0 0 12px ${valueColor}88` : 'none',
            fontWeight: dark ? 500 : 400,
            display: 'inline-block',
          }}
        />
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
