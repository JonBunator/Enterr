import { useState } from 'react'
import { getScreenshotUrl } from '../../api/hooks/useScreenshot.ts'

interface ScreenshotProps {
  screenshotId: string
}

export default function Screenshot(props: ScreenshotProps) {
  const { screenshotId } = props
  const [error, setError] = useState(false)

  const handleError = () => {
    setError(true)
  }

  return (
    <>
      {!error && (
        <img
          className="screenshot"
          src={getScreenshotUrl(screenshotId)}
          alt="Login Screenshot"
          onError={handleError}
        />
      )}
    </>
  )
}
