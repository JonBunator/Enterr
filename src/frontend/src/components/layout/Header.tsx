import { ArrowTopRightOnSquareIcon, Cog6ToothIcon, HomeIcon } from '@heroicons/react/24/solid'
import { Tab, Tabs } from '@mui/material'
import { matchPath, NavLink, useLocation } from 'react-router'
import AccountButton from '../settings/AccountButton.tsx'
import './Header.scss'

const navItems = [
  { path: '/', label: 'Home', icon: HomeIcon },
  { path: '/settings', label: 'Settings', icon: Cog6ToothIcon },
]

export default function Header() {
  const location = useLocation()
  const selectedTab = navItems.find(({ path }) =>
    matchPath({ path, end: path === '/' }, location.pathname),
  )?.path ?? false

  return (
    <header className="app-header">
      <div className="app-header-inner">
        <nav className="app-header-nav">
          <Tabs value={selectedTab}>
            {navItems.map(({ path, label, icon: Icon }) => (
              <Tab
                key={path}
                component={NavLink}
                to={path}
                end={path === '/'}
                value={path}
                label={label}
                icon={<Icon className="icon" />}
                iconPosition="start"
              />
            ))}
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
