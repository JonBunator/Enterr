import { Typography } from '@mui/material'
import Content from '../layout/Content.tsx'
import SettingsContent from '../settings/SettingsContent.tsx'
import ProtectedPage from './ProtectedPage.tsx'
import './MainPage.scss'

export default function SettingsPage() {
  return (
    <ProtectedPage>
      <Content header>
        <div className="main-page">
          <div className="main-page-header">
            <Typography variant="h4">Settings</Typography>
          </div>
          <SettingsContent />
        </div>
      </Content>
    </ProtectedPage>
  )
}
