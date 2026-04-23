import { T, LEVEL_STYLES } from '../../theme/tokens'
import { useTheme } from '../../theme/ThemeContext'

const PULSE_LEVELS: ReadonlySet<string> = new Set(['Needs Help', 'Very Hard'])

/** Level badge used in leaderboard rows and detail headers. */
export function Pill({ level }: { level: string }) {
  const style = LEVEL_STYLES[level] ?? { fg: T.ink3, label: level }
  const { themeKind } = useTheme()
  const dark = themeKind === 'dark'
  const pulse = dark && PULSE_LEVELS.has(level)
  return (
    <span
      data-level={level}
      className={pulse ? 'pill-pulse' : undefined}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        fontFamily: T.fMono,
        fontSize: 10.5,
        color: style.fg,
        letterSpacing: dark ? 0.8 : 0.5,
        textTransform: 'uppercase',
        padding: '2px 8px',
        border: `1px solid ${style.fg}`,
        borderRadius: dark ? 0 : 999,
        whiteSpace: 'nowrap',
        boxShadow: dark ? `0 0 8px ${style.fg}55, inset 0 0 8px ${style.fg}22` : 'none',
        // Custom property consumed by the levelPulse keyframes when pulsing.
        ...(pulse ? ({ ['--pulse-color' as string]: `${style.fg}55` } as Record<string, string>) : {}),
      }}
    >
      {dark && (
        <span
          style={{
            width: 5,
            height: 5,
            borderRadius: '50%',
            background: style.fg,
            boxShadow: `0 0 6px ${style.fg}`,
          }}
        />
      )}
      {style.label}
    </span>
  )
}
