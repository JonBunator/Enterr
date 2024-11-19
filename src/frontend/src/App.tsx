import Content from './components/Content'
import WebSocketProvider from './components/WebSocketProvider'
import './App.css'

export default function App() {
  return (
    <WebSocketProvider>
      <Content />
    </WebSocketProvider>
  )
}
