import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'
import { useTheme } from '../../theme/ThemeContext'

export function MobileThemeSwitcher() {
  const { theme, setTheme, themes, accents, accentId, setAccent } = useTheme()

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'stretch',
        gap: 5,
        padding: '6px 7px',
        background: T.card,
        border: `1px solid ${T.border}`,
      }}
    >
      <select
        value={theme}
        onChange={(e) => setTheme(e.target.value as typeof theme)}
        style={{
          fontFamily: T.fMono,
          fontSize: 10,
          padding: '3px 6px',
          background: T.card,
          color: T.ink1,
          border: `1px solid ${T.border}`,
          outline: 'none',
          cursor: 'pointer',
        }}
      >
        {themes.map((t) => (
          <option key={t.id} value={t.id}>
            {t.label}
          </option>
        ))}
      </select>

      <div style={{ display: 'flex', gap: 3, justifyContent: 'center' }}>
        {accents.map((a) => (
          <motion.button
            key={a.id}
            title={a.id}
            onClick={() => setAccent(a.id)}
            whileHover={{ scale: 1.15 }}
            whileTap={{ scale: 0.9 }}
            style={{
              width: 14,
              height: 14,
              borderRadius: '50%',
              background: `oklch(0.55 0.14 ${a.h})`,
              outline: accentId === a.id ? `2px solid ${T.ink0}` : 'none',
              outlineOffset: 1,
              border: `1px solid ${T.border}`,
              cursor: 'pointer',
              padding: 0,
            }}
          />
        ))}
      </div>
    </div>
  )
}
