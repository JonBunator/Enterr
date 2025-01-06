import type { Dayjs } from 'dayjs'
import type { ChangeWebsite } from '../../activity/activityRequests.ts'
import dayjs from 'dayjs'
import { useState } from 'react'
import TimeFieldForm from '../../form/TimeFieldForm.tsx'
import TimeTextfields from '../../form/TimeTextfields.tsx'
import FormGrouping from '../FormGrouping.tsx'

interface ActionIntervalFormProps {
  value: ChangeWebsite
  onChange?: (value: ChangeWebsite) => void
}

export default function ActionIntervalForm(props: ActionIntervalFormProps) {
  const { value, onChange } = props
  const [timeSpanEnabled, setTimeSpanEnabled] = useState<boolean>(value.action_interval.date_minutes_end !== null)
  const [timeOfDayEnabled, setTimeOfDayEnabled] = useState<boolean>(value.action_interval.allowed_time_minutes_start !== null || value.action_interval.allowed_time_minutes_end !== null)

  function minutesToString(minutes: number | null): string {
    const date: Dayjs | null = minutesToDayjs(minutes)
    const days = date?.day() ?? 0
    const hours = date?.hour() ?? 0
    const min = date?.minute() ?? 0

    const result = []
    if (days > 0)
      result.push(`${days}d`)
    if (hours > 0)
      result.push(`${hours}h`)
    if (min > 0)
      result.push(`${minutes}m`)
    return result.join(' ')
  }

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
    if (Number(minutes) < value.action_interval.date_minutes_start) {
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
        },
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
        },
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
      },
    })
  }

  function validateAllowedStartTime(time: Dayjs | null): string {
    if (time === null) {
      return ''
    }
    const minutes = time?.hour() * 60 + time?.minute()
    const endTime = value.action_interval.allowed_time_minutes_end
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
    const startTime = value.action_interval.allowed_time_minutes_start
    if (startTime !== null && minutes < startTime) {
      return 'Time must be after allowed start time.'
    }
    return ''
  }

  return (
    <FormGrouping
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
          value={value.action_interval.date_minutes_start}
          onChange={minutes =>
            onChange?.({
              ...value,
              action_interval: {
                ...value.action_interval,
                date_minutes_start: minutes,
              },
            })}
          onValidate={validateExecutionInterval}
        />
      </div>
      <FormGrouping
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
          value={value.action_interval.date_minutes_end ?? 0}
          onChange={minutes =>
            onChange?.({
              ...value,
              action_interval: {
                ...value.action_interval,
                date_minutes_end: minutes,
              },
            })}
          onValidate={validateTimespanInterval}
        />
      </FormGrouping>
      <FormGrouping
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
          value={minutesToDayjs(value.action_interval.allowed_time_minutes_start)}
          onChange={time => handleAllowedTimeChange(time, 'allowed_time_minutes_start')}
          onValidate={validateAllowedStartTime}
          required
        />

        <TimeFieldForm
          identifier="allowed_end_time"
          label="Allowed End Time"
          variant="filled"
          fullWidth
          value={minutesToDayjs(value.action_interval.allowed_time_minutes_end)}
          onChange={time => handleAllowedTimeChange(time, 'allowed_time_minutes_end')}
          onValidate={validateAllowedEndTime}
          required
        />
      </FormGrouping>
    </FormGrouping>
  )
}
