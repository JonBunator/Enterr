import { useState } from 'react'
import AddWebsite from '../actionBar/addWebsite/AddWebsite.tsx'
import Search from '../actionBar/Search.tsx'
import Activity from '../activity/Activity.tsx'
import Content from '../layout/Content.tsx'
import AccountSettings from '../settings/AccountSettings.tsx'
import ProtectedPage from './ProtectedPage.tsx'
import './MainPage.scss'

export default function MainPage() {
  const [searchTerm, setSearchTerm] = useState<string>('')

  return (
    <ProtectedPage>
      <AccountSettings />
      <Content>
        <div className="main-page">
          <div className="main-page-header">
            <Search value={searchTerm} onChange={setSearchTerm} />
            <AddWebsite />
          </div>
          <Activity searchTerm={searchTerm} />
        </div>
      </Content>
    </ProtectedPage>
  )
}
