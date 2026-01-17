import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import * as api from '../apiRequests'
import type { Website } from '../apiModels'
import type { ChangeWebsite } from '../../components/activity/activityRequests'

// Query hooks
export function useWebsites(
  options?: Omit<UseQueryOptions<Website[], AxiosError>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Website[], AxiosError>({
    queryKey: ['websites', 'list'],
    queryFn: api.getWebsites,
    ...options,
  })
}

export function useWebsite(
  websiteId: number,
  options?: Omit<UseQueryOptions<Website, AxiosError>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Website, AxiosError>({
    queryKey: ['websites', 'detail', websiteId],
    queryFn: () => api.getWebsite(websiteId),
    ...options,
  })
}

// Mutation hooks
export function useAddWebsite() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: api.addWebsite,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['websites'] }).then();
    },
  })
}

export function useEditWebsite() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, website }: { id: number; website: ChangeWebsite }) =>
      api.editWebsite(id, website),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["websites"] }).then();
      queryClient
        .invalidateQueries({ queryKey: ["websites", "detail", variables.id] })
        .then();
    },
  });
}

export function useDeleteWebsite() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: api.deleteWebsite,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["websites"] }).then();
    },
  })
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
    onSuccess: (_data, variables) => {
      queryClient
        .invalidateQueries({ queryKey: ["actionHistory", variables] })
        .then();
    },
  });
}

export function useTriggerAutomaticLogin() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: api.triggerAutomaticLogin,
    onSuccess: (_data, variables) => {
      queryClient
        .invalidateQueries({ queryKey: ["actionHistory", variables] })
        .then();
    },
  });
}
