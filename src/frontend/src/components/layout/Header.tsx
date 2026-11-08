import { ArrowTopRightOnSquareIcon, Cog6ToothIcon, HomeIcon } from '@heroicons/react/24/solid'
import { Button, Tab, Tabs } from '@mui/material'
import { NavLink, useLocation } from 'react-router'
import AccountButton from '../settings/AccountButton.tsx'
import './Header.scss'

const navPaths = ['/', '/settings']

export default function Header() {
  const location = useLocation()
  const selectedTab = navPaths.includes(location.pathname) ? location.pathname : false

  return (
    <header className="app-header">
      <div className="app-header-inner">
        <nav className="app-header-nav">
          <Tabs value={selectedTab}>
            <Tab
              component={NavLink}
              to="/"
              value="/"
              label="Home"
              icon={<HomeIcon className="icon" />}
              iconPosition="start"
            />
            <Tab
              component={NavLink}
              to="/settings"
              value="/settings"
              label="Settings"
              icon={<Cog6ToothIcon className="icon" />}
              iconPosition="start"
            />
          </Tabs>
          <Button
            component="a"
            href="https://github.com/JonBunator/Enterr/wiki"
            target="_blank"
            rel="noopener"
            endIcon={<ArrowTopRightOnSquareIcon className="icon" />}
          >
            Docs
          </Button>
        </nav>
        <div className="app-header-spacer" />
        <AccountButton />
      </div>
    </header>
  )
}
