import { CheckIcon, XMarkIcon } from '@heroicons/react/24/solid'

import { CircularProgress } from '@mui/material'
import './StatusIcon.scss'

export enum ActivityStatusCode {
  RUNNING = 0,
  ERROR = 1,
  PAUSED = 2,
  SUCCESS = 3,
}

interface StatusIconProps {
  activityStatus: ActivityStatusCode
  hover?: boolean
  clickable?: boolean
}

export default function StatusIcon(props: StatusIconProps) {
  const { activityStatus, hover, clickable } = props
  let icon
  let type
  switch (activityStatus) {
    case ActivityStatusCode.SUCCESS:
      icon = <CheckIcon />
      type = 'success'
      break
    case ActivityStatusCode.ERROR:
      icon = <XMarkIcon />
      type = 'error'
      break
    case ActivityStatusCode.RUNNING:
      icon = <CircularProgress size={14} />
      type = 'running'
      break
    case ActivityStatusCode.PAUSED:
      icon = <span>!</span>
      type = 'paused'
      break
    default:
      icon = null
      type = ''
  }
  const additonalStyles = (hover ? 'hover' : '') + (clickable ? ' clickable hover' : '')

  return (
    <div className={`status-icon-container ${additonalStyles} ${type}`}>{icon}</div>
  )
}
