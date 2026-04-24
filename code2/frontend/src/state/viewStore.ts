import { create } from 'zustand'
import { playNavigation, playSelection } from '../sound'

export type ViewId =
  | 'inclass'
  | 'analysis'
  | 'compare'
  | 'previous'
  | 'settings'
  | 'lab'
  | 'session-progression'

interface ViewState {
  view: ViewId
  selectedStudentId: string | null
  selectedQuestionId: string | null
  selectedSessionId: string | null
  soundsEnabled: boolean
  setSoundsEnabled: (v: boolean) => void
  setView: (v: ViewId) => void
  pickStudent: (id: string | null) => void
  pickQuestion: (id: string | null) => void
  openSessionProgression: (id: string) => void
  back: () => void
}

export const useViewStore = create<ViewState>((set, get) => ({
  view: 'inclass',
  selectedStudentId: null,
  selectedQuestionId: null,
  selectedSessionId: null,
  soundsEnabled: false,
  setSoundsEnabled: (v) => set({ soundsEnabled: v }),
  setView: (v) => {
    if (get().soundsEnabled) playNavigation()
    set({ view: v, selectedStudentId: null, selectedQuestionId: null })
  },
  pickStudent: (id) => {
    if (id && get().soundsEnabled) playSelection()
    set({ selectedStudentId: id, selectedQuestionId: null })
  },
  pickQuestion: (id) => {
    if (id && get().soundsEnabled) playSelection()
    set({ selectedQuestionId: id, selectedStudentId: null })
  },
  openSessionProgression: (id) => {
    if (get().soundsEnabled) playNavigation()
    set({
      view: 'session-progression',
      selectedSessionId: id,
      selectedStudentId: null,
      selectedQuestionId: null,
    })
  },
  back: () => set({ selectedStudentId: null, selectedQuestionId: null }),
}))
