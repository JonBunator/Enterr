import { Checkbox, FormControlLabel, Grid2, TextField } from '@mui/material'
import FormGrouping from '../FormGrouping.tsx'

export default function GeneralInfoForm() {
  return (
    <FormGrouping disableCheckbox title="General *" column>
      <TextField
        variant="filled"
        label="Name"
        required
        fullWidth
        helperText="The name to identify the login task. Does not have to be unique."
      />
      <Grid2 container spacing={2}>
        <Grid2 size={{ xs: 6 }}>
          <TextField
            variant="filled"
            label="URL"
            required
            fullWidth
            helperText="The url of the login page."
          />
        </Grid2>
        <Grid2 size={{ xs: 6 }}>
          <TextField
            variant="filled"
            label="Success URL"
            required
            fullWidth
            helperText="The url that is displayed after a successful login. This is used to check if the login was successful."
          />
        </Grid2>
        <Grid2 size={{ xs: 12 }}>
          <FormControlLabel control={<Checkbox defaultChecked />} label="Save screenshot" />
        </Grid2>
      </Grid2>
    </FormGrouping>

  )
}
