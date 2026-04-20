/** Thin fetch wrapper. Same-origin in prod (FastAPI serves dist/); Vite proxies /api → :8000 in dev. */

const BASE = '/api'
const DEFAULT_TIMEOUT_MS = 30_000

export class ApiError extends Error {
  readonly status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

function combineSignals(external?: AbortSignal): AbortSignal {
  const timeout = AbortSignal.timeout(DEFAULT_TIMEOUT_MS)
  if (!external) return timeout
  // AbortSignal.any is available in modern browsers; fall back to manual plumb.
  if (typeof (AbortSignal as { any?: (s: AbortSignal[]) => AbortSignal }).any === 'function') {
    return (AbortSignal as { any: (s: AbortSignal[]) => AbortSignal }).any([external, timeout])
  }
  const ac = new AbortController()
  const onAbort = () => ac.abort()
  external.addEventListener('abort', onAbort, { once: true })
  timeout.addEventListener('abort', onAbort, { once: true })
  return ac.signal
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  signal?: AbortSignal,
): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: combineSignals(signal),
    })
  } catch (e: unknown) {
    // Normalize AbortError / TimeoutError so callers can detect it.
    if (e instanceof DOMException && (e.name === 'AbortError' || e.name === 'TimeoutError')) {
      if (signal?.aborted) throw e  // upstream cancellation — let callers filter
      throw new ApiError(0, `Request timed out after ${DEFAULT_TIMEOUT_MS / 1000}s`)
    }
    throw e
  }
  if (!res.ok) {
    let detail: string
    try {
      detail = (await res.json())?.detail ?? res.statusText
    } catch {
      detail = res.statusText
    }
    throw new ApiError(res.status, detail)
  }
  return res.json() as Promise<T>
}

export const api = {
  get: <T>(path: string, signal?: AbortSignal) => request<T>('GET', path, undefined, signal),
  post: <T>(path: string, body?: unknown, signal?: AbortSignal) =>
    request<T>('POST', path, body, signal),
}
