import type { UseQueryOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import type { ChangeWebsite } from '../../components/activity/model.ts'
import type { Website } from '../apiModels'
import type { PaginatedResponse } from '../apiRequests'
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from '../apiRequests'

// Query hooks
export function useWebsites(
  page: number,
  pageSize: number,
  searchTerm?: string,
  orderBy?: string,
  options?: Omit<UseQueryOptions<PaginatedResponse<Website>, AxiosError>, 'queryKey' | 'queryFn' | 'placeholderData'>,
) {
  const queryKey = ['websites', 'all', `pageSize=${pageSize}`, `page=${page}`]
  if (searchTerm !== undefined && searchTerm !== '') {
    queryKey.push(`search=${searchTerm}`)
  }
  if (orderBy !== undefined && orderBy !== '') {
    queryKey.push(`sort=${orderBy}`)
  }
  return useQuery<PaginatedResponse<Website>, AxiosError>({
    queryKey,
    queryFn: async () => api.getWebsites(page, pageSize, searchTerm, orderBy),
    placeholderData: keepPreviousData,
    ...options,
  })
}

export function useWebsite(
  websiteId: number,
  options?: Omit<UseQueryOptions<Website, AxiosError>, 'queryKey' | 'queryFn'>,
) {
  const queryClient = useQueryClient()
  return useQuery<Website, AxiosError>({
    queryKey: ['websites', websiteId],
    queryFn: async () => api.getWebsite(websiteId),
    initialData: () => {
      // Search through paginated website caches for this website
      const queries = queryClient.getQueriesData<PaginatedResponse<Website>>({
        queryKey: ['websites', 'all'],
      })
      for (const [_queryKey, data] of queries) {
        const website = data?.items?.find(w => w.id === websiteId)
        if (website)
          return website
      }
      return undefined
    },
    initialDataUpdatedAt: () => {
      // Find the most recent update time from any paginated cache containing this website
      const queries = queryClient.getQueriesData<PaginatedResponse<Website>>({
        queryKey: ['websites', 'all'],
      })
      for (const [queryKey, data] of queries) {
        if (data?.items?.some(w => w.id === websiteId)) {
          return queryClient.getQueryState(queryKey)?.dataUpdatedAt
        }
      }
      return undefined
    },
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
    mutationFn: async ({ id, website }: { id: number, website: ChangeWebsite }) =>
      api.editWebsite(id, website),
    onSuccess: async (_data, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['websites'] }),
        queryClient.invalidateQueries({ queryKey: ['websites', variables.id] }),
      ])
    },
  })
}

export function useDeleteWebsite() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.deleteWebsite,
    onSuccess: async (_data, websiteId) => {
      queryClient.removeQueries({ queryKey: ['websites', websiteId] })
      await queryClient.invalidateQueries({ queryKey: ['websites'] })
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
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['actionHistory'] })
    },
  })
}

export function useTriggerAutomaticLogin() {
  return useMutation({
    mutationFn: api.triggerAutomaticLogin,
  })
}
