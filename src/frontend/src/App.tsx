import CssBaseline from '@mui/material/CssBaseline'
import { createTheme, ThemeProvider } from '@mui/material/styles'
import { LocalizationProvider } from '@mui/x-date-pickers'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { BrowserRouter, Route, Routes } from 'react-router'
import LoginPage from './components/pages/LoginPage.tsx'
import MainPage from './components/pages/MainPage.tsx'
import SnackbarProvider from './components/provider/SnackbarProvider.tsx'
import WebSocketProvider from './components/provider/WebSocketProvider.tsx'
import ReactQueryProvider from './components/provider/ReactQueryProvider.tsx'
import './globalStyles.scss'
import SettingsPage from "./components/pages/SettingsPage.tsx";
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';


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
      main: '#8dbf9f',
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
            <ReactQueryProvider>
              <BrowserRouter>
                <Routes>
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/" element={<MainPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Routes>
              </BrowserRouter>
            </ReactQueryProvider>
          </WebSocketProvider>
        </SnackbarProvider>
      </LocalizationProvider>
    </ThemeProvider>
  )
}
