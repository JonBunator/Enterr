import { GlobeAltIcon } from '@heroicons/react/24/outline'
import { Typography } from '@mui/material'
import { useState } from 'react'

interface WebsiteNameProps {
  /**
   * The name of the website to display.
   */
  name: string
  /**
   * The URL of the website. This is used to extract the host and to fetch the favicon.
   */
  url: string
}

function parseUrl(url: string): URL | null {
  try {
    return new URL(url)
  }
  catch {
    return null
  }
}

export default function WebsiteName(props: WebsiteNameProps) {
  const { name, url } = props
  const [faviconFailed, setFaviconFailed] = useState(false)

  const parsed = parseUrl(url)
  const host = parsed !== null ? parsed.host : null
  const faviconSrc = parsed !== null ? `${parsed.origin}/favicon.ico` : null

  return (
    <div className="website-name">
      {faviconSrc !== null && !faviconFailed
        ? <img className="favicon" src={faviconSrc} alt="" referrerPolicy="no-referrer" onError={() => setFaviconFailed(true)} />
        : <GlobeAltIcon className="favicon" />}
      <div className="text">
        <Typography className="name" sx={{ fontSize: 14 }}>
          {name}
        </Typography>
        <Typography className="host" sx={{ color: 'text.secondary', fontSize: 12 }}>
          {host}
        </Typography>
      </div>
    </div>
  )
}
