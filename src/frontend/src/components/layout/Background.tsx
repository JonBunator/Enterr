import type { ReactNode } from 'react'
import './Background.scss'

interface BackgroundProps {
  children?: ReactNode
}

export default function Background(props: BackgroundProps) {
  const { children } = props
  return (
    <div className="background">
      <div className="background-grid">
        <div className="background-feather">{children}</div>
      </div>
    </div>
  )
}
