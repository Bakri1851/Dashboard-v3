import { T } from '../../theme/tokens'

/** Inline sparkline — given y-values in 0..1, draws a line (optionally filled). */
export function Spark({
  data,
  width = 240,
  height = 70,
  color = T.ink,
  fill = false,
}: {
  data: number[]
  width?: number
  height?: number
  color?: string
  fill?: boolean
}) {
  if (data.length === 0) {
    return <div style={{ width, height, color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>no data</div>
  }
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const stepX = width / Math.max(data.length - 1, 1)
  const yOf = (v: number) => height - ((v - min) / range) * height

  let path = ''
  data.forEach((v, i) => {
    const x = i * stepX
    const y = yOf(v)
    path += (i === 0 ? 'M' : 'L') + x.toFixed(1) + ' ' + y.toFixed(1) + ' '
  })

  const fillPath = fill ? `${path} L ${width.toFixed(1)} ${height} L 0 ${height} Z` : ''

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {fill && <path d={fillPath} fill={color} opacity={0.12} />}
      <path d={path.trim()} stroke={color} strokeWidth={1.5} fill="none" />
      {data.map((v, i) => (
        <circle
          key={i}
          cx={i * stepX}
          cy={yOf(v)}
          r={i === data.length - 1 ? 3 : 1.5}
          fill={color}
        />
      ))}
    </svg>
  )
}
