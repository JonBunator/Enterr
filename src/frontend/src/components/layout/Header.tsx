import { ArrowTopRightOnSquareIcon, Cog6ToothIcon, HomeIcon } from '@heroicons/react/24/outline'
import { Button } from '@mui/material'
import { NavLink } from 'react-router'
import AccountButton from '../settings/AccountButton.tsx'
import './Header.scss'

export default function Header() {
  return (
    <header className="app-header">
      <div className="app-header-inner">
        <nav className="app-header-nav">
          <Button component={NavLink} to="/" end color="inherit" startIcon={<HomeIcon className="icon" />}>
            Home
          </Button>
          <Button component={NavLink} to="/settings" color="inherit" startIcon={<Cog6ToothIcon className="icon" />}>
            Settings
          </Button>
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
