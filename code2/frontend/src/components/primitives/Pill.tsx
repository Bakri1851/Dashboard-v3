import { T, LEVEL_STYLES } from '../../theme/tokens'
import { useTheme } from '../../theme/ThemeContext'

/** Level badge used in leaderboard rows and detail headers. */
export function Pill({ level }: { level: string }) {
  const style = LEVEL_STYLES[level] ?? { fg: T.ink3, label: level }
  const { themeKind } = useTheme()
  const dark = themeKind === 'dark'
  return (
    <span
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
