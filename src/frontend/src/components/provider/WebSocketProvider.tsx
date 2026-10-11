import type {
  ReactNode,
} from 'react'
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
} from 'react'

type Listener = (message: any) => void

interface WebSocketContextType {
  emit: (event: string, data: unknown) => void
  on: (event: string, callback: Listener) => () => void
}

const INITIAL_RECONNECT_DELAY = 1000
const MAX_RECONNECT_DELAY = 10000

function getSocketUrl() {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${protocol}://${window.location.host}/api/ws`
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(
  undefined,
)

interface WebSocketProviderProps {
  children: ReactNode
}

export default function WebSocketProvider({
  children,
}: WebSocketProviderProps) {
  const socketRef = useRef<WebSocket | null>(null)
  const listenersRef = useRef(new Map<string, Set<Listener>>())

  useEffect(() => {
    let disposed = false
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined
    let reconnectDelay = INITIAL_RECONNECT_DELAY

    const connect = () => {
      const socket = new WebSocket(getSocketUrl())
      socketRef.current = socket

      socket.onopen = () => {
        reconnectDelay = INITIAL_RECONNECT_DELAY
      }

      socket.onmessage = (messageEvent: MessageEvent<string>) => {
        let message: { event: string, data: unknown }
        try {
          message = JSON.parse(messageEvent.data) as { event: string, data: unknown }
        }
        catch {
          return
        }
        listenersRef.current.get(message.event)?.forEach(listener => listener(message.data))
      }

      socket.onclose = () => {
        if (socketRef.current === socket) {
          socketRef.current = null
        }
        if (disposed) {
          return
        }
        // Reconnect (e.g. after login, when the server rejected the unauthenticated connection)
        reconnectTimer = setTimeout(connect, reconnectDelay)
        reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY)
      }
    }

    connect()

    return () => {
      disposed = true
      clearTimeout(reconnectTimer)
      socketRef.current?.close()
      socketRef.current = null
    }
  }, [])

  const emit = useCallback((event: string, data: unknown) => {
    const socket = socketRef.current
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ event, data }))
    }
  }, [])

  const on = useCallback((event: string, callback: Listener) => {
    const listeners = listenersRef.current
    if (!listeners.has(event)) {
      listeners.set(event, new Set())
    }
    listeners.get(event)!.add(callback)

    return () => {
      listeners.get(event)?.delete(callback)
    }
  }, [])

  const value = useMemo(() => ({
    emit,
    on,
  }), [emit, on])

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
