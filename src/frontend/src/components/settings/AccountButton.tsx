import { AdjustmentsHorizontalIcon, ArrowRightEndOnRectangleIcon, UserCircleIcon } from "@heroicons/react/24/solid";
import { Chip, ListItemIcon, ListItemText, MenuItem, Popover } from '@mui/material'
import React, { useState } from 'react'
import { useNavigate } from 'react-router'
import { useSnackbar } from '../provider/SnackbarProvider.tsx'
import './AccountButton.scss'
import { useLogoutUser, useUserData } from "../../api/hooks";

export default function AccountButton() {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const navigate = useNavigate()
  const { clear, error, loading } = useSnackbar();
  const logoutMutation = useLogoutUser()
  const { data: userData, isLoading: userDataLoading, error: userDataError } = useUserData();

  const handleOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  async function openSettings() {
    await navigate('/settings')
  }

  async function logout() {
    handleClose()
    loading('Logging out...')
    try {
      await logoutMutation.mutateAsync();
      clear()
      await navigate('/login')
    }
    catch (e) {
      error('Failed to logout', (e as Error).message)
    }
  }

  let chipLabel = "";
  if (userDataLoading) {
    chipLabel = "Loading...";
  } else if (userDataError || userData == null) {
    chipLabel = "Unknown";
  } else {
    chipLabel = userData.username;
  }

  return (
    <div className="account-settings-button">
      <Chip
        label={chipLabel}
        icon={<UserCircleIcon className="icon" />}
        onClick={handleOpen}
        variant="outlined"
      />

      <Popover
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        style={{ marginTop: 8 }}
      >
        <MenuItem onClick={() => void openSettings()}>
          <ListItemIcon>
            <AdjustmentsHorizontalIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </MenuItem>
        <MenuItem onClick={() => void logout()}>
          <ListItemIcon>
            <ArrowRightEndOnRectangleIcon className="icon" />
          </ListItemIcon>
          <ListItemText primary="Log out" />
        </MenuItem>
      </Popover>
    </div>
  );
}
