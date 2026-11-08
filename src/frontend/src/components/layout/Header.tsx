import { ArrowTopRightOnSquareIcon, Cog6ToothIcon, HomeIcon } from '@heroicons/react/24/solid'
import { Tab, Tabs } from '@mui/material'
import { NavLink, useLocation } from 'react-router'
import AccountButton from '../settings/AccountButton.tsx'
import './Header.scss'

const navPaths = ['/', '/settings']

function isNavPathActive(path: string, pathname: string) {
  return path === '/' ? pathname === '/' : pathname === path || pathname.startsWith(`${path}/`)
}

export default function Header() {
  const location = useLocation()
  const selectedTab = navPaths.find(path => isNavPathActive(path, location.pathname)) ?? false

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
            <Tab
              component="a"
              className="app-header-external-tab"
              href="https://github.com/JonBunator/Enterr/wiki"
              target="_blank"
              rel="noopener noreferrer"
              label="Docs"
              icon={<ArrowTopRightOnSquareIcon className="icon" />}
              iconPosition="end"
            />
          </Tabs>
        </nav>
        <div className="app-header-spacer" />
        <AccountButton />
      </div>
    </header>
  )
}
