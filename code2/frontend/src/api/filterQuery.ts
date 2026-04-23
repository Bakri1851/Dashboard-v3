import { useEffect, useMemo, useState } from 'react'
import { useApiData } from './hooks'
import { filterToQuery, resolveFilter, useFilterStore } from '../state/filterStore'
import type { AcademicPeriod, LabState } from '../types/api'

/**
 * Combine the current filter selection with the live lab-session state +
 * academic calendar metadata into a query string ready to append to any
 * data-returning `/api/*` URL.
 *
 * Consumers: `const q = useFilterQuery(); useApiData('/live', 10000, q)`
 */
export function useFilterQuery(): string {
  const filter = useFilterStore()
  // Lab state is cheap — we piggy-back off the already-polled endpoint.
  const { data: lab } = useApiData<LabState>('/lab/state', 30_000)
  const { data: periods } = useApiData<AcademicPeriod[]>('/meta/academic-periods', 0)

  // `resolveFilter` calls `new Date()` internally for time-relative presets
  // (today, past_hour, past_24h, current_week, current_month, live). Without
  // a ticking dependency the window freezes at mount and silently drops any
  // submission newer than "now at mount" — Streamlit doesn't have this bug
  // because Streamlit re-runs top-to-bottom on every auto-refresh tick.
  // 60s cadence matches the default refresh_interval; ticking faster than
  // the compute cost causes cache-key thrash and _struggle_lock contention.
  const [tick, setTick] = useState(0)
  useEffect(() => {
    const id = window.setInterval(() => setTick((x) => x + 1), 60_000)
    return () => window.clearInterval(id)
  }, [])

  return useMemo(() => {
    const resolved = resolveFilter(filter, {
      labSessionStart: lab?.session_start ?? null,
      academicPeriods: periods ?? undefined,
    })
    return filterToQuery(resolved)
  }, [
    filter.preset,
    filter.customFrom,
    filter.customTo,
    filter.timeStart,
    filter.timeEnd,
    filter.academicWeek,
    lab?.session_start,
    periods,
    tick,
  ])
}
