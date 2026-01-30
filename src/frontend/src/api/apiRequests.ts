import type {
  ChangeWebsite,
} from "../components/activity/model.ts";
import {
  ActionHistory,
  EditNotification,
  Notification,
  UserData,
  Website,
} from "./apiModels.ts";
import apiClient from "./apiClient.ts";

export interface PaginatedResponse<T> {
  items: T[]
  total: number
}

export async function getWebsites(
  page: number,
  pageSize: number,
  searchTerm?: string,
): Promise<PaginatedResponse<Website>> {
  let url = `/websites?page=${page}&size=${pageSize}`;
  if(searchTerm !== undefined && searchTerm !== '') {
    url += `&search=${searchTerm}`;
  }
  const data = await apiClient.get(url);
  return {
    items: data.data.items as Website[],
    total: data.data.total as number,
  };
}

export async function getWebsite(websiteId: number): Promise<Website> {
  const data = await apiClient.get(`/websites/${websiteId}`)
  return data.data as Website
}

export async function getActionHistories(
  websiteId: number,
): Promise<ActionHistory[]> {
  const data = await apiClient.get(
    `/action_history?website_id=${websiteId}&page=1&size=4`,
  );
  return data.data.items as ActionHistory[];
}

export async function getActionHistory(
  actionHistoryId: number,
): Promise<ActionHistory> {
  const data = await apiClient.get(`/action_history/${actionHistoryId}`);
  return data.data as ActionHistory;
}

export async function getUserData(): Promise<UserData | null> {
  try {
    const data = await apiClient.get(`/user/data`)
    return data.data as UserData;
  } catch (error: any) {
    if (error?.response?.status === 401) {
      return null;
    }
    throw error;
  }
}

export async function addWebsite(website: ChangeWebsite) {
  await apiClient.post('/websites', website);
}

export async function deleteWebsite(websiteId: number) {
  await apiClient.delete(`/websites/${websiteId}`);
}

export async function editWebsite(websiteId: number, website: ChangeWebsite) {
  await apiClient.put(`/websites/${websiteId}`, website);
}

export async function checkCustomLoginScript(customLoginScript: string): Promise<string | null> {
  const body = { script: customLoginScript };
  const data = await apiClient.post(
    "/websites/check_custom_login_script",
    body,
  );
  return data.data.error;
}

export async function addManualLogin(websiteId: number) {
  await apiClient.post(`/action_history/manual_add/${websiteId}`);
}

export async function triggerAutomaticLogin(websiteId: number) {
  await apiClient.post(`/trigger_login/${websiteId}`);
}

export async function loginUser(username: string, password: string): Promise<boolean> {
  const body = new URLSearchParams();
  body.append('username', username);
  body.append('password', password);
  await apiClient.post('/user/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return true;

}

export async function logoutUser() {
  await apiClient.post('/user/logout');
}

export async function getNotifications(): Promise<Notification[]> {
  const data = await apiClient.get('/notifications')
  return data.data.items as Notification[]
}

export async function addNotification(notification: Notification) {
  await apiClient.post('/notifications', notification);
}

export async function testNotification(notification: Notification) {
  await apiClient.post('/notifications/test', notification);
}

export async function deleteNotification(notificationId: number) {
  await apiClient.delete(`/notifications/${notificationId}`);
}

export async function editNotification(notification: EditNotification) {
  await apiClient.put(`/notifications/${notification.id}`, notification);
}