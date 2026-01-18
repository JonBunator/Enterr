import type { ChangeWebsite } from '../../activity/model.ts'
import { Grid } from '@mui/material'
import TextFieldForm from '../../form/TextFieldForm.tsx'
import FormGrouping from '../FormGrouping.tsx'
import CustomLoginScriptForm from './customLoginScript/CustomLoginScriptForm.tsx'

interface AccessFormProps {
  value: ChangeWebsite
  onChange?: (value: ChangeWebsite) => void
  loading?: boolean
}

export default function AccessForm(props: AccessFormProps) {
  const { value, onChange, loading } = props
  return (
    <FormGrouping disableCheckbox title="Access *" column>
      <Grid container spacing={2}>
        <Grid size={{ xs: 6 }}>
          <TextFieldForm
            identifier="username"
            variant="filled"
            label="Username"
            disabled={loading}
            value={value.username}
            onChange={event =>
              onChange?.({
                ...value,
                username: event.target.value,
              })}
            required
            fullWidth
            helperText="The username that should be used to login."
          />
        </Grid>

        <Grid size={{ xs: 6 }}>
          <TextFieldForm
            identifier="password"
            variant="filled"
            label="Password"
            disabled={loading}
            value={value.password}
            onChange={event =>
              onChange?.({
                ...value,
                password: event.target.value,
              })}
            required
            fullWidth
            helperText="The password that should be used to login."
          />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <CustomLoginScriptForm value={value} onChange={onChange} loading={loading} />
        </Grid>
      </Grid>
    </FormGrouping>

  )
}
