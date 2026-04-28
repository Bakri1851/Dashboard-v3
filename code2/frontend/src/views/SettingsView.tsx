import { useState } from 'react'
import { motion } from 'framer-motion'
import { T, THEMES } from '../theme/tokens'
import { useTheme } from '../theme/ThemeContext'
import { useSettings } from '../api/useSettings'
import { useUiPrefsStore } from '../state/uiPrefsStore'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { AnimatedCard } from '../animation/AnimatedCard'
import { stagger, fadeUp } from '../animation/motion'
import { api } from '../api/client'

const AUTO_REFRESH_OPTIONS = [5, 10, 15, 30, 60, 120, 300]

export function SettingsView() {
  const { theme, setTheme, accents, accentId, setAccent } = useTheme()
  const { data, error, loading, update, reset } = useSettings()
  const inClassViewMode = useUiPrefsStore((s) => s.inClassViewMode)
  const setInClassViewMode = useUiPrefsStore((s) => s.setInClassViewMode)

  return (
    <motion.div
      variants={stagger}
      initial="initial"
      animate="animate"
      style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 960 }}
    >
      {/* Theme picker */}
      <AnimatedCard variants={fadeUp} style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={1}>Appearance · Theme</SectionLabel>
        <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3, marginBottom: 14, lineHeight: 1.6 }}>
          Seven visual skins — pick any. Changes persist in localStorage and apply immediately.
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 12 }}>
          {THEMES.map((t, i) => {
            const active = theme === t.id
            return (
              <motion.button
                key={t.id}
                onClick={() => setTheme(t.id)}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: i * 0.04 }}
                whileHover={{ y: -2, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
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
                <div style={{ fontFamily: T.fMono, fontSize: 10, marginTop: 6, opacity: 0.75 }}>{t.id}</div>
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
              </motion.button>
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
      </AnimatedCard>

      {/* Display — local UI prefs (no backend dependency) */}
      <AnimatedCard variants={fadeUp} style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={2}>Display</SectionLabel>
        <ToggleRow
          label="In-class layout"
          options={[
            { id: 'basic', label: 'Basic' },
            { id: 'advanced', label: 'Advanced' },
          ]}
          active={inClassViewMode}
          onChange={(v) => setInClassViewMode(v as 'basic' | 'advanced')}
        />
        <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3, marginTop: 12, lineHeight: 1.6 }}>
          Basic layout shows one row per student / question with a colour-coded bar. Bar lengths are
          stretched across the current cohort so small score differences stay visible. Advanced layout
          keeps the full leaderboard, distributions, and timeline view.
        </div>
      </AnimatedCard>

      {loading && !data && (
        <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>loading backend config…</div>
      )}
      {error && (
        <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.danger }}>{error}</div>
      )}

      {data && (
        <>
          {/* Scoring Models */}
          <AnimatedCard variants={fadeUp} style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
            <SectionLabel n={3}>Scoring Models</SectionLabel>
            <ToggleRow
              label="Struggle model"
              options={[
                { id: 'baseline', label: 'Baseline' },
                { id: 'improved', label: 'Improved (BKT + IRT-weighted)' },
              ]}
              active={data.runtime.struggle_model}
              onChange={(v) => update({ struggle_model: v })}
            />
            <ToggleRow
              label="Difficulty model"
              options={[
                { id: 'baseline', label: 'Baseline' },
                { id: 'irt', label: 'IRT (Rasch 1PL)' },
              ]}
              active={data.runtime.difficulty_model}
              onChange={(v) => update({ difficulty_model: v })}
            />
            <ToggleRow
              label="Collaborative Filtering"
              options={[
                { id: 'off', label: 'Off' },
                { id: 'on', label: 'On' },
              ]}
              active={data.runtime.cf_enabled ? 'on' : 'off'}
              onChange={(v) => update({ cf_enabled: v === 'on' })}
            />
            <div
              style={{
                marginTop: 12,
                padding: 12,
                background: T.bg2,
                fontFamily: T.fMono,
                fontSize: 11,
                color: T.ink2,
                lineHeight: 1.6,
              }}
            >
              CF compares students on 5 behavioural features (n̂, t̂, ī, Â, d̂) using cosine similarity.
              Threshold τ controls strictness.
            </div>
            <SliderRow
              label="CF threshold (τ)"
              value={data.runtime.cf_threshold}
              min={0}
              max={1}
              step={0.05}
              format={(v) => v.toFixed(2)}
              disabled={!data.runtime.cf_enabled}
              onChange={(v) => update({ cf_threshold: v })}
            />
          </AnimatedCard>

          {/* BKT Parameters */}
          <AnimatedCard
            variants={fadeUp}
            style={{
              padding: 24,
              background: T.card,
              border: `1px solid ${T.line}`,
              opacity: data.runtime.struggle_model === 'improved' ? 1 : 0.55,
            }}
          >
            <SectionLabel n={4}>BKT Parameters</SectionLabel>
            {data.runtime.struggle_model !== 'improved' && (
              <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3, marginBottom: 14 }}>
                Enabled only when struggle model is set to "Improved". Change the sliders anyway —
                they take effect once you flip the model.
              </div>
            )}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 14 }}>
              <BKTCard label="p_init"  value={data.runtime.bkt.p_init}  onChange={(v) => update({ bkt_p_init: v })} />
              <BKTCard label="p_learn" value={data.runtime.bkt.p_learn} onChange={(v) => update({ bkt_p_learn: v })} />
              <BKTCard label="p_guess" value={data.runtime.bkt.p_guess} max={0.5} onChange={(v) => update({ bkt_p_guess: v })} />
              <BKTCard label="p_slip"  value={data.runtime.bkt.p_slip}  max={0.5} onChange={(v) => update({ bkt_p_slip: v })} />
            </div>
          </AnimatedCard>

          {/* Environment */}
          <AnimatedCard variants={fadeUp} style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
            <SectionLabel n={5}>Environment</SectionLabel>
            <ToggleRow
              label="Sound effects"
              options={[
                { id: 'off', label: 'Off' },
                { id: 'on', label: 'On' },
              ]}
              active={data.runtime.sounds_enabled ? 'on' : 'off'}
              onChange={(v) => update({ sounds_enabled: v === 'on' })}
            />
            <ToggleRow
              label="Auto-refresh"
              options={[
                { id: 'off', label: 'Off' },
                { id: 'on', label: 'On' },
              ]}
              active={data.runtime.auto_refresh ? 'on' : 'off'}
              onChange={(v) => update({ auto_refresh: v === 'on' })}
            />
            <div
              style={{
                marginTop: 12,
                display: 'grid',
                gridTemplateColumns: '1fr auto',
                alignItems: 'center',
                gap: 10,
                opacity: data.runtime.auto_refresh ? 1 : 0.4,
              }}
            >
              <div style={{ fontFamily: T.fSans, fontSize: 13 }}>Refresh interval</div>
              <select
                disabled={!data.runtime.auto_refresh}
                value={data.runtime.refresh_interval}
                onChange={(e) => update({ refresh_interval: parseInt(e.target.value, 10) })}
                style={{
                  fontFamily: T.fMono,
                  fontSize: 12,
                  padding: '4px 8px',
                  background: T.card,
                  color: T.ink,
                  border: `1px solid ${T.line}`,
                }}
              >
                {AUTO_REFRESH_OPTIONS.map((s) => (
                  <option key={s} value={s}>
                    {s}s
                  </option>
                ))}
              </select>
            </div>
          </AnimatedCard>

          <DemoLabSection />

          {/* Reset + read-only config reference */}
          <AnimatedCard
            variants={fadeUp}
            style={{
              padding: '14px 18px',
              background: T.bg2,
              border: `1px dashed ${T.line}`,
              fontFamily: T.fMono,
              fontSize: 11,
              color: T.ink2,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <span>
              Changes persist for this backend process. Restart the server to reload <code>config.py</code>.
            </span>
            <button
              onClick={reset}
              style={{
                background: 'transparent',
                color: T.danger,
                border: `1px solid ${T.danger}`,
                padding: '4px 10px',
                fontFamily: T.fMono,
                fontSize: 10,
                letterSpacing: 1,
                textTransform: 'uppercase',
                cursor: 'pointer',
              }}
            >
              Reset Defaults
            </button>
          </AnimatedCard>

          {/* Read-only config reference (unchanged from Phase 3) */}
          <AnimatedCard variants={fadeUp} style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
            <SectionLabel n={6}>Read-only config reference</SectionLabel>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 16 }}>
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
                  <Line key={i} label={`${t[0].toFixed(2)}–${t[1].toFixed(2)}`} value={t[2]} valueColor={t[3]} />
                ))}
              </InfoBlock>
              <InfoBlock title="Difficulty thresholds">
                {data.thresholds.difficulty.map((t, i) => (
                  <Line key={i} label={`${t[0].toFixed(2)}–${t[1].toFixed(2)}`} value={t[2]} valueColor={t[3]} />
                ))}
              </InfoBlock>
              <InfoBlock title="Runtime (derived)">
                <Line label="cache_ttl (raw)" value={`${data.cache_ttl}s`} />
                <Line label="correct_threshold" value={data.correct_threshold.toFixed(2)} />
                <Line label="smoothing_alpha" value={data.smoothing_alpha.toFixed(2)} />
                <Line label="leaderboard_max" value={String(data.leaderboard_max_items)} />
              </InfoBlock>
            </div>
          </AnimatedCard>
        </>
      )}
    </motion.div>
  )
}

function ToggleRow({
  label,
  options,
  active,
  onChange,
}: {
  label: string
  options: { id: string; label: string }[]
  active: string
  onChange: (id: string) => void
}) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr auto',
        gap: 10,
        alignItems: 'center',
        padding: '10px 0',
        borderBottom: `1px dashed ${T.line2}`,
      }}
    >
      <div style={{ fontFamily: T.fSans, fontSize: 13, color: T.ink }}>{label}</div>
      <div style={{ display: 'flex', gap: 0 }}>
        {options.map((o) => {
          const isActive = o.id === active
          return (
            <button
              key={o.id}
              onClick={() => onChange(o.id)}
              style={{
                padding: '5px 12px',
                fontFamily: T.fMono,
                fontSize: 10.5,
                letterSpacing: 1,
                textTransform: 'uppercase',
                background: isActive ? T.accent : 'transparent',
                color: isActive ? '#fff' : T.ink2,
                border: `1px solid ${isActive ? T.accent : T.line}`,
                borderRight: 'none',
                cursor: 'pointer',
              }}
            >
              {o.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}

function SliderRow({
  label,
  value,
  min,
  max,
  step,
  disabled,
  format,
  onChange,
}: {
  label: string
  value: number
  min: number
  max: number
  step: number
  disabled?: boolean
  format: (v: number) => string
  onChange: (v: number) => void
}) {
  return (
    <div
      style={{
        marginTop: 14,
        display: 'grid',
        gridTemplateColumns: '1fr auto',
        alignItems: 'center',
        gap: 10,
        opacity: disabled ? 0.4 : 1,
      }}
    >
      <div style={{ fontFamily: T.fSans, fontSize: 13, color: T.ink }}>{label}</div>
      <div style={{ fontFamily: T.fMono, fontSize: 13, color: T.accent }}>{format(value)}</div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{ gridColumn: '1 / span 2', accentColor: T.accent }}
      />
    </div>
  )
}

function BKTCard({
  label,
  value,
  max = 1,
  onChange,
}: {
  label: string
  value: number
  max?: number
  onChange: (v: number) => void
}) {
  return (
    <div style={{ padding: 14, border: `1px solid ${T.line}`, background: T.bg2 }}>
      <div
        style={{
          fontFamily: T.fMono,
          fontSize: 10.5,
          color: T.ink3,
          letterSpacing: 1,
          textTransform: 'uppercase',
        }}
      >
        {label}
      </div>
      <div style={{ fontFamily: T.fSerif, fontSize: 24, color: T.ink, marginTop: 4 }}>
        {value.toFixed(2)}
      </div>
      <input
        type="range"
        min={0}
        max={max}
        step={0.01}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{ width: '100%', marginTop: 6, accentColor: T.accent }}
      />
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

function DemoLabSection() {
  const [busy, setBusy] = useState<'seed' | 'end' | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const run = async (action: 'seed' | 'end', path: string, doneText: string) => {
    setBusy(action)
    setMessage(null)
    try {
      await api.post(path, {})
      setMessage(doneText)
    } catch (e) {
      setMessage(`Failed: ${e instanceof Error ? e.message : String(e)}`)
    } finally {
      setBusy(null)
    }
  }

  return (
    <AnimatedCard
      variants={fadeUp}
      style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}
    >
      <SectionLabel n={6}>Demo Lab</SectionLabel>
      <div
        style={{
          fontFamily: T.fMono,
          fontSize: 11,
          color: T.ink3,
          marginBottom: 14,
          lineHeight: 1.6,
        }}
      >
        Populates a fake live session with 4 assistants so the In-Class assign column
        is visible without a real lab. Click again to end.
      </div>
      <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
        <motion.button
          onClick={() => run('seed', '/lab/seed-demo', 'Demo session seeded — open In Class.')}
          disabled={busy !== null}
          whileHover={busy ? undefined : { y: -1 }}
          whileTap={busy ? undefined : { scale: 0.97 }}
          style={{
            padding: '6px 14px',
            background: 'transparent',
            color: T.accent,
            border: `1px solid ${T.accent}`,
            fontFamily: T.fMono,
            fontSize: 11,
            letterSpacing: 1.2,
            textTransform: 'uppercase',
            cursor: busy ? 'wait' : 'pointer',
            opacity: busy && busy !== 'seed' ? 0.4 : 1,
          }}
        >
          {busy === 'seed' ? 'Seeding…' : 'Seed demo lab'}
        </motion.button>
        <motion.button
          onClick={() => run('end', '/lab/end', 'Demo session ended.')}
          disabled={busy !== null}
          whileHover={busy ? undefined : { y: -1 }}
          whileTap={busy ? undefined : { scale: 0.97 }}
          style={{
            padding: '6px 14px',
            background: 'transparent',
            color: T.danger,
            border: `1px solid ${T.danger}`,
            fontFamily: T.fMono,
            fontSize: 11,
            letterSpacing: 1.2,
            textTransform: 'uppercase',
            cursor: busy ? 'wait' : 'pointer',
            opacity: busy && busy !== 'end' ? 0.4 : 1,
          }}
        >
          {busy === 'end' ? 'Ending…' : 'End demo lab'}
        </motion.button>
        {message && (
          <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink2 }}>{message}</span>
        )}
      </div>
    </AnimatedCard>
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
