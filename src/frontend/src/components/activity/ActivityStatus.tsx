import type { ActivityStatusCode } from './StatusIcon.tsx'
import { Chip, Tooltip } from '@mui/material'
import { getStatusConfig } from './statusConfig.tsx'

interface ActivityStatusProps {
  status: ActivityStatusCode
}

export default function ActivityStatus(props: ActivityStatusProps) {
  const { status } = props
  const { label, description, color, icon } = getStatusConfig(status)

  return (
    <Tooltip title={description} arrow>
      <Chip className="activity-status-chip" label={label} color={color} icon={icon} />
    </Tooltip>
  )
}
