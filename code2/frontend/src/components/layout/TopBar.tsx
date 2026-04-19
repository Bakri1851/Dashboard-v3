import type { ReactNode } from 'react'
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
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, letterSpacing: 1.4, color: T.ink3, textTransform: 'uppercase' }}>
          {breadcrumbs}
        </div>
        <h2 style={{ fontSize: 28, fontWeight: 600, margin: '4px 0 0' }}>{title}</h2>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {right}

        <div style={{ display: 'flex', gap: 4 }}>
          {accents.map((a) => (
            <button
              key={a.id}
              title={a.id}
              onClick={() => setAccent(a.id)}
              style={{
                width: 18,
                height: 18,
                borderRadius: '50%',
                background: `oklch(0.55 0.14 ${a.h})`,
                outline: accentId === a.id ? `2px solid ${T.ink0}` : 'none',
                outlineOffset: 1,
                border: `1px solid ${T.border}`,
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
