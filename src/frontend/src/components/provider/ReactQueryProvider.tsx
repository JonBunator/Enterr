import type { ReactNode } from 'react'
import { useEffect } from 'react'
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useWebSocket } from './WebSocketProvider'

interface ReactQueryProviderProps {
  children: ReactNode
}

export default function ReactQueryProvider({ children }: ReactQueryProviderProps) {
  const { on } = useWebSocket()
  const queryClient = new QueryClient();

  useEffect(() => {
    // Invalidate queries when socket.io events occur

    on('website_updated', (data: { website_id: number }) => {
      queryClient.invalidateQueries({ queryKey: ['websites'] }).then();
      if (data.website_id) {
        queryClient.invalidateQueries({
          queryKey: ['websites', 'detail', data.website_id]
        }).then();
       }
    })

    on('website_added', () => {
      queryClient
        .invalidateQueries({ queryKey: ['websites'] })
        .then();
    })

    on('website_deleted', () => {
      queryClient
        .invalidateQueries({ queryKey: ['websites'] })
        .then();
    })

    // When action history changes
    on('action_history_updated', (data: { website_id: number }) => {
      if (data.website_id) {
        queryClient
          .invalidateQueries({
            queryKey: ['actionHistory', data.website_id],
          })
          .then();
      }
    })

    on('action_started', (data: { website_id: number }) => {
      if (data.website_id) {
        queryClient
          .invalidateQueries({
            queryKey: ['actionHistory', data.website_id],
          })
          .then();
        queryClient
          .invalidateQueries({
            queryKey: ['websites', 'detail', data.website_id],
          })
          .then();
      }
    })

    on('action_completed', (data: { website_id: number }) => {
      if (data.website_id) {
        queryClient
          .invalidateQueries({
            queryKey: ['actionHistory', data.website_id],
          })
          .then();
        queryClient
          .invalidateQueries({
            queryKey: ['websites', 'detail', data.website_id],
          })
          .then();
      }
    })

    // When notifications change
    on('notification_updated', () => {
      queryClient
        .invalidateQueries({ queryKey: ['notifications'] })
        .then();
    })

    on('notification_added', () => {
      queryClient
        .invalidateQueries({ queryKey: ['notifications'] })
        .then();
    })

    on('notification_deleted', () => {
      queryClient
        .invalidateQueries({ queryKey: ['notifications'] })
        .then();
    })

    // When user data changes
    on('user_updated', () => {
      queryClient.invalidateQueries({ queryKey: ['user'] }).then();
    })
  }, [on])

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
