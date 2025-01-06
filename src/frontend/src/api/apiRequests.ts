import type { ChangeWebsite } from '../components/activity/activityRequests.ts'
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

export async function addWebsite(website: ChangeWebsite) {
  await axios.post('/api/websites/add', website, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function deleteWebsite(websiteId: number) {
  const body = { id: websiteId }
  await axios.post('/api/websites/delete', body, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function editWebsite(websiteId: number, website: ChangeWebsite) {
  const body = { id: websiteId, ...website }
  await axios.post('/api/websites/edit', body, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}
