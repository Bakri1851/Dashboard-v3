import { motion } from 'framer-motion'
import { T, LEVEL_STYLES } from '../../theme/tokens'
import { Tooltip } from './Tooltip'

export interface LevelBucket {
  label: string
  count: number
}

/**
 * Compact horizontal strip of level-count chips — one per struggle/difficulty
 * bucket. Colour picked from LEVEL_STYLES so it matches the Pill palette.
 * Empty `buckets` renders nothing (caller can guard on loading state).
 */
export function LevelChips({
  buckets,
  tooltips,
  align = 'left',
}: {
  buckets: LevelBucket[]
  /** Optional per-label hover copy. */
  tooltips?: Partial<Record<string, string>>
  align?: 'left' | 'right'
}) {
  if (!buckets.length) return null
  const total = buckets.reduce((acc, b) => acc + b.count, 0)

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 6,
        justifyContent: align === 'right' ? 'flex-end' : 'flex-start',
        alignItems: 'center',
      }}
    >
      {buckets.map((b, i) => {
        const fg = LEVEL_STYLES[b.label]?.fg ?? T.ink3
        const short = LEVEL_STYLES[b.label]?.label ?? b.label
        const tip = tooltips?.[b.label]
        const chip = (
          <motion.span
            key={b.label}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22, delay: i * 0.04, ease: 'easeOut' }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '4px 10px',
              background: 'transparent',
              border: `1px solid ${fg}`,
              borderRadius: 999,
              fontFamily: T.fMono,
              fontSize: 11,
              color: T.ink,
              letterSpacing: 0.3,
              lineHeight: 1,
            }}
          >
            <span
              aria-hidden
              style={{
                width: 7,
                height: 7,
                borderRadius: '50%',
                background: fg,
                boxShadow: `0 0 6px ${fg}`,
                flexShrink: 0,
              }}
            />
            <span style={{ color: T.ink3, textTransform: 'uppercase', fontSize: 10, letterSpacing: 1 }}>
              {short}
            </span>
            <span style={{ color: fg, fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}>{b.count}</span>
          </motion.span>
        )
        return tip ? (
          <Tooltip key={b.label} content={tip}>
            {chip}
          </Tooltip>
        ) : (
          chip
        )
      })}
      <span
        style={{
          marginLeft: 4,
          fontFamily: T.fMono,
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 1,
          textTransform: 'uppercase',
        }}
      >
        Σ {total}
      </span>
    </div>
  )
}
