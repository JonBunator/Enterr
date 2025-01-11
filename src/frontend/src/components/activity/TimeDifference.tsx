import { useCallback, useEffect, useState } from 'react'

interface TimeDifferenceProps {
  datetime: Date
  /**
   * Prefix of the formatted time difference.
   */
  prefix?: string
  /**
   * String that is returned when the time difference is negative.
   */
  negativeDifference?: string
}

export default function TimeDifference(props: TimeDifferenceProps) {
  const { datetime, prefix, negativeDifference } = props

  const getFormatedTime = useCallback((): string => {
    const now = new Date()
    const diffInMs = datetime.getTime() - now.getTime()

    const diffInMinutes = Math.ceil(diffInMs / (1000 * 60))
    if (diffInMinutes < -1) {
      return negativeDifference ?? 'Time difference is negative'
    }

    const diffInHours = Math.floor(diffInMinutes / 60)
    const diffInDays = Math.floor(diffInHours / 24)
    const remainingMinutes = diffInMinutes % 60
    const prefixString = prefix ?? ''
    if (diffInMinutes === 0 || diffInMinutes === -1) {
      return `${prefixString}>1min`
    }
    if (diffInDays > 0) {
      return `${prefixString}${diffInDays}d}`
    }
    else if (diffInHours > 0) {
      return `${prefixString}${diffInHours}h${remainingMinutes > 0 ? ` ${remainingMinutes}m` : ''}`
    }
    else {
      return `${prefixString}${diffInMinutes}m`
    }
  }, [datetime, negativeDifference, prefix])

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
    <>
      {formattedTime}
    </>
  )
}
