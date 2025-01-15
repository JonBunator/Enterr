import { useState } from 'react'

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
          src={`/api/screenshot/${screenshotId}`}
          alt="Login Screenshot"
          onError={handleError}
        />
      )}
    </>
  )
}
