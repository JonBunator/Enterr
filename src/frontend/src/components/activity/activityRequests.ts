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
