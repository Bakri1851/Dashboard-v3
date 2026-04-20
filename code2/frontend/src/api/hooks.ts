import { useEffect, useState } from 'react'
import { api, ApiError } from './client'

export interface ApiState<T> {
  data: T | null
  error: string | null
  loading: boolean
  refetch: () => void
}

// Module-level prefetch map. `prefetchApi(path)` kicks off a fetch and memoises
// the in-flight promise. The first `useApiData` mount for that exact `fullPath`
// adopts the in-flight promise instead of starting a fresh request — letting
// hover-prefetch hide latency for slow endpoints like /rag/*.
const inflight = new Map<string, Promise<unknown>>()

export function prefetchApi<T>(path: string): Promise<T> {
  const existing = inflight.get(path)
  if (existing) return existing as Promise<T>
  const p = api.get<T>(path).finally(() => {
    setTimeout(() => {
      if (inflight.get(path) === p) inflight.delete(path)
    }, 30_000)
  })
  inflight.set(path, p)
  return p as Promise<T>
}

function isAbortError(e: unknown): boolean {
  return e instanceof DOMException && (e.name === 'AbortError' || e.name === 'TimeoutError')
}

/**
 * Fetch `path` once on mount (+ optional poll at `intervalMs`).
 * Uses an AbortController so unmount / dep change cancels the in-flight request
 * and the 30s fetch-level timeout in client.ts bounds any hung response.
 */
export function useApiData<T>(
  path: string,
  intervalMs?: number,
  query?: string
): ApiState<T> {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [tick, setTick] = useState(0)

  const skip = !path
  const fullPath = skip ? '' : query ? `${path}${path.includes('?') ? '&' : '?'}${query}` : path

  useEffect(() => {
    if (skip) {
      setData(null)
      setError(null)
      setLoading(false)
      return
    }
    const ac = new AbortController()
    setData(null)
    setError(null)
    setLoading(true)

    let firstRun = true
    const run = () => {
      if (ac.signal.aborted) return
      const prefetched = firstRun ? (inflight.get(fullPath) as Promise<T> | undefined) : undefined
      firstRun = false
      const promise = prefetched ?? api.get<T>(fullPath, ac.signal)
      promise
        .then((payload) => {
          if (ac.signal.aborted) return
          setData(payload)
          setError(null)
          setLoading(false)
        })
        .catch((e: unknown) => {
          if (ac.signal.aborted || isAbortError(e)) return
          setError(e instanceof ApiError ? `${e.status}: ${e.message}` : String(e))
          setLoading(false)
        })
    }

    run()
    let timer: number | undefined
    if (intervalMs && intervalMs > 0) {
      timer = window.setInterval(run, intervalMs)
    }
    return () => {
      ac.abort()
      if (timer) window.clearInterval(timer)
    }
  }, [fullPath, intervalMs, tick, skip])

  return { data, error, loading, refetch: () => setTick((x) => x + 1) }
}
