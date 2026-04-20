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

export type ThemeKind = 'dark' | 'light'

interface ThemeContextValue {
  theme: ThemeName
  themeKind: ThemeKind
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

const DARK_THEMES: ReadonlySet<ThemeName> = new Set(['scifi', 'blueprint', 'matrix', 'cyberpunk'])

function applyAccent(hue: number, theme: ThemeName) {
  const isDark = DARK_THEMES.has(theme)
  // --accent: border/bg tint — slightly brighter on dark themes so it reads
  // against a near-black panel.
  const accent = isDark ? `oklch(0.58 0.14 ${hue})` : `oklch(0.42 0.12 ${hue})`
  // --accent-soft: highlight wash behind selected items. Must contrast with
  // --ink, which is near-white on dark themes and near-black on light.
  const accentSoft = isDark ? `oklch(0.30 0.07 ${hue})` : `oklch(0.93 0.03 ${hue})`
  document.documentElement.style.setProperty('--accent', accent)
  document.documentElement.style.setProperty('--accent-soft', accentSoft)
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
    applyAccent(accentHue, theme)
    localStorage.setItem(STORAGE_KEY_ACCENT, accentId)
  }, [accentHue, accentId, theme])

  const setTheme = useCallback((t: ThemeName) => setThemeState(t), [])
  const setAccent = useCallback((id: string) => setAccentIdState(id), [])

  const themeKind: ThemeKind = DARK_THEMES.has(theme) ? 'dark' : 'light'

  const value = useMemo<ThemeContextValue>(
    () => ({ theme, themeKind, setTheme, accentId, accentHue, setAccent, themes: THEMES, accents: ACCENT_HUES }),
    [theme, themeKind, accentId, accentHue, setTheme, setAccent]
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>')
  return ctx
}
