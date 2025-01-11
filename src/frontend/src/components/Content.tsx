import { useState } from 'react'
import AddWebsite from './actionBar/addWebsite/AddWebsite.tsx'
import Search from './actionBar/Search.tsx'
import Activity from './activity/Activity.tsx'
import Background from './Background.tsx'
import './Content.scss'

export default function Content() {
  const [searchTerm, setSearchTerm] = useState<string>('')

  return (
    <>
      <Background />
      <div className="content">
        <Search value={searchTerm} onChange={setSearchTerm} />
        <AddWebsite />
        <Activity searchTerm={searchTerm} />
      </div>
    </>
  )
}
