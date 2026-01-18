import type { ReactNode } from 'react'
import { useEffect } from 'react'
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useWebSocket } from './WebSocketProvider'
import { QueryClient } from '@tanstack/react-query'

const queryClient = new QueryClient()

interface ReactQueryProviderProps {
  children: ReactNode
}

export default function ReactQueryProvider({ children }: ReactQueryProviderProps) {
  const { on } = useWebSocket()

  useEffect(() => {
    // Invalidate queries when socket.io events occur

    on('login_data_changed', async () => {
      await queryClient.invalidateQueries({ queryKey: ['websites'] })
    })

    on("action_history_changed", async (data: { id: number }) => {
      if (data.id) {
        await queryClient.invalidateQueries({
          queryKey: ["actionHistory"],
        });
      }
    });

    on('notifications_changed', async () => {
      await queryClient.invalidateQueries({ queryKey: ['notifications'] })
    })
  }, [on, queryClient])

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
