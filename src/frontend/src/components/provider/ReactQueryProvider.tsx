import type { ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useEffect } from 'react'
import { useWebSocket } from './WebSocketProvider'

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
    // Invalidate queries when websocket events occur

    const disposeLoginDataChanged = on('login_data_changed', async () => {
      await queryClient.invalidateQueries({ queryKey: ['websites'] })
    })

    const disposeActionHistoryChanged = on('action_history_changed', async (data: { action_history_id: number, website_id: number }) => {
      if (data.action_history_id && data.website_id) {
        await Promise.all([
          queryClient.invalidateQueries({
            queryKey: ['actionHistory', `websiteId=${data.website_id}`],
          }),
          queryClient.invalidateQueries({
            queryKey: ['websites'],
          }),
        ])
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
