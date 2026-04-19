import { T } from '../../theme/tokens'
import { useTheme } from '../../theme/ThemeContext'
import { useViewStore } from '../../state/viewStore'
import type { ViewId } from '../../state/viewStore'

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

export function Sidebar({ sessionCode, elapsed }: { sessionCode: string; elapsed: string }) {
  const { view, setView } = useViewStore()
  const { theme } = useTheme()

  return (
    <aside
      style={{
        width: 240,
        minWidth: 240,
        background: T.panel,
        borderRight: `1px solid ${T.border}`,
        padding: '28px 20px 20px',
        display: 'flex',
        flexDirection: 'column',
        gap: 24,
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

      <div style={{ border: `1px solid ${T.border}`, padding: '10px 12px' }}>
        <div style={{ fontSize: 10, letterSpacing: 1.4, textTransform: 'uppercase', color: T.ink3 }}>
          Session
        </div>
        <div style={{ fontFamily: T.fMono, fontSize: 18, marginTop: 4 }}>{sessionCode}</div>
        <div style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink2, marginTop: 2 }}>{elapsed}</div>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
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
                color: active ? T.ink0 : T.ink1,
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
