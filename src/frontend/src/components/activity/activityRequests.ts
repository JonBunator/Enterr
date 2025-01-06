import { getLoginHistory, getWebsites } from '../../api/apiRequests.ts'
import { ActivityStatusCode } from './StatusIcon.tsx'

export interface ActivityData {
  id: number
  status: ActivityStatusCode
  name: string
  nextLogin: Date
  expirationDate?: Date
  loginHistory: ActivityStatusCode[]
  screenshots: string
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
  url: string
  success_url: string
  name: string
  username: string
  password: string
  pin: string
  expiration_interval_minutes: number | null
  custom_access: CustomAccess | null
  action_interval: ActionInterval
}

export async function getActivity(): Promise<ActivityData[]> {
  const websites = await getWebsites()

  return Promise.all(websites.map(async (website): Promise<ActivityData> => {
    const loginHistory = await getLoginHistory(website.id)

    const loginHistoryStatuses = loginHistory.map((login) => {
      return login.execution_status
    })

    const lastSuccessfulLogin = loginHistory.find(login => login.execution_status === ActivityStatusCode.SUCCESS)
    let expirationDate: Date | undefined

    if (lastSuccessfulLogin && lastSuccessfulLogin.execution_ended != null && website.expiration_interval != null) {
      expirationDate = new Date(lastSuccessfulLogin.execution_ended)
      expirationDate.setDate(expirationDate.getUTCDate() + website.expiration_interval?.days)
      expirationDate.setHours(expirationDate.getUTCHours() + website.expiration_interval?.hours)
      expirationDate.setMinutes(expirationDate.getUTCMinutes() + website.expiration_interval?.minutes)
    }

    const nextLogin = website.next_schedule ? new Date(website.next_schedule.year, website.next_schedule.month - 1, website.next_schedule.day, website.next_schedule.hour, website.next_schedule.minute) : new Date(0)
    return {
      id: website.id,
      status: (loginHistory[0]?.execution_status ?? ActivityStatusCode.FAILED) as ActivityStatusCode,
      name: website.name,
      nextLogin,
      expirationDate,
      loginHistory: loginHistoryStatuses as ActivityStatusCode[],
      screenshots: '',
    }
  }))
}
