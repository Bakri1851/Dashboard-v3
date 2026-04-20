import { useEffect, useRef } from 'react'
import { playAssignmentReceived } from '../../sound'

/**
 * Play the assignment-received beep on the None → assigned transition.
 * Mirrors `assistant_app.py` `_prev_assigned_student` logic (lines 487–492):
 * only fires when a new student appears, not on subsequent polls.
 *
 * Gated by `soundsEnabled` (from `/api/settings.runtime.sounds_enabled`).
 */
export function useAssignmentSound(
  assignedStudent: string | null | undefined,
  soundsEnabled: boolean,
): void {
  const prev = useRef<string | null>(null)
  useEffect(() => {
    const curr = assignedStudent ?? null
    if (prev.current == null && curr != null && soundsEnabled) {
      playAssignmentReceived()
    }
    prev.current = curr
  }, [assignedStudent, soundsEnabled])
}
