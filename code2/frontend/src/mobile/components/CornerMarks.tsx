import { T } from '../../theme/tokens'

/** Four corner ticks that frame the hero student card. Pure decoration. */
export function CornerMarks({ color }: { color?: string }) {
  const c = color ?? T.accent
  const sz = 8
  const base = {
    position: 'absolute' as const,
    width: sz,
    height: sz,
    borderColor: c,
    borderStyle: 'solid' as const,
  }
  return (
    <>
      <span style={{ ...base, top: -1, left: -1, borderWidth: '1px 0 0 1px' }} />
      <span style={{ ...base, top: -1, right: -1, borderWidth: '1px 1px 0 0' }} />
      <span style={{ ...base, bottom: -1, left: -1, borderWidth: '0 0 1px 1px' }} />
      <span style={{ ...base, bottom: -1, right: -1, borderWidth: '0 1px 1px 0' }} />
    </>
  )
}
