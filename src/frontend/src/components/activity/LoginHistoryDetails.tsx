import type { ActionHistory } from '../../api/apiModels.ts'
import type { ActivityStatusCode } from './StatusIcon.tsx'
import { Paper, Popover, Typography } from '@mui/material'
import React, { useState } from 'react'
import { FailedDetails } from '../../api/apiModels.ts'
import ImageDialog from './ImageDialog.tsx'
import Screenshot from './Screenshot.tsx'
import StatusIcon from './StatusIcon.tsx'
import './LoginHistoryDetails.scss'

interface LoginHistoryDetailsProps {
  loginHistory: ActionHistory
}

export default function LoginHistoryDetails(props: LoginHistoryDetailsProps) {
  const { loginHistory } = props
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)
  const [imageDialogOpen, setImageDialogOpen] = useState(false)

  const handleMouseEnter = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMouseLeave = () => {
    setTimeout(() => setAnchorEl(null), 200)
  }

  function getStatusText(): string {
    switch (loginHistory.execution_status) {
      case 'SUCCESS':
        if (loginHistory.execution_started === loginHistory.execution_ended) {
          return 'Login was successful (Manually added)'
        }
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
    let message: string;

    switch (loginHistory.failed_details) {
      case FailedDetails.AUTOMATIC_FORM_DETECTION_FAILED:
        message = 'Automatic form detection failed. Try to define custom xpaths or submit an issue on GitHub.';
        break;
      case FailedDetails.USERNAME_FIELD_NOT_FOUND:
        message = 'Username field not found. Try to define custom username xpath or submit an issue on GitHub.';
        break;
      case FailedDetails.PASSWORD_FIELD_NOT_FOUND:
        message = 'Password field not found. Try to define custom password xpath or submit an issue on GitHub.';
        break;
      case FailedDetails.PIN_FIELD_NOT_FOUND:
        message = 'PIN field not not found. Try to define custom PIN xpath or submit an issue on GitHub.';
        break;
      case FailedDetails.SUBMIT_BUTTON_NOT_FOUND:
        message = 'Submit button not found. Try to define custom submit button xpath or submit an issue on GitHub.';
        break;
      case FailedDetails.SUCCESS_URL_DID_NOT_MATCH:
        message = 'The success URL did not match after login attempt.';
        break;
      case FailedDetails.UNKNOWN_EXECUTION_ERROR:
        message = 'An unknown error occurred while executing task.';
        break;
      case null:
        message = 'Unknown error';
        break;
      default:
        message = 'Unknown error';
    }

    const customMessage = loginHistory.custom_failed_details_message;

    return message + `${customMessage !== null ? " " + customMessage : ''}`;
  }
  const open = Boolean(anchorEl)

  function openImageDialog() {
    setImageDialogOpen(true)
    setAnchorEl(null)
  }

  return (
    <>
      <ImageDialog screenshotId={loginHistory.screenshot_id} open={imageDialogOpen} onClose={() => setImageDialogOpen(false)} />
      <div
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <StatusIcon hover onClick={loginHistory.screenshot_id !== null ? openImageDialog : undefined} activityStatus={loginHistory.execution_status as ActivityStatusCode} />
        <Popover
          className="login-history-details"
          open={open}
          anchorEl={anchorEl}
          onClose={handleMouseLeave}
          anchorOrigin={{
            vertical: 28,
            horizontal: 'center',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'center',
          }}
        >
          {loginHistory.screenshot_id !== null
            ? (
                <Screenshot screenshotId={loginHistory.screenshot_id} />
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
                {new Date(loginHistory.execution_started).toLocaleString()}
              </Typography>
              <Typography>
                <b>End time: </b>
                {loginHistory.execution_ended !== null ? new Date(loginHistory.execution_ended).toLocaleString() : 'Not finished yet'}
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
    </>

  )
}
