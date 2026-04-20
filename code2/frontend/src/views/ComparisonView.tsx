import { useState } from 'react'
import { T, LEVEL_STYLES } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import { useFilterQuery } from '../api/filterQuery'
import type {
  AgreementSummary,
  ModelCompareResponse,
  ModelPairRow,
  ModelRow,
} from '../types/api'
import { Pill } from '../components/primitives/Pill'
import { ScoreBar } from '../components/primitives/ScoreBar'
import { SectionLabel } from '../components/primitives/SectionLabel'
import { ScatterChart } from '../components/charts/ScatterChart'

type CmpTab = 'struggle' | 'difficulty'

export function ComparisonView() {
  const q = useFilterQuery()
  const { data, error, loading } = useApiData<ModelCompareResponse>('/models/compare', 120_000, q)
  const [tab, setTab] = useState<CmpTab>('struggle')

  return (
    <div style={{ padding: '20px 28px', display: 'flex', flexDirection: 'column', gap: 20 }}>
      {loading && !data && (
        <div style={{ color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>loading model comparison…</div>
      )}
      {error && <div style={{ color: T.danger, fontFamily: T.fMono, fontSize: 11 }}>{error}</div>}

      {data && (
        <>
          <TabSwitcher tab={tab} setTab={setTab} difficultyAvailable={!!data.difficulty} />

          {tab === 'struggle' && (
            <ComparisonSection
              title="Student Struggle"
              entityLabel="Student"
              baselineTitle="Baseline Struggle"
              baselineFormula="S = 0.10·n̂ + 0.10·t̂ + 0.20·ī + 0.10·r̂ + 0.38·A + 0.05·d̂ + 0.07·rep̂"
              improvedTitle="Improved (BKT + IRT-weighted)"
              improvedFormula="S = 0.45·behavioural + 0.30·(1 − mastery) + 0.25·difficulty_adj"
              baseline={data.baseline}
              improved={data.improved}
              baselineEmptyMessage="No students in the current window."
              improvedEmptyMessage="Improved struggle not available — BKT needs at least 50 scored attempts with both correct and incorrect responses."
              pairs={data.pairs}
              agreement={data.agreement}
              spearmanRho={data.spearman_rho}
              top10Overlap={data.top10_overlap}
            />
          )}

          {tab === 'difficulty' && data.difficulty && (
            <ComparisonSection
              title="Question Difficulty"
              entityLabel="Question"
              baselineTitle="Baseline Difficulty"
              baselineFormula="D = 0.28·c + 0.12·t̂ + 0.20·Â + 0.20·f̂ + 0.20·p"
              improvedTitle="IRT (Rasch) Difficulty"
              improvedFormula="D = σ(b̂_i) where b̂_i comes from a fitted 1PL/Rasch model"
              baseline={data.difficulty.baseline}
              improved={data.difficulty.improved}
              baselineEmptyMessage="No questions in the current window."
              improvedEmptyMessage="IRT Rasch fit not available — needs ≥2 students and ≥2 questions with both correct and incorrect responses after sparse-attempt filtering."
              pairs={data.difficulty.pairs}
              agreement={data.difficulty.agreement}
              spearmanRho={data.difficulty.spearman_rho}
              top10Overlap={data.difficulty.top10_overlap}
            />
          )}

          <div style={{ marginTop: 4, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, lineHeight: 1.6 }}>
            Both comparisons operate on the same cached DataFrame. Baseline weights are in{' '}
            <code style={{ background: T.bg2, padding: '1px 4px' }}>config.STRUGGLE_WEIGHT_*</code>
            {' '}/{' '}
            <code style={{ background: T.bg2, padding: '1px 4px' }}>config.DIFFICULTY_WEIGHT_*</code>; the
            improved struggle model layers BKT mastery + IRT difficulty adjustment on top, and the
            IRT difficulty score is σ(b̂_i) from a Rasch fit.
          </div>
        </>
      )}
    </div>
  )
}

function TabSwitcher({
  tab,
  setTab,
  difficultyAvailable,
}: {
  tab: CmpTab
  setTab: (t: CmpTab) => void
  difficultyAvailable: boolean
}) {
  const tabs: { id: CmpTab; label: string; disabled?: boolean }[] = [
    { id: 'struggle', label: 'Student Struggle' },
    { id: 'difficulty', label: 'Question Difficulty', disabled: !difficultyAvailable },
  ]
  return (
    <div style={{ display: 'flex', gap: 8, borderBottom: `1px solid ${T.line}` }}>
      {tabs.map((t) => {
        const active = tab === t.id
        return (
          <button
            key={t.id}
            onClick={() => !t.disabled && setTab(t.id)}
            disabled={t.disabled}
            style={{
              padding: '10px 18px',
              background: 'transparent',
              color: t.disabled ? T.ink3 : active ? T.ink : T.ink2,
              border: 'none',
              borderBottom: active ? `2px solid ${T.accent}` : '2px solid transparent',
              marginBottom: -1,
              fontFamily: T.fMono,
              fontSize: 11,
              letterSpacing: 1.2,
              textTransform: 'uppercase',
              cursor: t.disabled ? 'not-allowed' : 'pointer',
              opacity: t.disabled ? 0.5 : 1,
            }}
            title={t.disabled ? 'Difficulty comparison not available — IRT fit did not converge' : undefined}
          >
            {t.label}
          </button>
        )
      })}
    </div>
  )
}

interface ComparisonSectionProps {
  title: string
  entityLabel: string
  baselineTitle: string
  baselineFormula: string
  improvedTitle: string
  improvedFormula: string
  baseline: ModelRow[]
  improved: ModelRow[]
  baselineEmptyMessage: string
  improvedEmptyMessage: string
  pairs: ModelPairRow[]
  agreement: AgreementSummary | null
  spearmanRho: number | null
  top10Overlap: number | null
}

function ComparisonSection({
  title,
  entityLabel,
  baselineTitle,
  baselineFormula,
  improvedTitle,
  improvedFormula,
  baseline,
  improved,
  baselineEmptyMessage,
  improvedEmptyMessage,
  pairs,
  agreement,
  spearmanRho,
  top10Overlap,
}: ComparisonSectionProps) {
  const metrics: { label: string; value: string; accent: string; note?: string }[] = []
  if (agreement) {
    metrics.push(
      { label: 'Agreement', value: `${agreement.agreement_pct.toFixed(1)}%`, accent: T.ok },
      { label: 'Upgraded', value: String(agreement.upgraded), accent: T.warn },
      { label: 'Downgraded', value: String(agreement.downgraded), accent: T.accent },
      { label: 'Unchanged', value: String(agreement.unchanged), accent: T.ink2 },
    )
  }
  metrics.push(
    { label: 'Spearman ρ', value: spearmanRho == null ? '—' : spearmanRho.toFixed(2), accent: T.accent, note: 'rank corr' },
    {
      label: 'Top-10 overlap',
      value: top10Overlap == null ? '—' : `${Math.round(top10Overlap * 100)}%`,
      accent: T.accent,
      note: 'same flagged',
    },
  )

  return (
    <section style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ fontFamily: T.fSerif, fontSize: 22, color: T.ink }}>{title}</div>

      {/* Side-by-side top-10 leaderboards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 16 }}>
        <ModelCard title={baselineTitle} formula={baselineFormula} rows={baseline} emptyMessage={baselineEmptyMessage} />
        <ModelCard title={improvedTitle} formula={improvedFormula} rows={improved} emptyMessage={improvedEmptyMessage} />
      </div>

      {/* Compact stats strip — agreement + rank concordance together */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${metrics.length}, minmax(0, 1fr))`,
          gap: 8,
          padding: '14px 16px',
          background: T.card,
          border: `1px solid ${T.line}`,
        }}
      >
        {metrics.map((m) => (
          <MiniStat key={m.label} label={m.label} value={m.value} accent={m.accent} note={m.note} />
        ))}
      </div>

      {/* Scatter + disagreements side-by-side on wide screens */}
      {pairs.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 440px) minmax(0, 1fr)', gap: 16 }}>
          <div style={{ padding: '14px 16px', background: T.card, border: `1px solid ${T.line}` }}>
            <SectionLabel n={1}>Score Scatter</SectionLabel>
            <div style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, marginBottom: 6 }}>
              baseline (x) vs improved (y) · dashed line = perfect agreement
            </div>
            <ScatterChart
              points={pairs.map((p) => ({ x: p.baseline_score, y: p.improved_score, id: p.id }))}
              xLabel="baseline"
              yLabel="improved"
              maxWidth={420}
              height={300}
            />
          </div>
          <PairsTable pairs={pairs} entityLabel={entityLabel} />
        </div>
      )}
    </section>
  )
}

function MiniStat({ label, value, accent, note }: { label: string; value: string; accent: string; note?: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 2, minWidth: 0 }}>
      <div
        style={{
          fontFamily: T.fMono,
          fontSize: 9.5,
          letterSpacing: 1.1,
          textTransform: 'uppercase',
          color: T.ink3,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontFamily: T.fSerif,
          fontSize: 26,
          lineHeight: 1,
          color: accent,
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {value}
      </div>
      {note && (
        <div style={{ fontFamily: T.fMono, fontSize: 9.5, color: T.ink3, whiteSpace: 'nowrap' }}>{note}</div>
      )}
    </div>
  )
}

function ModelCard({
  title,
  formula,
  rows,
  emptyMessage,
}: {
  title: string
  formula: string
  rows: ModelRow[]
  emptyMessage: string
}) {
  return (
    <div style={{ background: T.card, border: `1px solid ${T.line}` }}>
      <div style={{ padding: '18px 22px', borderBottom: `1px solid ${T.line}` }}>
        <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>{title}</div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 6, lineHeight: 1.5 }}>{formula}</div>
      </div>
      {rows.length === 0 ? (
        <div style={{ padding: '20px 22px', fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>
          {emptyMessage}
        </div>
      ) : (
        rows.map((r, i) => (
          <div
            key={`${r.id}-${i}`}
            style={{
              padding: '10px 22px',
              borderBottom: i < rows.length - 1 ? `1px solid ${T.line2}` : 'none',
              display: 'grid',
              gridTemplateColumns: '28px 1fr auto 100px 56px',
              gap: 12,
              alignItems: 'center',
            }}
          >
            <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>{String(i + 1).padStart(2, '0')}</span>
            <span style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink }}>{r.id}</span>
            <Pill level={r.level} />
            <ScoreBar value={r.score} color={LEVEL_STYLES[r.level]?.fg ?? T.ink} height={3} width={100} />
            <span style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink, fontVariantNumeric: 'tabular-nums', textAlign: 'right' }}>
              {r.score.toFixed(2)}
            </span>
          </div>
        ))
      )}
    </div>
  )
}

function PairsTable({ pairs, entityLabel }: { pairs: ModelPairRow[]; entityLabel: string }) {
  const [showAll, setShowAll] = useState(false)
  const shown = showAll ? pairs : pairs.slice(0, 10)
  return (
    <div style={{ background: T.card, border: `1px solid ${T.line}` }}>
      <div
        style={{
          padding: '18px 22px',
          borderBottom: `1px solid ${T.line}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
        }}
      >
        <div>
          <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>Biggest Disagreements</div>
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>
            sorted by |Δ| · showing {shown.length} of {pairs.length}
          </div>
        </div>
        {pairs.length > 10 && (
          <button
            onClick={() => setShowAll((s) => !s)}
            style={{
              padding: '6px 12px',
              background: 'transparent',
              color: T.ink2,
              border: `1px solid ${T.line}`,
              fontFamily: T.fMono,
              fontSize: 10.5,
              letterSpacing: 1,
              textTransform: 'uppercase',
              cursor: 'pointer',
            }}
          >
            {showAll ? 'Show top 10' : `Show all ${pairs.length}`}
          </button>
        )}
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 80px 1fr 80px 80px',
          gap: 12,
          padding: '10px 22px',
          borderBottom: `1px solid ${T.line2}`,
          fontFamily: T.fMono,
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 1.2,
          textTransform: 'uppercase',
        }}
      >
        <span>{entityLabel}</span>
        <span>Baseline</span>
        <span style={{ textAlign: 'right' }}>Score</span>
        <span>Improved</span>
        <span style={{ textAlign: 'right' }}>Score</span>
        <span style={{ textAlign: 'right' }}>Δ</span>
      </div>
      {shown.map((p, i) => {
        const deltaColor = p.delta > 0 ? T.danger : p.delta < 0 ? T.ok : T.ink2
        return (
          <div
            key={`${p.id}-${i}`}
            style={{
              padding: '10px 22px',
              borderBottom: i < shown.length - 1 ? `1px solid ${T.line2}` : 'none',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr 80px 1fr 80px 80px',
              gap: 12,
              alignItems: 'center',
              fontFamily: T.fMono,
              fontSize: 12,
              color: T.ink,
            }}
          >
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {p.id}
            </span>
            <Pill level={p.baseline_level} />
            <span style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>
              {p.baseline_score.toFixed(2)}
            </span>
            <Pill level={p.improved_level} />
            <span style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>
              {p.improved_score.toFixed(2)}
            </span>
            <span
              style={{
                textAlign: 'right',
                color: deltaColor,
                fontVariantNumeric: 'tabular-nums',
                fontWeight: 500,
              }}
            >
              {p.delta > 0 ? '+' : ''}
              {p.delta.toFixed(2)}
            </span>
          </div>
        )
      })}
    </div>
  )
}
