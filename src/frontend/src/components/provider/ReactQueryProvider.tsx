import type { ReactNode } from 'react'
import { useEffect } from 'react'
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useWebSocket } from './WebSocketProvider'
import { QueryClient } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 3 * 60 * 1000, // 3 minutes
    },
  },
})

interface ReactQueryProviderProps {
  children: ReactNode
}

export default function ReactQueryProvider({ children }: ReactQueryProviderProps) {
  const { on } = useWebSocket()

  useEffect(() => {
    // Invalidate queries when socket.io events occur

    const disposeLoginDataChanged = on('login_data_changed', async () => {
      await queryClient.invalidateQueries({ queryKey: ['websites'] })
    })

    const disposeActionHistoryChanged = on("action_history_changed", async (data: { action_history_id: number; website_id: number }) => {
      if (data.action_history_id && data.website_id) {
        await Promise.all([
        queryClient.invalidateQueries({
          queryKey: ["actionHistory", `websiteId=${data.website_id}`],
        }),
        queryClient.invalidateQueries({
          queryKey: ["websites"],
        })]);
      }
    })

    const disposeNotificationsChanged = on('notifications_changed', async () => {
      await queryClient.invalidateQueries({ queryKey: ['notifications'] })
    })

    return () => {
      disposeLoginDataChanged()
      disposeActionHistoryChanged()
      disposeNotificationsChanged()
    }
  }, [on, queryClient])

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
