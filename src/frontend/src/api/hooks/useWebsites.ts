import { useQuery, useMutation, type UseQueryOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import * as api from '../apiRequests'
import type { Website } from '../apiModels'
import type { ChangeWebsite } from '../../components/activity/model.ts'
import { queryClient } from '../queryClient'

// Query hooks
export function useWebsites(
  options?: Omit<UseQueryOptions<Website[], AxiosError>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Website[], AxiosError>({
    queryKey: ['websites'],
    queryFn: api.getWebsites,
    ...options,
  })
}

export function useWebsite(
  websiteId: number,
  options?: Omit<UseQueryOptions<Website, AxiosError>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Website, AxiosError>({
    queryKey: ['websites', websiteId],
    queryFn: () => api.getWebsite(websiteId),
    ...options,
  })
}

// Mutation hooks
export function useAddWebsite() {
  return useMutation({
    mutationFn: api.addWebsite,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['websites'] })
    },
  })
}

export function useEditWebsite() {
  return useMutation({
    mutationFn: ({ id, website }: { id: number; website: ChangeWebsite }) =>
      api.editWebsite(id, website),
    onSuccess: async (_data, variables) => {
      await Promise.all([
          queryClient.invalidateQueries({ queryKey: ["websites"] }),
          queryClient.invalidateQueries({ queryKey: ["websites", variables.id] })
        ]
      )
    },
  });
}

export function useDeleteWebsite() {
  return useMutation({
    mutationFn: api.deleteWebsite,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["websites"] })
    },
  })
}

export function useCheckCustomLoginScript() {
  return useMutation({
    mutationFn: api.checkCustomLoginScript,
  })
}

export function useAddManualLogin() {
  return useMutation({
    mutationFn: api.addManualLogin,
    onSuccess: async (_data, websiteId) => {
      await queryClient.invalidateQueries({ queryKey: ["actionHistory", websiteId] })
    },
  })
}

export function useTriggerAutomaticLogin() {
  return useMutation({
    mutationFn: api.triggerAutomaticLogin,
  })
}
