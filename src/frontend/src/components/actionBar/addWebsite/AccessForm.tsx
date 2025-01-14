import type { ChangeWebsite } from '../../activity/activityRequests.ts'
import { Grid2 } from '@mui/material'
import TextFieldForm from '../../form/TextFieldForm.tsx'
import FormGrouping from '../FormGrouping.tsx'
import CustomAccessForm from './CustomAccessForm.tsx'

interface AccessFormProps {
  value: ChangeWebsite
  onChange?: (value: ChangeWebsite) => void
  loading?: boolean
}

export default function AccessForm(props: AccessFormProps) {
  const { value, onChange, loading } = props
  return (
    <FormGrouping disableCheckbox title="Access *" column>
      <Grid2 container spacing={2}>
        <Grid2 size={{ xs: 4 }}>
          <TextFieldForm
            identifier="username"
            variant="filled"
            label="Username"
            disabled={loading}
            value={value.username}
            onChange={username =>
              onChange?.({
                ...value,
                username,
              })}
            required
            fullWidth
            helperText="The username that should be used to login."
          />
        </Grid2>

        <Grid2 size={{ xs: 4 }}>
          <TextFieldForm
            identifier="password"
            variant="filled"
            label="Password"
            disabled={loading}
            value={value.password}
            onChange={password =>
              onChange?.({
                ...value,
                password,
              })}
            required
            fullWidth
            helperText="The password that should be used to login."
          />
        </Grid2>
        <Grid2 size={{ xs: 4 }}>
          <TextFieldForm
            identifier="pin"
            variant="filled"
            label="PIN"
            disabled={loading}
            value={value.pin}
            onChange={pin =>
              onChange?.({
                ...value,
                pin,
              })}
            fullWidth
            helperText="Some websites require an additional pin to login. This is not a 2FA pin that is receiced by SMS, email etc."
          />
        </Grid2>
        <Grid2 size={{ xs: 12 }}>
          <CustomAccessForm value={value} onChange={onChange} loading={loading} />
        </Grid2>
      </Grid2>
    </FormGrouping>

  )
}
