import type { ReactNode } from 'react'
import { AnimatePresence } from 'framer-motion'
import { Sidebar } from './components/layout/Sidebar'
import { TopBar } from './components/layout/TopBar'
import { ErrorBoundary } from './components/layout/ErrorBoundary'
import { Heartbeat } from './components/layout/Heartbeat'
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
import { SessionProgressionView } from './views/SessionProgression'
import { useEffect } from 'react'
import { useSettings } from './api/useSettings'
import { useAutoRefreshInterval } from './api/useAutoRefreshInterval'
import { ViewTransition } from './animation/ViewTransition'
import { AnimatedNumber } from './components/primitives/AnimatedNumber'

export default function App() {
  const {
    view,
    selectedStudentId,
    selectedQuestionId,
    selectedSessionId,
    pickStudent,
    pickQuestion,
    setView,
    back,
    setSoundsEnabled,
  } = useViewStore()
  const { data: settings } = useSettings()
  const { data: live, loading: liveLoading } = useApiData<LiveDataResponse>(
    '/live',
    useAutoRefreshInterval(10_000)
  )
  const { data: lab, loading: labLoading } = useApiData<LabState>('/lab/state', 3_000)
  const heartbeat = liveLoading || labLoading

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
  let viewKey: string = view
  const right = (
    <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3, fontVariantNumeric: 'tabular-nums' }}>
      {live ? (
        <>
          <AnimatedNumber value={String(live.records)} duration={0.8} /> records
        </>
      ) : (
        'loading…'
      )}
    </span>
  )

  if (selectedStudentId) {
    breadcrumbs = 'Instructor Console · Student'
    title = selectedStudentId
    viewKey = `student:${selectedStudentId}`
    screen = <StudentDetailView studentId={selectedStudentId} />
  } else if (selectedQuestionId) {
    breadcrumbs = 'Instructor Console · Question'
    title = selectedQuestionId
    viewKey = `question:${selectedQuestionId}`
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
            liveClassId={lab?.class_id ?? null}
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
      case 'session-progression':
        title = 'Session Progression'
        breadcrumbs = 'Instructor Console · Previous Sessions · Progression'
        viewKey = `session-progression:${selectedSessionId ?? ''}`
        screen = selectedSessionId ? (
          <SessionProgressionView sessionId={selectedSessionId} />
        ) : (
          <PreviousSessionsView />
        )
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
      <Heartbeat active={heartbeat} />
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
          <section style={{ flex: 1, overflow: 'auto' }}>
            <AnimatePresence mode="wait" initial={false}>
              <ViewTransition key={viewKey}>{screen}</ViewTransition>
            </AnimatePresence>
          </section>
        </main>
      </div>
    </ErrorBoundary>
  )
}
