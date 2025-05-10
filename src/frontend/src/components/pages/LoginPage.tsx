import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/solid'
import {
  Button,
  IconButton,
  InputAdornment,
  Link,
  Paper,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material'
import React, { useState } from 'react'
import { useNavigate } from 'react-router'
import { loginUser } from '../../api/apiRequests'
import Content from '../layout/Content.tsx'
import { useSnackbar } from '../provider/SnackbarProvider.tsx'
import ProtectedPage from './ProtectedPage.tsx'
import './LoginPage.scss'
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/16/solid";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loggingIn, setLoggingIn] = useState(false)
  const [usernameError, setUsernameError] = useState(false)
  const [passwordError, setPasswordError] = useState(false)

  const navigate = useNavigate()
  const { loading, error, clear } = useSnackbar()

  const handleClickShowPassword = () => setShowPassword(show => !show)

  const handleMouseDownPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
  }

  const handleMouseUpPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
  }

  const validateFields = () => {
    let valid = true
    if (username === '') {
      setUsernameError(true)
      valid = false
    }
    else {
      setUsernameError(false)
    }
    if (password === '') {
      setPasswordError(true)
      valid = false
    }
    else {
      setPasswordError(false)
    }
    return valid
  }

  async function login() {
    if (!validateFields()) {
      return
    }
    loading('Logging in...')
    try {
      setLoggingIn(true)
      const successful = await loginUser(username, password)
      if (successful) {
        await navigate('/')
      }
      clear()
    }
    catch {
      error('Invalid username or password')
    }
    finally {
      setLoggingIn(false)
    }
  }

  async function handlePasswordFieldKeyDown(event: React.KeyboardEvent<HTMLDivElement>) {
    if (event.key === 'Enter') {
      await login()
    }
  }

  return (
    <ProtectedPage loginPage>
      <Content>
        <div className="login">
          <img src="/images/logo.svg" alt="enterr logo"/>
          <Paper className="login-card">
            <TextField
              disabled={loggingIn}
              label="Username"
              variant="filled"
              fullWidth
              required
              value={username}
              onChange={event => setUsername(event.target.value)}
              error={usernameError}
              helperText={usernameError ? 'Username is required' : ''}
            />
            <TextField
              disabled={loggingIn}
              required
              value={password}
              variant="filled"
              fullWidth
              onChange={event => setPassword(event.target.value)}
              type={showPassword ? 'text' : 'password'}
              slotProps={{
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label={
                          showPassword ? 'hide the password' : 'display the password'
                        }
                        onClick={handleClickShowPassword}
                        onMouseDown={handleMouseDownPassword}
                        onMouseUp={handleMouseUpPassword}
                        edge="end"
                        tabIndex={-1}
                      >
                        {showPassword ? <EyeSlashIcon className="icon" /> : <EyeIcon className="icon" />}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
              label="Password"
              error={passwordError}
              helperText={passwordError ? 'Password is required' : ''}
              onKeyDown={event => void handlePasswordFieldKeyDown(event)}
            />
            <Button
              variant="contained"
              disabled={loggingIn}
              fullWidth
              onClick={() => void login()}
            >
              login
            </Button>
            <Tooltip title="You can reset your password via the terminal. See GitHub for more information.">
              <Link className="forgot-password" target="_blank" rel="noopener" href="https://github.com/JonBunator/Enterr" sx={{ fontSize: 14 }}>Forgot password?<ArrowTopRightOnSquareIcon className="icon-small"/></Link>
            </Tooltip>
          </Paper>
        </div>
      </Content>
    </ProtectedPage>
  )
}
