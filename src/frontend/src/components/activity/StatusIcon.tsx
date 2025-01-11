import type { ReactNode } from 'react'
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/solid'
import { CircularProgress } from '@mui/material'

import { useEffect, useState } from 'react'
import './StatusIcon.scss'

export enum ActivityStatusCode {
  IN_PROGRESS = 'IN_PROGRESS',
  FAILED = 'FAILED',
  PAUSED = 'PAUSED',
  SUCCESS = 'SUCCESS',
}

interface StatusIconProps {
  activityStatus: ActivityStatusCode
  hover?: boolean
}

export default function StatusIcon(props: StatusIconProps) {
  const { activityStatus, hover } = props
  const [type, setType] = useState<string>('')
  const [icon, setIcon] = useState<ReactNode | null>(null)

  useEffect(() => {
    let i
    let t
    switch (activityStatus) {
      case ActivityStatusCode.SUCCESS:
        i = <CheckIcon />
        t = 'success'
        break
      case ActivityStatusCode.FAILED:
        i = <XMarkIcon />
        t = 'error'
        break
      case ActivityStatusCode.IN_PROGRESS:
        i = <CircularProgress size={14} />
        t = 'running'
        break
      case ActivityStatusCode.PAUSED:
        i = <span>!</span>
        t = 'paused'
        break
      default:
        i = null
        t = ''
    }
    setIcon(i)
    setType(t)
  }, [activityStatus])

  return (
    <div className={`status-icon-container ${hover === true ? 'hover' : hover} ${type}`}>{icon}</div>
  )
}
