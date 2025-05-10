import type { ChangeWebsite, CustomAccess } from '../../activity/activityRequests.ts'
import { useState } from 'react'
import TextFieldForm from '../../form/TextFieldForm.tsx'
import FormGrouping from '../FormGrouping.tsx'

interface CustomAccessFormProps {
  value: ChangeWebsite
  onChange?: (value: ChangeWebsite) => void
  loading?: boolean
}

export default function CustomAccessForm(props: CustomAccessFormProps) {
  const { value, onChange, loading } = props
  const [customAccessEnabled, setCustomAccessEnabled] = useState<boolean>(value.custom_access !== null)

  function handleEnabledChange(enabled: boolean) {
    setCustomAccessEnabled(enabled)
    if (!enabled) {
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
      disabled={loading}
      checked={customAccessEnabled}
      onChange={handleEnabledChange}
      elevation={16}
      backgroundElevation={8}
      title="Custom Access (Optional)"
      subtitle="Allows to define custom XPath selectors for the username, password, pin fields and submit button."
    >
      <TextFieldForm
        label="Username XPath"
        variant="filled"
        identifier="username-xpath"
        placeholder="//input[@name='username']"
        disabled={loading}
        value={value?.custom_access?.username_xpath ?? ''}
        onChange={event => handleCustomAccessChange(event.target.value, 'username_xpath')}
        fullWidth
      />
      <TextFieldForm
        label="Password XPath"
        variant="filled"
        identifier="password-xpath"
        placeholder="//input[@type='password']"
        disabled={loading}
        value={value?.custom_access?.password_xpath ?? ''}
        onChange={event => handleCustomAccessChange(event.target.value, 'password_xpath')}
        fullWidth
      />
      <TextFieldForm
        label="Pin XPath"
        variant="filled"
        identifier="pin-xpath"
        placeholder="//input[@name='pin']"
        disabled={loading}
        value={value?.custom_access?.pin_xpath ?? ''}
        onChange={event => handleCustomAccessChange(event.target.value, 'pin_xpath')}
        fullWidth
      />
      <TextFieldForm
        label="Submit button XPath"
        variant="filled"
        identifier="submit-button-xpath"
        placeholder="//input[@type='submit']"
        disabled={loading}
        value={value?.custom_access?.submit_button_xpath ?? ''}
        onChange={event => handleCustomAccessChange(event.target.value, 'submit_button_xpath')}
        fullWidth
      />
    </FormGrouping>
  )
}
