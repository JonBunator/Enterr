import { Typography } from '@mui/material'
import './EmptyState.scss'

interface EmptyStateProps {
  noData?: boolean
  noDataHelperText?: string
}

export default function EmptyState(props: EmptyStateProps) {
  const { noData, noDataHelperText = '' } = props

  return (
    <div
      className="empty-state"
    >
      <img
        src={noData ? '/images/no-data.svg' : '/images/no-results.svg'}
        alt={noData ? 'no data' : 'no result found'}
      />
      <Typography variant="h6">
        {noData ? 'No data yet!' : 'No results found!'}
      </Typography>
      <Typography sx={{ color: 'text.secondary' }}>
        {noData ? noDataHelperText : 'Try a different search term'}
      </Typography>
    </div>
  )
}
