import type { FormProviderRef } from '../form/FormProvider.tsx'
import type { ChangeWebsite } from './activityRequests.ts'
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material'
import { useEffect, useRef, useState } from 'react'
import AccessForm from '../actionBar/addWebsite/AccessForm.tsx'
import ActionIntervalForm from '../actionBar/addWebsite/ActionIntervalForm.tsx'
import ExpirationIntervalForm from '../actionBar/addWebsite/ExpirationIntervalForm.tsx'
import GeneralInfoForm from '../actionBar/addWebsite/GeneralInfoForm.tsx'
import { FormProvider } from '../form/FormProvider.tsx'

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
  pin: '',
  take_screenshot: true,
  expiration_interval_minutes: null,
  custom_access: null,
  action_interval: {
    date_minutes_start: 0,
    date_minutes_end: null,
    allowed_time_minutes_start: null,
    allowed_time_minutes_end: null,
  },
}

export default function AddEditWebsite(props: AddEditWebsiteProps) {
  const { open, onClose, add, onChange, value } = props
  const [currentValue, setCurrentValue] = useState<ChangeWebsite>(emptyChangeWebsite)
  const formRef = useRef<FormProviderRef>(null)

  useEffect(() => {
    setCurrentValue(value ?? emptyChangeWebsite)
  }, [value])

  function handleSubmit() {
    if (formRef?.current) {
      const isValid = formRef?.current.validate()
      if (isValid) {
        onChange?.(currentValue)
      }
      else {
        formRef?.current.scrollToError()
      }
    }
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
        <FormProvider ref={formRef}>
          <div className="column">
            <GeneralInfoForm value={currentValue} onChange={setCurrentValue} />
            <AccessForm value={currentValue} onChange={setCurrentValue} />
            <ActionIntervalForm value={currentValue} onChange={setCurrentValue} />
            <ExpirationIntervalForm value={currentValue} onChange={setCurrentValue} />
          </div>

        </FormProvider>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => onClose()} variant="outlined" color="primary">
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          color="primary"
          variant="contained"
        >
          {add ? 'Add' : 'Edit'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
