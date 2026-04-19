import { useEffect, useRef, useState } from 'react'
import { api, ApiError } from './client'

export interface ApiState<T> {
  data: T | null
  error: string | null
  loading: boolean
  /** Force a refetch. */
  refetch: () => void
}

/**
 * Fetch `path` once on mount and poll every `intervalMs` if given.
 * Swallows errors into the `error` field rather than throwing, so views render.
 */
export function useApiData<T>(path: string, intervalMs?: number): ApiState<T> {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [tick, setTick] = useState(0)
  const aborted = useRef(false)

  useEffect(() => {
    aborted.current = false
    let cancel = false

    const run = () => {
      api
        .get<T>(path)
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
  }, [path, intervalMs, tick])

  return { data, error, loading, refetch: () => setTick((x) => x + 1) }
}
