import type { GridColDef, GridPaginationModel, GridSortModel } from '@mui/x-data-grid'
import type { ActivityData } from './model.ts'
import { Box, Card, CardContent, Typography } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import { useCallback, useMemo, useState } from 'react'
import { useActivity } from '../../api/hooks'
import ActionsPopover from './ActionsPopover.tsx'
import ActivityStatus from './ActivityStatus.tsx'
import EmptyState from './EmptyState.tsx'
import ExpirationDate from './ExpirationDate.tsx'
import LoginHistoryDetails from './LoginHistoryDetails.tsx'
import TimeDifference from './TimeDifference.tsx'
import WebsiteName from './WebsiteName.tsx'
import './Activity.scss'

interface ActivityProps {
  searchTerm?: string
}

const fieldMapping: Record<string, string> = {
  status: 'status',
  name: 'name',
  nextLogin: 'next_schedule',
  lastLoginAttempt: 'last_login_attempt',
}

export default function Activity(props: ActivityProps) {
  const { searchTerm } = props
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: 10,
  })
  const [sortModel, setSortModel] = useState<GridSortModel>([])

  // Convert sort model to backend format
  const orderBy = useMemo(() => {
    if (sortModel.length === 0)
      return undefined
    const sort = sortModel[0]
    const backendField = fieldMapping[sort.field]
    if (!backendField)
      return undefined
    const prefix = sort.sort === 'desc' ? '-' : '+'
    return `${prefix}${backendField}`
  }, [sortModel])

  const {
    data: rows = [],
    rowCount,
    isLoading,
  } = useActivity(
    paginationModel.page + 1,
    paginationModel.pageSize,
    searchTerm,
    orderBy,
  )

  const handleSortModelChange = useCallback((newSortModel: GridSortModel) => {
    setSortModel(newSortModel)
  }, [])

  const columns: GridColDef<ActivityData>[] = useMemo(
    () => [
      {
        field: 'status',
        headerName: 'Status',
        flex: 1,
        minWidth: 220,
        sortable: true,
        renderCell: params => (
          <ActivityStatus
            status={params.row.status}
          />
        ),
      },
      {
        field: 'website',
        headerName: 'Website',
        flex: 1,
        minWidth: 200,
        sortable: true,
        renderCell: params => (
          <WebsiteName
            key={params.row.url}
            name={params.row.name}
            url={params.row.url}
          />
        ),
      },
      {
        field: 'expiration',
        headerName: 'Expiration',
        flex: 1,
        minWidth: 100,
        sortable: false,
        renderCell: params => (
          <ExpirationDate expirationDate={params.row.expirationDate} />
        ),
      },
      {
        field: 'nextLogin',
        headerName: 'Next Login',
        flex: 1,
        minWidth: 150,
        sortable: true,
        renderCell: params => (
          <TimeDifference
            datetime={params.row.nextLogin}
            tooltip
            negativeDifference="No login scheduled"
          />
        ),
      },
      {
        field: 'lastLoginAttempt',
        headerName: 'Last Login Attempt',
        flex: 1,
        minWidth: 150,
        sortable: true,
        renderCell: params =>
          params.row.lastLoginAttempt !== undefined
            ? (
                <TimeDifference
                  tooltip
                  datetime={params.row.lastLoginAttempt}
                />
              )
            : (
                <Box sx={{ color: 'text.secondary' }}>No logins yet</Box>
              ),
      },
      {
        field: 'loginHistory',
        headerName: 'Login History',
        flex: 1,
        minWidth: 150,
        sortable: false,
        renderCell: params =>
          params.row.loginHistory !== null && (
            <div className="login-history">
              {params.row.loginHistory.slice(0, 3).map((lh, index) => (
                <LoginHistoryDetails key={index} loginHistory={lh} />
              ))}
              {params.row.loginHistory.length > 3 && (
                <Typography>...</Typography>
              )}
            </div>
          ),
      },
      {
        field: 'actions',
        type: 'actions',
        hideable: false,
        resizable: false,
        renderCell: params => (
          <ActionsPopover
            websiteId={params.row.id}
            websiteURL={params.row.url}
          />
        ),
      },
    ],
    [],
  )

  const getTogglableColumns = (columns: GridColDef[]) => {
    // hide the column with field `actions` from list of togglable columns
    return columns
      .filter(column => column.field !== 'actions')
      .map(column => column.field)
  }

  return (
    <Card className="activity">
      <CardContent className="activity-card">
        <DataGrid
          className="data-grid"
          rows={rows}
          columns={columns}
          loading={isLoading}
          rowCount={rowCount}
          paginationMode="server"
          paginationModel={paginationModel}
          onPaginationModelChange={setPaginationModel}
          sortingMode="server"
          sortModel={sortModel}
          disableColumnFilter
          onSortModelChange={handleSortModelChange}
          pageSizeOptions={[10, 20, 50]}
          disableRowSelectionOnClick
          slots={{
            noRowsOverlay: () => (
              <EmptyState
                noData={searchTerm === undefined || searchTerm === ''}
                noDataHelperText="Add a website to get started"
              />
            ),
          }}
          slotProps={{
            columnsManagement: {
              getTogglableColumns,
            },
          }}
        />
      </CardContent>
    </Card>
  )
}
