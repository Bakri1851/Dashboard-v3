import { useEffect, useRef, useState } from 'react'
import { api, ApiError } from './client'

export interface ApiState<T> {
  data: T | null
  error: string | null
  loading: boolean
  refetch: () => void
}

/**
 * Fetch `path` once on mount (+ optional poll at `intervalMs`).
 *
 * `query` is an optional URL query-string fragment (without the leading `?`)
 * — typically produced by `filterToQuery(resolveFilter(...))`. Changing it
 * triggers a refetch and invalidates the cached response.
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
      setLoading(false)
      return
    }

    const run = () => {
      api
        .get<T>(fullPath)
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
