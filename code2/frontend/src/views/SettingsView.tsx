import { T, THEMES } from '../theme/tokens'
import { useTheme } from '../theme/ThemeContext'
import { useApiData } from '../api/hooks'
import type { Settings } from '../types/api'
import { SectionLabel } from '../components/primitives/SectionLabel'

export function SettingsView() {
  const { theme, setTheme, accents, accentId, setAccent } = useTheme()
  const { data, error, loading } = useApiData<Settings>('/settings')

  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 960 }}>
      {/* Theme picker */}
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={1}>Appearance · Theme</SectionLabel>
        <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3, marginBottom: 14, lineHeight: 1.6 }}>
          Seven visual skins — pick any. Changes persist in localStorage and apply immediately.
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 12 }}>
          {THEMES.map((t) => {
            const active = theme === t.id
            return (
              <button
                key={t.id}
                onClick={() => setTheme(t.id)}
                style={{
                  padding: '16px 18px',
                  background: t.preview,
                  color: ['scifi', 'blueprint', 'matrix', 'cyberpunk'].includes(t.id) ? '#fff' : '#1a1a1a',
                  border: `2px solid ${active ? T.accent : T.line}`,
                  textAlign: 'left',
                  cursor: 'pointer',
                  position: 'relative',
                  minHeight: 84,
                }}
              >
                <div style={{ fontFamily: T.fSerif, fontSize: 15 }}>{t.label}</div>
                <div style={{ fontFamily: T.fMono, fontSize: 10, marginTop: 6, opacity: 0.75 }}>
                  {t.id}
                </div>
                {active && (
                  <span
                    style={{
                      position: 'absolute',
                      top: 10,
                      right: 10,
                      fontFamily: T.fMono,
                      fontSize: 9,
                      letterSpacing: 1.4,
                      padding: '2px 6px',
                      background: T.accent,
                      color: '#fff',
                    }}
                  >
                    ACTIVE
                  </span>
                )}
              </button>
            )
          })}
        </div>

        <div style={{ marginTop: 18, display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1, textTransform: 'uppercase' }}>
            Accent
          </span>
          {accents.map((a) => (
            <button
              key={a.id}
              onClick={() => setAccent(a.id)}
              title={a.id}
              style={{
                width: 22,
                height: 22,
                borderRadius: '50%',
                background: `oklch(0.55 0.14 ${a.h})`,
                outline: accentId === a.id ? `2px solid ${T.ink}` : 'none',
                outlineOffset: 2,
                border: `1px solid ${T.line}`,
                cursor: 'pointer',
              }}
            />
          ))}
        </div>
      </div>

      {/* Current backend configuration (read-only) */}
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={2}>Backend Configuration · read-only</SectionLabel>
        {loading && <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>loading…</div>}
        {error && <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.danger }}>{error}</div>}
        {data && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}>
            <InfoBlock title="Struggle weights (sum = 1.00)">
              {Object.entries(data.struggle_weights).map(([k, v]) => (
                <Line key={k} label={k} value={v.toFixed(2)} />
              ))}
            </InfoBlock>

            <InfoBlock title="Difficulty weights (sum = 1.00)">
              {Object.entries(data.difficulty_weights).map(([k, v]) => (
                <Line key={k} label={k} value={v.toFixed(2)} />
              ))}
            </InfoBlock>

            <InfoBlock title="Struggle thresholds">
              {data.thresholds.struggle.map((t, i) => (
                <Line
                  key={i}
                  label={`${t[0].toFixed(2)}–${t[1].toFixed(2)}`}
                  value={t[2]}
                  valueColor={t[3]}
                />
              ))}
            </InfoBlock>

            <InfoBlock title="Difficulty thresholds">
              {data.thresholds.difficulty.map((t, i) => (
                <Line
                  key={i}
                  label={`${t[0].toFixed(2)}–${t[1].toFixed(2)}`}
                  value={t[2]}
                  valueColor={t[3]}
                />
              ))}
            </InfoBlock>

            <InfoBlock title="BKT parameters">
              <Line label="p_init" value={data.bkt.p_init.toFixed(2)} />
              <Line label="p_learn" value={data.bkt.p_learn.toFixed(2)} />
              <Line label="p_guess" value={data.bkt.p_guess.toFixed(2)} />
              <Line label="p_slip" value={data.bkt.p_slip.toFixed(2)} />
              <Line label="mastery_threshold" value={data.bkt.mastery_threshold.toFixed(2)} />
            </InfoBlock>

            <InfoBlock title="Runtime">
              <Line label="cache_ttl (raw)" value={`${data.cache_ttl}s`} />
              <Line label="correct_threshold" value={data.correct_threshold.toFixed(2)} />
              <Line label="smoothing_alpha" value={data.smoothing_alpha.toFixed(2)} />
              <Line label="leaderboard_max" value={String(data.leaderboard_max_items)} />
            </InfoBlock>
          </div>
        )}
        <div style={{ marginTop: 14, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, lineHeight: 1.6 }}>
          Live weight/threshold editing is out of scope for this frontend. Change the values in{' '}
          <code style={{ background: T.bg2, padding: '1px 4px' }}>code2/learning_dashboard/config.py</code>{' '}
          then restart the backend.
        </div>
      </div>
    </div>
  )
}

function InfoBlock({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ padding: 14, border: `1px solid ${T.line2}`, background: T.bg2 }}>
      <div
        style={{
          fontFamily: T.fMono,
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 1.2,
          textTransform: 'uppercase',
          marginBottom: 8,
        }}
      >
        {title}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>{children}</div>
    </div>
  )
}

function Line({ label, value, valueColor }: { label: string; value: string; valueColor?: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, fontFamily: T.fMono, fontSize: 12 }}>
      <span style={{ color: T.ink2 }}>{label}</span>
      <span style={{ color: valueColor ?? T.ink }}>{value}</span>
    </div>
  )
}
