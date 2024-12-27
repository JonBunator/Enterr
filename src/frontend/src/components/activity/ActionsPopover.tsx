import {
  GlobeAltIcon,
  PauseCircleIcon,
  PencilSquareIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'
import { EllipsisVerticalIcon } from '@heroicons/react/24/solid'
import { IconButton, ListItemIcon, ListItemText, MenuItem, Popover, Tooltip } from '@mui/material'
import React, { useState } from 'react'
import { deleteWebsite } from '../../api/apiRequests.ts'
import ApprovalDialog from '../ApprovalDialog.tsx'

interface ActionsPopoverProps {
  websiteId: number
}

export default function ActionsPopover(props: ActionsPopoverProps) {
  const { websiteId } = props

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [deletionApprovalDialogOpen, setDeletionApprovalDialogOpen] = useState<boolean>(false)

  const handleOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  function handleDelete() {
    handleClose()
    setDeletionApprovalDialogOpen(true)
  }

  return (
    <>
      <Tooltip title="Options">
        <IconButton onClick={handleOpen}>
          <EllipsisVerticalIcon className="icon" />
        </IconButton>
      </Tooltip>
      <ApprovalDialog
        open={deletionApprovalDialogOpen}
        onClose={() => setDeletionApprovalDialogOpen(false)}
        onApproval={() => void deleteWebsite(websiteId)}
        header="Delete website"
        description="Are you sure you want to delete this website?"
      />
      <Popover
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={() => console.log('')}>
          <ListItemIcon>
            <PauseCircleIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Pause automatic login" />
        </MenuItem>
        <MenuItem onClick={() => console.log('')}>
          <ListItemIcon>
            <GlobeAltIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Open website" />
        </MenuItem>
        <MenuItem onClick={() => console.log('')}>
          <ListItemIcon>
            <PencilSquareIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Edit" />
        </MenuItem>
        <MenuItem onClick={() => handleDelete()}>
          <ListItemIcon>
            <TrashIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Delete" />
        </MenuItem>
      </Popover>
    </>
  )
}
