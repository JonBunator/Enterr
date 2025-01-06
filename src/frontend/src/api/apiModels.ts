export interface ActionInterval {
  id: number
  date_minutes_start: number
  date_minutes_end: number
  allowed_time_minutes_start: number
  allowed_time_minutes_end: number
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
  username_xpath: string
  password_xpath: string
  pin_xpath: string
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
  take_screenshot: boolean
  expiration_interval_minutes: number | null
  custom_access: CutomAccess | null
  action_interval: ActionInterval | null
  next_schedule: NextSchedule | null
}

export type ActionStatusCode = 'SUCCESS' | 'FAILED' | 'IN_PROGRESS'

export enum FailedDetails {
  AUTOMATIC_FORM_DETECTION_FAILED = 'AUTOMATIC_FORM_DETECTION_FAILED',
  USERNAME_FIELD_NOT_FOUND = 'USERNAME_FIELD_NOT_FOUND',
  PASSWORD_FIELD_NOT_FOUND = 'PASSWORD_FIELD_NOT_FOUND',
  PIN_FIELD_NOT_FOUND = 'PIN_FIELD_NOT_FOUND',
  SUBMIT_BUTTON_NOT_FOUND = 'SUBMIT_BUTTON_NOT_FOUND',
}

export interface ActionHistory {
  id: number
  execution_started: string
  execution_ended: string | null
  execution_status: ActionStatusCode
  failed_details: FailedDetails | null
  screenshot_id: string | null
}
