import type {
  ReactNode,
} from 'react'
import type { Socket } from 'socket.io-client'
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { io } from 'socket.io-client'

interface WebSocketContextType {
  socket: Socket | null
  emit: (event: string, data: any) => void
  on: (event: string, callback: (message: any) => void) => void
}

const SOCKET_URL = import.meta.env.PROD ? window.location.origin : 'http://localhost:7653'

const WebSocketContext = createContext<WebSocketContextType | undefined>(
  undefined,
)

interface WebSocketProviderProps {
  children: ReactNode
}

export default function WebSocketProvider({
  children,
}: WebSocketProviderProps) {
  const [socket, setSocket] = useState<Socket | null>(null)

  useEffect(() => {
    const socketIo = io(SOCKET_URL)
    setSocket(socketIo)
    return () => {
      socketIo.disconnect()
    }
  }, [])

  const emit = useCallback((event: string, data: any) => {
    if (socket) {
      socket.emit(event, data)
    }
  }, [socket])

  const on = useCallback((event: string, callback: (message: any) => void) => {
    if (socket) {
      socket.on(event, callback)
    }
  }, [socket])

  const value = useMemo(() => ({
    socket,
    emit,
    on,
  }), [socket, emit, on])

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket(): WebSocketContextType {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}
