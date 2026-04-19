import { T } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import type { SavedSession } from '../types/api'
import { SectionLabel } from '../components/primitives/SectionLabel'

function fmtDuration(mins: number | null): string {
  if (mins == null) return '—'
  const h = Math.floor(mins / 60)
  const m = Math.round(mins % 60)
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

function fmtTimestamp(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

export function PreviousSessionsView() {
  const { data, error, loading } = useApiData<SavedSession[]>('/sessions')

  return (
    <div style={{ padding: '28px 36px' }}>
      <div style={{ background: T.card, border: `1px solid ${T.line}` }}>
        <div style={{ padding: '18px 22px', borderBottom: `1px solid ${T.line}` }}>
          <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>Saved Sessions</div>
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>
            Sessions persisted by the Streamlit instructor app (<code style={{ background: T.bg2, padding: '1px 4px' }}>data/saved_sessions.json</code>) — read-only in this UI for now.
          </div>
        </div>

        {loading && (
          <div style={{ padding: 28, color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>loading…</div>
        )}
        {error && (
          <div style={{ padding: 28, color: T.danger, fontFamily: T.fMono, fontSize: 11 }}>{error}</div>
        )}
        {!loading && !error && data && data.length === 0 && (
          <div style={{ padding: 28, color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>
            No saved sessions yet. Start one via the Streamlit instructor app — it will show up here.
          </div>
        )}
        {data && data.length > 0 && (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
            <thead>
              <tr>
                {['Name', 'Start', 'Duration', 'Students', 'Flagged', 'Module'].map((h) => (
                  <th
                    key={h}
                    style={{
                      textAlign: 'left',
                      padding: '10px 22px',
                      fontFamily: T.fMono,
                      fontSize: 10,
                      color: T.ink3,
                      letterSpacing: 1.2,
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
              {data.map((s) => (
                <tr key={s.id}>
                  <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line2}`, color: T.ink }}>{s.name}</td>
                  <td
                    style={{
                      padding: '14px 22px',
                      borderBottom: `1px solid ${T.line2}`,
                      fontFamily: T.fMono,
                      fontSize: 12,
                      color: T.ink2,
                    }}
                  >
                    {fmtTimestamp(s.start_time)}
                  </td>
                  <td
                    style={{
                      padding: '14px 22px',
                      borderBottom: `1px solid ${T.line2}`,
                      fontFamily: T.fMono,
                      fontSize: 12,
                      color: T.ink2,
                    }}
                  >
                    {fmtDuration(s.duration_minutes)}
                  </td>
                  <td
                    style={{
                      padding: '14px 22px',
                      borderBottom: `1px solid ${T.line2}`,
                      fontFamily: T.fMono,
                      fontSize: 12,
                      color: T.ink,
                    }}
                  >
                    {s.students ?? '—'}
                  </td>
                  <td
                    style={{
                      padding: '14px 22px',
                      borderBottom: `1px solid ${T.line2}`,
                      fontFamily: T.fMono,
                      fontSize: 12,
                      color: (s.flagged ?? 0) > 0 ? T.danger : T.ink3,
                    }}
                  >
                    {s.flagged ?? '—'}
                  </td>
                  <td
                    style={{
                      padding: '14px 22px',
                      borderBottom: `1px solid ${T.line2}`,
                      fontFamily: T.fMono,
                      fontSize: 12,
                      color: T.ink3,
                    }}
                  >
                    {s.module_filter ?? '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div style={{ marginTop: 16, padding: '10px 14px', fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
        <SectionLabel n={2}>How to save</SectionLabel>
        Run the Streamlit instructor app (<code style={{ background: T.bg2, padding: '1px 4px' }}>code/app.py</code>), use "End session" to persist. This UI will auto-refresh the list the next time you open Previous Sessions.
      </div>
    </div>
  )
}
