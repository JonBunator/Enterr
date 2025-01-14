import type { Dayjs } from 'dayjs'
import type { ActionInterval, ChangeWebsite } from '../../activity/activityRequests.ts'
import dayjs from 'dayjs'
import { useState } from 'react'
import TimeFieldForm from '../../form/TimeFieldForm.tsx'
import TimeTextfields from '../../form/TimeTextfields.tsx'
import FormGrouping from '../FormGrouping.tsx'

interface ActionIntervalFormProps {
  value: ChangeWebsite
  onChange?: (value: ChangeWebsite) => void
  loading?: boolean
}

export default function ActionIntervalForm(props: ActionIntervalFormProps) {
  const { value, onChange, loading } = props
  const [timeSpanEnabled, setTimeSpanEnabled] = useState<boolean>(value.action_interval?.date_minutes_end !== null)
  const [timeOfDayEnabled, setTimeOfDayEnabled] = useState<boolean>(value.action_interval?.allowed_time_minutes_start !== null || value.action_interval.allowed_time_minutes_end !== null)

  function validateExecutionInterval(minutes: string): string {
    if (Number(minutes) <= 0) {
      return 'Execution interval must be greater than 0min.'
    }
    return ''
  }

  function validateTimespanInterval(minutes: string): string {
    if (Number(minutes) <= 0) {
      return 'Timespan end values must be greater than 0min.'
    }
    if (Number(minutes) < (value.action_interval?.date_minutes_start ?? 0)) {
      return 'Timespan end values must be greater than execution interval.'
    }
    return ''
  }

  function minutesToDayjs(minutes: number | null): Dayjs | null {
    if (minutes === null) {
      return null
    }
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return dayjs().set('hour', hours).set('minute', mins).set('second', 0).set('millisecond', 0)
  }

  function handleTimeOfDayEnabledChange(enabled: boolean) {
    if (!enabled) {
      onChange?.({
        ...value,
        action_interval: {
          ...value.action_interval,
          allowed_time_minutes_start: null,
          allowed_time_minutes_end: null,
        } as ActionInterval,
      })
    }
    setTimeOfDayEnabled(enabled)
  }

  function handleTimeSpanEnabledChange(enabled: boolean) {
    if (!enabled) {
      onChange?.({
        ...value,
        action_interval: {
          ...value.action_interval,
          date_minutes_end: null,
        } as ActionInterval,
      })
    }
    setTimeSpanEnabled(enabled)
  }

  function handleAllowedTimeChange(time: Dayjs | null, key: string) {
    let minutes = null
    if (time !== null && time.isValid()) {
      minutes = time?.hour() * 60 + time?.minute()
    }
    onChange?.({
      ...value,
      action_interval: {
        ...value.action_interval,
        [key]: minutes,
      } as ActionInterval,
    })
  }

  function validateAllowedStartTime(time: Dayjs | null): string {
    if (time === null) {
      return ''
    }
    const minutes = time?.hour() * 60 + time?.minute()
    const endTime = value.action_interval?.allowed_time_minutes_end ?? 0
    if (endTime !== null && minutes > endTime) {
      return 'Time must be before allowed end time.'
    }
    return ''
  }

  function validateAllowedEndTime(time: Dayjs | null): string {
    if (time === null) {
      return ''
    }
    const minutes = time?.hour() * 60 + time?.minute()
    const startTime = value.action_interval?.allowed_time_minutes_start ?? 0
    if (startTime !== null && minutes < startTime) {
      return 'Time must be after allowed start time.'
    }
    return ''
  }

  return (
    <FormGrouping
      disabled={loading}
      subtitle="Defines the interval at which the automatic login should be triggered. For example, if Days=5, an automatic login is performed every 5 days."
      disableCheckbox
      title="Execution Interval *"
      column
    >
      <div className="row">
        <TimeTextfields
          identifier="execution-interval-start"
          hoursHelperText="Only allowed when time of day execution is disabled."
          minutesHelperText="Only allowed when time of day execution is disabled."
          disableHoursMinutes={timeOfDayEnabled}
          loading={loading}
          value={value.action_interval?.date_minutes_start ?? 0}
          onChange={minutes =>
            onChange?.({
              ...value,
              action_interval: {
                ...value.action_interval,
                date_minutes_start: minutes,
              } as ActionInterval,
            })}
          onValidate={validateExecutionInterval}
        />
      </div>
      <FormGrouping
        disabled={loading}
        elevation={16}
        backgroundElevation={8}
        checked={timeSpanEnabled}
        onChange={handleTimeSpanEnabledChange}
        title="Timespan (Optional)"
        subtitle="Selects a random time within the specified time period. This can be used, to trigger a login on a random day every 10 to 15 days."
      >
        <TimeTextfields
          identifier="execution-interval-end"
          hoursHelperText="Only allowed when time of day execution is disabled."
          minutesHelperText="Only allowed when time of day execution is disabled."
          disableHoursMinutes={timeOfDayEnabled}
          loading={loading}
          value={value.action_interval?.date_minutes_end ?? 0}
          onChange={minutes =>
            onChange?.({
              ...value,
              action_interval: {
                ...value.action_interval,
                date_minutes_end: minutes,
              } as ActionInterval,
            })}
          onValidate={validateTimespanInterval}
        />
      </FormGrouping>
      <FormGrouping
        disabled={loading}
        elevation={16}
        backgroundElevation={8}
        checked={timeOfDayEnabled}
        onChange={handleTimeOfDayEnabledChange}
        title="Time of day execution (Optional)"
        subtitle="Execution should take place within a certain time window of the day."
      >
        <TimeFieldForm
          identifier="allowed_start_time"
          label="Allowed Start Time"
          variant="filled"
          fullWidth
          disabled={loading}
          value={minutesToDayjs(value.action_interval?.allowed_time_minutes_start ?? 0)}
          onChange={time => handleAllowedTimeChange(time, 'allowed_time_minutes_start')}
          onValidate={validateAllowedStartTime}
          required
        />

        <TimeFieldForm
          identifier="allowed_end_time"
          label="Allowed End Time"
          variant="filled"
          fullWidth
          disabled={loading}
          value={minutesToDayjs(value.action_interval?.allowed_time_minutes_end ?? 0)}
          onChange={time => handleAllowedTimeChange(time, 'allowed_time_minutes_end')}
          onValidate={validateAllowedEndTime}
          required
        />
      </FormGrouping>
    </FormGrouping>
  )
}
