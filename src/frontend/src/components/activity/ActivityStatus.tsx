import { Typography } from '@mui/material'
import StatusIcon, { ActivityStatusCode } from './StatusIcon.tsx'

interface ActivityStatusProps {
  status: ActivityStatusCode
}

export default function ActivityStatus(props: ActivityStatusProps) {
  const { status } = props

  function getInfoText(): string {
    switch (status) {
      case ActivityStatusCode.SUCCESS:
        return 'Last login was successful'
      case ActivityStatusCode.FAILED:
        return 'Last login failed'
      case ActivityStatusCode.IN_PROGRESS:
        return 'Currently running...'
      case ActivityStatusCode.PAUSED:
        return 'Automatic login is paused'
    }
  }

  return (
    <div className="activity-status">
      <StatusIcon activityStatus={status} />
      <div className="text">
        <Typography className="next-run" sx={{ fontSize: 14 }}>
          {getInfoText()}
        </Typography>
      </div>
    </div>
  )
}
