import type { CSSProperties } from 'react'
import { T } from '../../theme/tokens'

export type SkeletonVariant = 'text' | 'block' | 'circle'

interface Props {
  variant?: SkeletonVariant
  width?: number | string
  height?: number | string
  rows?: number
  radius?: number | string
  style?: CSSProperties
}

/** Shimmer placeholder used while API data loads. Shares `@keyframes pulse`
 *  with RagPanel so every skeleton in the app breathes in lockstep. */
export function Skeleton({ variant = 'text', width, height, rows, radius, style }: Props) {
  if (rows && rows > 1 && variant === 'text') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, ...style }}>
        {Array.from({ length: rows }).map((_, i) => (
          <Bone
            key={i}
            variant="text"
            width={width ?? `${85 - i * 10}%`}
            height={height ?? 12}
            radius={radius ?? 2}
            delay={i * 120}
          />
        ))}
      </div>
    )
  }
  return (
    <Bone
      variant={variant}
      width={width ?? (variant === 'circle' ? 28 : '100%')}
      height={height ?? (variant === 'text' ? 12 : variant === 'circle' ? 28 : 64)}
      radius={
        radius ?? (variant === 'circle' ? '50%' : variant === 'block' ? 4 : 2)
      }
      delay={0}
      style={style}
    />
  )
}

function Bone({
  width,
  height,
  radius,
  delay,
  style,
}: Required<Pick<Props, 'width' | 'height'>> & {
  variant: SkeletonVariant
  radius: number | string
  delay: number
  style?: CSSProperties
}) {
  return (
    <div
      style={{
        width,
        height,
        background: T.line2,
        borderRadius: radius,
        opacity: 0.55,
        animation: 'pulse 1.4s ease-in-out infinite',
        animationDelay: `${delay}ms`,
        ...style,
      }}
    />
  )
}

/** Convenience preset: a row of stat-card skeletons. */
export function SkeletonStatCard({ height = 128 }: { height?: number }) {
  return (
    <div
      style={{
        position: 'relative',
        padding: '20px 22px',
        background: T.card,
        border: `1px solid ${T.line}`,
        minHeight: height,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        gap: 16,
      }}
    >
      <Skeleton variant="text" width="35%" height={10} />
      <Skeleton variant="block" width="60%" height={38} radius={2} />
    </div>
  )
}
