import type { ReactNode } from 'react'
import Background from './Background.tsx'
import Header from './Header.tsx'
import './Content.scss'

interface ContentProps {
  /**
   * Whether to show the navigation header
   */
  header?: boolean
  children?: ReactNode
}

export default function Content({ header, children }: ContentProps) {
  return (
    <>
      <Background />
      <div className="content-layout">
        {header && <Header />}
        <div className="content-root">
          <div className="content">
            {children}
          </div>
        </div>
      </div>
    </>
  )
}
