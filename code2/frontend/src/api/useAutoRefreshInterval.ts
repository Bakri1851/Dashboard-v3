import { useSettings } from './useSettings'

/**
 * Returns the effective polling interval (ms) honouring the Settings
 * auto_refresh toggle and refresh_interval dropdown. Falls back to
 * `fallbackMs` while settings are still loading so first-paint polling
 * behaves the same as the hardcoded literal did before.
 *
 * A return value of 0 disables polling — `useApiData` treats 0/undefined
 * as "fetch once, no interval" (see hooks.ts).
 */
export function useAutoRefreshInterval(fallbackMs: number): number {
  const { data: settings } = useSettings()
  if (!settings) return fallbackMs
  if (!settings.runtime.auto_refresh) return 0
  return settings.runtime.refresh_interval * 1000
}
