import type { ChangeWebsite } from './activityRequests.ts'
import {
  GlobeAltIcon,
  PauseCircleIcon,
  PencilSquareIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'
import { EllipsisVerticalIcon } from '@heroicons/react/24/solid'
import { IconButton, Link, ListItemIcon, ListItemText, MenuItem, Popover, Tooltip, Typography } from '@mui/material'
import React, { useState } from 'react'
import { deleteWebsite, editWebsite } from '../../api/apiRequests.ts'
import ApprovalDialog from '../ApprovalDialog.tsx'
import { useSnackbar } from '../SnackbarProvider.tsx'
import { getChangeWebsite } from './activityRequests.ts'
import AddEditWebsite from './AddEditWebsite.tsx'

interface ActionsPopoverProps {
  websiteId: number
  websiteURL: string
}

export default function ActionsPopover(props: ActionsPopoverProps) {
  const { websiteId, websiteURL } = props

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [deletionApprovalDialogOpen, setDeletionApprovalDialogOpen] = useState<boolean>(false)
  const [saveWebsiteVisitDialogOpen, setSaveWebsiteVisitDialogOpen] = useState<boolean>(false)

  const [editDialogOpen, setEditDialogOpen] = useState<boolean>(false)
  const [editWebsiteValue, setEditWebsiteValue] = useState<ChangeWebsite | undefined>(undefined)

  const { success, error, loading } = useSnackbar()

  const handleOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  function handleOpenWebsite() {
    handleClose()
    setSaveWebsiteVisitDialogOpen(true)
    window.open(websiteURL, '_blank')
  }

  function handleDeleteRequest() {
    handleClose()
    setDeletionApprovalDialogOpen(true)
  }

  async function handleDelete() {
    loading('Deleting website...')
    try {
      await deleteWebsite(websiteId)
      success('Website deleted successfully')
    }
    catch (e) {
      error('Failed to delete website', (e as Error).message)
    }
  }

  async function handleOpenEditDialog() {
    handleClose()
    setEditDialogOpen(true)
    setEditWebsiteValue(await getChangeWebsite(websiteId))
  }

  async function handleEdit(value: ChangeWebsite) {
    setEditDialogOpen(false)
    loading('Editing website...')
    try {
      await editWebsite(websiteId, value)
      success('Website edited successfully')
    }
    catch (e) {
      error('Failed to edit website', (e as Error).message)
    }
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
        onApproval={() => void handleDelete()}
        header="Delete website"
        description="Are you sure you want to delete this website?"
        approvalText="Delete"
      />
      <ApprovalDialog
        open={saveWebsiteVisitDialogOpen}
        onClose={() => setSaveWebsiteVisitDialogOpen(false)}
        onApproval={() => console.log('approved')}
        header="Save login"
        description={(
          <>
            <Typography>You manually visited the website </Typography>
            <Link>{websiteURL}</Link>
            <Typography>Do you want to save the potential login as a successful?</Typography>
          </>
        )}
      />
      <AddEditWebsite value={editWebsiteValue} open={editDialogOpen} add={false} onClose={() => setEditDialogOpen(false)} onChange={value => void handleEdit(value)} />
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
        <MenuItem onClick={handleOpenWebsite}>
          <ListItemIcon>
            <GlobeAltIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Open website" />
        </MenuItem>
        <MenuItem onClick={() => void handleOpenEditDialog()}>
          <ListItemIcon>
            <PencilSquareIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Edit" />
        </MenuItem>
        <MenuItem onClick={handleDeleteRequest}>
          <ListItemIcon>
            <TrashIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Delete" />
        </MenuItem>
      </Popover>
    </>
  )
}
