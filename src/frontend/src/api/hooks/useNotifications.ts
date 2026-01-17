import { useQuery, useMutation, type UseQueryOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import * as api from '../apiRequests'
import type { Notification } from '../apiModels'
import { queryClient } from '../queryClient'

// Query hooks
export function useNotifications(
  options?: Omit<UseQueryOptions<Notification[], AxiosError>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Notification[], AxiosError>({
    queryKey: ['notifications'],
    queryFn: api.getNotifications,
    ...options,
  })
}

// Mutation hooks
export function useAddNotification() {
  return useMutation({
    mutationFn: api.addNotification,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useEditNotification() {
  return useMutation({
    mutationFn: api.editNotification,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useDeleteNotification() {
  return useMutation({
    mutationFn: api.deleteNotification,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useTestNotification() {
  return useMutation({
    mutationFn: api.testNotification,
  })
}
