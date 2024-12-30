import { TextField } from '@mui/material'
import { useEffect, useState } from 'react'

interface TimeTextfieldsProps {
  disableHoursMinutes?: boolean
  value: number
  hoursHelperText?: string
  minutesHelperText?: string
  onChange?: (minutes: number) => void
}

export default function TimeTextfields(props: TimeTextfieldsProps) {
  const { disableHoursMinutes, value, hoursHelperText, minutesHelperText, onChange } = props
  const [weeks, setWeeks] = useState<number>(0)
  const [days, setDays] = useState<number>(0)
  const [hours, setHours] = useState<number>(0)
  const [minutes, setMinutes] = useState<number>(0)

  useEffect(() => {
    handleMinutesChange(value)
  }, [value]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (disableHoursMinutes) {
      setHours(0)
      setMinutes(0)
    }
  }, [disableHoursMinutes])

  useEffect(() => {
    const total = weeks * 7 * 24 * 60 + days * 24 * 60 + hours * 60 + minutes
    onChange?.(total)
  }, [weeks, days, hours, minutes, onChange])

  function handleWeeksChange(value: number) {
    setWeeks(value)
  }

  function handleDaysChange(value: number) {
    const newWeeks = Math.floor(value / 7)
    handleWeeksChange(weeks + newWeeks)
    setDays(value % 7)
  }

  function handleHoursChange(value: number) {
    const newDays = Math.floor(value / 24)
    handleDaysChange(days + newDays)
    setHours(value % 24)
  }

  function handleMinutesChange(value: number) {
    const newHours = Math.floor(value / 60)
    handleHoursChange(hours + newHours)
    setMinutes(value % 60)
  }

  return (
    <>
      <TextField
        onChange={event => setWeeks(Number(event.target.value))}
        onBlur={event => handleWeeksChange(Number(event.target.value))}
        type="number"
        value={weeks}
        label="Weeks"
        variant="filled"
        fullWidth
      />
      <TextField
        onChange={event => setDays(Number(event.target.value))}
        onBlur={event => handleDaysChange(Number(event.target.value))}
        type="number"
        value={days}
        label="Days"
        variant="filled"
        fullWidth
      />
      <TextField
        onChange={event => setHours(Number(event.target.value))}
        onBlur={event => handleHoursChange(Number(event.target.value))}
        type="number"
        value={hours}
        label="Hours"
        disabled={disableHoursMinutes}
        variant="filled"
        fullWidth
        helperText={hoursHelperText}
      />
      <TextField
        onChange={event => setMinutes(Number(event.target.value))}
        onBlur={event => handleMinutesChange(Number(event.target.value))}
        type="number"
        value={minutes}
        label="Minutes"
        disabled={disableHoursMinutes}
        variant="filled"
        fullWidth
        helperText={minutesHelperText}
      />
    </>
  )
}
