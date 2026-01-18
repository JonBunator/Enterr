import type { ActionHistory } from '../../api/apiModels.ts'
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

export interface ActionInterval {
  date_minutes_start: number
  date_minutes_end: number | null
  allowed_time_minutes_start: number | null
  allowed_time_minutes_end: number | null
}

export interface ChangeWebsite {
  url?: string;
  success_url?: string;
  name?: string;
  username?: string;
  password?: string;
  take_screenshot?: boolean;
  paused?: boolean;
  expiration_interval_minutes?: number | null;
  custom_login_script?: string | null;
  action_interval?: ActionInterval | null;
}
