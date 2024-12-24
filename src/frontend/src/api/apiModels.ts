export interface ActionInterval {
  id: number
  date_minutes_start: number
  date_minutes_end: number
  allowed_time_minutes_start: number
  allowed_time_minutes_end: number
}

export interface ExpirationInterval {
  days: number
  hours: number
  minutes: number
}

export interface NextSchedule {
  day: number
  hour: number
  minute: number
  month: number
  year: number
}

export interface CutomAccess {
  id: number
  username_xpath: number
  password_xpath: string
  pin_xpath: string | null
  submit_button_xpath: string
}

export interface Website {
  id: number
  url: string
  success_url: string
  name: string
  username: string
  password: string
  pin: string | null
  expiration_interval: ExpirationInterval | null
  custom_access: CutomAccess | null
  action_interval: ActionInterval | null
  next_schedule: NextSchedule | null
}

export type ActionStatusCode = 'SUCCESS' | 'FAILED' | 'IN_PROGRESS'

export interface ActionHistory {
  id: number
  execution_started: string
  execution_ended: string | null
  execution_status: ActionStatusCode
  failed_details: string | null
}
