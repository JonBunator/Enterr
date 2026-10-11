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
    if (!image) {
      return
    }
    image.src = `/api/action_history/${actionHistoryId}/live`
    return () => {
      // Remove the src attribute to stop the image from loading when the component is unmounted
      image.removeAttribute('src')
    }
  }, [actionHistoryId])

  if (error) {
    return <Typography className="live-feed-unavailable">Live view not available</Typography>
  }

  return (
    <img
      ref={imageRef}
      className="screenshot"
      alt="Live view of the running login"
      onError={() => setError(true)}
    />
  )
}
