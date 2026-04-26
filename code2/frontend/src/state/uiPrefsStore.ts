import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export type InClassViewMode = 'basic' | 'advanced'

interface UiPrefsState {
  inClassViewMode: InClassViewMode
  setInClassViewMode: (mode: InClassViewMode) => void
}

export const useUiPrefsStore = create<UiPrefsState>()(
  persist(
    (set) => ({
      inClassViewMode: 'basic',
      setInClassViewMode: (mode) => set({ inClassViewMode: mode }),
    }),
    {
      name: 'dash-ui-prefs',
      storage: createJSONStorage(() => localStorage),
      version: 1,
    }
  )
)
