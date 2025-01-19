import type { ActionHistory } from '../../api/apiModels.ts'
import { getLoginHistory, getWebsite, getWebsites } from '../../api/apiRequests.ts'
import { ActivityStatusCode } from './StatusIcon.tsx'

export interface ActivityData {
  id: number
  status: ActivityStatusCode
  name: string
  url: string
  success_url: string
  nextLogin: Date
  lastLoginAttempt?: Date
  expirationDate?: Date
  loginHistory: ActionHistory[] | null
}

export interface CustomAccess {
  username_xpath: string
  password_xpath: string
  pin_xpath: string
  submit_button_xpath: string
}

export interface ActionInterval {
  date_minutes_start: number
  date_minutes_end: number | null
  allowed_time_minutes_start: number | null
  allowed_time_minutes_end: number | null
}

export interface ChangeWebsite {
  url?: string
  success_url?: string
  name?: string
  username?: string
  password?: string
  pin?: string | null
  take_screenshot?: boolean
  paused?: boolean
  expiration_interval_minutes?: number | null
  custom_access?: CustomAccess | null
  action_interval?: ActionInterval | null
}

export async function getActivity(): Promise<ActivityData[]> {
  const websites = await getWebsites()
  return Promise.all(websites.map(async (website): Promise<ActivityData> => {
    const loginHistory = await getLoginHistory(website.id)

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
  }))
}

export async function getChangeWebsite(websiteId: number): Promise<ChangeWebsite> {
  const website = await getWebsite(websiteId)
  const { next_schedule, id, ...rest } = website
  return rest
}
