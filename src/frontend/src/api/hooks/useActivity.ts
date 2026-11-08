import type { AxiosError } from 'axios'
import type { ActivityData } from '../../components/activity/model.ts'
import type { WebsiteStatusCode } from '../apiModels.ts'
import { useQueries } from '@tanstack/react-query'
import * as api from '../apiRequests'
import { useWebsites } from './useWebsites'

export function useActivity(
  page: number,
  pageSize: number,
  searchTerm?: string,
  orderBy?: string,
  status?: WebsiteStatusCode,
) {
  const {
    data: websitesData,
    isLoading: isLoadingWebsites,
    isPlaceholderData,
    isSuccess: isWebsitesSuccess,
  } = useWebsites(
    page,
    pageSize,
    searchTerm,
    orderBy,
    status,
  )
  const websites = websitesData?.items ?? []
  const rowCount = websitesData?.total ?? 0

  const loginHistoryQueries = useQueries({
    queries: websites.map(website => ({
      queryKey: ['actionHistory', `websiteId=${website.id}`],
      queryFn: async () => api.getActionHistories(website.id),
      enabled: !isLoadingWebsites,
    })),
  })

  const isLoading = isLoadingWebsites || loginHistoryQueries.some(q => q.isLoading)
  const error = loginHistoryQueries.find(q => q.error)?.error as AxiosError | undefined

  const data: ActivityData[] = websites.map((website, index) => {
    const loginHistory = loginHistoryQueries[index]?.data ?? []

    const expirationDate = website.expiration_date != null ? new Date(website.expiration_date) : undefined

    const lastLoginAttempt = loginHistory[0] !== undefined ? new Date(loginHistory[0]?.execution_started) : undefined
    const nextLogin = website?.next_schedule !== null ? new Date(website?.next_schedule) : new Date(0)

    return {
      id: website.id,
      status: website.status,
      name: website.name,
      url: website.url,
      success_url: website.success_url,
      nextLogin,
      lastLoginAttempt,
      expirationDate,
      loginHistory,
    }
  })

  return {
    data,
    rowCount,
    isRowCountFresh: isWebsitesSuccess && !isPlaceholderData,
    isLoading,
    error,
    isError: !!error,
    isSuccess: !isLoading && !error,
  }
}
