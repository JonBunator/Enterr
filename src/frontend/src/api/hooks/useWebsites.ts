import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import * as api from '../apiRequests'
import type { Website } from '../apiModels'
import type { ChangeWebsite } from '../../components/activity/model.ts'

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
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.addWebsite,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['websites'] })
    },
  })
}

export function useEditWebsite() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, website }: { id: number; website: ChangeWebsite }) =>
      api.editWebsite(id, website),
    onSuccess: async (_data, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['websites'] }),
        queryClient.invalidateQueries({ queryKey: ['websites', variables.id] }),
      ])
    },
  });
}

export function useDeleteWebsite() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.deleteWebsite,
    onSuccess: async (_data, websiteId) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["websites", websiteId] }),
        queryClient.invalidateQueries({ queryKey: ["websites"] }),
      ]);
    },
  });
}

export function useCheckCustomLoginScript() {
  return useMutation({
    mutationFn: api.checkCustomLoginScript,
  })
}

export function useAddManualLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.addManualLogin,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["actionHistory"] })
    },
  })
}

export function useTriggerAutomaticLogin() {
  return useMutation({
    mutationFn: api.triggerAutomaticLogin,
  })
}
