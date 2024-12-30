import { useState } from 'react'
import FormGrouping from '../FormGrouping.tsx'
import TimeTextfields from './TimeTextfields.tsx'

export default function ExpirationIntervalForm() {
  const [expirationIntervalEnabled, setExpirationIntervalEnabled] = useState<boolean>(false)

  return (
    <FormGrouping
      checked={expirationIntervalEnabled}
      onChange={setExpirationIntervalEnabled}
      title="Account expiration (Optional)"
      subtitle="Determines after what period of time since the last successful login the account should be marked as expired."
    >
      <TimeTextfields value={0} />

    </FormGrouping>

  )
}
