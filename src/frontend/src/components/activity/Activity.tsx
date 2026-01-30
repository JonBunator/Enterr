import type { ActivityData } from './model.ts'
import type { GridColDef, GridPaginationModel } from '@mui/x-data-grid'
import { Card, CardContent, Typography } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import { useMemo, useState } from 'react'
import { useActivity } from '../../api/hooks'
import ActionsPopover from './ActionsPopover.tsx'
import ActivityStatus from './ActivityStatus.tsx'
import EmptyState from './EmptyState.tsx'
import LoginHistoryDetails from './LoginHistoryDetails.tsx'
import TimeDifference from './TimeDifference.tsx'
import './Activity.scss'

interface ActivityProps {
  searchTerm?: string
}

export default function Activity(props: ActivityProps) {
  const { searchTerm } = props
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: 10,
  })

  const {
    data: rows = [],
    rowCount,
    isLoading,
  } = useActivity(
    paginationModel.page + 1,
    paginationModel.pageSize,
    searchTerm,
  );

  const columns: GridColDef<ActivityData>[] = useMemo(
    () => [
      {
        field: 'status',
        headerName: 'Status',
        flex: 1,
        minWidth: 250,
        sortable: true,
        renderCell: params => (
          <ActivityStatus
            status={params.row.status}
            expirationDate={params.row.expirationDate}
          />
        ),
      },
      {
        field: 'name',
        headerName: 'Name',
        flex: 1,
        minWidth: 150,
        sortable: true,
      },
      {
        field: 'nextLogin',
        headerName: 'Next Login',
        flex: 1,
        minWidth: 150,
        sortable: true,
        renderCell: params => (
          <TimeDifference
            prefix=""
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
          params.row.lastLoginAttempt !== undefined ? (
            <TimeDifference
              prefix=""
              tooltip
              datetime={params.row.lastLoginAttempt}
            />
          ) : (
            'No logins yet'
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
        resizable: false,
        renderCell: params => (
          <ActionsPopover websiteId={params.row.id} websiteURL={params.row.url} />
        ),
      },
    ],
    []
  )

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
          pageSizeOptions={[10, 20, 50]}
          disableColumnMenu
          disableRowSelectionOnClick
          getRowHeight={() => "auto"}
          slots={{
            noRowsOverlay: () => (
              <EmptyState
                noData
                noDataHelperText="Add a website to get started"
              />
            ),
          }}
        />
      </CardContent>
    </Card>
  );
}
