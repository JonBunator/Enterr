import { TextField } from '@mui/material'
import { useState } from 'react'
import FormGrouping from '../FormGrouping.tsx'

export default function CustomAccessForm() {
  const [customAccessEnabled, setCustomAccessEnabled] = useState<boolean>(false)

  return (
    <FormGrouping
      checked={customAccessEnabled}
      onChange={setCustomAccessEnabled}
      elevation={24}
      backgroundElevation={12}
      title="Custom Access (Optional)"
      subtitle="Allows to define custom XPath selectors for the username, password, pin and submit button."
    >
      <TextField
        label="Username XPath"
        variant="filled"
        fullWidth
      />
      <TextField
        label="Password XPath"
        variant="filled"
        fullWidth
      />
      <TextField
        label="Pin XPath"
        variant="filled"
        fullWidth
      />
      <TextField
        label="Submit button XPath"
        variant="filled"
        fullWidth
      />
    </FormGrouping>
  )
}
