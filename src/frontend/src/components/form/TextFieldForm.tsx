import type { InputBaseComponentProps, TextFieldProps } from "@mui/material";
import type { ElementType } from 'react'
import { Input, TextField } from '@mui/material'
import { forwardRef, useCallback, useEffect, useState } from 'react'
import { IMaskInput } from 'react-imask'
import { useForm } from './FormProvider.tsx'

export type TextFieldFormProps = Omit<TextFieldProps, 'onChange' | 'error' | 'required'> & {
  /**
   * Is used to identify the textfield for form validation. Must be unique.
   */
  identifier: string
  /**
   * Is called when value changes.
   * @param value The changed value.
   */
  onChange?: (value: string) => void
  /**
   * The value that should be validated. When undefined the value of the textfield will be validated.
   */
  validationValue?: string
  /**
   * Is called when validating the textfield. Returns an error message when validation failed.
   * @param value The value that will be validated.
   */
  onValidate?: (value: string) => string
  /**
   * True when the textfield should be required.
   */
  required?: boolean
  /**
   * When true the input becomes a number input.
   */
  numberInput?: boolean
}

interface MaskComponentProps {
  onChange: (event: { target: { name: string, value: string } }) => void
  name: string
}

const NumberMask = forwardRef<HTMLInputElement, MaskComponentProps>(
  (props, ref) => {
    const { onChange, name, ...other } = props
    return (
      <IMaskInput
        {...other}
        mask={Number}
        min={0}
        scale={0}
        inputRef={ref}
        onAccept={(value: any) => onChange({ target: { name, value: value as string } })}
        overwrite
      />
    )
  },
)

export default function TextFieldForm(props: TextFieldFormProps) {
  const { identifier, onChange, onValidate, validationValue, numberInput, value, required, helperText, ...otherProps } = props
  const [errorMessage, setErrorMessage] = useState<string>('')

  const { subscribe, unsubscribe } = useForm()

  function handleChange(newValue: string) {
    if (errorMessage !== '') {
      setErrorMessage('')
    }
    onChange?.(newValue)
  }

  const validate = useCallback((): boolean => {
    let error = ''
    if (onValidate) {
      error = onValidate(validationValue ?? (value as string))
    }
    if (required && value === '') {
      error = 'This field is required'
    }
    setErrorMessage(error)
    return error === ''
  }, [onValidate, required, validationValue, value])

  useEffect(() => {
    subscribe({ identifier, callback: validate })
    return () => {
      unsubscribe(identifier)
    }
  }, [identifier, subscribe, unsubscribe, validate])

  return (
    <TextField
      {...otherProps}
      required={required}
      value={value?.toString() ?? ''}
      slotProps={{
        input: {
          inputComponent: (numberInput ? NumberMask : Input) as any as ElementType<InputBaseComponentProps>,
          onChange: (event) => { handleChange(event.target.value) },
        },
      }}
      onChange={event => handleChange(event.target.value)}
      helperText={errorMessage === '' ? helperText : errorMessage}
      error={errorMessage !== ''}
    />
  )
}
