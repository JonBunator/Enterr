import { Typography } from '@mui/material'
import StatusIcon, { ActivityStatusCode } from './StatusIcon.tsx'
import TimeDifference from './TimeDifference.tsx'

interface ActivityStatusProps {
  status: ActivityStatusCode
  expirationDate?: Date
}

export default function ActivityStatus(props: ActivityStatusProps) {
  const { status, expirationDate } = props

  function getInfoText(): string {
    switch (status) {
      case ActivityStatusCode.SUCCESS:
        return 'Last pages was successful'
      case ActivityStatusCode.FAILED:
        return 'Last pages failed'
      case ActivityStatusCode.IN_PROGRESS:
        return 'Currently running...'
      case ActivityStatusCode.PAUSED:
        return 'Automatic pages is paused'
    }
  }

  return (
    <div className="activity-status">
      <StatusIcon activityStatus={status} />
      <div className="text">
        <Typography className="next-run" sx={{ fontSize: 14 }}>
          {getInfoText()}
        </Typography>
        <Typography className="expiration" sx={{ color: 'text.secondary', fontSize: 12 }}>
          {expirationDate !== undefined
            ? <TimeDifference prefix="Account expires in " datetime={expirationDate} negativeDifference="Account might be expired" />
            : 'Account expires at unknown date'}
        </Typography>
      </div>
    </div>
  )
}
