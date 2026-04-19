import { useCallback } from 'react'
import { useApiData } from './hooks'
import { api } from './client'
import type { RuntimeSettings, Settings } from '../types/api'

/**
 * Hook wrapping `/api/settings`. Returns the current settings + helpers to
 * mutate them. Every mutation POSTs a partial dict to the backend and
 * refetches — the backend flushes analytics caches on every update so the
 * next `/api/live` / `/api/struggle` call reflects the new flags.
 */
export function useSettings() {
  const { data, error, loading, refetch } = useApiData<Settings>('/settings', 0)

  const update = useCallback(
    async (patch: Partial<RuntimeSettings & { [key: string]: unknown }>) => {
      try {
        await api.post('/settings', patch)
      } catch (e) {
        console.error('settings update failed:', e)
      } finally {
        refetch()
      }
    },
    [refetch]
  )

  const reset = useCallback(async () => {
    if (!confirm('Reset all settings to defaults?')) return
    try {
      await api.post('/settings/reset')
    } catch (e) {
      console.error('settings reset failed:', e)
    } finally {
      refetch()
    }
  }, [refetch])

  return { data, error, loading, update, reset }
}
