import { useQuery, type UseQueryOptions } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import * as api from '../apiRequests'
import type { ActionHistory } from '../apiModels'

export function useLoginHistory(
  websiteId: number,
  options?: Omit<UseQueryOptions<ActionHistory[], AxiosError>, 'queryKey' | 'queryFn'>
) {
  return useQuery<ActionHistory[], AxiosError>({
    queryKey: ['actionHistory', websiteId],
    queryFn: () => api.getLoginHistory(websiteId),
    enabled: websiteId > 0,
    ...options,
  })
}
