import { useQueries } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import type { ActivityData } from '../../components/activity/model.ts'
import { useWebsites } from './useWebsites'
import * as api from '../apiRequests'
import { ActivityStatusCode } from '../../components/activity/StatusIcon'

export function useActivity() {
  const { data: websites = [], isLoading: isLoadingWebsites } = useWebsites()
  
  const loginHistoryQueries = useQueries({
    queries: websites.map(website => ({
      queryKey: ['actionHistory', website.id],
      queryFn: () => api.getActionHistories(website.id),
      enabled: !isLoadingWebsites,
    })),
  })

  const isLoading = isLoadingWebsites || loginHistoryQueries.some(q => q.isLoading)
  const error = loginHistoryQueries.find(q => q.error)?.error as AxiosError | undefined

  const data: ActivityData[] = websites.map((website, index) => {
    const loginHistory = loginHistoryQueries[index]?.data ?? []

    const lastSuccessfulLogin = loginHistory.find(login => login.execution_status === ActivityStatusCode.SUCCESS)
    let expirationDate: Date | undefined
    if (lastSuccessfulLogin && lastSuccessfulLogin.execution_ended != null && website.expiration_interval_minutes != null) {
      expirationDate = new Date(lastSuccessfulLogin.execution_ended)
      expirationDate.setMinutes(expirationDate.getUTCMinutes() + website.expiration_interval_minutes)
    }

    const lastLoginAttempt = loginHistory[0] !== undefined ? new Date(loginHistory[0]?.execution_started) : undefined
    let status = (loginHistory[0]?.execution_status ?? ActivityStatusCode.FAILED) as ActivityStatusCode
    status = website.paused ? ActivityStatusCode.PAUSED : status

    const nextLogin = website?.next_schedule !== null ? new Date(website?.next_schedule) : new Date(0)
    
    return {
      id: website.id,
      status,
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
    isLoading,
    error,
    isError: !!error,
    isSuccess: !isLoading && !error,
  }
}
