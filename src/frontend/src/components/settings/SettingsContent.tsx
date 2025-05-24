import {Divider, Paper, Tab, Tabs} from "@mui/material";
import { useState } from "react";
import { BellAlertIcon } from "@heroicons/react/24/outline";
import {UserCircleIcon} from "@heroicons/react/24/solid";
import NotificationsSettings from "./notifications/NotificationsSettings.tsx";
import AccountSettings from "./AccountSettings.tsx";
import './SettingsContent.scss';

export default function SettingsContent() {

  const [selectedTab, setSelectedTab] = useState(0);

  const handleTabChange = (value: number) => {
    setSelectedTab(value);
  };

  return (
    <Paper className="settings-content">
      <Tabs
        value={selectedTab}
        onChange={(_event, value) => handleTabChange(value)}
        orientation="vertical"
      >
        <Tab
          icon={<BellAlertIcon className="icon" />}
          iconPosition="start"
          label="Notifications"
        />
        <Tab
          icon={<UserCircleIcon className="icon" />}
          iconPosition="start"
          label="Account"
        />
      </Tabs>
      <Divider orientation="vertical" flexItem />
      <div className="settings-content-container">
        {selectedTab === 0 && <NotificationsSettings />}
        {selectedTab === 1 && <AccountSettings />}
      </div>
    </Paper>
  );
}