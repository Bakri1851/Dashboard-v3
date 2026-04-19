import type { ReactNode } from 'react'
import { Sidebar } from './components/layout/Sidebar'
import { TopBar } from './components/layout/TopBar'
import { ErrorBoundary } from './components/layout/ErrorBoundary'
import { T } from './theme/tokens'
import { useApiData } from './api/hooks'
import type { LabState, LiveDataResponse } from './types/api'
import { useViewStore } from './state/viewStore'
import { InClassView } from './views/InClassView'
import { StudentDetailView } from './views/StudentDetail'
import { QuestionDetailView } from './views/QuestionDetail'
import { PreviousSessionsView } from './views/PreviousSessions'
import { SettingsView } from './views/SettingsView'
import { DataAnalysisView } from './views/DataAnalysisView'
import { ComparisonView } from './views/ComparisonView'
import { LabAssistantView } from './views/LabAssistantView'
import { useEffect } from 'react'
import { useSettings } from './api/useSettings'

export default function App() {
  const { view, selectedStudentId, selectedQuestionId, pickStudent, pickQuestion, setView, back, setSoundsEnabled } =
    useViewStore()
  const { data: settings } = useSettings()
  const { data: live } = useApiData<LiveDataResponse>('/live', 10_000)
  const { data: lab } = useApiData<LabState>('/lab/state', 3_000)

  // Mirror runtime sounds_enabled into the view store so navigation/selection
  // can check a sync flag without having to call useSettings everywhere.
  useEffect(() => {
    setSoundsEnabled(settings?.runtime.sounds_enabled ?? false)
  }, [settings?.runtime.sounds_enabled, setSoundsEnabled])

  const sessionActive = lab?.session_active ?? false
  const sessionCode = lab?.session_code ?? null

  let breadcrumbs = 'Instructor Console'
  let title = 'In Class'
  let screen: ReactNode = null
  const right = (
    <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>
      {live ? `${live.records.toLocaleString()} records` : 'loading…'}
    </span>
  )

  if (selectedStudentId) {
    breadcrumbs = 'Instructor Console · Student'
    title = selectedStudentId
    screen = <StudentDetailView studentId={selectedStudentId} />
  } else if (selectedQuestionId) {
    breadcrumbs = 'Instructor Console · Question'
    title = selectedQuestionId
    screen = <QuestionDetailView questionId={selectedQuestionId} />
  } else {
    switch (view) {
      case 'inclass':
        breadcrumbs =
          sessionActive && sessionCode ? `Session Live · ${sessionCode}` : 'Instructor Console'
        title = 'In Class'
        screen = (
          <InClassView
            onPickStudent={(id) => pickStudent(id)}
            onPickQuestion={(id) => pickQuestion(id)}
            onOpenLab={() => setView('lab')}
            sessionActive={sessionActive}
          />
        )
        break
      case 'analysis':
        title = 'Data Analysis'
        screen = <DataAnalysisView />
        break
      case 'compare':
        title = 'Model Comparison'
        screen = <ComparisonView />
        break
      case 'previous':
        title = 'Previous Sessions'
        screen = <PreviousSessionsView />
        break
      case 'lab':
        title = 'Lab Assistants'
        screen = <LabAssistantView />
        break
      case 'settings':
        title = 'Settings'
        screen = <SettingsView />
        break
    }
  }

  return (
    <ErrorBoundary>
      <div style={{ display: 'flex', minHeight: '100vh', background: T.bg, color: T.ink }}>
        <Sidebar />
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <TopBar
            breadcrumbs={breadcrumbs}
            title={title}
            right={
              <>
                {(selectedStudentId || selectedQuestionId) && (
                  <button
                    onClick={back}
                    style={{
                      fontFamily: T.fMono,
                      fontSize: 11,
                      padding: '4px 10px',
                      border: `1px solid ${T.line}`,
                      color: T.ink2,
                    }}
                  >
                    ← back
                  </button>
                )}
                {right}
              </>
            }
          />
          <section style={{ flex: 1, overflow: 'auto' }}>{screen}</section>
        </main>
      </div>
    </ErrorBoundary>
  )
}
