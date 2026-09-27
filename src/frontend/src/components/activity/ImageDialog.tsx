import { XMarkIcon } from '@heroicons/react/24/solid'
import { Dialog, DialogContent, IconButton } from '@mui/material'
import Screenshot from './Screenshot.tsx'
import './ImageDialog.scss'

interface ImageDialogProps {
  open?: boolean
  onClose?: () => void
  screenshotId: string | null
  showLiveFeed?: boolean

}

export default function ImageDialog(props: ImageDialogProps) {
  const { open, onClose, screenshotId, showLiveFeed } = props
  return (
    <Dialog className="image-dialog" open={open ?? false} maxWidth="lg" onClose={onClose}>
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
        {showLiveFeed
          ? (
              <img
                className="screenshot"
                src="/api/stream/display"
                alt="Live display stream"
              />
            )
          : screenshotId !== null
          ? (
              <Screenshot screenshotId={screenshotId} />
            )
          : (
              []
            )}
      </DialogContent>
    </Dialog>
  )
}
