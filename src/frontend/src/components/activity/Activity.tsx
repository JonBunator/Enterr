import type { ChangeEvent } from 'react'
import {
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  Tooltip,
  Typography,
} from '@mui/material'
import { motion } from 'framer-motion'
import React, { useEffect, useState } from 'react'
import { useWebSocket } from '../WebSocketProvider.tsx'
import ActionsPopover from './ActionsPopover.tsx'
import { getActivity } from './activityRequests.ts'
import ActivityStatus from './ActivityStatus.tsx'
import StatusIcon, { ActivityStatusCode } from './StatusIcon.tsx'
import TimeDifference from './TimeDifference.tsx'
import './Activity.scss'

interface ActivityRow {
  id: number
  status: ActivityStatusCode
  name: string
  nextLogin: Date
  expirationDate?: Date
  loginHistory: ActivityStatusCode[]
  screenshots: string
}

enum Order {
  ASC = 'asc',
  DESC = 'desc,',
}

type OrderType = 'asc' | 'desc'

export default function Activity() {
  const [order, setOrder] = useState<Order>(Order.ASC)
  const [orderBy, setOrderBy] = useState<keyof ActivityRow>('status')
  const [page, setPage] = useState<number>(0)
  const [rowsPerPage, setRowsPerPage] = useState<number>(10)
  const [rawData, setRawData] = useState<ActivityRow[]>([])
  const [processedData, setProcessedData] = useState<ActivityRow[]>([])

  const { on } = useWebSocket()

  function fetchData() {
    getActivity()
      .then((data) => { setRawData(data) })
      .catch(console.error)
  }

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    on('login_data_changed', (_d) => {
      fetchData()
    })
  }, [on])

  useEffect(() => {
    on('action_history_changed', (_d) => {
      fetchData()
    })
  }, [on])

  const handleSortRequest = async (property: keyof ActivityRow) => {
    const isAsc = orderBy === property && order === Order.ASC
    setOrder(isAsc ? Order.DESC : Order.ASC)
    setOrderBy(property)
  }

  const handleChangePage = (_event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(Number.parseInt(event.target.value, 10))
    setPage(0)
  }

  useEffect(() => {
    const sortedData = rawData.slice().sort((a, b) => {
      if (orderBy === 'status') {
        const statusOrder = [
          ActivityStatusCode.IN_PROGRESS,
          ActivityStatusCode.FAILED,
          ActivityStatusCode.PAUSED,
          ActivityStatusCode.SUCCESS,
        ]
        const aIndex = statusOrder.indexOf(a.status)
        const bIndex = statusOrder.indexOf(b.status)
        return order === Order.ASC ? aIndex - bIndex : bIndex - aIndex
      }
      if (orderBy === 'nextLogin') {
        return order === Order.ASC ? a[orderBy].getTime() - b[orderBy].getTime() : b[orderBy].getTime() - a[orderBy].getTime()
      }
      return order === Order.ASC
        ? (a[orderBy] as string).localeCompare(b[orderBy] as string)
        : (b[orderBy] as string).localeCompare(a[orderBy] as string)
    })

    const paginatedData = sortedData.slice(
      page * rowsPerPage,
      page * rowsPerPage + rowsPerPage,
    )
    setProcessedData(paginatedData)
  }, [rawData, order, orderBy, page, rowsPerPage])

  return (
    <Card className="activity" component={motion.div} layout initial={{ height: 0 }} animate={{ height: 'auto' }}>
      <CardContent className="activity-card" component={motion.div} layout>
        <TableContainer sx={{ height: 600, width: 1100 }} component={motion.div} layout>
          <Table stickyHeader className="activity-table" component={motion.table} layout>
            <TableHead component={motion.thead} layout>
              <TableRow component={motion.tr} layout>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'status'}
                    direction={(orderBy === 'status' ? order : Order.ASC) as OrderType}
                    onClick={() => void handleSortRequest('status')}
                  >
                    Status
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'name'}
                    direction={(orderBy === 'name' ? order : Order.ASC) as OrderType}
                    onClick={() => void handleSortRequest('name')}
                  >
                    Name
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'nextLogin'}
                    direction={(orderBy === 'nextLogin' ? order : Order.ASC) as OrderType}
                    onClick={() => void handleSortRequest('nextLogin')}
                  >
                    Schedule of Next Login
                  </TableSortLabel>
                </TableCell>
                <TableCell>Login History</TableCell>
                <TableCell>Screenshots</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody component={motion.tbody} layout>
              {processedData.map(row => (
                <TableRow
                  key={row.id}
                  component={motion.tr}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  layout
                >
                  <TableCell>
                    <ActivityStatus
                      status={row.status}
                      expirationDate={row.expirationDate}
                    />
                  </TableCell>
                  <TableCell>{row.name}</TableCell>
                  <TableCell>
                    <TimeDifference
                      prefix="Next login in "
                      datetime={row.nextLogin}
                      negativeDifference="No login scheduled"
                    />
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Show login history">
                      <div className="login-history">
                        {row.loginHistory.slice(0, 3).map((status, index) => (
                          <StatusIcon key={index} activityStatus={status} />
                        ))}
                        {row.loginHistory.length > 3
                        && <Typography>...</Typography>}
                      </div>
                    </Tooltip>
                  </TableCell>
                  <TableCell>{row.screenshots}</TableCell>
                  <TableCell>
                    <ActionsPopover websiteId={row.id} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {processedData.length > 0
        && (
          <TablePagination
            rowsPerPageOptions={[10, 20, 50]}
            colSpan={5}
            component={motion.div}
            layout
            count={processedData.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        )}
      </CardContent>
    </Card>
  )
}
