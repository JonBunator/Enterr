import { useQuery, useMutation, useQueryClient, type UseQueryOptions, keepPreviousData } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import * as api from '../apiRequests'
import type { Website } from '../apiModels'
import type { ChangeWebsite } from '../../components/activity/model.ts'
import { PaginatedResponse } from '../apiRequests'

// Query hooks
export function useWebsites(
  page: number,
  pageSize: number,
  searchTerm?: string,
  options?: Omit<UseQueryOptions<PaginatedResponse<Website>, AxiosError>, 'queryKey' | 'queryFn' | 'placeholderData'>
) {
  const queryKey = ["websites", `pageSize=${pageSize}`, `page=${page}`];
  if(searchTerm !== undefined || searchTerm === '') {
    queryKey.push(`searchTerm=${searchTerm}`)
  }
  return useQuery<PaginatedResponse<Website>, AxiosError>({
    queryKey: queryKey,
    queryFn: () => api.getWebsites(page, pageSize, searchTerm),
    placeholderData: keepPreviousData,
    ...options,
  });
}

export function useWebsite(
  websiteId: number,
  options?: Omit<UseQueryOptions<Website, AxiosError>, 'queryKey' | 'queryFn'>
) {
  const queryClient = useQueryClient()
  return useQuery<Website, AxiosError>({
    queryKey: ['websites', websiteId],
    queryFn: () => api.getWebsite(websiteId),
    initialData: () => {
      return queryClient.getQueryData<Website[]>(['websites'])?.find((w) => w.id === websiteId);
    },
    initialDataUpdatedAt: () =>
      queryClient.getQueryState(['websites'])?.dataUpdatedAt,
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
        queryClient.removeQueries({ queryKey: ["websites", websiteId] })
        await queryClient.invalidateQueries({ queryKey: ["websites"] })
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
