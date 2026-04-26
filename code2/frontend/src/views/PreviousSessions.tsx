import { useCallback, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { T } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import { api } from '../api/client'
import type { SavedSession } from '../types/api'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { Skeleton } from '../components/primitives/Skeleton'
import { useFilterStore } from '../state/filterStore'
import { useViewStore } from '../state/viewStore'
import { AnimatedCard } from '../animation/AnimatedCard'
import { stagger, fadeUp } from '../animation/motion'

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

function isoToDate(iso: string | null): string {
  if (!iso) return ''
  return iso.slice(0, 10)
}

export function PreviousSessionsView() {
  const { data, error, loading, refetch } = useApiData<SavedSession[]>('/sessions')
  const filter = useFilterStore()
  const setView = useViewStore((s) => s.setView)
  const openSessionProgression = useViewStore((s) => s.openSessionProgression)

  const [saveOpen, setSaveOpen] = useState(false)
  const [saveName, setSaveName] = useState('')
  const [saveFrom, setSaveFrom] = useState('')
  const [saveTo, setSaveTo] = useState('')
  const [busy, setBusy] = useState(false)

  const loadSession = useCallback(
    (s: SavedSession) => {
      if (!s.start_time || !s.end_time) {
        alert('This session has no start/end times and cannot be loaded as a filter window.')
        return
      }
      filter.setCustom(s.start_time.slice(0, 10), s.end_time.slice(0, 10))
      filter.setTimes(s.start_time.slice(11, 16) || '00:00', s.end_time.slice(11, 16) || '23:59')
      const moduleSlug = s.class_id?.split('|')[0] ?? null
      const lockedModule = moduleSlug
        ? moduleSlug.toUpperCase()
        : (s.module_filter && s.module_filter !== 'All Modules' && s.module_filter !== 'All'
            ? s.module_filter.toUpperCase()
            : null)
      filter.setLoadedSession(s.id, lockedModule)
      setView('inclass')
    },
    [filter, setView]
  )

  const deleteSession = useCallback(
    async (s: SavedSession) => {
      if (!confirm(`Delete "${s.name}"? This removes it from data/saved_sessions.json.`)) return
      setBusy(true)
      try {
        await api.post(`/sessions/${encodeURIComponent(s.id)}`.replace('/sessions/', '/sessions/') as string)
      } catch {
        /* fall through */
      }
      // DELETE via fetch directly (our api client only has GET/POST)
      try {
        await fetch(`/api/sessions/${encodeURIComponent(s.id)}`, { method: 'DELETE' })
      } catch (e) {
        console.error('delete failed:', e)
      } finally {
        setBusy(false)
        refetch()
      }
    },
    [refetch]
  )

  const openSaveDialog = () => {
    setSaveOpen(true)
    setSaveName(`Session ${new Date().toLocaleDateString()}`)
    setSaveFrom(filter.customFrom ?? isoToDate(new Date().toISOString()))
    setSaveTo(filter.customTo ?? isoToDate(new Date().toISOString()))
  }

  const submitSave = async () => {
    if (!saveName.trim() || !saveFrom || !saveTo) {
      alert('Name, From and To are required.')
      return
    }
    setBusy(true)
    try {
      const startIso = new Date(`${saveFrom}T${filter.timeStart || '00:00'}:00`).toISOString()
      const endIso = new Date(`${saveTo}T${filter.timeEnd || '23:59'}:59`).toISOString()
      await api.post('/sessions/save', {
        name: saveName.trim(),
        start_time: startIso,
        end_time: endIso,
        time_filter_preset: filter.preset,
      })
    } catch (e) {
      console.error('save failed:', e)
      alert('Save failed — check console.')
    } finally {
      setBusy(false)
      setSaveOpen(false)
      refetch()
    }
  }

  return (
    <motion.div
      variants={stagger}
      initial="initial"
      animate="animate"
      style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 18 }}
    >
      <AnimatedCard variants={fadeUp} style={{ background: T.card, border: `1px solid ${T.line}` }}>
        <div
          style={{
            padding: '18px 22px',
            borderBottom: `1px solid ${T.line}`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 12,
            flexWrap: 'wrap',
          }}
        >
          <div>
            <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>Saved Sessions</div>
            <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>
              Stored in <code style={{ background: T.bg2, padding: '1px 4px' }}>data/saved_sessions.json</code>. Click Load to apply a session as the current filter.
            </div>
          </div>
          <motion.button
            onClick={openSaveDialog}
            whileHover={{ filter: 'brightness(1.1)' }}
            whileTap={{ scale: 0.96 }}
            style={{
              padding: '6px 14px',
              background: T.accent,
              color: '#fff',
              border: 'none',
              fontFamily: T.fMono,
              fontSize: 11,
              letterSpacing: 1.2,
              textTransform: 'uppercase',
              cursor: 'pointer',
            }}
          >
            Save Retroactive Session
          </motion.button>
        </div>

        {loading && !data && (
          <div style={{ padding: 22, display: 'flex', flexDirection: 'column', gap: 10 }}>
            <Skeleton variant="text" rows={4} />
          </div>
        )}
        {error && <div style={{ padding: 28, color: T.danger, fontFamily: T.fMono, fontSize: 11 }}>{error}</div>}
        {!loading && !error && data && data.length === 0 && (
          <div style={{ padding: 28, color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>
            No saved sessions yet. Click "Save Retroactive Session" to create one from the current time window, or end the active session from the Sidebar.
          </div>
        )}

        {data && data.length > 0 && (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
            <thead>
              <tr>
                {['Class', 'Name', 'Start', 'Duration', 'Students', 'Flagged', 'Module', ''].map((h) => (
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
              <AnimatePresence initial={false}>
              {data.map((s, i) => (
                <motion.tr
                  key={s.id}
                  layout
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: 12 }}
                  transition={{ duration: 0.25, delay: i * 0.03 }}
                >
                  <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line2}`, color: s.class_label ? T.ink : T.ink3, fontFamily: T.fMono, fontSize: 12 }}>
                    {s.class_label ?? 'Legacy (time-only)'}
                  </td>
                  <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line2}`, color: T.ink }}>{s.name}</td>
                  <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line2}`, fontFamily: T.fMono, fontSize: 12, color: T.ink2 }}>
                    {fmtTimestamp(s.start_time)}
                  </td>
                  <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line2}`, fontFamily: T.fMono, fontSize: 12, color: T.ink2 }}>
                    {fmtDuration(s.duration_minutes)}
                  </td>
                  <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line2}`, fontFamily: T.fMono, fontSize: 12, color: T.ink }}>
                    {s.students ?? '—'}
                  </td>
                  <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line2}`, fontFamily: T.fMono, fontSize: 12, color: (s.flagged ?? 0) > 0 ? T.danger : T.ink3 }}>
                    {s.flagged ?? '—'}
                  </td>
                  <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line2}`, fontFamily: T.fMono, fontSize: 12, color: T.ink3 }}>
                    {s.module_filter ?? '—'}
                  </td>
                  <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line2}`, textAlign: 'right', whiteSpace: 'nowrap' }}>
                    <motion.button
                      onClick={() => openSessionProgression(s.id)}
                      whileHover={{ borderColor: T.ink, color: T.ink }}
                      whileTap={{ scale: 0.95 }}
                      style={{
                        padding: '4px 10px',
                        fontFamily: T.fMono,
                        fontSize: 10,
                        background: 'transparent',
                        color: T.ink2,
                        border: `1px solid ${T.line}`,
                        letterSpacing: 1,
                        textTransform: 'uppercase',
                        cursor: 'pointer',
                        marginRight: 6,
                      }}
                      title="Replay how this session progressed over time"
                    >
                      Progression →
                    </motion.button>
                    <motion.button
                      onClick={() => loadSession(s)}
                      whileHover={{ filter: 'brightness(1.1)' }}
                      whileTap={{ scale: 0.95 }}
                      style={{
                        padding: '4px 10px',
                        fontFamily: T.fMono,
                        fontSize: 10,
                        background: T.accent,
                        color: '#fff',
                        border: 'none',
                        letterSpacing: 1,
                        textTransform: 'uppercase',
                        cursor: 'pointer',
                        marginRight: 6,
                      }}
                      title="Apply this session as the current time filter (final state)"
                    >
                      Load
                    </motion.button>
                    <motion.button
                      onClick={() => deleteSession(s)}
                      disabled={busy}
                      whileHover={busy ? undefined : { background: T.danger, color: '#fff' }}
                      whileTap={busy ? undefined : { scale: 0.95 }}
                      transition={{ duration: 0.15 }}
                      style={{
                        padding: '4px 10px',
                        fontFamily: T.fMono,
                        fontSize: 10,
                        background: 'transparent',
                        color: T.danger,
                        border: `1px solid ${T.danger}`,
                        letterSpacing: 1,
                        textTransform: 'uppercase',
                        cursor: busy ? 'progress' : 'pointer',
                        opacity: busy ? 0.6 : 1,
                      }}
                    >
                      Delete
                    </motion.button>
                  </td>
                </motion.tr>
              ))}
              </AnimatePresence>
            </tbody>
          </table>
        )}
      </AnimatedCard>

      <AnimatePresence>
      {saveOpen && (
        <motion.div
          key="save-dialog"
          layout
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
          style={{
            padding: 18,
            background: T.card,
            border: `1px solid ${T.accent}`,
            overflow: 'hidden',
          }}
        >
          <SectionLabel n={2}>Save Retroactive Session</SectionLabel>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 10, alignItems: 'end' }}>
            <Field label="Name">
              <input value={saveName} onChange={(e) => setSaveName(e.target.value)} style={inputStyle()} />
            </Field>
            <Field label="From">
              <input type="date" value={saveFrom} onChange={(e) => setSaveFrom(e.target.value)} style={inputStyle()} />
            </Field>
            <Field label="To">
              <input type="date" value={saveTo} onChange={(e) => setSaveTo(e.target.value)} style={inputStyle()} />
            </Field>
          </div>
          <div style={{ marginTop: 12, display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <button
              onClick={() => setSaveOpen(false)}
              style={{
                padding: '6px 14px',
                background: 'transparent',
                color: T.ink2,
                border: `1px solid ${T.line}`,
                fontFamily: T.fMono,
                fontSize: 11,
                letterSpacing: 1,
                textTransform: 'uppercase',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              onClick={submitSave}
              disabled={busy}
              style={{
                padding: '6px 14px',
                background: T.accent,
                color: '#fff',
                border: 'none',
                fontFamily: T.fMono,
                fontSize: 11,
                letterSpacing: 1.2,
                textTransform: 'uppercase',
                cursor: busy ? 'progress' : 'pointer',
                opacity: busy ? 0.6 : 1,
              }}
            >
              Save
            </button>
          </div>
        </motion.div>
      )}
      </AnimatePresence>
    </motion.div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <span style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, letterSpacing: 1, textTransform: 'uppercase' }}>
        {label}
      </span>
      {children}
    </label>
  )
}

function inputStyle(): React.CSSProperties {
  return {
    padding: '6px 8px',
    fontFamily: T.fMono,
    fontSize: 12,
    background: T.bg2,
    color: T.ink,
    border: `1px solid ${T.line}`,
  }
}
