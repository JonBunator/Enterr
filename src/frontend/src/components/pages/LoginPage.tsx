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
import { useState } from 'react'
import { useNavigate } from 'react-router'
import { loginUser } from '../../api/apiRequests'
import Content from '../layout/Content.tsx'
import { useSnackbar } from '../provider/SnackbarProvider.tsx'
import ProtectedPage from './ProtectedPage.tsx'
import './LoginPage.scss'

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const navigate = useNavigate()
  const { error } = useSnackbar()

  const handleClickShowPassword = () => setShowPassword(show => !show)

  const handleMouseDownPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
  }

  const handleMouseUpPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
  }

  async function login() {
    try {
      const successful = await loginUser(username, password)
      if (successful) {
        await navigate('/')
      }
    }
    catch {
      error('Invalid username or password')
    }
  }

  return (
    <ProtectedPage loginPage>
      <Content>
        <div className="login">
          <Typography variant="h3" component="h2">Enterr</Typography>
          <Paper className="login-card">
            <TextField label="Username" variant="filled" fullWidth required value={username} onChange={event => setUsername(event.target.value)} />
            <TextField
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
            />
            <Button
              variant="contained"
              fullWidth
              onClick={() => void login()}
            >
              login
            </Button>
            <Tooltip title="You can reset your password via the terminal. See GitHub for more information.">
              <Link className="forgot-password" target="_blank" rel="noopener" href="https://github.com/JonBunator/Enterr" sx={{ fontSize: 14 }}>Forgot password?</Link>
            </Tooltip>
          </Paper>
        </div>
      </Content>
    </ProtectedPage>

  )
}
