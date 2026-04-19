import { useMemo } from 'react'
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
  ])
}
