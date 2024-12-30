import AddWebsite from './actionBar/addWebsite/AddWebsite.tsx'
import Search from './actionBar/Search.tsx'
import Activity from './activity/Activity.tsx'
import Background from './Background.tsx'
import './Content.scss'

export default function Content() {
  return (
    <>
      <Background />
      <div className="content">
        <Search />
        <AddWebsite />
        <Activity />
      </div>
    </>
  )
}
