import type { ChangeWebsite } from '../../activity/model.ts'
import { useState } from 'react'
import TimeTextfields from '../../form/TimeTextfields.tsx'
import FormGrouping from '../FormGrouping.tsx'

interface ExpirationIntervalFormProps {
  value: ChangeWebsite
  onChange?: (value: ChangeWebsite) => void
  loading?: boolean
}

export default function ExpirationIntervalForm(props: ExpirationIntervalFormProps) {
  const { value, onChange, loading } = props
  const [expirationIntervalEnabled, setExpirationIntervalEnabled] = useState<boolean>(value.expiration_interval_minutes !== null)

  function handleEnabledChange(enabled: boolean) {
    setExpirationIntervalEnabled(enabled)
    if (!enabled) {
      onChange?.({
        ...value,
        expiration_interval_minutes: null,
      })
    }
  }

  function validateExpirationInterval(minutes: string): string {
    if (Number(minutes) <= 0) {
      return 'Expiration interval must be greater than 0min.'
    }
    return ''
  }

  return (
    <FormGrouping
      checked={expirationIntervalEnabled}
      disabled={loading}
      onChange={handleEnabledChange}
      title="Account expiration (Optional)"
      subtitle="Determines after what period of time since the last successful login the account should be marked as expired."
    >
      <TimeTextfields
        identifier="expiration-interval"
        loading={loading}
        value={value.expiration_interval_minutes ?? 0}
        onChange={minutes => onChange?.({
          ...value,
          expiration_interval_minutes: minutes,
        })}
        onValidate={validateExpirationInterval}
      />

    </FormGrouping>

  )
}
