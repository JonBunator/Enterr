import type { ReactNode } from 'react'
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Typography } from '@mui/material'

interface ApprovalDialogProps {
  /**
   * Controls whether the dialog is open or not
   */
  open: boolean
  /**
   * Callback to handle closing the dialog
   */
  onClose: () => void
  /**
   * Callback to handle approval action
   */
  onApproval: () => void
  /**
   * The header text for the dialog
   */
  header: ReactNode
  /**
   * The description text for the dialog
   */
  description: ReactNode
  /**
   * Text of the approval button. "Yes" when undefined.
   */
  approvalText?: string
}

export default function ApprovalDialog(props: ApprovalDialogProps) {
  const { open, onClose, onApproval, header, description, approvalText } = props
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{header}</DialogTitle>
      <DialogContent>
        <Typography>{description}</Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="outlined" color="primary">
          Cancel
        </Button>
        <Button
          onClick={() => {
            onApproval()
            onClose()
          }}
          color="primary"
          variant="contained"
        >
          {approvalText ?? 'Yes'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
