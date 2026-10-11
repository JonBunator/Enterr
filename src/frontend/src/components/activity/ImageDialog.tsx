import { XMarkIcon } from '@heroicons/react/24/solid'
import { CircularProgress, Dialog, DialogContent, IconButton, Typography } from '@mui/material'
import LiveFeed from './LiveFeed.tsx'
import Screenshot from './Screenshot.tsx'
import './ImageDialog.scss'

interface ImageDialogProps {
  open?: boolean
  onClose?: () => void
  screenshotId: string | null
  screenshotPending?: boolean
  liveActionHistoryId?: number

}

export default function ImageDialog(props: ImageDialogProps) {
  const { open, onClose, screenshotId, screenshotPending, liveActionHistoryId } = props

  // Must not depend on the content, otherwise the dialog closes when a running login finishes
  const dialogOpen = open ?? false

  function renderContent() {
    if (liveActionHistoryId !== undefined) {
      return <LiveFeed actionHistoryId={liveActionHistoryId} />
    }
    if (screenshotId !== null) {
      return <Screenshot screenshotId={screenshotId} />
    }
    if (screenshotPending) {
      return (
        <div className="image-dialog-loading">
          <CircularProgress />
        </div>
      )
    }
    return <Typography className="image-dialog-message">No screenshot available</Typography>
  }

  return (
    <Dialog className="image-dialog" open={dialogOpen} maxWidth="lg" onClose={onClose}>
      <IconButton
        aria-label="close"
        onClick={onClose}
        sx={{
          position: 'absolute',
          top: 8,
          right: 8,
          color: theme => theme.palette.grey[500],
        }}
      >
        <XMarkIcon className="icon" />
      </IconButton>
      <DialogContent className="image-dialog-content">
        {renderContent()}
      </DialogContent>
    </Dialog>
  )
}
