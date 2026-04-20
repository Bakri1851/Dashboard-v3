import { useEffect, useRef, useState } from 'react'
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
    // Drop after 30s so a delayed mount still gets fresh-ish data, and so
    // the map doesn't leak across long-lived tabs.
    setTimeout(() => {
      if (inflight.get(path) === p) inflight.delete(path)
    }, 30_000)
  })
  inflight.set(path, p)
  return p as Promise<T>
}

/**
 * Fetch `path` once on mount (+ optional poll at `intervalMs`).
 *
 * `query` is an optional URL query-string fragment (without the leading `?`)
 * — typically produced by `filterToQuery(resolveFilter(...))`. Changing it
 * triggers a refetch and invalidates the cached response.
 *
 * On the first run for a given `fullPath`, an in-flight promise from
 * `prefetchApi()` is adopted if present — subsequent polls bypass the cache.
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
  const aborted = useRef(false)

  const skip = !path
  const fullPath = skip ? '' : query ? `${path}${path.includes('?') ? '&' : '?'}${query}` : path

  useEffect(() => {
    aborted.current = false
    let cancel = false
    if (skip) {
      setData(null)
      setError(null)
      setLoading(false)
      return
    }
    setData(null)
    setError(null)
    setLoading(true)

    let firstRun = true
    const run = () => {
      const prefetched = firstRun ? (inflight.get(fullPath) as Promise<T> | undefined) : undefined
      firstRun = false
      const promise = prefetched ?? api.get<T>(fullPath)
      promise
        .then((payload) => {
          if (cancel || aborted.current) return
          setData(payload)
          setError(null)
          setLoading(false)
        })
        .catch((e: unknown) => {
          if (cancel || aborted.current) return
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
      cancel = true
      aborted.current = true
      if (timer) window.clearInterval(timer)
    }
  }, [fullPath, intervalMs, tick, skip])

  return { data, error, loading, refetch: () => setTick((x) => x + 1) }
}
