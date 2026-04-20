/**
 * Identity persistence for the lab assistant: the `?aid=` URL query param
 * survives browser refreshes on mobile, mirroring the Streamlit original
 * (`_coerce_query_value` + `st.query_params`).
 */

const QUERY_KEY = 'aid'

function coerce(raw: string | null): string | null {
  if (raw == null) return null
  const trimmed = raw.trim()
  return trimmed.length ? trimmed : null
}

export function readAid(): string | null {
  if (typeof window === 'undefined') return null
  return coerce(new URLSearchParams(window.location.search).get(QUERY_KEY))
}

export function writeAid(aid: string): void {
  const params = new URLSearchParams(window.location.search)
  params.set(QUERY_KEY, aid)
  const qs = params.toString()
  const next = `${window.location.pathname}${qs ? '?' + qs : ''}${window.location.hash}`
  window.history.replaceState(null, '', next)
}

export function clearAid(): void {
  const params = new URLSearchParams(window.location.search)
  params.delete(QUERY_KEY)
  const qs = params.toString()
  const next = `${window.location.pathname}${qs ? '?' + qs : ''}${window.location.hash}`
  window.history.replaceState(null, '', next)
}
