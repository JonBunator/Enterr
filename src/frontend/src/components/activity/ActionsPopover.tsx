import type { ChangeWebsite } from './activityRequests.ts'
import {
  CheckCircleIcon,
  GlobeAltIcon,
  PauseCircleIcon,
  PencilSquareIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'
import { ArrowPathIcon, EllipsisVerticalIcon, PlayCircleIcon } from '@heroicons/react/24/solid'
import {
  Divider,
  IconButton,
  Link,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Popover,
  Tooltip,
  Typography,
} from '@mui/material'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { addManualLogin, deleteWebsite, editWebsite, triggerAutomaticLogin } from '../../api/apiRequests.ts'
import ApprovalDialog from '../ApprovalDialog.tsx'
import { useSnackbar } from '../provider/SnackbarProvider.tsx'
import { useWebSocket } from '../provider/WebSocketProvider.tsx'
import { getChangeWebsite } from './activityRequests.ts'
import AddEditWebsite, { type AddEditWebsiteRef } from './AddEditWebsite.tsx'
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/16/solid";

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
  const [loadingEditData, setLoadingEditData] = useState<boolean>(false)

  const editWebsiteDialogRef = useRef<AddEditWebsiteRef | null>(null)

  const { success, error, loading } = useSnackbar()
  const { on } = useWebSocket()

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

  async function handleAddManualLogin() {
    handleClose()
    loading('Saving manual pages...')
    try {
      await addManualLogin(websiteId)
      success('Manual pages saved successfully')
    }
    catch (e) {
      error('Failed to save manual pages', (e as Error).message)
    }
  }

  const fetchData = useCallback(() => {
    setLoadingEditData(true)
    getChangeWebsite(websiteId)
      .then((result) => {
        setEditWebsiteValue(result)
        setLoadingEditData(false)
      })
      .catch(console.error)
  }, [websiteId])

  useEffect(() => {
    on('login_data_changed', (_d) => {
      fetchData()
    })
  }, [on, fetchData])

  useEffect(() => {
    fetchData()
  }, [fetchData, websiteId])

  async function handleOpenEditDialog() {
    handleClose()
    setEditDialogOpen(true)
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

  async function handlePause() {
    handleClose()
    if (editWebsiteValue === undefined) {
      error('Failed to change pause state of website pages', 'Loading website data failed.')
      return
    }
    const paused = !editWebsiteValue.paused
    setEditWebsiteValue(prev => ({ ...prev, paused }))
    loading(`${paused ? 'Pausing' : 'Resuming'} website login...`)
    try {
      await editWebsite(websiteId, { paused })
      success(`Website login successfully ${paused ? 'paused' : 'resumed'}`)
    }
    catch (e) {
      error('Failed to change pause state of website pages', (e as Error).message)
    }
  }

  async function triggerLogin() {
    handleClose()

    loading(`Triggering login...`)
    try {
      await triggerAutomaticLogin(websiteId)
      success(`Website login successfully started`)
    }
    catch (e) {
      error('Failed to trigger website pages', (e as Error).message)
    }
  }

  function handleEditCloseDialog() {
    setEditDialogOpen(false)
    editWebsiteDialogRef.current?.resetForm()
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
        onApproval={() => void handleAddManualLogin()}
        header="Save login"
        description={(
          <>
            <Typography>You manually visited the website </Typography>
            <Link rel="noopener" href={websiteURL}>{websiteURL}<ArrowTopRightOnSquareIcon className="icon-small"/></Link>
            <Typography>
              Do you want to save the potential login as successful?
            </Typography>
          </>
        )}
      />
      <AddEditWebsite
        loading={loadingEditData}
        value={editWebsiteValue}
        open={editDialogOpen}
        add={false}
        ref={editWebsiteDialogRef}
        onClose={() => handleEditCloseDialog()}
        onChange={value => void handleEdit(value)}
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
        <MenuItem onClick={() => void handlePause()}>
          <ListItemIcon>
            {editWebsiteValue?.paused
              ? <PlayCircleIcon className="icon" />
              : <PauseCircleIcon className="icon" />}
          </ListItemIcon>
          <ListItemText primary={`${editWebsiteValue?.paused ? 'Resume' : 'Pause'} automatic login`} />
        </MenuItem>
        <MenuItem onClick={() => void triggerLogin()}>
          <ListItemIcon>
            <ArrowPathIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Trigger automatic login" />
        </MenuItem>
        <MenuItem onClick={handleOpenWebsite}>
          <ListItemIcon>
            <GlobeAltIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Open website" />
        </MenuItem>
        <MenuItem onClick={() => void handleAddManualLogin()}>
          <ListItemIcon>
            <CheckCircleIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Save successful login" />
        </MenuItem>
        <MenuItem onClick={() => void handleOpenEditDialog()}>
          <ListItemIcon>
            <PencilSquareIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Edit" />
        </MenuItem>
        <Divider />
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
