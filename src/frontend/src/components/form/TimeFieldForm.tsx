import type { TimeFieldProps } from '@mui/x-date-pickers'
import type { Dayjs } from 'dayjs'
import { TimeField } from '@mui/x-date-pickers'
import { useCallback, useEffect, useState } from 'react'
import { useForm } from './FormProvider.tsx'

export type TimeFieldFormProps = Omit<TimeFieldProps, 'onChange' | 'error' | 'required'> & {
  /**
   * Is used to identify the timefield for form validation. Must be unique.
   */
  identifier: string
  /**
   * Is called when value changes.
   * @param value The changed value.
   */
  onChange?: (value: Dayjs | null) => void
  /**
   * The value that should be validated. When undefined the value of the timefield will be validated.
   */
  validationValue?: Dayjs | null
  /**
   * Is called when validating the textfield. Returns an error message when validation failed.
   * @param value The value that will be validated.
   */
  onValidate?: (value: Dayjs | null) => string
  /**
   * True when the textfield should be required.
   */
  required?: boolean
}

export default function TimeFieldForm(props: TimeFieldFormProps) {
  const { identifier, onChange, onValidate, validationValue, value, required, helperText, ...otherProps } = props
  const [error, setError] = useState<string>('')

  const { subscribe, unsubscribe } = useForm()

  function handleChange(newValue: Dayjs | null) {
    if (error !== '') {
      setError('')
    }
    onChange?.(newValue)
  }

  const validate = useCallback((): boolean => {
    let error = ''
    if (onValidate) {
      error = onValidate(validationValue ?? (value as Dayjs | null))
    }
    if (required && value === null) {
      error = 'This field is required'
    }
    setError(error)
    return error === ''
  }, [onValidate, required, validationValue, value])

  useEffect(() => {
    subscribe({ identifier, callback: validate })
    return () => {
      unsubscribe(identifier)
    }
  }, [identifier, subscribe, unsubscribe, validate])

  return (
    <TimeField
      {...otherProps}
      required={required}
      value={value}
      onChange={time => handleChange(time)}
      helperText={error === '' ? helperText : error}
      slotProps={{ textField: { error: error !== '' } }}
    />
  )
}
