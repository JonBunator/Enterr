import type { InputBaseComponentProps, TextFieldProps } from "@mui/material";
import type { ElementType } from 'react'
import { TextField } from '@mui/material'
import { forwardRef, useCallback, useEffect, useState } from 'react'
import { IMaskInput } from 'react-imask'
import { useForm } from './FormProvider.tsx'

export type TextFieldFormProps = Omit<TextFieldProps, 'error'> & {
  /**
   * Is used to identify the textfield for form validation. Must be unique.
   */
  identifier: string
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
  const { identifier, onChange, onValidate, validationValue, slotProps, numberInput, value, required, helperText, ...otherProps } = props
  const [errorMessage, setErrorMessage] = useState<string>('')

  const { subscribe, unsubscribe } = useForm()

  function handleChange(event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    if (errorMessage !== '') {
      setErrorMessage('')
    }
    onChange?.(event)
  }

  const validate = useCallback((): boolean => {
    let error = ''
    const valueToValidate = validationValue ?? (value as string);
    if (onValidate) {
      error = onValidate(valueToValidate)
    }
    if (required && (valueToValidate === '' || valueToValidate === undefined || valueToValidate === null)) {
      console.log(valueToValidate)
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
      value={numberInput ? value?.toString() : value}
      slotProps={numberInput ? {
        input: {
          inputComponent: NumberMask as any as ElementType<InputBaseComponentProps>,
          onChange: (event) => { handleChange(event) },
        },
      } : {...slotProps}}
      onChange={event => handleChange(event)}
      helperText={errorMessage === '' ? helperText : errorMessage}
      error={errorMessage !== ''}
    />
  )
}
