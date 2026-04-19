import { useCallback, useEffect, useState } from 'react'
import { T } from '../../theme/tokens'
import { useTheme } from '../../theme/ThemeContext'
import { useViewStore } from '../../state/viewStore'
import type { ViewId } from '../../state/viewStore'
import { useFilterStore } from '../../state/filterStore'
import type { FilterPreset } from '../../state/filterStore'
import { useApiData } from '../../api/hooks'
import { api } from '../../api/client'
import type { AcademicPeriod, FilterPresetMeta, LabState } from '../../types/api'

interface NavItem {
  id: ViewId
  label: string
  hint: string
}

const NAV: NavItem[] = [
  { id: 'inclass',  label: '01  In Class',         hint: 'Live leaderboards' },
  { id: 'analysis', label: '04  Data Analysis',    hint: 'Historical view' },
  { id: 'compare',  label: '05  Model Comparison', hint: 'IRT · BKT · improved' },
  { id: 'previous', label: '06  Previous Sessions',hint: 'Saved records' },
  { id: 'lab',      label: '07  Lab Assistants',   hint: 'Assign / monitor' },
  { id: 'settings', label: '08  Settings',         hint: 'Weights · thresholds' },
]

function fmtElapsed(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = totalSeconds % 60
  return [h, m, s].map((n) => String(n).padStart(2, '0')).join(':')
}

export function Sidebar() {
  const { view, setView } = useViewStore()
  const { theme } = useTheme()
  const { data: lab, refetch } = useApiData<LabState>('/lab/state', 3_000)
  const { data: presetMeta } = useApiData<FilterPresetMeta[]>('/meta/filter-presets', 0)
  const { data: academicPeriods } = useApiData<AcademicPeriod[]>('/meta/academic-periods', 0)
  const [busy, setBusy] = useState(false)

  const filter = useFilterStore()

  // Live elapsed-since-session-start (hh:mm:ss)
  const [now, setNow] = useState<number>(() => Date.now())
  useEffect(() => {
    const t = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(t)
  }, [])
  const elapsedSec = (() => {
    if (!lab?.session_active || !lab.session_start) return 0
    const start = new Date(lab.session_start).getTime()
    if (isNaN(start)) return 0
    return Math.max(0, Math.floor((now - start) / 1000))
  })()

  const startSession = useCallback(async () => {
    setBusy(true)
    try { await api.post('/lab/start') } catch (e) { console.error('start session failed:', e) } finally { setBusy(false); refetch() }
  }, [refetch])

  const endSession = useCallback(async () => {
    if (!confirm('End the current lab session? Assistants will be unassigned.')) return
    setBusy(true)
    try { await api.post('/lab/end') } catch (e) { console.error('end session failed:', e) } finally { setBusy(false); refetch() }
  }, [refetch])

  const sessionActive = lab?.session_active ?? false
  const sessionCode = lab?.session_code ?? null
  const assistants = lab?.lab_assistants ?? []
  const helpingCount = (lab?.assignments ?? []).filter((a) => a.status === 'helping').length

  const presets = presetMeta ?? []
  const isCustom = filter.preset === 'custom'

  return (
    <aside
      style={{
        width: 260,
        minWidth: 260,
        background: T.panel,
        borderRight: `1px solid ${T.border}`,
        padding: '28px 20px 20px',
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        overflowY: 'auto',
      }}
    >
      <div>
        <div style={{ height: 4, width: 56, background: T.accent, marginBottom: 10 }} />
        <h1 style={{ fontSize: 16, fontWeight: 600, letterSpacing: 0.3, margin: 0 }}>
          Learning Analytics
        </h1>
        <div style={{ fontSize: 10.5, letterSpacing: 1.5, textTransform: 'uppercase', color: T.ink3, marginTop: 4 }}>
          Studio — Thesis Design
        </div>
      </div>

      {/* Lab session */}
      <div>
        <Label>Lab Session</Label>
        {!sessionActive ? (
          <button
            onClick={startSession}
            disabled={busy}
            style={{
              width: '100%',
              padding: '10px 12px',
              background: T.accent,
              color: '#ffffff',
              border: 'none',
              fontFamily: T.fMono,
              fontSize: 11,
              letterSpacing: 1.4,
              textTransform: 'uppercase',
              cursor: busy ? 'progress' : 'pointer',
              opacity: busy ? 0.6 : 1,
            }}
          >
            Start Session
          </button>
        ) : (
          <div style={{ background: T.card, border: `1px solid ${T.border}`, padding: '10px 12px' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
              <span style={{ fontFamily: T.fMono, fontSize: 9.5, color: T.ok, letterSpacing: 1.5 }}>● LIVE</span>
              <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink, fontVariantNumeric: 'tabular-nums' }}>
                {fmtElapsed(elapsedSec)}
              </span>
            </div>
            <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 9.5, color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase' }}>
              Code
            </div>
            <div style={{ fontFamily: T.fMono, fontSize: 22, color: T.ink, letterSpacing: 3, marginTop: 2 }}>
              {sessionCode ?? '—'}
            </div>
            <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 10.5, color: T.ink2 }}>
              {helpingCount} of {assistants.length} assistants helping
            </div>
            <button
              onClick={endSession}
              disabled={busy}
              style={{
                width: '100%',
                marginTop: 10,
                padding: '6px 10px',
                background: 'transparent',
                color: T.danger,
                border: `1px solid ${T.danger}`,
                fontFamily: T.fMono,
                fontSize: 10.5,
                letterSpacing: 1.2,
                textTransform: 'uppercase',
                cursor: busy ? 'progress' : 'pointer',
                opacity: busy ? 0.6 : 1,
              }}
            >
              End Session
            </button>
          </div>
        )}
      </div>

      {/* Time filter */}
      <div>
        <Label>Time Filter</Label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {presets.map((p) => {
            const active = filter.preset === (p.id as FilterPreset)
            const disabled = p.id === 'live' && !sessionActive
            return (
              <button
                key={p.id}
                disabled={disabled}
                onClick={() => filter.setPreset(p.id as FilterPreset)}
                title={disabled ? 'Requires an active session' : p.label}
                style={{
                  padding: '4px 8px',
                  fontFamily: T.fMono,
                  fontSize: 10,
                  letterSpacing: 0.5,
                  background: active ? T.accent : 'transparent',
                  color: active ? '#ffffff' : disabled ? T.ink3 : T.ink2,
                  border: `1px solid ${active ? T.accent : T.line}`,
                  borderRadius: 999,
                  cursor: disabled ? 'not-allowed' : 'pointer',
                  opacity: disabled ? 0.45 : 1,
                }}
              >
                {p.label}
              </button>
            )
          })}
        </div>

        {isCustom && (
          <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <SmallLabel>From</SmallLabel>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 4 }}>
              <input
                type="date"
                value={filter.customFrom ?? ''}
                onChange={(e) => filter.setCustom(e.target.value || null, filter.customTo)}
                style={inputStyle()}
              />
              <input
                type="time"
                value={filter.timeStart}
                onChange={(e) => filter.setTimes(e.target.value, filter.timeEnd)}
                style={{ ...inputStyle(), width: 82 }}
              />
            </div>
            <SmallLabel>To</SmallLabel>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 4 }}>
              <input
                type="date"
                value={filter.customTo ?? ''}
                onChange={(e) => filter.setCustom(filter.customFrom, e.target.value || null)}
                style={inputStyle()}
              />
              <input
                type="time"
                value={filter.timeEnd}
                onChange={(e) => filter.setTimes(filter.timeStart, e.target.value)}
                style={{ ...inputStyle(), width: 82 }}
              />
            </div>
            <SmallLabel>Academic week</SmallLabel>
            <select
              value={filter.academicWeek ?? ''}
              onChange={(e) => filter.setAcademicWeek(e.target.value || null)}
              style={inputStyle()}
            >
              <option value="">— any —</option>
              {(academicPeriods ?? []).map((p) => (
                <option key={p.label} value={p.label}>
                  {p.label}
                </option>
              ))}
            </select>
            <button
              onClick={() => filter.reset()}
              style={{
                marginTop: 4,
                padding: '4px 8px',
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
              Reset to All Time
            </button>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Label>View</Label>
        {NAV.map((item) => {
          const active = item.id === view
          return (
            <button
              key={item.id}
              onClick={() => setView(item.id)}
              style={{
                textAlign: 'left',
                padding: '10px 12px',
                borderLeft: `2px solid ${active ? T.accent : 'transparent'}`,
                background: active ? T.accentSoft : 'transparent',
                color: active ? T.ink : T.ink2,
                cursor: 'pointer',
              }}
            >
              <div style={{ fontSize: 13, fontWeight: active ? 600 : 500 }}>{item.label}</div>
              <div style={{ fontSize: 10.5, color: T.ink3, marginTop: 2 }}>{item.hint}</div>
            </button>
          )
        })}
      </nav>

      <div style={{ marginTop: 'auto', fontFamily: T.fMono, fontSize: 10, color: T.ink3, letterSpacing: 0.5 }}>
        theme · {theme}
      </div>
    </aside>
  )
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        fontFamily: T.fMono,
        fontSize: 10,
        color: T.ink3,
        letterSpacing: 1.5,
        textTransform: 'uppercase',
        marginBottom: 8,
      }}
    >
      {children}
    </div>
  )
}

function SmallLabel({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        fontFamily: T.fMono,
        fontSize: 9,
        color: T.ink3,
        letterSpacing: 1.2,
        textTransform: 'uppercase',
      }}
    >
      {children}
    </div>
  )
}

function inputStyle(): React.CSSProperties {
  return {
    padding: '4px 6px',
    fontFamily: T.fMono,
    fontSize: 11,
    background: T.card,
    color: T.ink,
    border: `1px solid ${T.line}`,
    width: '100%',
  }
}
