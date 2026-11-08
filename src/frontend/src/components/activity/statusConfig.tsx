import type { ChipProps } from '@mui/material'
import { ClockIcon } from '@heroicons/react/24/outline'
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/solid'
import { CircularProgress } from '@mui/material'
import { WebsiteStatusCode } from '../../api/apiModels.ts'

export interface StatusConfig {
  label: string
  description: string
  color: NonNullable<Exclude<ChipProps['color'], 'default'>>
  icon: ChipProps['icon']
}

export function getStatusConfig(status: WebsiteStatusCode): StatusConfig {
  switch (status) {
    case WebsiteStatusCode.SUCCESS:
      return {
        label: 'Success',
        description: 'The last login attempt was successful.',
        color: 'success',
        icon: <CheckIcon />,
      }
    case WebsiteStatusCode.FAILED:
      return {
        label: 'Failed',
        description: 'The last login attempt failed. Check the login history for details.',
        color: 'error',
        icon: <XMarkIcon />,
      }
    case WebsiteStatusCode.NO_LOGIN:
      return {
        label: 'No login',
        description: 'No login has been attempted yet.',
        color: 'error',
        icon: <XMarkIcon />,
      }
    case WebsiteStatusCode.IN_PROGRESS:
      return {
        label: 'Running',
        description: 'A login is currently in progress.',
        color: 'info',
        icon: <CircularProgress size={16} color="inherit" />,
      }
    case WebsiteStatusCode.PAUSED:
      return {
        label: 'Paused',
        description: 'Automatic login is paused. No logins will be scheduled until it is resumed.',
        color: 'warning',
        icon: <ClockIcon />,
      }
  }
}
