import type { ReactNode } from 'react'
import { T } from '../../theme/tokens'

/** Numbered section header — e.g. "(1) Struggle Distribution". */
export function SectionLabel({ n, children }: { n: number; children: ReactNode }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        marginBottom: 14,
      }}
    >
      <span
        style={{
          fontFamily: T.fMono,
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 1.4,
        }}
      >
        {String(n).padStart(2, '0')}
      </span>
      <span
        style={{
          fontFamily: T.fSerif,
          fontSize: 14,
          color: T.ink,
          fontWeight: 500,
        }}
      >
        {children}
      </span>
    </div>
  )
}
