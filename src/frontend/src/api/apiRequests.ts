import type { ActionHistory, Website } from './apiModels.ts'
import axios from 'axios'

export async function getWebsites(): Promise<Website[]> {
  const data = await axios.get('/api/websites')
  return data.data.data as Website[]
}

export async function getLoginHistory(website_id: number): Promise<ActionHistory[]> {
  const data = await axios.get(`/api/action_history/${website_id}`)
  return data.data.data as ActionHistory[]
}
