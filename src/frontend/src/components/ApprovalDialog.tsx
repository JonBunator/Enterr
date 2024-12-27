import { Button, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material'

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
  header: string
  /**
   * The description text for the dialog
   */
  description: string
}

export default function ApprovalDialog(props: ApprovalDialogProps) {
  const { open, onClose, onApproval, header, description } = props
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{header}</DialogTitle>
      <DialogContent>
        <p>{description}</p>
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
          Approve
        </Button>
      </DialogActions>
    </Dialog>
  )
}
