import type { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'
import { useTheme } from '../../theme/ThemeContext'

export function TopBar({
  breadcrumbs,
  title,
  right,
}: {
  breadcrumbs: string
  title: string
  right?: ReactNode
}) {
  const { theme, setTheme, themes, accents, accentId, setAccent } = useTheme()

  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'flex-end',
        justifyContent: 'space-between',
        padding: '26px 36px 18px',
        borderBottom: `1px solid ${T.border}`,
        background: T.bg,
        gap: 24,
      }}
    >
      <div>
        <motion.div
          key={breadcrumbs}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          style={{ fontFamily: T.fMono, fontSize: 10.5, letterSpacing: 1.4, color: T.ink3, textTransform: 'uppercase' }}
        >
          {breadcrumbs}
        </motion.div>
        <motion.h2
          key={title}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          style={{ fontSize: 28, fontWeight: 600, margin: '4px 0 0' }}
        >
          {title}
        </motion.h2>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {right}

        <div style={{ display: 'flex', gap: 4 }}>
          {accents.map((a) => (
            <motion.button
              key={a.id}
              title={a.id}
              onClick={() => setAccent(a.id)}
              whileHover={{ scale: 1.15 }}
              whileTap={{ scale: 0.9 }}
              style={{
                width: 18,
                height: 18,
                borderRadius: '50%',
                background: `oklch(0.55 0.14 ${a.h})`,
                outline: accentId === a.id ? `2px solid ${T.ink0}` : 'none',
                outlineOffset: 1,
                border: `1px solid ${T.border}`,
                cursor: 'pointer',
              }}
            />
          ))}
        </div>

        <select
          value={theme}
          onChange={(e) => setTheme(e.target.value as typeof theme)}
          style={{
            fontFamily: T.fMono,
            fontSize: 11,
            padding: '4px 8px',
            background: T.card,
            color: T.ink1,
            border: `1px solid ${T.border}`,
          }}
        >
          {themes.map((t) => (
            <option key={t.id} value={t.id}>
              {t.label}
            </option>
          ))}
        </select>
      </div>
    </header>
  )
}
