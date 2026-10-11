import { Typography } from '@mui/material'
import { useEffect, useRef, useState } from 'react'

// The live view is briefly unavailable right after a login starts
const MAX_RETRIES = 3
const RETRY_DELAY_MS = 2000

interface LiveFeedProps {
  actionHistoryId: number
}

export default function LiveFeed(props: LiveFeedProps) {
  const { actionHistoryId } = props
  const [attempt, setAttempt] = useState(0)
  const [retrying, setRetrying] = useState(false)
  const [error, setError] = useState(false)
  const imageRef = useRef<HTMLImageElement>(null)
  const retryTimeoutRef = useRef<number | undefined>(undefined)

  useEffect(() => {
    const image = imageRef.current
    return () => {
      window.clearTimeout(retryTimeoutRef.current)
      // Removing the image from the DOM does not reliably abort the stream
      if (image) {
        image.src = ''
      }
    }
  }, [actionHistoryId])

  const handleError = () => {
    if (attempt >= MAX_RETRIES) {
      setError(true)
      return
    }
    setRetrying(true)
    retryTimeoutRef.current = window.setTimeout(() => {
      setRetrying(false)
      setAttempt(previous => previous + 1)
    }, RETRY_DELAY_MS)
  }

  if (error) {
    return <Typography className="live-feed-unavailable">Live view not available</Typography>
  }

  const src = `/api/action_history/${actionHistoryId}/live`
  return (
    <img
      ref={imageRef}
      className="screenshot"
      // A new url makes the browser request the stream again
      src={attempt === 0 ? src : `${src}?attempt=${attempt}`}
      alt="Live view of the running login"
      // Hides the broken image icon until the next attempt
      style={retrying ? { display: 'none' } : undefined}
      onError={handleError}
    />
  )
}
