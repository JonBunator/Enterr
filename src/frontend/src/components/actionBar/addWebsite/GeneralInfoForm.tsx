import type { ChangeWebsite } from '../../activity/activityRequests.ts'
import { Checkbox, FormControlLabel, FormHelperText, Grid } from '@mui/material'
import TextFieldForm from '../../form/TextFieldForm.tsx'
import FormGrouping from '../FormGrouping.tsx'

interface GeneralInfoFormProps {
  value: ChangeWebsite
  onChange?: (value: ChangeWebsite) => void
  loading?: boolean
}

export default function GeneralInfoForm(props: GeneralInfoFormProps) {
  const { value, onChange, loading } = props

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
        disabled={loading}
        value={value.name}
        onChange={event =>
          onChange?.({
            ...value,
            name: event.target.value,
          })}
        variant="filled"
        label="Name"
        required
        fullWidth
        helperText="The name to identify the login task. Does not have to be unique."
      />
      <Grid container spacing={2}>
        <Grid size={{ xs: 6 }}>
          <TextFieldForm
            identifier="url"
            disabled={loading}
            value={value.url}
            onChange={event =>
              onChange?.({
                ...value,
                url: event.target.value,
              })}
            variant="filled"
            label="URL"
            required
            fullWidth
            helperText="The URL of the login page."
            placeholder="https://www.example.com"
            onValidate={validateURL}
          />
        </Grid>
        <Grid size={{ xs: 6 }}>
          <TextFieldForm
            identifier="success_url"
            disabled={loading}
            value={value.success_url}
            onChange={event =>
              onChange?.({
                ...value,
                success_url: event.target.value,
              })}
            variant="filled"
            label="Success URL"
            required
            fullWidth
            placeholder="https://www.example.com/success"
            helperText="Redirects to URL after login. This is used to check if the login was successful. Make sure that the URL is not accessible when logged out."
            onValidate={validateURL}
          />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <div className="row">
            <div>
              <FormControlLabel
                control={(
                  <Checkbox
                    disabled={loading}
                    checked={value.take_screenshot}
                    onChange={event => onChange?.({ ...value, take_screenshot: event.target.checked })}
                  />
                )}
                label="Save screenshot"
              />
              <FormHelperText sx={{ marginTop: 0 }}>Saves screenshot after login attempt.</FormHelperText>
            </div>
            <div>
              <FormControlLabel
                control={(
                  <Checkbox
                    disabled={loading}
                    checked={value.paused}
                    onChange={event => onChange?.({ ...value, paused: event.target.checked })}
                  />
                )}
                label="Pause automatic login"
              />
              <FormHelperText sx={{ marginTop: 0 }}>Automatic login will not be triggered while in paused state.</FormHelperText>
            </div>
          </div>
        </Grid>
      </Grid>
    </FormGrouping>

  )
}
