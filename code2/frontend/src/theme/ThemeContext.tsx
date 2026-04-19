import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import {
  ACCENT_HUES,
  DEFAULT_ACCENT,
  DEFAULT_THEME,
  STORAGE_KEY_ACCENT,
  STORAGE_KEY_THEME,
  THEMES,
} from './tokens'
import type { ThemeName } from './tokens'

interface ThemeContextValue {
  theme: ThemeName
  setTheme: (t: ThemeName) => void
  accentId: string
  accentHue: number
  setAccent: (id: string) => void
  themes: typeof THEMES
  accents: typeof ACCENT_HUES
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

function applyThemeClass(theme: ThemeName) {
  const html = document.documentElement
  THEMES.forEach((t) => html.classList.remove(`theme-${t.id}`))
  html.classList.add(`theme-${theme}`)
}

function applyAccent(hue: number) {
  document.documentElement.style.setProperty('--accent', `oklch(0.42 0.12 ${hue})`)
  document.documentElement.style.setProperty('--accent-soft', `oklch(0.93 0.03 ${hue})`)
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemeName>(() => {
    const stored = localStorage.getItem(STORAGE_KEY_THEME) as ThemeName | null
    return stored && THEMES.some((t) => t.id === stored) ? stored : DEFAULT_THEME
  })

  const [accentId, setAccentIdState] = useState<string>(() => {
    const stored = localStorage.getItem(STORAGE_KEY_ACCENT)
    return stored && ACCENT_HUES.some((a) => a.id === stored) ? stored : DEFAULT_ACCENT.id
  })

  const accentHue = useMemo(
    () => ACCENT_HUES.find((a) => a.id === accentId)?.h ?? DEFAULT_ACCENT.h,
    [accentId]
  )

  useEffect(() => {
    applyThemeClass(theme)
    localStorage.setItem(STORAGE_KEY_THEME, theme)
  }, [theme])

  useEffect(() => {
    applyAccent(accentHue)
    localStorage.setItem(STORAGE_KEY_ACCENT, accentId)
  }, [accentHue, accentId])

  const setTheme = useCallback((t: ThemeName) => setThemeState(t), [])
  const setAccent = useCallback((id: string) => setAccentIdState(id), [])

  const value = useMemo<ThemeContextValue>(
    () => ({ theme, setTheme, accentId, accentHue, setAccent, themes: THEMES, accents: ACCENT_HUES }),
    [theme, accentId, accentHue, setTheme, setAccent]
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>')
  return ctx
}
