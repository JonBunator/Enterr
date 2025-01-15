import { Typography } from '@mui/material'
import { motion } from 'framer-motion'
import './EmptyState.scss'

interface EmptyStateProps {
  noData?: boolean
}

export default function EmptyState(props: EmptyStateProps) {
  const { noData } = props

  const containerAnimation = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { duration: 1 } },
  }

  const imageAnimation = {
    hidden: { opacity: 0, y: 50, scale: 0.1 },
    visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.4 } },
  }

  return (
    <motion.div
      className="empty-state"
      layout
      initial="hidden"
      animate="visible"
      variants={containerAnimation}
      key={noData ? 0 : 1}
    >
      <motion.img
        src={noData ? 'assets/images/no-data.svg' : 'assets/images/no-results.svg'}
        alt={noData ? 'no data' : 'no result found'}
        variants={imageAnimation}
      />
      <Typography variant="h6">
        {noData ? 'No data yet!' : 'No results found!'}
      </Typography>
      <Typography sx={{ color: 'text.secondary' }}>
        {noData ? 'Add a website to get started' : 'Try a different search term'}
      </Typography>
    </motion.div>
  )
}
