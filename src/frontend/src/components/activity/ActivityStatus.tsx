import type { ChipProps } from '@mui/material'
import { ClockIcon } from '@heroicons/react/24/outline'
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/solid'
import { Chip, CircularProgress, Tooltip } from '@mui/material'
import { ActivityStatusCode } from './StatusIcon.tsx'

interface ActivityStatusProps {
  status: ActivityStatusCode
}

interface StatusConfig {
  label: string
  description: string
  color: ChipProps['color']
  icon: ChipProps['icon']
}

export default function ActivityStatus(props: ActivityStatusProps) {
  const { status } = props

  function getConfig(): StatusConfig {
    switch (status) {
      case ActivityStatusCode.SUCCESS:
        return {
          label: 'Success',
          description: 'The last login attempt was successful.',
          color: 'success',
          icon: <CheckIcon />,
        }
      case ActivityStatusCode.FAILED:
        return {
          label: 'Failed',
          description: 'The last login attempt failed. Check the login history for details.',
          color: 'error',
          icon: <XMarkIcon />,
        }
      case ActivityStatusCode.IN_PROGRESS:
        return {
          label: 'Running',
          description: 'A login is currently in progress.',
          color: 'info',
          icon: <CircularProgress size={16} color="inherit" />,
        }
      case ActivityStatusCode.PAUSED:
        return {
          label: 'Paused',
          description: 'Automatic login is paused. No logins will be scheduled until it is resumed.',
          color: 'warning',
          icon: <ClockIcon />,
        }
    }
  }

  const { label, description, color, icon } = getConfig()

  return (
    <Tooltip title={description} arrow>
      <Chip className="activity-status-chip" label={label} color={color} icon={icon} />
    </Tooltip>
  )
}
