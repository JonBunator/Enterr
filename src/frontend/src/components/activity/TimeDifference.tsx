import { Tooltip } from '@mui/material'
import { useCallback, useEffect, useState } from 'react'
import './TimeDifference.scss'

interface TimeDifferenceProps {
  datetime: Date
  /**
   * String that is returned when the time difference is negative.
   */
  negativeDifference?: string
  /**
   * Display tooltip with exact time.
   */
  tooltip?: boolean
}

export default function TimeDifference(props: TimeDifferenceProps) {
  const { datetime, negativeDifference, tooltip } = props

  const getFormatedTime = useCallback((): string => {
    const now = new Date()
    const diffInMs = datetime.getTime() - now.getTime()

    let diffInMinutes = Math.ceil(diffInMs / (1000 * 60))
    let suffix = ''

    if (diffInMinutes < -1 && negativeDifference !== undefined) {
      return negativeDifference
    }

    if (diffInMs < 0) {
      suffix = ' ago'
      diffInMinutes = Math.abs(diffInMinutes)
    }

    const diffInHours = Math.floor(diffInMinutes / 60)
    const diffInDays = Math.floor(diffInHours / 24)
    const remainingMinutes = diffInMinutes % 60
    if (diffInMinutes === 0 || diffInMinutes === -1) {
      return `<1min${suffix}`
    }
    if (diffInDays > 0) {
      return `${diffInDays}d${suffix}`
    }
    else if (diffInHours > 0) {
      return `${diffInHours}h${remainingMinutes > 0 ? ` ${remainingMinutes}m` : ''}${suffix}`
    }
    else {
      return `${diffInMinutes}m${suffix}`
    }
  }, [datetime, negativeDifference])

  const [formattedTime, setFormattedTime] = useState<string>(getFormatedTime())

  useEffect(() => {
    const interval = setInterval(() => {
      setFormattedTime(getFormatedTime())
    }, 60000) // Update every 60 seconds

    return () => clearInterval(interval)
  }, [getFormatedTime])

  useEffect(() => {
    setFormattedTime(getFormatedTime())
  }, [datetime, getFormatedTime])

  return (
    tooltip && formattedTime !== negativeDifference
      ? (
          <Tooltip title={datetime.toLocaleString()}>
            <div className="time-diff">
              {formattedTime}
            </div>
          </Tooltip>
        )
      : (
          <div>
            {formattedTime}
          </div>
        )
  )
}
