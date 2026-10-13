import { Typography } from '@mui/material'
import TimeDifference from './TimeDifference.tsx'

interface ExpirationDateProps {
  /**
   * The expiration date of the activity. If undefined, it will be displayed as "Unknown".
   */
  expirationDate?: Date
}

export default function ExpirationDate(props: ExpirationDateProps) {
  const { expirationDate } = props

  if (expirationDate === undefined) {
    return (
      <Typography sx={{ fontSize: 14 }}>
        Unknown
      </Typography>
    )
  }

  return (
    <Typography component="div" sx={{ fontSize: 14 }}>
      <TimeDifference
        datetime={expirationDate}
        tooltip
        negativeDifference="Might be expired"
      />
    </Typography>
  )
}
