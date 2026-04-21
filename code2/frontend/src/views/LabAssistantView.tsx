import { useCallback, useMemo } from 'react'
import { T } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import { useAutoRefreshInterval } from '../api/useAutoRefreshInterval'
import { api } from '../api/client'
import type { LabState, StudentStruggle } from '../types/api'
import { Pill } from '../components/primitives/Pill'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { useViewStore } from '../state/viewStore'

const URGENT_LEVELS = new Set(['Needs Help', 'Struggling'])

export function LabAssistantView() {
  const pickStudent = useViewStore((s) => s.pickStudent)
  const { data: state, error: stateErr, loading: stateLoading, refetch: refetchState } =
    useApiData<LabState>('/lab/state', 3_000)
  // When a session is active, scope the dispatch queue to students seen in
  // the current session window. Without this, the queue shows every urgent
  // student in the historical data — unhelpful when triaging live.
  const sessionQuery = state?.session_start
    ? `from=${encodeURIComponent(state.session_start)}`
    : undefined
  const strugInterval = useAutoRefreshInterval(15_000)
  const { data: struggle } = useApiData<StudentStruggle[]>('/struggle', strugInterval, sessionQuery)

  // Students that need help but aren't already assigned.
  const assignedSet = useMemo(() => new Set((state?.assignments ?? []).map((a) => a.student_id)), [state])
  const queue = useMemo(() => {
    if (!struggle) return []
    return struggle
      .filter((s) => URGENT_LEVELS.has(s.level) && !assignedSet.has(s.id))
      .slice(0, 10)
  }, [struggle, assignedSet])

  const idleAssistants = useMemo(
    () => (state?.lab_assistants ?? []).filter((a) => !a.assigned_student),
    [state]
  )

  const post = useCallback(
    async (path: string, body: unknown) => {
      try {
        await api.post(path, body)
      } catch (e) {
        console.error('lab action failed:', e)
      } finally {
        refetchState()
      }
    },
    [refetchState]
  )

  if (stateLoading && !state) {
    return <div style={{ padding: 36, color: T.ink2, fontFamily: T.fMono, fontSize: 12 }}>loading lab state…</div>
  }
  if (stateErr) {
    return <div style={{ padding: 36, color: T.danger, fontFamily: T.fMono, fontSize: 12 }}>{stateErr}</div>
  }
  if (!state) return null

  // No active session — show start prompt
  if (!state.session_active) {
    return (
      <div style={{ padding: 48, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18, textAlign: 'center' }}>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 2, textTransform: 'uppercase' }}>
          No active session
        </div>
        <div style={{ fontFamily: T.fSerif, fontSize: 28, color: T.ink }}>Start a lab session to coordinate assistants.</div>
        <div style={{ fontFamily: T.fSans, fontSize: 13.5, color: T.ink2, maxWidth: 480, lineHeight: 1.6 }}>
          Starting a session generates a 6-character join code and writes to{' '}
          <code style={{ fontFamily: T.fMono, background: T.bg2, padding: '1px 4px' }}>data/lab_session.json</code>.
          All active processes (React frontend, FastAPI backend, and any Streamlit fallbacks in code/) see the same state via the file-lock.
        </div>
        <button
          onClick={() => post('/lab/start', undefined)}
          style={{
            marginTop: 10,
            padding: '10px 20px',
            background: T.accent,
            color: '#ffffff',
            border: 'none',
            fontFamily: T.fMono,
            fontSize: 11,
            letterSpacing: 1.4,
            textTransform: 'uppercase',
            cursor: 'pointer',
          }}
        >
          Start session
        </button>
      </div>
    )
  }

  const totalHelping = state.assignments.filter((a) => a.status === 'helping').length

  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Session banner */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) auto auto auto',
          gap: 24,
          alignItems: 'center',
          padding: '22px 28px',
          background: T.card,
          border: `1px solid ${T.line}`,
        }}
      >
        <div>
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.3, textTransform: 'uppercase' }}>
            Session Code · share with assistants
          </div>
          <div style={{ fontFamily: T.fMono, fontSize: 42, color: T.ink, letterSpacing: 8, marginTop: 4 }}>
            {state.session_code ?? '—'}
          </div>
          {state.session_start && (
            <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>
              started {formatTimestamp(state.session_start)}
            </div>
          )}
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase' }}>
            Assistants
          </div>
          <div style={{ fontFamily: T.fSerif, fontSize: 32, color: T.ink, fontFeatureSettings: '"tnum"' }}>
            {state.lab_assistants.length}
          </div>
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
            {totalHelping} helping
          </div>
        </div>
        <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={state.allow_self_allocation}
            onChange={(e) => post('/lab/allow-self-alloc', { enabled: e.target.checked })}
          />
          <span style={{ fontFamily: T.fSans, fontSize: 12.5, color: T.ink2 }}>Allow self-allocation</span>
        </label>
        <button
          onClick={() => post('/lab/end', undefined)}
          style={{
            padding: '8px 16px',
            background: 'transparent',
            color: T.danger,
            border: `1px solid ${T.danger}`,
            fontFamily: T.fMono,
            fontSize: 11,
            letterSpacing: 1.2,
            textTransform: 'uppercase',
            cursor: 'pointer',
          }}
        >
          End session
        </button>
      </div>

      {/* Two columns */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1.3fr)', gap: 24 }}>
        {/* Assistants */}
        <div style={{ background: T.card, border: `1px solid ${T.line}`, minWidth: 0 }}>
          <div style={{ padding: '18px 22px', borderBottom: `1px solid ${T.line}` }}>
            <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>Lab Assistants</div>
            <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>
              Live roster · polled every 3s
            </div>
          </div>
          {state.lab_assistants.length === 0 ? (
            <div style={{ padding: 22, color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>
              Nobody has joined yet. Assistants join at /mobile on this server with the code above.
            </div>
          ) : (
            state.lab_assistants.map((a, i) => {
              const isLast = i === state.lab_assistants.length - 1
              const initials = a.name
                .split(/\s+/)
                .map((n) => n[0])
                .filter(Boolean)
                .slice(0, 2)
                .join('')
                .toUpperCase()
              return (
                <div
                  key={a.id}
                  style={{
                    padding: '16px 22px',
                    borderBottom: isLast ? 'none' : `1px solid ${T.line2}`,
                    display: 'grid',
                    gridTemplateColumns: 'minmax(0, 1fr) auto auto',
                    gap: 12,
                    alignItems: 'center',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
                    <div
                      style={{
                        width: 32,
                        height: 32,
                        borderRadius: '50%',
                        background: T.bg2,
                        border: `1px solid ${T.line2}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontFamily: T.fMono,
                        fontSize: 11,
                        color: T.ink2,
                        flexShrink: 0,
                      }}
                    >
                      {initials || '—'}
                    </div>
                    <div style={{ minWidth: 0 }}>
                      <div
                        style={{
                          fontFamily: T.fSans,
                          fontSize: 13.5,
                          color: T.ink,
                          fontWeight: 500,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {a.name}
                      </div>
                      <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 2 }}>
                        joined {formatTimestamp(a.joined_at)}
                        {a.assigned_student && (
                          <>
                            {' '}·{' '}
                            <button
                              onClick={() => pickStudent(a.assigned_student!)}
                              style={{
                                color: T.accent,
                                fontFamily: T.fMono,
                                fontSize: 10.5,
                                padding: 0,
                                cursor: 'pointer',
                              }}
                            >
                              → {a.assigned_student}
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  {a.assigned_student ? (
                    <span
                      style={{
                        fontFamily: T.fMono,
                        fontSize: 10,
                        color: T.warn,
                        letterSpacing: 1.2,
                        textTransform: 'uppercase',
                      }}
                    >
                      ● Helping
                    </span>
                  ) : (
                    <span
                      style={{
                        fontFamily: T.fMono,
                        fontSize: 10,
                        color: T.ink3,
                        letterSpacing: 1.2,
                        textTransform: 'uppercase',
                      }}
                    >
                      ○ Waiting
                    </span>
                  )}
                  {a.assigned_student ? (
                    <button
                      onClick={() => post('/lab/unassign', { student_id: a.assigned_student })}
                      style={{
                        padding: '5px 10px',
                        fontFamily: T.fMono,
                        fontSize: 10.5,
                        border: `1px solid ${T.line}`,
                        color: T.ink2,
                        letterSpacing: 1,
                        textTransform: 'uppercase',
                        cursor: 'pointer',
                      }}
                    >
                      Release
                    </button>
                  ) : (
                    <button
                      onClick={() => post('/lab/remove-assistant', { assistant_id: a.id })}
                      style={{
                        padding: '5px 10px',
                        fontFamily: T.fMono,
                        fontSize: 10.5,
                        border: `1px solid ${T.line}`,
                        color: T.ink3,
                        letterSpacing: 1,
                        textTransform: 'uppercase',
                        cursor: 'pointer',
                      }}
                      title="Remove from roster"
                    >
                      Remove
                    </button>
                  )}
                </div>
              )
            })
          )}
        </div>

        {/* Dispatch queue */}
        <div style={{ background: T.card, border: `1px solid ${T.line}`, minWidth: 0 }}>
          <div
            style={{
              padding: '18px 22px',
              borderBottom: `1px solid ${T.line}`,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              gap: 10,
            }}
          >
            <div>
              <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>Dispatch Queue</div>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>
                Flagged students · ranked by struggle score
              </div>
            </div>
            <span
              style={{
                fontFamily: T.fMono,
                fontSize: 11,
                color: T.danger,
                letterSpacing: 1.2,
                textTransform: 'uppercase',
              }}
            >
              {queue.length} open
            </span>
          </div>
          {queue.length === 0 ? (
            <div style={{ padding: 22, color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>
              Nobody needs help right now. 🎉
            </div>
          ) : (
            queue.map((s, i) => {
              const isLast = i === queue.length - 1
              const firstIdle = idleAssistants[0]
              return (
                <div
                  key={s.id}
                  style={{
                    padding: '14px 22px',
                    borderBottom: isLast ? 'none' : `1px solid ${T.line2}`,
                    display: 'grid',
                    gridTemplateColumns: 'minmax(0, 1fr) auto auto',
                    gap: 16,
                    alignItems: 'center',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 14, minWidth: 0 }}>
                    <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3, flexShrink: 0 }}>
                      {String(i + 1).padStart(2, '0')}
                    </span>
                    <div style={{ minWidth: 0 }}>
                      <button
                        onClick={() => pickStudent(s.id)}
                        style={{
                          fontFamily: T.fMono,
                          fontSize: 13,
                          color: T.ink,
                          padding: 0,
                          cursor: 'pointer',
                        }}
                      >
                        {s.id}
                      </button>
                      <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 2 }}>
                        recent {s.recent.toFixed(2)} · score {s.score.toFixed(2)}
                      </div>
                    </div>
                  </div>
                  <Pill level={s.level} />
                  <button
                    disabled={!firstIdle}
                    onClick={() => {
                      if (!firstIdle) return
                      post('/lab/assign', { student_id: s.id, assistant_id: firstIdle.id })
                    }}
                    title={firstIdle ? `Assign to ${firstIdle.name}` : 'No idle assistant available'}
                    style={{
                      padding: '6px 12px',
                      background: firstIdle ? T.accent : 'transparent',
                      color: firstIdle ? '#ffffff' : T.ink3,
                      border: firstIdle ? 'none' : `1px solid ${T.line}`,
                      fontFamily: T.fMono,
                      fontSize: 11,
                      letterSpacing: 1.2,
                      textTransform: 'uppercase',
                      cursor: firstIdle ? 'pointer' : 'not-allowed',
                    }}
                  >
                    Dispatch →
                  </button>
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* Assignment list (if any in progress) */}
      {state.assignments.length > 0 && (
        <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={1}>Active Assignments</SectionLabel>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
            <thead>
              <tr>
                {['Student', 'Assistant', 'Status', 'Since', ''].map((h) => (
                  <th
                    key={h}
                    style={{
                      textAlign: 'left',
                      padding: '10px 0',
                      fontFamily: T.fMono,
                      fontSize: 10,
                      letterSpacing: 1,
                      color: T.ink3,
                      textTransform: 'uppercase',
                      fontWeight: 500,
                      borderBottom: `1px solid ${T.line}`,
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {state.assignments.map((asg) => {
                const assistant = state.lab_assistants.find((a) => a.id === asg.assistant_id)
                return (
                  <tr key={asg.student_id}>
                    <td
                      style={{
                        padding: '10px 0',
                        fontFamily: T.fMono,
                        fontSize: 12,
                        color: T.ink,
                        borderBottom: `1px solid ${T.line2}`,
                      }}
                    >
                      <button
                        onClick={() => pickStudent(asg.student_id)}
                        style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink, padding: 0, cursor: 'pointer' }}
                      >
                        {asg.student_id}
                      </button>
                    </td>
                    <td
                      style={{
                        padding: '10px 0',
                        fontFamily: T.fSans,
                        fontSize: 12,
                        color: T.ink2,
                        borderBottom: `1px solid ${T.line2}`,
                      }}
                    >
                      {assistant?.name ?? asg.assistant_id}
                    </td>
                    <td
                      style={{
                        padding: '10px 0',
                        fontFamily: T.fMono,
                        fontSize: 10.5,
                        color: asg.status === 'helped' ? T.ok : T.warn,
                        letterSpacing: 1,
                        textTransform: 'uppercase',
                        borderBottom: `1px solid ${T.line2}`,
                      }}
                    >
                      ● {asg.status}
                    </td>
                    <td
                      style={{
                        padding: '10px 0',
                        fontFamily: T.fMono,
                        fontSize: 11,
                        color: T.ink2,
                        borderBottom: `1px solid ${T.line2}`,
                      }}
                    >
                      {formatTimestamp(asg.assigned_at)}
                    </td>
                    <td
                      style={{
                        padding: '10px 0',
                        borderBottom: `1px solid ${T.line2}`,
                        textAlign: 'right',
                        display: 'flex',
                        gap: 6,
                        justifyContent: 'flex-end',
                      }}
                    >
                      {asg.status === 'helping' && (
                        <button
                          onClick={() => post('/lab/mark-helped', { student_id: asg.student_id })}
                          style={{
                            padding: '4px 10px',
                            fontFamily: T.fMono,
                            fontSize: 10,
                            background: T.ok,
                            color: '#fff',
                            border: 'none',
                            letterSpacing: 1,
                            textTransform: 'uppercase',
                            cursor: 'pointer',
                          }}
                        >
                          Helped
                        </button>
                      )}
                      <button
                        onClick={() => post('/lab/unassign', { student_id: asg.student_id })}
                        style={{
                          padding: '4px 10px',
                          fontFamily: T.fMono,
                          fontSize: 10,
                          background: 'transparent',
                          color: T.ink3,
                          border: `1px solid ${T.line}`,
                          letterSpacing: 1,
                          textTransform: 'uppercase',
                          cursor: 'pointer',
                        }}
                      >
                        Release
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function formatTimestamp(iso: string | null | undefined): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
