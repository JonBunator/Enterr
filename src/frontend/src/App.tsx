import CssBaseline from '@mui/material/CssBaseline'
import { createTheme, ThemeProvider } from '@mui/material/styles'
import { LocalizationProvider } from '@mui/x-date-pickers'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import Content from './components/Content'
import WebSocketProvider from './components/WebSocketProvider'
import './globalStyles.scss'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
})
export default function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <CssBaseline />
        <WebSocketProvider>
          <Content />
        </WebSocketProvider>
      </LocalizationProvider>
    </ThemeProvider>
  )
}
