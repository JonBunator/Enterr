import type { ChangeWebsite } from './activityRequests.ts'
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material'
import { useState } from 'react'
import AccessForm from '../actionBar/addWebsite/AccessForm.tsx'
import ActionIntervalForm from '../actionBar/addWebsite/ActionIntervalForm.tsx'
import ExpirationIntervalForm from '../actionBar/addWebsite/ExpirationIntervalForm.tsx'
import GeneralInfoForm from '../actionBar/addWebsite/GeneralInfoForm.tsx'

interface AddEditWebsiteProps {
  /**
   * When true, the dialog is open.
   */
  open: boolean
  /**
   * A callback function that is invoked when a close action is triggered.
   */
  onClose: () => void
  /**
   * When true, add text is displayed, edit text when false.
   */
  add: boolean
  /**
   * OnChange event.
   */
  onChange?: (value: ChangeWebsite) => void
  /**
   * Value that is displayed in dialog
   */
  value?: ChangeWebsite
}

const emptyChangeWebsite: ChangeWebsite = {
  url: '',
  success_url: '',
  name: '',
  username: '',
  password: '',
  pin: null,
  expiration_interval: null,
  custom_access: null,
  action_interval: {
    date_minutes_start: 0,
    date_minutes_end: 0,
    allowed_time_minutes_start: 0,
    allowed_time_minutes_end: 0,
  },
}

export default function AddEditWebsite(props: AddEditWebsiteProps) {
  const { open, onClose, add, onChange, value } = props
  const [currentValue, setCurrentValue] = useState<ChangeWebsite>(emptyChangeWebsite)

  const handleInputChange = (field: keyof ChangeWebsite, newValue: any) => {
    setCurrentValue(prev => ({
      ...prev,
      [field]: newValue,
    }))
  }

  return (
    <Dialog
      open={open}
      onClose={(_, reason) => {
        if (reason !== 'backdropClick') {
          onClose()
        }
      }}
      maxWidth="lg"
      fullWidth
    >
      <DialogTitle>
        {add ? 'Add ' : 'Edit '}
        website
      </DialogTitle>
      <DialogContent>
        <div className="column">
          <GeneralInfoForm />
          <AccessForm />
          <ActionIntervalForm value={currentValue.action_interval} />
          <ExpirationIntervalForm />
        </div>

      </DialogContent>
      <DialogActions>
        <Button onClick={() => onClose()} variant="outlined" color="primary">
          Cancel
        </Button>
        <Button
          disabled={!currentValue}
          onClick={() => {
            if (currentValue)
              onChange?.(currentValue)
          }}
          color="primary"
          variant="contained"
        >
          {add ? 'Add' : 'Edit'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
