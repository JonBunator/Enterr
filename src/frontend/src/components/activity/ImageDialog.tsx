import { XMarkIcon } from '@heroicons/react/24/solid'
import { Dialog, DialogContent, IconButton } from '@mui/material'
import LiveFeed from './LiveFeed.tsx'
import Screenshot from './Screenshot.tsx'
import './ImageDialog.scss'

interface ImageDialogProps {
  open?: boolean
  onClose?: () => void
  screenshotId: string | null
  liveActionHistoryId?: number

}

export default function ImageDialog(props: ImageDialogProps) {
  const { open, onClose, screenshotId, liveActionHistoryId } = props

  const dialogOpen = ((screenshotId !== null || liveActionHistoryId !== undefined) && open) ?? false

  function renderContent() {
    if (liveActionHistoryId !== undefined) {
      return <LiveFeed actionHistoryId={liveActionHistoryId} />
    }
    if (screenshotId !== null) {
      return <Screenshot screenshotId={screenshotId} />
    }
    return []
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
