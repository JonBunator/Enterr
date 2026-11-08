import { ArrowTopRightOnSquareIcon, Cog6ToothIcon, HomeIcon } from '@heroicons/react/24/outline'
import { Button } from '@mui/material'
import { useLayoutEffect, useRef, useState } from 'react'
import { NavLink, useLocation } from 'react-router'
import AccountButton from '../settings/AccountButton.tsx'
import './Header.scss'

interface Indicator {
  left: number
  width: number
}

export default function Header() {
  const location = useLocation()
  const navRef = useRef<HTMLElement>(null)
  const [indicator, setIndicator] = useState<Indicator>()
  const [animate, setAnimate] = useState(false)

  useLayoutEffect(() => {
    const nav = navRef.current
    if (!nav)
      return

    const measure = () => {
      const active = nav.querySelector<HTMLElement>('.active')
      setIndicator(active ? { left: active.offsetLeft, width: active.offsetWidth } : undefined)
    }
    measure()

    const observer = new ResizeObserver(measure)
    observer.observe(nav)
    return () => observer.disconnect()
  }, [location.pathname])

  // Enable the transition only after the initial position is painted, so the
  // underline doesn't slide in from the left on first load
  useLayoutEffect(() => {
    if (indicator && !animate) {
      const frame = requestAnimationFrame(() => setAnimate(true))
      return () => cancelAnimationFrame(frame)
    }
  }, [indicator, animate])

  return (
    <header className="app-header">
      <div className="app-header-inner">
        <nav className="app-header-nav" ref={navRef}>
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
          <span
            className={`app-header-indicator${animate ? ' animate' : ''}`}
            style={{
              opacity: indicator ? 1 : 0,
              width: indicator?.width ?? 0,
              transform: `translateX(${indicator?.left ?? 0}px)`,
            }}
          />
        </nav>
        <div className="app-header-spacer" />
        <AccountButton />
      </div>
    </header>
  )
}
