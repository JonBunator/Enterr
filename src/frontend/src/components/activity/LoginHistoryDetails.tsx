import type { ActionHistory } from '../../api/apiModels.ts'
import type { ActivityStatusCode } from './StatusIcon.tsx'
import { Paper, Popover, Typography } from '@mui/material'
import React, { useState } from 'react'
import { FailedDetails } from '../../api/apiModels.ts'
import StatusIcon from './StatusIcon.tsx'
import './LoginHistoryDetails.scss'

interface LoginHistoryDetailsProps {
  loginHistory: ActionHistory
}

export default function LoginHistoryDetails(props: LoginHistoryDetailsProps) {
  const { loginHistory } = props
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)

  const handleMouseEnter = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMouseLeave = () => {
    setTimeout(() => setAnchorEl(null), 200)
  }

  function getStatusText(): string {
    switch (loginHistory.execution_status) {
      case 'SUCCESS':
        return 'Login was successful'
      case 'FAILED':
        return 'Login failed'
      case 'IN_PROGRESS':
        return 'Task is still running'
      default:
        return 'Unknown'
    }
  }

  function getExecutionTime(): string {
    const startTime = new Date(loginHistory.execution_started)
    if (loginHistory.execution_ended === null) {
      return 'Not finished yet'
    }
    const endTime = new Date(loginHistory.execution_ended)
    const diff = endTime.getTime() - startTime.getTime()
    const seconds = Math.floor(diff / 1000)
    return `${seconds} seconds`
  }

  function getFailedDetails(): string {
    switch (loginHistory.failed_details) {
      case FailedDetails.AUTOMATIC_FORM_DETECTION_FAILED:
        return 'Automatic form detection failed. Try to define custom xpaths or submit a issue on GitHub.'
      case FailedDetails.USERNAME_FIELD_NOT_FOUND:
        return 'Username field not found. Try to define custom username xpath or submit a issue on GitHub.'
      case FailedDetails.PASSWORD_FIELD_NOT_FOUND:
        return 'Password field not found. Try to define custom password xpath or submit a issue on GitHub.'
      case FailedDetails.PIN_FIELD_NOT_FOUND:
        return 'PIN field not found. Try to define custom PIN xpath or submit a issue on GitHub.'
      case FailedDetails.SUBMIT_BUTTON_NOT_FOUND:
        return 'Submit button not found. Try to define custom submit button xpath or submit a issue on GitHub.'
      case null: { throw new Error('Not implemented yet: null case') }
      default:
        return 'Unknown error'
    }
  }
  const open = Boolean(anchorEl)

  return (
    <div
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <StatusIcon hover activityStatus={loginHistory.execution_status as ActivityStatusCode} />
      <Popover
        className="login-history-details"
        open={open}
        anchorEl={anchorEl}
        onClose={handleMouseLeave}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'center',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}
      >
        {loginHistory.screenshot_id !== null
          ? (
              <img className="screenshot" src={`/api/screenshot/${loginHistory.screenshot_id}`} alt="Login Screenshot" />
            )
          : (
              []
            )}
        <div>
          <Paper className="login-history-details-header">
            <StatusIcon activityStatus={loginHistory.execution_status as ActivityStatusCode} />
            <Typography>{getStatusText()}</Typography>
          </Paper>
          <div className="login-history-details-content">
            <Typography>
              <b>Start time: </b>
              {loginHistory.execution_started}
            </Typography>
            <Typography>
              <b>End time: </b>
              {loginHistory.execution_ended !== null ? loginHistory.execution_ended : 'Not finished yet'}
            </Typography>
            <Typography>
              <b>Execution time: </b>
              {getExecutionTime()}
            </Typography>
            {loginHistory.failed_details !== null
            && (
              <Typography>
                <b>Failed details: </b>
                {getFailedDetails()}
              </Typography>
            )}
          </div>

        </div>
      </Popover>
    </div>
  )
}
