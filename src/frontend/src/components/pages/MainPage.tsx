import type { WebsiteStatusCode } from '../../api/apiModels.ts'
import { Typography } from '@mui/material'
import { useState } from 'react'
import AddWebsite from '../actionBar/addWebsite/AddWebsite.tsx'
import Search from '../actionBar/Search.tsx'
import Activity from '../activity/Activity.tsx'
import StatusSummary from '../activity/StatusSummary.tsx'
import Content from '../layout/Content.tsx'
import AccountButton from '../settings/AccountButton.tsx'
import ProtectedPage from './ProtectedPage.tsx'
import './MainPage.scss'

export default function MainPage() {
  const [searchTerm, setSearchTerm] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<WebsiteStatusCode>()

  return (
    <ProtectedPage>
      <AccountButton />
      <Content>
        <div className="main-page">
          <section className="main-page-section">
            <Typography variant="h6" component="h2">
              Overview
            </Typography>
            <StatusSummary
              searchTerm={searchTerm}
              selected={statusFilter}
              onSelect={setStatusFilter}
            />
          </section>
          <section className="main-page-section activity-section">
            <Typography variant="h6" component="h2">
              Activity
            </Typography>
            <div className="main-page-header">
              <Search value={searchTerm} onChange={setSearchTerm} />
              <AddWebsite />
            </div>
            <Activity searchTerm={searchTerm} statusFilter={statusFilter} />
          </section>
        </div>
      </Content>
    </ProtectedPage>
  )
}
