import type { ActionInterval } from '../../activity/activityRequests.ts'
import { TimeField } from '@mui/x-date-pickers'
import { useState } from 'react'
import FormGrouping from '../FormGrouping.tsx'
import TimeTextfields from './TimeTextfields.tsx'

interface ActionIntervalFormProps {
  value: ActionInterval
  onChange?: (value: ActionInterval) => void
}

export default function ActionIntervalForm(props: ActionIntervalFormProps) {
  const { value, onChange } = props
  const [timeSpanEnabled, setTimeSpanEnabled] = useState<boolean>(false)
  const [timeOfDayEnabled, setTimeOfDayEnabled] = useState<boolean>(false)

  return (
    <FormGrouping
      subtitle="Defines the interval at which the automatic login should be triggered. For example, if Days=5, an automatic login is performed every 5 days."
      disableCheckbox
      title="Execution Interval *"
      column
    >
      <div className="row">
        <TimeTextfields hoursHelperText="Only allowed when time of day execution is disabled." minutesHelperText="Only allowed when time of day execution is disabled." disableHoursMinutes={timeOfDayEnabled} value={value.date_minutes_start} onChange={minutes => onChange?.({ ...value, date_minutes_start: minutes })} />
      </div>
      <FormGrouping
        elevation={24}
        backgroundElevation={12}
        checked={timeSpanEnabled}
        onChange={setTimeSpanEnabled}
        title="Timespan (Optional)"
        subtitle="Selects a random time within the specified time period. This can be used, to trigger a login on a random day every 10 to 15 days."
      >
        <TimeTextfields hoursHelperText="Only allowed when time of day execution is disabled." minutesHelperText="Only allowed when time of day execution is disabled." disableHoursMinutes={timeOfDayEnabled} value={value.date_minutes_end} onChange={minutes => onChange?.({ ...value, date_minutes_end: minutes })} />

      </FormGrouping>
      <FormGrouping
        elevation={24}
        backgroundElevation={12}
        checked={timeOfDayEnabled}
        onChange={setTimeOfDayEnabled}
        title="Time of day execution (Optional)"
        subtitle="Execution should take place within a certain time window of the day."
      >
        <TimeField label="From" variant="filled" fullWidth />
        <TimeField label="To" variant="filled" fullWidth />

      </FormGrouping>
    </FormGrouping>

  )
}
