import type { FormProviderRef } from '../form/FormProvider.tsx'
import type { ChangeWebsite } from './activityRequests.ts'
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material'
import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react'
import AccessForm from '../actionBar/addWebsite/AccessForm.tsx'
import ActionIntervalForm from '../actionBar/addWebsite/ActionIntervalForm.tsx'
import ExpirationIntervalForm from '../actionBar/addWebsite/ExpirationIntervalForm.tsx'
import GeneralInfoForm from '../actionBar/addWebsite/GeneralInfoForm.tsx'
import { FormProvider } from '../form/FormProvider.tsx'

const emptyChangeWebsite: ChangeWebsite = {
  url: '',
  success_url: '',
  name: '',
  username: '',
  password: '',
  take_screenshot: true,
  paused: false,
  expiration_interval_minutes: null,
  custom_login_script: null,
  action_interval: {
    date_minutes_start: 0,
    date_minutes_end: null,
    allowed_time_minutes_start: null,
    allowed_time_minutes_end: null,
  },
}

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
  /**
   * When true dialog is in loading state. No values can be inputted.
   */
  loading?: boolean
}

export interface AddEditWebsiteRef {
  resetForm: () => void
}

const AddEditWebsite = forwardRef<AddEditWebsiteRef, AddEditWebsiteProps>((props, ref) => {
  const { open, onClose, add, onChange, value, loading } = props

  const [currentValue, setCurrentValue] = useState<ChangeWebsite>(emptyChangeWebsite)
  const formRef = useRef<FormProviderRef>(null)

  useImperativeHandle(ref, () => ({
    resetForm: () => {
      setCurrentValue(value ?? emptyChangeWebsite)
    },
  }))

  useEffect(() => {
    setCurrentValue(value ?? emptyChangeWebsite)
  }, [value])

  async function handleSubmit() {
    if (formRef?.current) {
      const isValid = await formRef?.current.validate()
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
            <GeneralInfoForm value={currentValue} onChange={setCurrentValue} loading={loading} />
            <AccessForm value={currentValue} onChange={setCurrentValue} loading={loading} />
            <ActionIntervalForm value={currentValue} onChange={setCurrentValue} loading={loading} />
            <ExpirationIntervalForm value={currentValue} onChange={setCurrentValue} loading={loading} />
          </div>

        </FormProvider>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => onClose()} variant="outlined" color="primary">
          Cancel
        </Button>
        <Button
          disabled={loading}
          onClick={handleSubmit}
          color="primary"
          variant="contained"
        >
          {add ? 'Add' : 'Edit'}
        </Button>
      </DialogActions>
    </Dialog>
  )
})
export default AddEditWebsite
