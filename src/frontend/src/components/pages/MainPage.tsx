import { useState } from 'react'
import AddWebsite from '../actionBar/addWebsite/AddWebsite.tsx'
import Search from '../actionBar/Search.tsx'
import Activity from '../activity/Activity.tsx'
import Content from '../layout/Content.tsx'
import AccountSettings from '../settings/AccountSettings.tsx'
import ProtectedPage from './ProtectedPage.tsx'

export default function MainPage() {
  const [searchTerm, setSearchTerm] = useState<string>('')

  return (
    <ProtectedPage>
      <AccountSettings />
      <Content>
        <Search value={searchTerm} onChange={setSearchTerm} />
        <AddWebsite />
        <Activity searchTerm={searchTerm} />
      </Content>
    </ProtectedPage>
  )
}
