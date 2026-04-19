import { T, LEVEL_STYLES } from '../theme/tokens'
import { useApiData } from '../api/hooks'
import { useFilterQuery } from '../api/filterQuery'
import type { ModelCompareResponse, ModelRow } from '../types/api'
import { Pill } from '../components/primitives/Pill'
import { ScoreBar } from '../components/primitives/ScoreBar'
import { Stat } from '../components/primitives/Stat'
import { SectionLabel } from '../components/primitives/SectionLabel'

export function ComparisonView() {
  const q = useFilterQuery()
  const { data, error, loading } = useApiData<ModelCompareResponse>('/models/compare', 120_000, q)

  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}>
      {loading && !data && (
        <div style={{ color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>loading model comparison…</div>
      )}
      {error && <div style={{ color: T.danger, fontFamily: T.fMono, fontSize: 11 }}>{error}</div>}

      {data && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 20 }}>
            <ModelCard
              title="Baseline Struggle"
              formula="S = 0.10·n̂ + 0.10·t̂ + 0.20·ī + 0.10·r̂ + 0.38·A + 0.05·d̂ + 0.07·rep̂"
              rows={data.baseline}
            />
            <ModelCard
              title="Improved (BKT + IRT-weighted)"
              formula="S = 0.45·behavioural + 0.30·(1 − mastery) + 0.25·difficulty_adj"
              rows={data.improved}
            />
          </div>

          <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
            <SectionLabel n={1}>Rank Concordance</SectionLabel>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 16 }}>
              <Stat
                label="Spearman ρ"
                value={data.spearman_rho == null ? '—' : data.spearman_rho.toFixed(2)}
                note="baseline vs improved, full set"
                accent={T.accent}
              />
              <Stat
                label="Top-10 overlap"
                value={data.top10_overlap == null ? '—' : `${Math.round(data.top10_overlap * 100)}%`}
                note="same students flagged by both"
                accent={T.accent}
              />
            </div>
            <div style={{ marginTop: 16, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, lineHeight: 1.6 }}>
              Both models use the same cached DataFrame. Baseline weights are in{' '}
              <code style={{ background: T.bg2, padding: '1px 4px' }}>config.STRUGGLE_WEIGHT_*</code>;
              improved blends BKT mastery gap + IRT difficulty adjustment on top of baseline behavioural features.
            </div>
          </div>
        </>
      )}
    </div>
  )
}

function ModelCard({ title, formula, rows }: { title: string; formula: string; rows: ModelRow[] }) {
  return (
    <div style={{ background: T.card, border: `1px solid ${T.line}` }}>
      <div style={{ padding: '18px 22px', borderBottom: `1px solid ${T.line}` }}>
        <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>{title}</div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 6, lineHeight: 1.5 }}>{formula}</div>
      </div>
      {rows.length === 0 ? (
        <div style={{ padding: '20px 22px', fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>
          Not enough observations — improved model needs at least {50} attempts to fit BKT.
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
