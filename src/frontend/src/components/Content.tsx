import axios from 'axios'
import { useEffect } from 'react'
import Activity from './activity/Activity.tsx'
import Background from './Background.tsx'
import { useWebSocket } from './WebSocketProvider'
import './Content.scss'

export default function Content() {
  const { emit, on } = useWebSocket()

  const fetchAPI = async () => {
    const response = await axios.get('/api/users')
    // eslint-disable-next-line ts/no-unsafe-member-access
    console.log(response.data.users)
  }

  useEffect(() => {
    fetchAPI().catch(console.error)
  }, [])

  function handleClick() {
    emit('custom_event', { message: 'Hello from React!' })
  }

  useEffect(() => {
    on('message', (data) => {
      console.log(data)
    })
    emit('custom_event', { message: 'Hello from React!' })
  }, [on, emit])

  return (
    <>
      <Background />
      <div className="content">
        <button type="button" onClick={handleClick}>Send message</button>
        <Activity />
      </div>
    </>
  )
}
