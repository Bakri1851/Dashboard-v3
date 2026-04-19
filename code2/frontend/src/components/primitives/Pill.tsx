import { T, LEVEL_STYLES } from '../../theme/tokens'

/** Level badge used in leaderboard rows and detail headers. */
export function Pill({ level }: { level: string }) {
  const style = LEVEL_STYLES[level] ?? { fg: T.ink3, label: level }
  return (
    <span
      style={{
        fontFamily: T.fMono,
        fontSize: 10.5,
        color: style.fg,
        letterSpacing: 0.5,
        padding: '2px 8px',
        border: `1px solid ${style.fg}`,
        borderRadius: 999,
        whiteSpace: 'nowrap',
      }}
    >
      {style.label}
    </span>
  )
}
