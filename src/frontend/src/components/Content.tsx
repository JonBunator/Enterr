import Activity from './activity/Activity.tsx'
import Background from './Background.tsx'
import './Content.scss'

export default function Content() {
  return (
    <>
      <Background />
      <div className="content">
        <Activity />
      </div>
    </>
  )
}
