import { Typography } from '@mui/material'
import SettingsContent from '../settings/SettingsContent.tsx'
import './MainPage.scss'

export default function SettingsPage() {
  return (
    <div className="main-page">
      <div className="main-page-header">
        <Typography variant="h4">Settings</Typography>
      </div>
      <SettingsContent />
    </div>
  )
}
