import type { ChangeWebsite, CustomAccess } from '../../activity/activityRequests.ts'
import { TextField } from '@mui/material'
import { useState } from 'react'
import FormGrouping from '../FormGrouping.tsx'

interface CustomAccessFormProps {
  value: ChangeWebsite
  onChange?: (value: ChangeWebsite) => void
}

export default function CustomAccessForm(props: CustomAccessFormProps) {
  const { value, onChange } = props
  const [customAccessEnabled, setCustomAccessEnabled] = useState<boolean>(value.custom_access !== null)

  function handleEnabledChange(enabled: boolean) {
    setCustomAccessEnabled(enabled)
    if (enabled) {
      onChange?.({
        ...value,
        custom_access: null,
      })
    }
  }

  function handleCustomAccessChange(val: string, key: string) {
    const newCustomAccess = {
      ...value?.custom_access,
      [key]: val,
    }

    const allEmpty = Object.values(newCustomAccess).every(v => v === '' || v === null)

    onChange?.({
      ...value,
      custom_access: allEmpty ? null : newCustomAccess as CustomAccess,
    })
  }

  return (
    <FormGrouping
      checked={customAccessEnabled}
      onChange={handleEnabledChange}
      elevation={16}
      backgroundElevation={8}
      title="Custom Access (Optional)"
      subtitle="Allows to define custom XPath selectors for the username, password, pin fields and submit button."
    >
      <TextField
        label="Username XPath"
        variant="filled"
        value={value?.custom_access?.username_xpath ?? ''}
        onChange={event => handleCustomAccessChange(event.target.value, 'username_xpath')}
        fullWidth
      />
      <TextField
        label="Password XPath"
        variant="filled"
        value={value?.custom_access?.password_xpath ?? ''}
        onChange={event => handleCustomAccessChange(event.target.value, 'password_xpath')}
        fullWidth
      />
      <TextField
        label="Pin XPath"
        variant="filled"
        value={value?.custom_access?.pin_xpath ?? ''}
        onChange={event => handleCustomAccessChange(event.target.value, 'pin_xpath')}
        fullWidth
      />
      <TextField
        label="Submit button XPath"
        variant="filled"
        value={value?.custom_access?.submit_button_xpath ?? ''}
        onChange={event => handleCustomAccessChange(event.target.value, 'submit_button_xpath')}
        fullWidth
      />
    </FormGrouping>
  )
}
