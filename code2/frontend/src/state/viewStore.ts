import { create } from 'zustand'

export type ViewId =
  | 'inclass'
  | 'analysis'
  | 'compare'
  | 'previous'
  | 'settings'
  | 'lab'

interface ViewState {
  view: ViewId
  selectedStudentId: string | null
  selectedQuestionId: string | null
  setView: (v: ViewId) => void
  pickStudent: (id: string | null) => void
  pickQuestion: (id: string | null) => void
  back: () => void
}

export const useViewStore = create<ViewState>((set) => ({
  view: 'inclass',
  selectedStudentId: null,
  selectedQuestionId: null,
  setView: (v) => set({ view: v, selectedStudentId: null, selectedQuestionId: null }),
  pickStudent: (id) => set({ selectedStudentId: id, selectedQuestionId: null }),
  pickQuestion: (id) => set({ selectedQuestionId: id, selectedStudentId: null }),
  back: () => set({ selectedStudentId: null, selectedQuestionId: null }),
}))
