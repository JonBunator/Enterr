import type { ChangeWebsite } from '../../activity/activityRequests.ts'
import { Checkbox, FormControlLabel, FormHelperText, Grid2 } from '@mui/material'
import TextFieldForm from '../../form/TextFieldForm.tsx'
import FormGrouping from '../FormGrouping.tsx'

interface GeneralInfoFormProps {
  value: ChangeWebsite
  onChange?: (value: ChangeWebsite) => void
}

export default function GeneralInfoForm(props: GeneralInfoFormProps) {
  const { value, onChange } = props

  function validateURL(url: string | undefined): string {
    const regex = /(^$|(http(s)?:\/\/)([\w-]+\.)+[\w-]+([\w- ;,./?%&=]*))/
    if (url === undefined || !regex.test(url)) {
      return 'URL is not valid.'
    }
    return ''
  }

  return (
    <FormGrouping disableCheckbox title="General *" column>
      <TextFieldForm
        identifier="name"
        value={value.name}
        onChange={name =>
          onChange?.({
            ...value,
            name,
          })}
        variant="filled"
        label="Name"
        required
        fullWidth
        helperText="The name to identify the login task. Does not have to be unique."
      />
      <Grid2 container spacing={2}>
        <Grid2 size={{ xs: 6 }}>
          <TextFieldForm
            identifier="url"
            value={value.url}
            onChange={url =>
              onChange?.({
                ...value,
                url,
              })}
            variant="filled"
            label="URL"
            required
            fullWidth
            helperText="The url of the login page."
            placeholder="https://www.example.com"
            onValidate={validateURL}
          />
        </Grid2>
        <Grid2 size={{ xs: 6 }}>
          <TextFieldForm
            identifier="success_url"
            value={value.success_url}
            onChange={success_url =>
              onChange?.({
                ...value,
                success_url,
              })}
            variant="filled"
            label="Success URL"
            required
            fullWidth
            placeholder="https://www.example.com/success"
            helperText="The url that is displayed after a successful login. This is used to check if the login was successful."
            onValidate={validateURL}
          />
        </Grid2>
        <Grid2 size={{ xs: 12 }}>
          <FormControlLabel control={<Checkbox checked={value.take_screenshot} onChange={event => onChange?.({ ...value, take_screenshot: event.target.checked })} />} label="Save screenshot" />
          <FormHelperText sx={{ marginTop: 0 }}>Saves screenshot after login attempt.</FormHelperText>
        </Grid2>
      </Grid2>
    </FormGrouping>

  )
}
