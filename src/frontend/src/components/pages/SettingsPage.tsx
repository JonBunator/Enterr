import Content from '../layout/Content.tsx'
import ProtectedPage from './ProtectedPage.tsx'
import './MainPage.scss'
import SettingsContent from "../settings/SettingsContent.tsx";
import AccountButton from "../settings/AccountButton.tsx";
import { Typography, IconButton } from "@mui/material";
import { ArrowLeftIcon } from "@heroicons/react/24/solid";
import { useNavigate } from "react-router";

export default function SettingsPage() {

  const navigate = useNavigate();

  return (
    <ProtectedPage>
      <AccountButton />
      <Content>
        <div className="main-page">
          <div className="main-page-header">
            <IconButton onClick={() => navigate(-1)}><ArrowLeftIcon className="icon" /></IconButton>
            <Typography variant="h4">Settings</Typography>
          </div>
          <SettingsContent/>
        </div>
      </Content>
    </ProtectedPage>
  )
}
