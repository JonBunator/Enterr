import { Typography } from '@mui/material'
import { useEffect, useRef, useState } from 'react'

interface LiveFeedProps {
  actionHistoryId: number
}

export default function LiveFeed(props: LiveFeedProps) {
  const { actionHistoryId } = props
  const [error, setError] = useState(false)
  const imageRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    const image = imageRef.current
    return () => {
      // Removing the image from the DOM does not reliably abort the stream
      if (image) {
        image.src = ''
      }
    }
  }, [actionHistoryId])

  const handleError = () => {
    setError(true)
  }

  if (error) {
    return <Typography className="live-feed-unavailable">Live view not available</Typography>
  }

  return (
    <img
      ref={imageRef}
      className="screenshot"
      src={`/api/action_history/${actionHistoryId}/live`}
      alt="Live view of the running login"
      onError={handleError}
    />
  )
}
