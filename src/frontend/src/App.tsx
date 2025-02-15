import CssBaseline from '@mui/material/CssBaseline'
import { createTheme, ThemeProvider } from '@mui/material/styles'
import { LocalizationProvider } from '@mui/x-date-pickers'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { BrowserRouter, Route, Routes } from 'react-router'
import LoginPage from './components/pages/LoginPage.tsx'
import MainPage from './components/pages/MainPage.tsx'
import SnackbarProvider from './components/provider/SnackbarProvider.tsx'
import WebSocketProvider from './components/provider/WebSocketProvider.tsx'
import './globalStyles.scss'

const darkTheme = createTheme({
  components: {
    MuiDialog: {
      defaultProps: {
        PaperProps: {
          elevation: 2,
        },
      },
    },
    MuiPaper: {
      defaultProps: {
        elevation: 1,
      },
    },
  },
  palette: {
    mode: 'dark',
    primary: {
      main: '#c2b8fc',
    },
    background: {
      default: '#080808',
      paper: '#080808',
    },
  },
})
export default function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <CssBaseline />
        <SnackbarProvider>
          <WebSocketProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/" element={<MainPage />} />
              </Routes>
            </BrowserRouter>
          </WebSocketProvider>
        </SnackbarProvider>
      </LocalizationProvider>
    </ThemeProvider>
  )
}
