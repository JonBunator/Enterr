import type {
  ChangeWebsite,
} from "../components/activity/activityRequests.ts";
import {
  ActionHistory,
  EditNotification,
  Notification,
  UserData,
  Website,
} from "./apiModels.ts";
import apiClient from "./apiClient.ts";

export async function getWebsites(): Promise<Website[]> {
  const data = await apiClient.get('/websites')
  return data.data as Website[]
}

export async function getWebsite(website_id: number): Promise<Website> {
  const data = await apiClient.get(`/websites/${website_id}`)
  return data.data as Website
}

export async function getLoginHistory(website_id: number): Promise<ActionHistory[]> {
  const data = await apiClient.get(`/action_history/${website_id}`)
  return data.data as ActionHistory[]
}

export async function getUserData(): Promise<UserData> {
  const data = await apiClient.get(`/user/data`)
  return data.data as UserData;
}

export async function addWebsite(website: ChangeWebsite) {
  await apiClient.post('/websites/add', website);
}

export async function deleteWebsite(websiteId: number) {
  const body = { id: websiteId }
  await apiClient.post('/websites/delete', body);
}

export async function editWebsite(websiteId: number, website: ChangeWebsite) {
  const body = { id: websiteId, ...website };
  await apiClient.post("/websites/edit", body);
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
  const body = { id: websiteId }
  await apiClient.post('/action_history/manual_add', body);
}

export async function triggerAutomaticLogin(websiteId: number) {
  const body = { id: websiteId }
  await apiClient.post('/trigger_login', body);
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
  return data.data as Notification[]
}

export async function addNotification(notification: Notification) {
  await apiClient.post('/notifications/add', notification);
}

export async function testNotification(notification: Notification) {
  await apiClient.post('/notifications/test', notification);
}

export async function deleteNotification(notificationId: number) {
  const body = { id: notificationId }
  await apiClient.post('/notifications/delete', body);
}

export async function editNotification(notification: EditNotification) {
  await apiClient.post('/notifications/edit', notification);
}