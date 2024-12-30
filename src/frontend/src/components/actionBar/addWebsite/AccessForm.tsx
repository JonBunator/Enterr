import { Grid2, TextField } from '@mui/material'
import FormGrouping from '../FormGrouping.tsx'
import CustomAccessForm from './CustomAccessForm.tsx'

export default function AccessForm() {
  return (
    <FormGrouping disableCheckbox title="Access *" column>
      <Grid2 container spacing={2}>
        <Grid2 size={{ xs: 4 }}>
          <TextField
            variant="filled"
            label="Username"
            required
            fullWidth
            helperText="The username that should be used to login."
          />
        </Grid2>

        <Grid2 size={{ xs: 4 }}>
          <TextField
            variant="filled"
            label="Password"
            required
            fullWidth
            helperText="The password that should be used to login."
          />
        </Grid2>
        <Grid2 size={{ xs: 4 }}>
          <TextField
            variant="filled"
            label="PIN"
            fullWidth
            helperText="Some websites require an additional pin to login. This is not a 2FA pin that is receiced by SMS, email etc."
          />
        </Grid2>
        <Grid2 size={{ xs: 12 }}>
          <CustomAccessForm />
        </Grid2>
      </Grid2>
    </FormGrouping>

  )
}
