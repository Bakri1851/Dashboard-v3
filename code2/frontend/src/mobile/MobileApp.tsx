import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api, ApiError } from '../api/client'
import { useApiData } from '../api/hooks'
import { T } from '../theme/tokens'
import type {
  JoinResult,
  LabState,
  RagSuggestions,
  Settings,
  StrugglingQuestionRow,
  StudentDetail,
  StudentStruggle,
} from '../types/api'
import { clearAid, readAid, writeAid } from './state/aid'
import { useAssignmentSound } from './hooks/useAssignmentSound'
import { MobileAssigned } from './views/MobileAssigned'
import { MobileJoin } from './views/MobileJoin'
import { MobileSessionEnded } from './views/MobileSessionEnded'
import { MobileUnassigned } from './views/MobileUnassigned'

const URGENT_LEVELS = new Set(['Needs Help', 'Struggling'])
const HIDDEN_LEVELS = new Set(['Minor Issues', 'On Track'])

export function MobileApp() {
  const [aid, setAid] = useState<string | null>(() => readAid())
  const [joinName, setJoinName] = useState('')
  const [joinCode, setJoinCode] = useState('')
  const [joinError, setJoinError] = useState<string | null>(null)
  const [joinNotice, setJoinNotice] = useState<string | null>(null)
  const [joining, setJoining] = useState(false)
  const [claimingStudent, setClaimingStudent] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [helpedFlash, setHelpedFlash] = useState(false)
  const helpedTimer = useRef<number | null>(null)

  const {
    data: labState,
    error: stateErr,
    loading: stateLoading,
    refetch: refetchState,
  } = useApiData<LabState>('/lab/state', 5000)

  const { data: settings } = useApiData<Settings>('/settings')

  const assistant = useMemo(() => {
    if (!labState || !aid) return null
    return labState.lab_assistants.find((a) => a.id === aid) ?? null
  }, [labState, aid])
  // Defensive: if the assistant's `assigned_student` field points at a
  // student whose assignment now belongs to someone else (stale state),
  // treat ourselves as unassigned. Mirrors `assistant_app.py:494-497`.
  const assignedStudent = useMemo(() => {
    const sid = assistant?.assigned_student ?? null
    if (!sid || !assistant || !labState) return null
    const asg = labState.assignments.find((a) => a.student_id === sid)
    if (asg && asg.assistant_id !== assistant.id) return null
    return sid
  }, [assistant, labState])
  const assignment = useMemo(() => {
    if (!labState || !assignedStudent) return null
    return labState.assignments.find((a) => a.student_id === assignedStudent) ?? null
  }, [labState, assignedStudent])

  // Mirror the Streamlit session-window filter: every data endpoint that
  // accepts `?from=` gets the active session's `session_start` so the mobile
  // only ever sees data since the instructor pressed Start Session.
  const sessionQuery = labState?.session_start
    ? `from=${encodeURIComponent(labState.session_start)}`
    : undefined

  const canShowUnassigned =
    !!labState && labState.session_active && !!assistant && assignedStudent == null

  const struggleQ = useApiData<StudentStruggle[]>(
    canShowUnassigned ? '/struggle' : '',
    10_000,
    sessionQuery
  )

  const studentPath = assignedStudent ? `/student/${encodeURIComponent(assignedStudent)}` : ''
  const ragPath = assignedStudent ? `/rag/student/${encodeURIComponent(assignedStudent)}` : ''
  const topPath = assignedStudent
    ? `/lab/student/${encodeURIComponent(assignedStudent)}/struggling-questions?limit=3`
    : ''

  // Student profile + top questions ignore the session window — assistants
  // need the student's historic context, not just the current lab slice
  // (which is usually empty for the first few minutes of a session).
  const { data: studentDetail, loading: studentLoading } = useApiData<StudentDetail>(studentPath)
  const { data: ragData } = useApiData<RagSuggestions>(ragPath, undefined, sessionQuery)
  const { data: topQuestions } = useApiData<StrugglingQuestionRow[]>(topPath)

  const soundsEnabled = settings?.runtime.sounds_enabled ?? false
  useAssignmentSound(assignedStudent, soundsEnabled)

  // If our aid is orphaned (session rolled, we got kicked, etc.), drop it.
  useEffect(() => {
    if (aid && labState && labState.session_active && !assistant) {
      clearAid()
      setAid(null)
      setJoinNotice('Your session was closed. Please rejoin.')
    }
  }, [aid, labState, assistant])

  useEffect(() => {
    return () => {
      if (helpedTimer.current != null) window.clearTimeout(helpedTimer.current)
    }
  }, [])

  const { available, hiddenCount } = useMemo(() => {
    if (!struggleQ.data || !labState) {
      return { available: [] as StudentStruggle[], hiddenCount: 0 }
    }
    const assignedIds = new Set(labState.assignments.map((a) => a.student_id))
    const avail = struggleQ.data
      .filter((s) => URGENT_LEVELS.has(s.level) && !assignedIds.has(s.id))
      .sort((a, b) => b.score - a.score)
    const hidden = struggleQ.data.filter((s) => HIDDEN_LEVELS.has(s.level)).length
    return { available: avail, hiddenCount: hidden }
  }, [struggleQ.data, labState])

  const doJoin = useCallback(async () => {
    const name = joinName.trim()
    const code = joinCode.trim().toUpperCase()
    if (!name) {
      setJoinError('Please enter your name.')
      return
    }
    if (code.length !== 6) {
      setJoinError('Session code must be 6 characters.')
      return
    }
    setJoinError(null)
    setJoinNotice(null)
    setJoining(true)
    try {
      let res = await api.post<JoinResult>('/lab/join', { code, name })
      // If the first attempt fails with a transient "no session / invalid
      // code" error, the mobile's cached lab state is probably stale (the
      // instructor just started the session). Refetch and retry silently.
      if (!res.ok) {
        const msg = (res.error ?? '').toLowerCase()
        const looksStale = msg.includes('invalid') || msg.includes('no active')
        if (looksStale) {
          await refetchState()
          await new Promise((r) => setTimeout(r, 150))
          res = await api.post<JoinResult>('/lab/join', { code, name })
        }
      }
      if (!res.ok || !res.assistant_id) {
        setJoinError(res.error ?? 'Could not join session.')
      } else {
        writeAid(res.assistant_id)
        setAid(res.assistant_id)
        setJoinCode('')
        refetchState()
      }
    } catch (e) {
      setJoinError(e instanceof ApiError ? `${e.status}: ${e.message}` : String(e))
    } finally {
      setJoining(false)
    }
  }, [joinName, joinCode, refetchState])

  const doLeave = useCallback(async () => {
    if (!aid) return
    setBusy(true)
    try {
      await api.post('/lab/leave', { assistant_id: aid })
    } catch (e) {
      console.error('leave failed:', e)
    } finally {
      clearAid()
      setAid(null)
      setJoinNotice('You have left the session. Rejoin when you are ready.')
      setBusy(false)
      refetchState()
    }
  }, [aid, refetchState])

  const doClaim = useCallback(
    async (studentId: string) => {
      if (!aid) return
      setClaimingStudent(studentId)
      try {
        await api.post('/lab/self-claim', { assistant_id: aid, student_id: studentId })
      } catch (e) {
        console.error('self-claim failed:', e)
      } finally {
        setClaimingStudent(null)
        refetchState()
      }
    },
    [aid, refetchState]
  )

  const doMarkHelped = useCallback(async () => {
    if (!assignedStudent) return
    setBusy(true)
    try {
      await api.post('/lab/mark-helped', { student_id: assignedStudent })
      setHelpedFlash(true)
      if (helpedTimer.current != null) window.clearTimeout(helpedTimer.current)
      helpedTimer.current = window.setTimeout(() => setHelpedFlash(false), 2000)
    } catch (e) {
      console.error('mark-helped failed:', e)
    } finally {
      setBusy(false)
      refetchState()
    }
  }, [assignedStudent, refetchState])

  const doRelease = useCallback(async () => {
    if (!assignedStudent) return
    setBusy(true)
    try {
      await api.post('/lab/unassign', { student_id: assignedStudent })
    } catch (e) {
      console.error('unassign failed:', e)
    } finally {
      setBusy(false)
      setHelpedFlash(false)
      refetchState()
    }
  }, [assignedStudent, refetchState])

  // --- Render ----------------------------------------------------------
  if (stateLoading && !labState) {
    return (
      <div
        style={{
          minHeight: '100vh',
          background: T.bg,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: T.ink3,
          fontFamily: T.fMono,
          fontSize: 12,
          letterSpacing: 1.4,
          textTransform: 'uppercase',
        }}
      >
        connecting…
      </div>
    )
  }
  if (stateErr && !labState) {
    return (
      <div
        style={{
          minHeight: '100vh',
          background: T.bg,
          padding: 36,
          color: T.danger,
          fontFamily: T.fMono,
          fontSize: 12,
        }}
      >
        {stateErr}
      </div>
    )
  }
  if (!labState) return null

  let body: React.ReactNode
  if (!labState.session_active) {
    body = <MobileSessionEnded />
  } else if (!aid || !assistant) {
    body = (
      <MobileJoin
        name={joinName}
        code={joinCode}
        error={joinError}
        notice={joinNotice}
        busy={joining}
        onNameChange={setJoinName}
        onCodeChange={setJoinCode}
        onJoin={doJoin}
      />
    )
  } else if (!assignedStudent) {
    body = (
      <MobileUnassigned
        assistantName={assistant.name}
        sessionCode={labState.session_code}
        available={available}
        hiddenCount={hiddenCount}
        allowSelfAlloc={labState.allow_self_allocation}
        claiming={claimingStudent}
        onClaim={doClaim}
        onLeave={doLeave}
      />
    )
  } else {
    body = (
      <MobileAssigned
        assistantName={assistant.name}
        sessionCode={labState.session_code}
        studentId={assignedStudent}
        detail={studentDetail}
        detailLoading={studentLoading}
        suggestions={ragData}
        topQuestions={topQuestions}
        helpedFlash={helpedFlash}
        assignmentStatus={assignment?.status ?? 'helping'}
        busy={busy}
        onMarkHelped={doMarkHelped}
        onRelease={doRelease}
        onLeave={doLeave}
      />
    )
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: T.bg,
        color: T.ink,
        fontFamily: T.fSans,
      }}
    >
      {body}
    </div>
  )
}
