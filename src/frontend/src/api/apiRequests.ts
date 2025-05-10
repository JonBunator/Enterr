import type { ChangeWebsite } from '../components/activity/activityRequests.ts'
import {
  ActionHistory,
  EditNotification,
  Notification,
  UserData,
  Website,
} from "./apiModels.ts";
import axios from 'axios'

export async function getWebsites(): Promise<Website[]> {
  const data = await axios.get('/api/websites')
  return data.data.data as Website[]
}

export async function getWebsite(website_id: number): Promise<Website> {
  const data = await axios.get(`/api/websites/${website_id}`)
  return data.data.data as Website
}

export async function getLoginHistory(website_id: number): Promise<ActionHistory[]> {
  const data = await axios.get(`/api/action_history/${website_id}`)
  return data.data.data as ActionHistory[]
}

export async function getUserData(): Promise<UserData> {
  const data = await axios.get(`/api/user/data`)
  return data.data.data as UserData
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

export async function addManualLogin(websiteId: number) {
  const body = { id: websiteId }
  await axios.post('/api/action_history/manual_add', body, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function triggerAutomaticLogin(websiteId: number) {
  const body = { id: websiteId }
  await axios.post('/api/trigger_login', body, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function loginUser(username: string, password: string): Promise<boolean> {
  const body = { username, password }
  const response = await axios.post('/api/user/login', body, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
  return response.data.success as boolean
}

export async function logoutUser() {
  await axios.post('/api/user/logout', {}, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function getNotifications(): Promise<Notification[]> {
  const data = await axios.get('/api/notifications')
  return data.data.data as Notification[]
}

export async function addNotification(notification: Notification) {
  await axios.post('/api/notifications/add', notification, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function testNotification(notification: Notification) {
  await axios.post('/api/notifications/test', notification, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function deleteNotification(notificationId: number) {
  const body = { id: notificationId }
  await axios.post('/api/notifications/delete', body, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

export async function editNotification(notification: EditNotification) {
  await axios.post('/api/notifications/edit', notification, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
}