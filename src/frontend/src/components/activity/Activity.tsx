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
import React, { useEffect, useState } from 'react'
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

const sampleData: ActivityRow[] = [
  {
    id: 1,
    status: ActivityStatusCode.RUNNING,
    name: 'Test Website',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 25),
    loginHistory: [
      ActivityStatusCode.PAUSED,
      ActivityStatusCode.ERROR,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'None',
  },
  {
    id: 2,
    status: ActivityStatusCode.SUCCESS,
    name: 'This is',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },
  {
    id: 3,
    status: ActivityStatusCode.ERROR,
    name: 'Jane Smith',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },
  {
    id: 4,
    status: ActivityStatusCode.ERROR,
    name: 'Jane Smith',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },
  {
    id: 5,
    status: ActivityStatusCode.PAUSED,
    name: 'Jane Smith',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },
  {
    id: 6,
    status: ActivityStatusCode.SUCCESS,
    name: 'Jane Smith',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },
  {
    id: 7,
    status: ActivityStatusCode.SUCCESS,
    name: 'Jane Smith',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },
  {
    id: 8,
    status: ActivityStatusCode.SUCCESS,
    name: 'Jane Smith',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },
  {
    id: 9,
    status: ActivityStatusCode.SUCCESS,
    name: 'Jane Smith',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },
  {
    id: 10,
    status: ActivityStatusCode.SUCCESS,
    name: 'Jane Smith',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },
  {
    id: 11,
    status: ActivityStatusCode.SUCCESS,
    name: 'Jane Smith',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },
  {
    id: 12,
    status: ActivityStatusCode.SUCCESS,
    name: 'Jane Smith',
    nextLogin: new Date(new Date().getTime() + 1000 * 60 * 60 * 50),
    loginHistory: [
      ActivityStatusCode.SUCCESS,
      ActivityStatusCode.SUCCESS,
    ],
    screenshots: 'Available',
  },

]

export default function Activity() {
  const [order, setOrder] = useState<Order>(Order.ASC)
  const [orderBy, setOrderBy] = useState<keyof ActivityRow>('status')
  const [page, setPage] = useState<number>(0)
  const [rowsPerPage, setRowsPerPage] = useState<number>(10)
  const [processedData, setProcessedData] = useState<ActivityRow[]>([])

  const handleSortRequest = (property: keyof ActivityRow) => {
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
    const sortedData = sampleData.slice().sort((a, b) => {
      if (orderBy === 'status') {
        const statusOrder = [
          ActivityStatusCode.RUNNING,
          ActivityStatusCode.ERROR,
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
  }, [order, orderBy, page, rowsPerPage])

  return (
    <Card className="activity">
      <CardContent className="activity-card">
        <TableContainer sx={{ height: 600, width: 900 }}>
          <Table stickyHeader className="activity-table">
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'status'}
                    direction={(orderBy === 'status' ? order : Order.ASC) as OrderType}
                    onClick={() => handleSortRequest('status')}
                  >
                    Status
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'name'}
                    direction={(orderBy === 'name' ? order : Order.ASC) as OrderType}
                    onClick={() => handleSortRequest('name')}
                  >
                    Name
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'nextLogin'}
                    direction={(orderBy === 'nextLogin' ? order : Order.ASC) as OrderType}
                    onClick={() => handleSortRequest('nextLogin')}
                  >
                    Schedule of Next Login
                  </TableSortLabel>
                </TableCell>
                <TableCell>Login History</TableCell>
                <TableCell>Screenshots</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {processedData.map(row => (
                <TableRow key={row.id}>
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
                        {row.loginHistory.map((status, index) => (
                          <StatusIcon key={index} activityStatus={status} />
                        ))}
                        <Typography>...</Typography>
                      </div>
                    </Tooltip>
                  </TableCell>
                  <TableCell>{row.screenshots}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[9, 20, 50]}
          colSpan={5}
          component="div"
          count={sampleData.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </CardContent>
    </Card>
  )
}
