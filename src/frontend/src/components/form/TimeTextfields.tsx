import { useEffect, useState } from 'react'
import TextFieldForm from './TextFieldForm.tsx'

interface TimeTextfieldsProps {
  identifier: string
  disableHoursMinutes?: boolean
  value: number
  hoursHelperText?: string
  minutesHelperText?: string
  onChange?: (minutes: number) => void
  onValidate?: (minutes: string) => string
}

export default function TimeTextfields(props: TimeTextfieldsProps) {
  const { identifier, disableHoursMinutes, value, hoursHelperText, minutesHelperText, onChange, onValidate } = props
  const [weeks, setWeeks] = useState<number>(0)
  const [days, setDays] = useState<number>(0)
  const [hours, setHours] = useState<number>(0)
  const [minutes, setMinutes] = useState<number>(0)

  useEffect(() => {
    let remainingMinutes = value
    const calculatedWeeks = Math.floor(remainingMinutes / (7 * 24 * 60))
    remainingMinutes %= 7 * 24 * 60
    const calculatedDays = Math.floor(remainingMinutes / (24 * 60))
    remainingMinutes %= 24 * 60
    const calculatedHours = Math.floor(remainingMinutes / 60)
    const calculatedMinutes = remainingMinutes % 60

    setWeeks(calculatedWeeks)
    setDays(calculatedDays)
    setHours(calculatedHours)
    setMinutes(calculatedMinutes)
  }, [value])

  useEffect(() => {
    if (disableHoursMinutes) {
      setHours(0)
      setMinutes(0)
    }
  }, [disableHoursMinutes])

  const calculateTotalMinutes = (
    weeks: number,
    days: number,
    hours: number,
    minutes: number,
  ): number => weeks * 7 * 24 * 60 + days * 24 * 60 + hours * 60 + minutes

  function handleWeeksChange(newWeeks: number) {
    setWeeks(newWeeks)
    const total = calculateTotalMinutes(newWeeks, days, hours, minutes)
    onChange?.(total)
  }

  function handleDaysChange(newDays: number) {
    setDays(newDays)
    const total = calculateTotalMinutes(weeks, newDays, hours, minutes)
    onChange?.(total)
  }

  function handleHoursChange(newHours: number) {
    setHours(newHours)
    const total = calculateTotalMinutes(weeks, days, newHours, minutes)
    onChange?.(total)
  }

  function handleMinutesChange(newMinutes: number) {
    setMinutes(newMinutes)
    const total = calculateTotalMinutes(weeks, days, hours, newMinutes)
    onChange?.(total)
  }

  return (
    <>
      <TextFieldForm
        identifier={`${identifier}-weeks`}
        onChange={val => setWeeks(Number(val))}
        onBlur={event => handleWeeksChange(Number(event.target.value))}
        value={weeks}
        numberInput
        label="Weeks"
        variant="filled"
        fullWidth
      />
      <TextFieldForm
        identifier={`${identifier}-days`}
        onChange={val => setDays(Number(val))}
        onBlur={event => handleDaysChange(Number(event.target.value))}
        value={days}
        numberInput
        label="Days"
        variant="filled"
        fullWidth
      />
      <TextFieldForm
        identifier={`${identifier}-hours`}
        onChange={val => setHours(Number(val))}
        onBlur={event => handleHoursChange(Number(event.target.value))}
        value={hours}
        numberInput
        label="Hours"
        disabled={disableHoursMinutes}
        variant="filled"
        fullWidth
        helperText={hoursHelperText}
      />
      <TextFieldForm
        identifier={`${identifier}-minutes`}
        onChange={val => setMinutes(Number(val))}
        onBlur={event => handleMinutesChange(Number(event.target.value))}
        value={minutes}
        numberInput
        label="Minutes"
        disabled={disableHoursMinutes}
        variant="filled"
        fullWidth
        helperText={minutesHelperText}
        validationValue={minutes.toString()}
        onValidate={onValidate}
      />
    </>
  )
}
