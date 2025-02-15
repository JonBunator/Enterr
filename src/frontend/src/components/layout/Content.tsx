import type { ReactNode } from 'react'
import Background from './Background.tsx'
import './Content.scss'

interface ContentProps {
  children?: ReactNode
}

export default function Content({ children }: ContentProps) {
  return (
    <>
      <Background />
      <div className="content-root">
        <div className="content">
          {children}
        </div>
      </div>
    </>
  )
}
