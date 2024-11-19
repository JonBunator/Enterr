import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';

interface WebSocketContextType {
  socket: Socket | null;
  emit: (event: string, data: any) => void;
  on: (event: string, callback: (message: any) => void) => void;
}

const SOCKET_URL = 'http://localhost:8080';

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

interface WebSocketProviderProps {
  children: ReactNode;
}

export default function WebSocketProvider({ children }: WebSocketProviderProps) {
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    const socketIo = io(SOCKET_URL);
    setSocket(socketIo);
    return () => {
      socketIo.disconnect();
    };
  }, []);

  const emit = (event: string, data: any) => {
    if (socket) {
      socket.emit(event, data);
    }
  };

  const on = (event: string, callback: (message: any) => void) => {
    if (socket) {
      socket.on(event, callback);
    }
  };

  return (
    <WebSocketContext.Provider value={{ socket, emit, on }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};
