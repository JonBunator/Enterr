import type { WebsiteStatusCounts } from '../../api/apiModels.ts'
import { Card, CardActionArea, Skeleton, Typography } from '@mui/material'
import { useWebsiteStatusCounts } from '../../api/hooks'
import { getStatusConfig } from './statusConfig.tsx'
import { ActivityStatusCode } from './StatusIcon.tsx'
import './StatusSummary.scss'

const summaryStatuses = [
  ActivityStatusCode.SUCCESS,
  ActivityStatusCode.FAILED,
  ActivityStatusCode.PAUSED,
]

interface StatusSummaryProps {
  searchTerm?: string
  selected: ActivityStatusCode | null
  onSelect: (status: ActivityStatusCode | null) => void
}

export default function StatusSummary(props: StatusSummaryProps) {
  const { searchTerm, selected, onSelect } = props
  const { data: counts, isLoading } = useWebsiteStatusCounts(searchTerm)

  return (
    <div className="status-summary">
      {summaryStatuses.map((status) => {
        const { label, color, icon } = getStatusConfig(status)
        const isSelected = selected === status

        return (
          <Card
            key={status}
            className={`status-card status-card-${color} ${isSelected ? 'selected' : ''}`}
          >
            <CardActionArea
              className="status-card-action"
              aria-pressed={isSelected}
              onClick={() => onSelect(isSelected ? null : status)}
            >
              <div className="status-card-icon">{icon}</div>
              <div className="status-card-text">
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  {label}
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>
                  {isLoading ? <Skeleton width={100} /> : (counts?.[status.toLowerCase() as keyof WebsiteStatusCounts] ?? 0)}
                </Typography>
              </div>
            </CardActionArea>
          </Card>
        )
      })}
    </div>
  )
}
