import './App.css'
import WebSocketProvider from './components/WebSocketProvider';
import Content from './components/Content';


export default function App() {
  return (
    <WebSocketProvider>
      <Content/>
    </WebSocketProvider>
  )
}