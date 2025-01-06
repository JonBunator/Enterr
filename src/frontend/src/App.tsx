import CssBaseline from '@mui/material/CssBaseline'
import { createTheme, ThemeProvider } from '@mui/material/styles'
import { LocalizationProvider } from '@mui/x-date-pickers'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import Content from './components/Content'
import WebSocketProvider from './components/WebSocketProvider'
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
        <WebSocketProvider>
          <Content />
        </WebSocketProvider>
      </LocalizationProvider>
    </ThemeProvider>
  )
}
