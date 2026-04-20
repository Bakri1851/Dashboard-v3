import { create } from 'zustand'

export type FilterPreset =
  | 'all'
  | 'live'
  | 'today'
  | 'past_hour'
  | 'past_24h'
  | 'current_week'
  | 'last_week'
  | 'current_month'
  | 'custom'

export interface FilterState {
  preset: FilterPreset
  customFrom: string | null        // YYYY-MM-DD
  customTo: string | null          // YYYY-MM-DD
  timeStart: string                // HH:MM — applied to customFrom
  timeEnd: string                  // HH:MM — applied to customTo
  academicWeek: string | null      // label string from /api/meta/academic-periods
  /** True once InClassView has auto-switched from 'today' to 'all' because
   *  today returned no records. Prevents ping-ponging between the two. */
  autoFallbackApplied: boolean
  setPreset: (p: FilterPreset) => void
  setCustom: (from: string | null, to: string | null) => void
  setTimes: (start: string, end: string) => void
  setAcademicWeek: (label: string | null) => void
  setAutoFallbackApplied: (v: boolean) => void
  reset: () => void
}

export const useFilterStore = create<FilterState>((set) => ({
  preset: 'today',
  customFrom: null,
  customTo: null,
  timeStart: '00:00',
  timeEnd: '23:59',
  academicWeek: null,
  autoFallbackApplied: false,
  setPreset: (preset) =>
    // Re-arm the fallback when picking 'today' so an empty today can fall
    // back to 'all' again on the next /live tick.
    set(preset === 'today' ? { preset, autoFallbackApplied: false } : { preset }),
  setCustom: (customFrom, customTo) => set({ customFrom, customTo, preset: 'custom' }),
  setTimes: (timeStart, timeEnd) => set({ timeStart, timeEnd }),
  setAcademicWeek: (academicWeek) =>
    set({ academicWeek, preset: academicWeek ? 'custom' : 'all' }),
  setAutoFallbackApplied: (autoFallbackApplied) => set({ autoFallbackApplied }),
  reset: () =>
    set({
      preset: 'all',
      customFrom: null,
      customTo: null,
      timeStart: '00:00',
      timeEnd: '23:59',
      academicWeek: null,
      autoFallbackApplied: false,
    }),
}))

/**
 * Map the current filter selection to ISO-8601 `from`/`to` strings for the
 * backend. Returns `{from: null, to: null}` for "all" which means no
 * filtering. `labSessionStart` (from `/api/lab/state`) is used by the "live"
 * preset.
 */
export interface ResolvedWindow {
  from: string | null
  to: string | null
}

export function resolveFilter(
  state: Pick<FilterState, 'preset' | 'customFrom' | 'customTo' | 'timeStart' | 'timeEnd' | 'academicWeek'>,
  ctx: { labSessionStart?: string | null; academicPeriods?: { label: string; start_date: string; end_date: string }[] } = {}
): ResolvedWindow {
  const now = new Date()

  const startOf = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0, 0)
  const isoUtc = (d: Date) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString()

  switch (state.preset) {
    case 'all':
      return { from: null, to: null }
    case 'live': {
      const from = ctx.labSessionStart ?? null
      return { from: from ? new Date(from).toISOString() : null, to: now.toISOString() }
    }
    case 'today':
      return { from: isoUtc(startOf(now)), to: now.toISOString() }
    case 'past_hour':
      return { from: new Date(now.getTime() - 60 * 60 * 1000).toISOString(), to: now.toISOString() }
    case 'past_24h':
      return { from: new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString(), to: now.toISOString() }
    case 'current_week': {
      const day = now.getDay() || 7            // Mon=1…Sun=7
      const monday = startOf(now)
      monday.setDate(monday.getDate() - (day - 1))
      return { from: isoUtc(monday), to: now.toISOString() }
    }
    case 'last_week': {
      const day = now.getDay() || 7
      const lastMonday = startOf(now)
      lastMonday.setDate(lastMonday.getDate() - (day - 1) - 7)
      const lastSunday = new Date(lastMonday)
      lastSunday.setDate(lastSunday.getDate() + 7)
      lastSunday.setMilliseconds(-1)
      return { from: isoUtc(lastMonday), to: isoUtc(lastSunday) }
    }
    case 'current_month': {
      const first = new Date(now.getFullYear(), now.getMonth(), 1)
      return { from: isoUtc(first), to: now.toISOString() }
    }
    case 'custom': {
      // Academic week picker takes precedence over manual date range.
      if (state.academicWeek && ctx.academicPeriods) {
        const p = ctx.academicPeriods.find((x) => x.label === state.academicWeek)
        if (p) {
          return {
            from: new Date(`${p.start_date}T00:00:00`).toISOString(),
            to: new Date(`${p.end_date}T23:59:59`).toISOString(),
          }
        }
      }
      const from = state.customFrom
        ? new Date(`${state.customFrom}T${state.timeStart || '00:00'}:00`).toISOString()
        : null
      const to = state.customTo
        ? new Date(`${state.customTo}T${state.timeEnd || '23:59'}:59`).toISOString()
        : null
      return { from, to }
    }
    default:
      return { from: null, to: null }
  }
}

/** Lowercase human-readable label for the current filter preset. Used by
 *  stat/metric tiles whose value is scoped to the active time window, so the
 *  caption accurately describes the window rather than hardcoding "all time".
 */
const PRESET_NOTE: Record<FilterPreset, string> = {
  all: 'all time',
  live: 'live session',
  today: 'today',
  past_hour: 'past hour',
  past_24h: 'past 24h',
  current_week: 'current week',
  last_week: 'last week',
  current_month: 'current month',
  custom: 'custom range',
}

export function presetNote(preset: FilterPreset): string {
  return PRESET_NOTE[preset] ?? 'filtered'
}

/** Serialise a ResolvedWindow into URLSearchParams form (no leading `?`). */
export function filterToQuery(window: ResolvedWindow): string {
  const p = new URLSearchParams()
  if (window.from) p.set('from', window.from)
  if (window.to) p.set('to', window.to)
  const q = p.toString()
  return q
}
