import type { ChangeEvent } from 'react'
import type { ActivityData } from './activityRequests.ts'
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
  Typography
} from "@mui/material";
import { motion } from 'framer-motion'
import React, { useEffect, useState } from 'react'
import { useWebSocket } from '../provider/WebSocketProvider.tsx'
import ActionsPopover from './ActionsPopover.tsx'
import { getActivity } from './activityRequests.ts'
import ActivityStatus from './ActivityStatus.tsx'
import EmptyState from './EmptyState.tsx'
import LoginHistoryDetails from './LoginHistoryDetails.tsx'
import { ActivityStatusCode } from './StatusIcon.tsx'
import TimeDifference from './TimeDifference.tsx'
import './Activity.scss'
import ActivitySkeleton from "./ActivitySkeleton.tsx";

enum Order {
  ASC = 'asc',
  DESC = 'desc,',
}

type OrderType = 'asc' | 'desc'

interface ActivityProps {
  searchTerm?: string
}

export default function Activity(props: ActivityProps) {
  const { searchTerm } = props
  const [order, setOrder] = useState<Order>(Order.ASC)
  const [orderBy, setOrderBy]
    = useState<keyof ActivityData>('lastLoginAttempt')
  const [page, setPage] = useState<number>(0)
  const [rowsPerPage, setRowsPerPage] = useState<number>(10)
  const [rawData, setRawData] = useState<ActivityData[]>([])
  const [processedData, setProcessedData] = useState<ActivityData[]>([])
  const [isLoading, setIsLoading] = useState(false);

  const { on } = useWebSocket()

  function fetchData(initialFetch: boolean = true) {
    if(rawData.length === 0 && initialFetch) {
      setIsLoading(true);
    }
    getActivity()
      .then((data) => {
        {setRawData(data); setIsLoading(false);}
      })
      .catch(error => {console.error(error); setIsLoading(false);});
  }

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    on('login_data_changed', (_d) => {
      fetchData(false)
    })
  }, [on])

  useEffect(() => {
    on('action_history_changed', (_d) => {
      fetchData(false)
    })
  }, [on])

  const handleSortRequest = async (property: keyof ActivityData) => {
    const isAsc = orderBy === property && order === Order.ASC
    setOrder(isAsc ? Order.DESC : Order.ASC)
    setOrderBy(property)
  }

  const handleChangePage = (
    _event: React.MouseEvent<HTMLButtonElement> | null,
    newPage: number,
  ) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(Number.parseInt(event.target.value, 10))
    setPage(0)
  }

  function orderByTime(
    order: Order,
    a?: Date,
    b?: Date,
    reverse?: boolean,
  ): number {
    const aTime = a?.getTime() ?? 0
    const bTime = b?.getTime() ?? 0
    if (reverse) {
      order = order === Order.ASC ? Order.DESC : Order.ASC
    }
    return order === Order.ASC ? bTime - aTime : aTime - bTime
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
        const orderByStatus
          = order === Order.ASC ? aIndex - bIndex : bIndex - aIndex
        if (orderByStatus === 0) {
          return orderByTime(order, a.nextLogin, b.nextLogin)
        }
        return orderByStatus
      }
      if (orderBy === 'nextLogin') {
        return orderByTime(order, a[orderBy], b[orderBy], true)
      }
      else if (orderBy === 'lastLoginAttempt') {
        return orderByTime(order, a[orderBy], b[orderBy])
      }
      return order === Order.ASC
        ? (a[orderBy] as string).localeCompare(b[orderBy] as string)
        : (b[orderBy] as string).localeCompare(a[orderBy] as string)
    })

    const filteredData
      = searchTerm !== undefined
        ? sortedData.filter(item =>
            item.name.toLowerCase().includes(searchTerm.toLowerCase()),
          )
        : sortedData

    const paginatedData = filteredData.slice(
      page * rowsPerPage,
      page * rowsPerPage + rowsPerPage,
    )
    setProcessedData(paginatedData)
  }, [rawData, order, orderBy, page, rowsPerPage, searchTerm])

  return (
    <Card
      className="activity"
      component={motion.div}
      layout
      initial={{ height: 0 }}
      animate={{ height: 'auto' }}
    >
      <CardContent className="activity-card" component={motion.div} layout>
        <TableContainer component={motion.div} layout>
          <Table
            stickyHeader
            className="activity-table"
            component={motion.table}
            layout
          >
            <TableHead component={motion.thead} layout>
              <TableRow component={motion.tr} layout>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'status'}
                    direction={
                      (orderBy === 'status' ? order : Order.ASC) as OrderType
                    }
                    onClick={() => void handleSortRequest('status')}
                  >
                    Status
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'name'}
                    direction={
                      (orderBy === 'name' ? order : Order.ASC) as OrderType
                    }
                    onClick={() => void handleSortRequest('name')}
                  >
                    Name
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'nextLogin'}
                    direction={
                      (orderBy === 'nextLogin' ? order : Order.ASC) as OrderType
                    }
                    onClick={() => void handleSortRequest('nextLogin')}
                  >
                    Next Login
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'lastLoginAttempt'}
                    direction={
                      (orderBy === 'lastLoginAttempt'
                        ? order
                        : Order.ASC) as OrderType
                    }
                    onClick={() => void handleSortRequest('lastLoginAttempt')}
                  >
                    Last Login Attempt
                  </TableSortLabel>
                </TableCell>
                <TableCell>Login History</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody component={motion.tbody} layout>
              {isLoading && <ActivitySkeleton />}
              {rawData.length === 0 && !isLoading
                ? (
                    <TableRow>
                      <TableCell
                        className="empty-state-cell"
                        colSpan={6}
                        rowSpan={10}
                      >
                        {searchTerm === '' && rawData.length === 0
                          ? (
                              <EmptyState noData noDataHelperText="Add a website to get started"/>
                            )
                          : (
                              <EmptyState />
                            )}
                      </TableCell>
                    </TableRow>
                  )
                : (
                    processedData.map(row => (
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
                            prefix=""
                            datetime={row.nextLogin}
                            tooltip
                            negativeDifference="No login scheduled"
                          />
                        </TableCell>
                        <TableCell>
                          {row.lastLoginAttempt !== undefined
                            ? (
                                <TimeDifference
                                  prefix=""
                                  tooltip
                                  datetime={row.lastLoginAttempt}
                                />
                              )
                            : 'No logins yet'}
                        </TableCell>
                        <TableCell>
                          {row.loginHistory !== null && (
                            <div className="login-history">
                              {row.loginHistory.slice(0, 3).map((lh, index) => (
                                <LoginHistoryDetails
                                  key={index}
                                  loginHistory={lh}
                                />
                              ))}
                              {row.loginHistory.length > 3 && (
                                <Typography>...</Typography>
                              )}
                            </div>
                          )}
                        </TableCell>
                        <TableCell>
                          <ActionsPopover websiteId={row.id} websiteURL={row.url} />
                        </TableCell>
                      </TableRow>
                    ))
                  )}
            </TableBody>
          </Table>
        </TableContainer>
        {rawData.length > 0
          ? (
              <TablePagination
                rowsPerPageOptions={[10, 20, 50]}
                colSpan={5}
                component={motion.div}
                layout
                count={rawData.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            )
          : (
              <div className="activity-empty-pagination-spacer" />
            )}
      </CardContent>
    </Card>
  )
}
