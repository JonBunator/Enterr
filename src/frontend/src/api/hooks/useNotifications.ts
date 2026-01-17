import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import * as api from '../apiRequests'
import type { Notification, EditNotification } from '../apiModels'

// Query hooks
export function useNotifications(
  options?: Omit<UseQueryOptions<Notification[], AxiosError>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Notification[], AxiosError>({
    queryKey: ['notifications', 'list'],
    queryFn: api.getNotifications,
    ...options,
  })
}

// Mutation hooks
export function useAddNotification() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: api.addNotification,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useEditNotification() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: api.editNotification,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useDeleteNotification() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: api.deleteNotification,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useTestNotification() {
  return useMutation({
    mutationFn: api.testNotification,
  })
}
