import type { WebsiteStatusCounts } from '../../api/apiModels.ts'
import { Card, CardActionArea, Skeleton, Typography } from '@mui/material'
import { WebsiteStatusCode } from '../../api/apiModels.ts'
import { useWebsiteStatusCounts } from '../../api/hooks'
import { getStatusConfig } from './statusConfig.tsx'
import './StatusSummary.scss'

const summaryStatuses = [
  WebsiteStatusCode.SUCCESS,
  WebsiteStatusCode.FAILED,
  WebsiteStatusCode.PAUSED,
]

interface StatusSummaryProps {
  searchTerm?: string
  selected?: WebsiteStatusCode
  onSelect: (status?: WebsiteStatusCode) => void
}

export default function StatusSummary(props: StatusSummaryProps) {
  const { searchTerm, selected, onSelect } = props
  const { data: counts, isLoading } = useWebsiteStatusCounts(searchTerm)

  return (
    <div className="status-summary">
      {summaryStatuses.map((status) => {
        const { label, color, icon } = getStatusConfig(status)
        const isSelected = selected === status
        const count = counts?.[status.toLowerCase() as keyof WebsiteStatusCounts] ?? 0
        const isDisabled = !isSelected && (isLoading || count === 0)

        return (
          <Card
            key={status}
            className={`status-card status-card-${color} ${isSelected ? 'selected' : ''}`}
          >
            <CardActionArea
              className="status-card-action"
              aria-pressed={isSelected}
              disabled={isDisabled}
              onClick={() => onSelect(isSelected ? undefined : status)}
            >
              <div className="status-card-icon">{icon}</div>
              <div className="status-card-text">
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  {label}
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>
                  {isLoading ? <Skeleton width={100} /> : count}
                </Typography>
              </div>
              {isSelected && (
                <Typography
                  className="status-card-selected"
                  aria-hidden
                  variant="caption"
                  sx={{ color: 'text.secondary', fontStyle: 'italic' }}
                >
                  selected
                </Typography>
              )}
            </CardActionArea>
          </Card>
        )
      })}
    </div>
  )
}
