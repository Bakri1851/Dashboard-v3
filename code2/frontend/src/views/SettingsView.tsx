import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { T, THEMES } from '../theme/tokens'
import { useTheme } from '../theme/ThemeContext'
import { useSettings } from '../api/useSettings'
import { useUiPrefsStore } from '../state/uiPrefsStore'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { Tabs } from '../components/primitives/Tabs'
import type { TabDef } from '../components/primitives/Tabs'
import { AnimatedCard } from '../animation/AnimatedCard'
import { stagger, fadeUp } from '../animation/motion'
import { api } from '../api/client'

const AUTO_REFRESH_OPTIONS = [5, 10, 15, 30, 60, 120, 300]

const STORAGE_KEY_SETTINGS_TAB = 'dash-settings-tab'
type SettingsTabId = 'appearance' | 'models' | 'system' | 'advanced'
const SETTINGS_TABS: TabDef[] = [
  { id: 'appearance', label: 'Appearance' },
  { id: 'models', label: 'Models' },
  { id: 'system', label: 'System' },
  { id: 'advanced', label: 'Advanced' },
]
const VALID_TAB_IDS = new Set<SettingsTabId>(['appearance', 'models', 'system', 'advanced'])

function readStoredTab(): SettingsTabId {
  try {
    const stored = localStorage.getItem(STORAGE_KEY_SETTINGS_TAB)
    if (stored && VALID_TAB_IDS.has(stored as SettingsTabId)) return stored as SettingsTabId
  } catch {
    // localStorage unavailable (private mode etc.) — fall through to default
  }
  return 'appearance'
}

export function SettingsView() {
  const { theme, setTheme, accents, accentId, setAccent } = useTheme()
  const { data, error, loading, update, reset } = useSettings()
  const inClassViewMode = useUiPrefsStore((s) => s.inClassViewMode)
  const setInClassViewMode = useUiPrefsStore((s) => s.setInClassViewMode)
  const [activeTab, setActiveTab] = useState<SettingsTabId>(readStoredTab)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_SETTINGS_TAB, activeTab)
    } catch {
      // ignore quota/availability errors — non-essential preference
    }
  }, [activeTab])

  return (
    <motion.div
      variants={stagger}
      initial="initial"
      animate="animate"
      style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 960 }}
    >
      <Tabs
        tabs={SETTINGS_TABS}
        activeId={activeTab}
        onChange={(id) => setActiveTab(id as SettingsTabId)}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {activeTab === 'appearance' && (
            <AppearancePanel
              theme={theme}
              setTheme={setTheme}
              accents={accents}
              accentId={accentId}
              setAccent={setAccent}
              inClassViewMode={inClassViewMode}
              setInClassViewMode={setInClassViewMode}
            />
          )}

          {loading && !data && (
            <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>loading backend config…</div>
          )}
          {error && (
            <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.danger }}>{error}</div>
          )}

          {data && activeTab === 'models' && <ModelsPanel data={data} update={update} />}
          {data && activeTab === 'system' && <SystemPanel data={data} update={update} reset={reset} />}
          {data && activeTab === 'advanced' && <AdvancedPanel data={data} update={update} />}
        </div>
      </Tabs>
    </motion.div>
  )
}

type SettingsData = NonNullable<ReturnType<typeof useSettings>['data']>
type SettingsUpdate = ReturnType<typeof useSettings>['update']
type SettingsReset = ReturnType<typeof useSettings>['reset']

function AppearancePanel({
  theme,
  setTheme,
  accents,
  accentId,
  setAccent,
  inClassViewMode,
  setInClassViewMode,
}: {
  theme: ReturnType<typeof useTheme>['theme']
  setTheme: ReturnType<typeof useTheme>['setTheme']
  accents: ReturnType<typeof useTheme>['accents']
  accentId: string
  setAccent: ReturnType<typeof useTheme>['setAccent']
  inClassViewMode: 'basic' | 'advanced'
  setInClassViewMode: (v: 'basic' | 'advanced') => void
}) {
  return (
    <>
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
    </>
  )
}

function ModelsPanel({ data, update }: { data: SettingsData; update: SettingsUpdate }) {
  return (
    <>
      {/* Scoring Models */}
      <AnimatedCard variants={fadeUp} style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={1}>Scoring Models</SectionLabel>
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
    </>
  )
}

function SystemPanel({
  data,
  update,
  reset,
}: {
  data: SettingsData
  update: SettingsUpdate
  reset: SettingsReset
}) {
  return (
    <>
      {/* Environment */}
      <AnimatedCard variants={fadeUp} style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={1}>Environment</SectionLabel>
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

      <DemoLabSection n={2} />

      {/* Reset Defaults footer */}
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
    </>
  )
}

function AdvancedPanel({ data, update }: { data: SettingsData; update: SettingsUpdate }) {
  return (
    <>
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
        <SectionLabel n={1}>BKT Parameters</SectionLabel>
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

      {/* Optimised Weights (v2) — Phase 5 toggles */}
      <AnimatedCard variants={fadeUp} style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={2}>Optimised Weights (v2)</SectionLabel>
        <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3, marginBottom: 14, lineHeight: 1.6 }}>
          The deployed defaults are the hand-set v1 weights (see Read-only config reference below).
          v2 weights are empirically trained against second-opinion labels and stored at
          <code style={{ marginLeft: 4 }}>data/eval/optimised_*_weights_v2.json</code>.
          Flip a toggle to v2 to use the trained weights live — leaderboards re-rank immediately.
          Toggles default v1 so no behaviour changes unless you opt in.
        </div>

        <ToggleRow
          label="Struggle weights"
          options={[
            { id: 'v1', label: 'Hand-set (v1)' },
            { id: 'v2', label: 'Optimised (v2)' },
          ]}
          active={data.runtime.struggle_weights_version}
          onChange={(v) => update({ struggle_weights_version: v })}
        />
        {data.runtime.struggle_weights_version === 'v2' && (
          <V2InfoBlock kind="ok">
            v2 trained via ordinary least-squares linear regression with session-grouped 5-fold CV
            — held-out Spearman ρ = +0.588 [+0.490, +0.686] against the LLM's 4-band rating
            (v1 baseline ρ = +0.471, rater upgraded to gpt-4o on 2026-05-26).
            <strong>Deployment-ready.</strong>
          </V2InfoBlock>
        )}

        <ToggleRow
          label="Difficulty weights"
          options={[
            { id: 'v1', label: 'Hand-set (v1)' },
            { id: 'v2', label: 'Optimised (v2)' },
          ]}
          active={data.runtime.difficulty_weights_version}
          onChange={(v) => update({ difficulty_weights_version: v })}
        />
        {data.runtime.difficulty_weights_version === 'v2' && (
          <V2InfoBlock kind="ok">
            v2 trained via ordinary least-squares linear regression on LOO CV — pooled
            Spearman ρ = +0.468 against the LLM's 4-band rating (v1 baseline near-flat).
            Substantial moderate-positive correlation under the upgraded gpt-4o rater
            (2026-05-26); previously +0.287 under gpt-4o-mini — a +0.18 ρ gain from rater
            upgrade alone. N=72 with heavily skewed "Very Hard" cohort still constrains
            absolute ρ but no longer dominates the ceiling.
            <strong> Deployment-ready.</strong>
          </V2InfoBlock>
        )}
        {data.runtime.difficulty_model === 'irt' && (
          <V2InfoBlock kind="info">
            Difficulty model is set to IRT, which bypasses the weights entirely.
            The v1/v2 toggle above has no effect until you switch the difficulty model back to
            "Baseline".
          </V2InfoBlock>
        )}

        <ToggleRow
          label="Improved-struggle blend"
          options={[
            { id: 'v1', label: 'Hand-set (v1)' },
            { id: 'v2', label: 'Optimised (v2)' },
          ]}
          active={data.runtime.improved_struggle_weights_version}
          onChange={(v) => update({ improved_struggle_weights_version: v })}
        />
        {data.runtime.improved_struggle_weights_version === 'v2' && (
          <V2InfoBlock kind="ok">
            v2 trained via ordinary least-squares linear regression with session-grouped 5-fold CV
            — held-out Spearman ρ = +0.201 [+0.047, +0.356] against the LLM's 4-band rating.
            Under the upgraded gpt-4o rater (2026-05-26) the v2 weights now match the
            non-linear RandomForest ceiling (+0.202) found in a model-class bake-off, suggesting
            OLS reaches the achievable ceiling on these features. Trained weights still assign
            NEGATIVE values to w_M (mastery-gap) and w_D (IRT-adjusted exposure). v2 outranks v1,
            but the improved-struggle model overall is still much weaker than the seven-signal
            struggle model alone (ρ +0.588). <strong>If you want best rank quality, leave the
            Struggle Model selector on "Baseline" rather than switching to "Improved".</strong>
          </V2InfoBlock>
        )}
        {data.runtime.struggle_model !== 'improved' && (
          <V2InfoBlock kind="info">
            Improved-struggle weights only apply when "Struggle model" (above) is set to
            "Improved". Flip the model first.
          </V2InfoBlock>
        )}

        <ToggleRow
          label="Scalar hyperparams (CF τ, K, BKT priors)"
          options={[
            { id: 'v1', label: 'Defaults (v1)' },
            { id: 'v2', label: 'Optimised (v2)' },
          ]}
          active={data.runtime.hyperparams_version}
          onChange={(v) => update({ hyperparams_version: v })}
        />
        {data.runtime.hyperparams_version === 'v1' && (
          <V2InfoBlock kind="info">
            v1 defaults: shrinkage K = 5, CF threshold τ = 0.7. Flip to v2 to apply the
            Optuna-tuned values from{' '}
            <code>data/eval/optimised_hyperparams_v2.json</code>.
          </V2InfoBlock>
        )}
        {data.runtime.hyperparams_version === 'v2' && (
          <V2InfoBlock kind="ok">
            v2 hyperparameters tuned via Optuna TPE (50 trials per parameter, session-grouped
            5-fold CV against the LLM's 4-band rating; gpt-4o labels). <strong>CF threshold τ:</strong>
            v1=0.7 → v2=0.900 (Δ ρ = +0.160, substantial gain — v1's τ was too permissive,
            optimum still at the upper boundary of the [0.4, 0.9] search range).
            <strong>Shrinkage K:</strong> v1=5 → v2=0 (Δ ρ = +0.009, within fold-variance noise
            — either value is defensible). BKT priors and BKT mastery threshold are not tuned in
            v2 and stay at their v1 defaults.
          </V2InfoBlock>
        )}
      </AnimatedCard>

      {/* Read-only config reference (unchanged from Phase 3) */}
      <AnimatedCard variants={fadeUp} style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={3}>Read-only config reference</SectionLabel>
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

function DemoLabSection({ n }: { n: number }) {
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
      <SectionLabel n={n}>Demo Lab</SectionLabel>
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

function V2InfoBlock({
  kind,
  children,
}: {
  kind: 'ok' | 'warn' | 'info'
  children: React.ReactNode
}) {
  // Three muted variants so the per-toggle annotation is unambiguous
  // (warn = red-ish) but doesn't shout (the page already has a lot going
  // on). 'ok' = deployment-ready v2, 'warn' = a problem the user should
  // see before flipping the toggle, 'info' = neutral context.
  const color = kind === 'warn' ? T.danger : kind === 'ok' ? T.accent : T.ink3
  const border = kind === 'warn' ? T.danger : T.line2
  return (
    <div
      style={{
        marginTop: 6,
        marginBottom: 4,
        padding: '8px 12px',
        borderLeft: `2px solid ${border}`,
        fontFamily: T.fMono,
        fontSize: 10.5,
        color,
        background: T.bg2,
        lineHeight: 1.55,
      }}
    >
      {children}
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
