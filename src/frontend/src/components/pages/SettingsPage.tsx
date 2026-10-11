import { ArrowLeftIcon } from '@heroicons/react/24/solid'
import { IconButton, Typography } from '@mui/material'
import { useNavigate } from 'react-router'
import Content from '../layout/Content.tsx'
import AccountButton from '../settings/AccountButton.tsx'
import SettingsContent from '../settings/SettingsContent.tsx'
import ProtectedPage from './ProtectedPage.tsx'
import './MainPage.scss'

export default function SettingsPage() {
  const navigate = useNavigate()

  return (
    <ProtectedPage>
      <AccountButton />
      <Content>
        <div className="main-page">
          <div className="main-page-header">
            <IconButton onClick={async () => navigate(-1)}><ArrowLeftIcon className="icon" /></IconButton>
            <Typography variant="h4">Settings</Typography>
          </div>
          <SettingsContent />
        </div>
      </Content>
    </ProtectedPage>
  )
}
