import { Link, Typography } from '@mui/material'
import { ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline'

interface ExternalLinkProps {
  /**
   * The URL the link points to
   */
  href: string
  /**
   * The text to display. Use INSERT_LINK as placeholder for the link.
   * Example: "Visit INSERT_LINK for more information."
   */
  text: string
  /**
   * The text to display for the link itself
   */
  linkText: string
}

export default function ExternalLink(props: ExternalLinkProps) {
  const { href, text, linkText } = props;
  const parts = text.split('INSERT_LINK')

  return (
    <Typography>
      {parts[0]}
      <Link rel="noopener" target="_blank" href={href}>
        {linkText}
        <ArrowTopRightOnSquareIcon className="icon-small" />
      </Link>
      {parts[1]}
    </Typography>
  )
}
