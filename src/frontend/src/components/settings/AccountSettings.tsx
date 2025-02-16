import type { UserData } from '../../api/apiModels.ts'
import { ArrowRightEndOnRectangleIcon, UserCircleIcon } from '@heroicons/react/24/solid'
import { Chip, ListItemIcon, ListItemText, MenuItem, Popover } from '@mui/material'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { getUserData, logoutUser } from '../../api/apiRequests.ts'
import { useSnackbar } from '../provider/SnackbarProvider.tsx'
import './AccountSettings.scss'

export default function AccountSettings() {
  const [userData, setUserData] = useState<UserData | null>(null)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const navigate = useNavigate()
  const { clear, error, loading } = useSnackbar()

  useEffect(() => {
    getUserData()
      .then(data => setUserData(data))
      .catch(error => console.error(error))
  }, [])

  const handleOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  async function logout() {
    handleClose()
    loading('Logging out...')
    try {
      await logoutUser()
      clear()
      await navigate('/login')
    }
    catch (e) {
      error('Failed to logout', (e as Error).message)
    }
  }

  return (
    <div className="account-settings-button">
      <Chip

        label={userData?.username ?? 'Unknown'}
        icon={<UserCircleIcon className="icon" />}
        onClick={handleOpen}
        variant="outlined"
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
        style={{ marginTop: 8 }}
      >
        <MenuItem onClick={() => void logout()}>
          <ListItemIcon>
            <ArrowRightEndOnRectangleIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Log out" />
        </MenuItem>
      </Popover>
    </div>
  )
}
